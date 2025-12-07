import json
import os
from jsonschema import validate, ValidationError

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