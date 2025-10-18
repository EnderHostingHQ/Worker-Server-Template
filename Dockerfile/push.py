from result import Ok, Err, Result, is_ok, is_err
import subprocess
import json
import os
from typing import List, Tuple

from utils import discover_builds, get_project_root

def main():
    push_all()

def push(name: str, tag: str) -> Result[str, str]:
    """
    Push a Docker image with the specified name and tag to Docker Hub.
ch
    Args:
        name: The name of the image
        tag: The tag of the image

    Returns:
        Result[str, str]: Ok with success message or Err with error message
    """
    try:
        image_name = f"enderhostinghq/{name}:{tag}"

        cmd = ["docker", "push", image_name]

        print(f"Pushing Docker image: {image_name}")
        print(f"Command: {' '.join(cmd)}")

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True
        )

        return Ok(f"Docker image '{image_name}' pushed successfully")

    except subprocess.CalledProcessError as e:
        error_msg = f"Docker push failed: {e.stderr if e.stderr else e.stdout}"
        return Err(error_msg)
    except Exception as e:
        return Err(f"Unexpected error: {str(e)}")

def get_successful_builds_from_manifest() -> List[Tuple[str, str]]:
    """
    Read the manifest.json to get only successfully built images.

    Returns:
        List[Tuple[str, str]]: List of (name, tag) tuples from the manifest
    """
    manifest_path = get_project_root("dist", "Dockerfile", "manifest.json")

    if not os.path.exists(manifest_path):
        print(f"Warning: Manifest file not found at {manifest_path}")
        print("Falling back to auto-discovery...")
        return discover_builds()

    try:
        with open(manifest_path, 'r', encoding='utf-8') as f:
            manifest = json.load(f)

        builds = []
        for name, tags_dict in manifest.items():
            for tag in tags_dict.keys():
                builds.append((name, tag))

        return builds

    except (json.JSONDecodeError, Exception) as e:
        print(f"Warning: Could not read manifest: {e}")
        print("Falling back to auto-discovery...")
        return discover_builds()

def push_all(builds: List[Tuple[str, str]] = None) -> None:
    """
    Push Docker images based on successful builds from manifest.
    """
    if builds is None:
        builds = get_successful_builds_from_manifest()

    if not builds:
        print("No successful builds found to push!")
        return

    print(f"Found {len(builds)} successfully built configurations:")
    for name, tag in builds:
        print(f"  - {name}:{tag}")

    print("\nStarting pushes...\n")

    success_count = 0
    for name, tag in builds:
        print(f"--- Pushing {name}:{tag} ---")
        result = push(name, tag)

        if is_ok(result):
            print(f"✅ {result.unwrap()}")
            success_count += 1
        else:
            print(f"❌ {result.unwrap_err()}")
        print()

    print(f"Push complete: {success_count}/{len(builds)} succeeded")

if __name__ == "__main__":
    main()
