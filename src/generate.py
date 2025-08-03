import requests
import shutil
from pathlib import Path
from urllib.parse import urljoin
from utils import load_merged_routes

# Base settings
BASE_URL = "http://localhost:8000"
allowed_routes = load_merged_routes()

ASSET_DIR = Path(__file__).parent / "assets"
OUTPUT_DIR = Path(__file__).parent.parent / "output"

# Clean output directory
if OUTPUT_DIR.exists():
    for item in OUTPUT_DIR.iterdir():
        if item.is_file() or item.is_symlink():
            item.unlink()
        elif item.is_dir():
            shutil.rmtree(item)
else:
    OUTPUT_DIR.mkdir(parents=True)

# Step 1: Copy assets
shutil.copytree(ASSET_DIR, OUTPUT_DIR, dirs_exist_ok=True)
print("✅ Copied assets")

# Download each route from the web server
for route in allowed_routes:
    try:
        url = urljoin(BASE_URL, route)
        response = requests.get(url)
        response.raise_for_status()

        # Determine output file path
        relative_path = Path(route.lstrip("/")) or Path("index.html")
        if route.endswith("/") or relative_path.suffix != ".html":
            relative_path = relative_path / "index.html"

        output_path = OUTPUT_DIR / relative_path
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_bytes(response.content)

        print(f"✅ Saved {url} → {output_path.relative_to(OUTPUT_DIR)}")

    except requests.RequestException as e:
        print(f"❌ Failed to fetch {route}: {e}")

print("🎉 Static site build complete.")
