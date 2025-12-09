import datetime
import math
import time
import json
import logging
import shutil
import argparse
from pathlib import Path
from typing import List, Dict, Any, Union

from jinja2 import Environment, FileSystemLoader, select_autoescape
from jsonschema import validate, ValidationError

# -----------------------------
# Configuration (Explicitly Defined)
# -----------------------------
PAGES_FILE = Path("data/pages.json")
ROCKETS_FILE = Path("data/rockets.json")
ROCKETS_SCHEMA_FILE = Path("models/rockets.schema.json")

OUTPUT_DIR = Path("output_site")
TEMPLATE_DIR = Path("templates")
ASSETS_DIR = Path("assets")

ITEMS_PER_PAGE = 30

INDEX_TITLE = "Home"
ROCKET_LIST_TITLE = "Rockets"
ABOUT_TITLE = "About SpaceDB"

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s", datefmt="%H:%M:%S")
logger = logging.getLogger(__name__)

# -----------------------------
# Utility Functions
# -----------------------------
def load_json(file_path: Path) -> Any:
    """Loads a JSON file."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        logger.error(f"File not found: {file_path}")
        return []

def cleanup_and_setup(output_path: Path, assets_path: Path):
    """Safely removes and recreates the output directory, then copies assets."""
    if output_path.exists():
        shutil.rmtree(output_path)
    output_path.mkdir(parents=True, exist_ok=True)
    
    if assets_path.exists():
        shutil.copytree(assets_path, output_path / "assets", dirs_exist_ok=True)
    logger.info("Output directory cleaned and assets copied.")

def compute_base_url(output_path: Path) -> str:
    """Calculates the relative path (e.g., '../', '../../') to the root index."""
    try:
        # Determine depth from output_dir
        rel_path = output_path.relative_to(OUTPUT_DIR)
        depth = len(rel_path.parents) - 1
        return "../" * depth if depth > 0 else ""
    except ValueError:
        return "" # Should only happen if output_path isn't in OUTPUT_DIR

def render_template(env: Environment, template_name: str, output_rel_path: str, **context):
    """Renders a Jinja template to a file."""
    output_path = OUTPUT_DIR / output_rel_path
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    base_url = compute_base_url(output_path)
    
    # Global context available to all pages
    full_context = {
        "date": datetime.datetime.now().strftime("%Y-%m-%d"),
        "base_url": base_url,
        "home_link": f"{base_url}index.html",
        **context
    }
    
    template = env.get_template(template_name)
    output_path.write_text(template.render(**full_context), encoding="utf-8")

def get_pagination_range(current: int, total: int, delta: int = 3) -> List[Union[int, str]]:
    """Calculates the range of page numbers for navigation."""
    if total <= 1: return [1]
    start, end = max(2, current - delta), min(total - 1, current + delta)
    pages = [1, "..."] if start > 2 else [1]
    pages.extend(range(start, end + 1))
    pages.extend(["...", total]) if end < total - 1 else pages.append(total) if end < total else None
    return pages

# -----------------------------
# Page Generators
# -----------------------------
def generate_index(env: Environment, pages_data: List[Dict], total_rockets: int, total_variants: int, commit_sha: str):
    """Generates the main index.html file."""
    render_template(
        env, 
        "index.html", 
        "index.html",
        title=INDEX_TITLE,
        description="SpaceDB home page listing catalog entries.",
        canonical="index.html",
        pages=pages_data,
        num_rockets=total_rockets,
        num_variants=total_variants,
        commit_sha=commit_sha
    )
    logger.info("Generated index.html")

def generate_about_page(env: Environment, commit_sha: str):
    """Generates the about.html file."""
    render_template(
        env, 
        "about.html", 
        "about.html",
        title=ABOUT_TITLE,
        description="Learn about SpaceDB.",
        canonical="about.html",
        commit_sha=commit_sha
    )
    logger.info("Generated about.html")

def generate_rockets_listing(env: Environment, rockets: List[Dict], items_per_page: int, commit_sha: str):
    """Generates paginated listing pages for Rockets and their Variants."""
    
    # Flatten rockets + variants into one list for pagination
    rows = []
    for rocket in rockets:
        rows.append({"type": "rocket", "data": rocket})
        for variant in rocket.get("variants", []):
            rows.append({"type": "variant", "data": variant, "root": rocket})

    total_pages = math.ceil(len(rows) / items_per_page)
    
    for page_num in range(1, total_pages + 1):
        start = (page_num - 1) * items_per_page
        page_rows = rows[start : start + items_per_page]
        pagination = get_pagination_range(page_num, total_pages)

        filename = f"{ROCKET_LIST_TITLE.lower()}.html" if page_num == 1 else f"{ROCKET_LIST_TITLE.lower()}_page_{page_num}.html"

        render_template(
            env, 
            "rockets.html", 
            filename,
            title=f"{ROCKET_LIST_TITLE} – Page {page_num}",
            description=f"SpaceDB listing rockets – page {page_num}",
            canonical=filename,
            rockets_page=page_rows,
            current_page=page_num,
            total_pages=total_pages,
            pagination=pagination,
            commit_sha=commit_sha
        )
    logger.info(f"Generated {total_pages} rocket listing page(s).")

def generate_rocket_and_variant_details(env: Environment, rockets: List[Dict], commit_sha: str):
    """Generates individual detail pages for each Rocket and Variant."""
    
    for rocket in rockets:
        r_slug = rocket.get("slug", "unknown-rocket")
        
        # Rocket detail page
        render_template(
            env, 
            "rocket.html", 
            f"rocket/{r_slug}.html",
            title=f"{rocket['name']} ({rocket.get('manufacturer', 'Unknown')})",
            description=f"Details for the {rocket['name']} rocket.",
            canonical=f"rocket/{r_slug}.html",
            rocket=rocket,
            commit_sha=commit_sha
        )

        # Variant detail pages
        for variant in rocket.get("variants", []):
            v_slug = variant.get("slug", "unknown-variant")
            
            render_template(
                env, 
                "variant.html", 
                f"rocket/{r_slug}/{v_slug}.html",
                title=f"{variant['name']} ({rocket.get('manufacturer', 'Unknown')})",
                description=f"Details for the {variant['name']} variant.",
                canonical=f"rocket/{r_slug}/{v_slug}.html",
                variant=variant,
                rocket=rocket,
                commit_sha=commit_sha
            )
    logger.info("Generated all individual rocket and variant detail pages.")

# -----------------------------
# Main Execution Flow (The Simple Script)
# -----------------------------
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--commit-sha", default="", help="Git commit SHA for footer display")
    args = parser.parse_args()
    commit_sha = args.commit_sha

    start_time = time.time()

    # 1. Setup Environment
    cleanup_and_setup(OUTPUT_DIR, ASSETS_DIR)
    
    # Secure Jinja2 Setup
    jinja_env = Environment(
        loader=FileSystemLoader(str(TEMPLATE_DIR)),
        autoescape=select_autoescape(['html', 'xml']),
        trim_blocks=True, 
        lstrip_blocks=True
    )

    # 2. Load and Validate Data
    pages_data = load_json(PAGES_FILE)
    rockets_data = load_json(ROCKETS_FILE)
    
    try:
        validate(instance=rockets_data, schema=load_json(ROCKETS_SCHEMA_FILE))
        logger.info("Rocket data validation successful.")
    except (ValidationError, FileNotFoundError) as e:
        logger.error(f"FATAL: Rocket data validation failed. Aborting. Error: {e}")
        exit(1)

    # Sort data for consistent output
    rockets_data.sort(key=lambda r: r.get("name", "").lower())
    
    total_rockets = len(rockets_data)
    total_variants = sum(len(r.get("variants", [])) for r in rockets_data)
    
    # 3. Generate All Pages Sequentially
    
    # 3a. Static Pages
    generate_index(jinja_env, pages_data, total_rockets, total_variants, commit_sha)
    generate_about_page(jinja_env, commit_sha)
    
    # 3b. Catalog Listing Pages (Rockets)
    generate_rockets_listing(jinja_env, rockets_data, ITEMS_PER_PAGE, commit_sha)
    
    # 3c. Detail Pages (Rockets and Variants)
    generate_rocket_and_variant_details(jinja_env, rockets_data, commit_sha)

    # 4. Final Output
    elapsed_time = time.time() - start_time
    logger.info(f"Site generation finished in {elapsed_time:.2f} seconds.")