from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path
import os

from utils import (
    load_merged_data,
    load_merged_routes,
    format_us_date,
    shuffle,
    format_date_range,
    minify_html,
    reload_env_vars,
    unique,
)

BASE_DIR = Path(__file__).parent
TEMPLATE_DIR = BASE_DIR / "templates"
STATIC_DIR = BASE_DIR / "static"

allowed_routes = load_merged_routes()
app = FastAPI(title="Portfolio Web Server", docs_url=None, redoc_url=None)

# Jinja2
templates = Jinja2Templates(directory=str(TEMPLATE_DIR))
templates.env.filters["format_us_date"] = format_us_date
templates.env.filters["shuffle"] = shuffle
templates.env.filters["date_range"] = format_date_range
templates.env.filters["unique"] = unique


@app.get("/{path:path}", response_class=HTMLResponse)
async def handle_request(request: Request, path: str = ""):
    route = "/" + path if path else "/"

    # Check if it's an allowed HTML route
    if route in allowed_routes:
        template_rel_path = allowed_routes[route]
        template_path = TEMPLATE_DIR / template_rel_path
        if not template_path.exists():
            raise HTTPException(status_code=404, detail=f"Template not found: {template_rel_path}")

        try:
            reload_env_vars()
            template = templates.get_template(template_rel_path)
            data = load_merged_data()
            data["env"] = dict(os.environ)
            data["__ctx__"] = data

            html = template.render(request=request, **data)
            html = minify_html(html)
            print(f"Served template {route} → {template_rel_path}")
            return HTMLResponse(content=html, status_code=200)
        except Exception as e:
            print(f"❌ Error rendering route {route}: {e}")
            raise HTTPException(status_code=500, detail=f"Error rendering template: {e}")

    # Otherwise, check if it's a static file in STATIC_DIR
    static_file = STATIC_DIR / path
    if static_file.exists() and static_file.is_file():
        print(f"Served static file /{path}")
        return FileResponse(static_file)

    # Not found
    raise HTTPException(status_code=404, detail=f"Route or file not found: {route}")
