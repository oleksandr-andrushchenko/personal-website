import requests
import shutil
from pathlib import Path
from urllib.parse import urljoin
from utils import load_merged_routes

# Base settings
BASE_URL = "http://localhost:8000"
allowed_routes = load_merged_routes()

ASSET_DIR = Path(__file__).parent / "static"
OUTPUT_DIR = Path(__file__).parent.parent / ".site-build"

# Clean output directory
if OUTPUT_DIR.exists():
    for item in OUTPUT_DIR.iterdir():
        if item.is_file() or item.is_symlink():
            item.unlink()
        elif item.is_dir():
            shutil.rmtree(item)
else:
    OUTPUT_DIR.mkdir(parents=True)

# Step 1: Copy static
shutil.copytree(ASSET_DIR, OUTPUT_DIR, dirs_exist_ok=True)
print("✅ Copied static")

# Download each route from the web server
for route, template_path in allowed_routes.items():
    try:
        url = urljoin(BASE_URL, route)
        response = requests.get(url)
        response.raise_for_status()

        output_path = OUTPUT_DIR / template_path
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_bytes(response.content)

        print(f"✅ Saved {url} → {output_path.relative_to(OUTPUT_DIR)}")

    except requests.RequestException as e:
        print(f"❌ Failed to fetch {route}: {e}")

print("🎉 Static site build complete.")
