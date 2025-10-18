import os
import json
from datetime import datetime, date
from typing import List, Tuple


def _parse_version_key(tag: str) -> Tuple:
    """
    Parse a version tag into a tuple for sorting purposes.
    Handles semantic versioning with pre-release identifiers.

    Args:
        tag: Version tag string (e.g., "3.10", "1.2.3-alpha", "latest")

    Returns:
        Tuple: Sortable tuple where "latest" sorts last, and versions sort naturally
    """
    if tag == "latest":
        return (float('inf'),)

    try:
        version_part = tag.split('-')[0]
        version_numbers = [int(x) for x in version_part.split('.')]

        if '-' in tag:
            pre_release = tag.split('-', 1)[1]
            return tuple(version_numbers + [0, pre_release])
        else:
            return tuple(version_numbers + [1])

    except ValueError:
        return (tag,)


def get_project_root(*paths: str) -> str:
    """
    Get the project root path and optionally join additional paths.
    Since the Python files are located in the 'Dockerfile/' subdirectory,
    this function navigates up to find the project root.

    Args:
        *paths: Optional path components to join with the project root

    Returns:
        str: The project root path, optionally joined with additional paths
    """
    current_dir = os.path.dirname(os.path.abspath(__file__))

    project_root = os.path.dirname(current_dir)

    if paths:
        return os.path.join(project_root, *paths)

    return project_root


def discover_builds() -> List[Tuple[str, str]]:
    """
    Automatically discover available build configurations by scanning directories.
    Only returns builds that are not yet in end_of_life status.

    Returns:
        List[Tuple[str, str]]: List of (name, tag) tuples for available builds that are still supported,
        sorted by name first, then by version (with "latest" at the end of each name group)
    """
    builds = []
    current_dir = os.path.dirname(os.path.abspath(__file__))
    today = date.today()

    for item in os.listdir(current_dir):
        item_path = os.path.join(current_dir, item)

        if not os.path.isdir(item_path):
            continue

        for tag_item in os.listdir(item_path):
            tag_path = os.path.join(item_path, tag_item)

            if os.path.isdir(tag_path):
                dockerfile_path = os.path.join(tag_path, "Dockerfile")
                config_path = os.path.join(tag_path, "config.json")

                if os.path.exists(dockerfile_path) and os.path.exists(config_path):
                    try:
                        with open(config_path, 'r', encoding='utf-8') as f:
                            config = json.load(f)

                        end_of_life_str = config.get('end_of_life')
                        if end_of_life_str is not None:
                            end_of_life_date = datetime.strptime(end_of_life_str, '%Y-%m-%d').date()
                            if end_of_life_date > today:
                                builds.append((item, tag_item))
                        else:
                            builds.append((item, tag_item))

                    except (json.JSONDecodeError, ValueError, KeyError) as e:
                        print(f"Warning: Could not parse config for {item}/{tag_item}: {e}")
                        continue

    def sort_key(build_tuple):
        name, tag = build_tuple
        return (name, _parse_version_key(tag))

    builds.sort(key=sort_key)
    return builds
