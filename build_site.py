import datetime
import math
import time
import json
import os
import argparse
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from jsonschema import validate, ValidationError

# -----------------------------
# Configuration
# -----------------------------
PAGES_FILE = Path("data/pages.json")
ROCKETS_FILE = Path("data/rockets.json")
ROCKETS_SCHEMA_FILE = Path("models/rockets.schema.json")
OUTPUT_DIR = Path("output_site")
TEMPLATE_DIR = Path("templates")
ASSETS_DIR = Path("assets")

ITEMS_PER_PAGE = 25

INDEX_TITLE = "Home"
INDEX_DESCRIPTION = "SpaceDB home page listing rocket pages"

ROCKETS_TITLE_PATTERN = "Rockets – Page {page_num}"
ROCKETS_DESCRIPTION_PATTERN = "SpaceDB listing rockets – page {page_num}"

ROCKET_TITLE_PATTERN = "{rocket_name} ({manufacturer})"
ROCKET_DESCRIPTION_PATTERN = "{rocket_name} – Manufacturer: {manufacturer}, First Flight: {first_flight}"

# -----------------------------
# Helper Functions
# -----------------------------
def copy_assets(src_dir: Path, dest_dir: Path):
    dest_dir.mkdir(parents=True, exist_ok=True)
    for file_path in src_dir.iterdir():
        if file_path.is_file():
            (dest_dir / file_path.name).write_bytes(file_path.read_bytes())

def render_template(env, template_name, output_path, **context):
    template = env.get_template(template_name)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(template.render(**context), encoding="utf-8")

def compute_base_url(output_path: Path):
    depth = len(output_path.relative_to(OUTPUT_DIR).parents) - 1
    if depth <= 0:
        return ""
    return "../" * depth

def compute_home_link(output_path: Path):
    return compute_base_url(output_path) + "index.html"

def load_json(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)

def remove_and_recreate_dir(path):
    if os.path.exists(path):
        for entry in os.listdir(path):
            entry_path = os.path.join(path, entry)
            if os.path.isfile(entry_path) or os.path.islink(entry_path):
                os.remove(entry_path)
            elif os.path.isdir(entry_path):
                remove_and_recreate_dir(entry_path)
                os.rmdir(entry_path)
        try:
            os.rmdir(path)
        except OSError:
            pass
    os.makedirs(path, exist_ok=True)

def validate_json(data, schema):
    try:
        validate(instance=data, schema=schema)
    except ValidationError as e:
        raise ValueError(f"JSON validation failed: {e}")

def get_pagination_range(current_page, total_pages, delta=3):
    range_pages = []

    if current_page - delta > 2:
        range_pages.append(1)
        range_pages.append('...')
        start = current_page - delta
    else:
        start = 1

    if current_page + delta < total_pages - 1:
        end = current_page + delta
    else:
        end = total_pages

    range_pages.extend(range(start, end + 1))

    if end < total_pages:
        range_pages.append('...')
        range_pages.append(total_pages)

    return range_pages

# -----------------------------
# Page Generators
# -----------------------------
def generate_index(env, pages, current_date, commit_sha="", num_rockets=0, num_variants=0):
    output_path = OUTPUT_DIR / "index.html"
    render_template(
        env, "index.html", output_path,
        title=INDEX_TITLE,
        description=INDEX_DESCRIPTION,
        canonical="index.html",
        pages=pages,
        date=current_date,
        base_url=compute_base_url(output_path),
        home_link=compute_home_link(output_path),
        num_rockets=num_rockets,
        num_variants=num_variants,
        commit_sha=commit_sha
    )
    
def generate_about_page(env, current_date, commit_sha=""):
    output_path = OUTPUT_DIR / "about.html"
    render_template(
        env, "about.html", output_path,
        title="About SpaceDB",
        description="Learn about SpaceDB, an open-source rocket and launch database",
        canonical="about.html",
        date=current_date,
        base_url=compute_base_url(output_path),
        home_link=compute_home_link(output_path),
        commit_sha=commit_sha
    )

    

