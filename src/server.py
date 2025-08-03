import mimetypes
import urllib.parse
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from utils import load_merged_data, load_merged_routes, format_us_date, shuffle, format_date_range
import re

allowed_routes = load_merged_routes()

# Jinja2 environment
TEMPLATE_DIR = Path(__file__).parent / "templates"
ASSET_DIR = Path(__file__).parent / "assets"
env = Environment(loader=FileSystemLoader(str(TEMPLATE_DIR)))
env.filters['format_us_date'] = format_us_date
env.filters['shuffle'] = shuffle
env.filters['date_range'] = format_date_range


class RequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed_path = urllib.parse.urlparse(self.path)
        route = parsed_path.path

        # Serve static assets freely
        if route.startswith("/assets/"):
            return self.serve_asset(route)

        # Restrict to known routes
        if route not in allowed_routes:
            self.send_error(404, f"Route not allowed: {route}")
            return

        # Map route to template path
        if route == "/":
            template_rel_path = "index.html"
        else:
            rel_path = route.lstrip("/")
            if rel_path.endswith("/"):
                rel_path += "index.html"
            template_rel_path = rel_path

        template_path = TEMPLATE_DIR / template_rel_path
        if not template_path.exists():
            self.send_error(404, f"Template not found: {template_rel_path}")
            return

        try:
            template = env.get_template(template_rel_path)
            data = load_merged_data()
            data["__ctx__"] = data
            html = template.render(**data)

            # Step 1: Collapse multiple spaces between tag attributes
            def collapse_tag_attributes(match):
                tag = match.group(0)
                # Replace any whitespace (except inside quotes) with a single space
                # Assumes tag does not span multiple lines unnecessarily
                tag = re.sub(r'\s{2,}', ' ', tag)  # collapse multiple spaces
                return tag

            html = re.sub(r'<[^>]+>', collapse_tag_attributes, html)

            # Step 2: Replace any whitespace between tags with a single space
            html = re.sub(r'>\s+<', '> <', html)

            # Step 3: Collapse internal content whitespace to one space
            def collapse_content_whitespace(match):
                text = match.group(1)
                text = re.sub(r'\s+', ' ', text)
                return f'>{text}<'

            html = re.sub(r'>([^<]+)<', collapse_content_whitespace, html)

            html = html.strip()

        except Exception as e:
            self.send_error(500, f"Error rendering template: {e}")
            return

        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.end_headers()
        self.wfile.write(html.encode("utf-8"))

    def serve_asset(self, path: str):
        rel_path = Path(path).relative_to("/assets")

        # Prioritize custom asset if it exists
        custom_asset = Path(__file__).parent.parent / "assets" / rel_path
        default_asset = Path(__file__).parent / "assets" / rel_path

        asset_path = custom_asset if custom_asset.exists() else default_asset

        if not asset_path.exists() or not asset_path.is_file():
            self.send_error(404, f"Asset not found: {path}")
            return

        mime_type, _ = mimetypes.guess_type(str(asset_path))
        self.send_response(200)
        self.send_header("Content-Type", mime_type or "application/octet-stream")
        self.end_headers()
        self.wfile.write(asset_path.read_bytes())


if __name__ == "__main__":
    print("🌐 Webserver running at http://localhost:8000")
    print("🧩 Serving only these routes:", ", ".join(sorted(allowed_routes)))
    print("🖼  Templates: /templates | Assets: /assets")

    server = HTTPServer(("0.0.0.0", 8000), RequestHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Server stopped.")
