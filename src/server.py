import mimetypes
import urllib.parse
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from utils import load_merged_data, load_merged_routes, format_us_date, shuffle, format_date_range, minify_html, \
    reload_env_vars, unique
import os

allowed_routes = load_merged_routes()

# Jinja2 environment
TEMPLATE_DIR = Path(__file__).parent / "templates"
ASSET_DIR = Path(__file__).parent / "assets"
env = Environment(loader=FileSystemLoader(str(TEMPLATE_DIR)))
env.filters['format_us_date'] = format_us_date
env.filters['shuffle'] = shuffle
env.filters['date_range'] = format_date_range
env.filters['unique'] = unique


class RequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed_path = urllib.parse.urlparse(self.path)
        route = parsed_path.path

        # Serve static assets if match
        if self.serve_asset(route):
            return

        # Restrict to known routes
        if route not in allowed_routes:
            self.send_error(404, f"Route not allowed: {route}")
            return

        # Map route to template path
        template_rel_path = allowed_routes.get(route)

        template_path = TEMPLATE_DIR / template_rel_path
        if not template_path.exists():
            self.send_error(404, f"Template not found: {template_rel_path}")
            return

        try:
            reload_env_vars()
            template = env.get_template(template_rel_path)
            data = load_merged_data()
            data["env"] = dict(os.environ)
            data["__ctx__"] = data
            html = template.render(**data)
            html = minify_html(html)
        except Exception as e:
            self.send_error(500, f"Error rendering template: {e}")
            return

        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.end_headers()
        self.wfile.write(html.encode("utf-8"))

    def serve_asset(self, path: str):
        print(path)

        # Strip the leading slash from the route
        rel_path = Path(path.lstrip("/"))
        asset_path = (ASSET_DIR / rel_path).resolve()

        # Prevent directory traversal: ensure it's within the assets folder
        assets_root = ASSET_DIR.resolve()
        if not str(asset_path).startswith(str(assets_root)):
            return False

        # Serve only if it's an existing file
        if not asset_path.exists() or not asset_path.is_file():
            return False

        mime_type, _ = mimetypes.guess_type(str(asset_path))
        self.send_response(200)
        self.send_header("Content-Type", mime_type or "application/octet-stream")
        self.end_headers()
        self.wfile.write(asset_path.read_bytes())
        return True


if __name__ == "__main__":
    print("🌐 Webserver running at http://localhost:8000")
    print("🧩 Serving only these routes:", ", ".join(sorted(allowed_routes)))
    print("🖼  Templates: /templates | Assets: /assets")

    server = HTTPServer(("0.0.0.0", 8000), RequestHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Server stopped.")