def generate_rockets_pages(env, rockets, current_date, commit_sha=""):
    total_pages = math.ceil(len(rockets) / ITEMS_PER_PAGE)
    template_name = "rockets.html"

    for page_num in range(1, total_pages + 1):
        start = (page_num - 1) * ITEMS_PER_PAGE
        rockets_page = rockets[start:start + ITEMS_PER_PAGE]
        pagination = get_pagination_range(page_num, total_pages, delta=3)

        rockets_path = OUTPUT_DIR / (f"rockets.html" if page_num == 1 else f"rockets_page_{page_num}.html")

        render_template(
            env, template_name, rockets_path,
            title=ROCKETS_TITLE_PATTERN.format(page_num=page_num),
            description=ROCKETS_DESCRIPTION_PATTERN.format(page_num=page_num),
            canonical=f"{rockets_path.name}",
            rockets=rockets_page,
            current_page=page_num,
            total_pages=total_pages,
            pagination=pagination,
            date=current_date,
            base_url=compute_base_url(rockets_path),
            home_link=compute_home_link(rockets_path),
            commit_sha=commit_sha
        )

def generate_rocket_and_variant_pages(env, rockets, current_date, commit_sha=""):
    rocket_dir = OUTPUT_DIR / "rocket"
    rocket_dir.mkdir(parents=True, exist_ok=True)

    for rocket in rockets:
        rocket.setdefault("manufacturer", "Unknown")
        rocket.setdefault("first_flight", "Unknown")
        rocket.setdefault("rocket_height", 0)
        rocket.setdefault("stages", 0)
        rocket.setdefault("strap_ons", 0)
        rocket.setdefault("liftoff_thrust", 0)
        rocket.setdefault("payload_LEO", 0)
        rocket.setdefault("payload_GTO", 0)
        rocket.setdefault("missions", 0)
        rocket.setdefault("launches", [])

        for v in rocket.get("variants", []):
            v.setdefault("name", "Unknown")
            v.setdefault("slug", "unknown")
            v.setdefault("first_flight", "Unknown")
            v.setdefault("remarks", "")

        # Rocket page
        rocket_path = rocket_dir / f"{rocket['slug']}.html"
        render_template(
            env, "rocket.html", rocket_path,
            title=f"{rocket['name']} ({rocket['manufacturer']})",
            description=f"{rocket['name']} – Manufacturer: {rocket['manufacturer']}, First Flight: {rocket['first_flight']}",
            canonical=f"rocket/{rocket['slug']}.html",
            rocket=rocket,
            date=current_date,
            base_url=compute_base_url(rocket_path),
            home_link=compute_home_link(rocket_path),
            show_title=True,
            commit_sha=commit_sha
        )

        # Variant pages
        variant_dir = rocket_dir / rocket['slug']
        variant_dir.mkdir(parents=True, exist_ok=True)
        for variant in rocket.get("variants", []):
            variant_path = variant_dir / f"{variant['slug']}.html"
            render_template(
                env, "variant.html", variant_path,
                title=f"{variant['name']} ({rocket['manufacturer']})",
                description=f"{variant['name']} – First Flight: {variant['first_flight']}",
                canonical=f"rocket/{rocket['slug']}/{variant['slug']}.html",
                variant=variant,
                rocket=rocket,
                date=current_date,
                base_url=compute_base_url(variant_path),
                home_link=compute_home_link(variant_path),
                show_title=True,
                commit_sha=commit_sha
            )

# -----------------------------
# Main Script
# -----------------------------
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--commit-sha", default="", help="Git commit SHA for footer display")
    args = parser.parse_args()
    commit_sha = args.commit_sha

    start_time = time.time()
    current_date = datetime.datetime.now().strftime("%Y-%m-%d")

    rockets = load_json(ROCKETS_FILE)
    validate_json(rockets, load_json(ROCKETS_SCHEMA_FILE))
    pages = load_json(PAGES_FILE)
    rockets.sort(key=lambda r: r["name"].lower())

    remove_and_recreate_dir(OUTPUT_DIR)
    copy_assets(ASSETS_DIR, OUTPUT_DIR / "assets")

    env = Environment(loader=FileSystemLoader(str(TEMPLATE_DIR)))

    total_rockets = len(rockets)
    total_variants = sum(len(r.get("variants", [])) for r in rockets)

    generate_index(env, pages, current_date, commit_sha=commit_sha, num_rockets=total_rockets, num_variants=total_variants)
    generate_about_page(env, current_date, commit_sha=commit_sha)

    generate_rockets_pages(env, rockets, current_date, commit_sha=commit_sha)
    generate_rocket_and_variant_pages(env, rockets, current_date, commit_sha=commit_sha)

    total_pages_created = (
        1 +
        math.ceil(len(rockets) / ITEMS_PER_PAGE) +
        len(rockets) +
        sum(len(r.get("variants", [])) for r in rockets)
    )
    elapsed_time = time.time() - start_time
    print(f"Site generated in '{OUTPUT_DIR}' folder.")
    print(f"Total pages created: {total_pages_created}")
    print(f"Time elapsed: {elapsed_time:.2f} seconds")
