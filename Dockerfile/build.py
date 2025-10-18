from result import Ok, Err, Result, is_ok, is_err
import subprocess
import os
import json
import shutil
from typing import List, Tuple

from utils import discover_builds, get_project_root

def get_domain() -> str:
    """
    Read domain from /dist/CNAME file. If reading fails, return default domain.

    Returns:
        str: The domain to use for config URLs
    """
    default_domain = "worker-server.endkind.cloud"
    cname_path = get_project_root("dist", "CNAME")

    try:
        if os.path.exists(cname_path):
            with open(cname_path, 'r', encoding='utf-8') as f:
                domain = f.read().strip()
                if domain:
                    return domain
    except Exception as e:
        print(f"Warning: Could not read domain from {cname_path}: {e}")

    return default_domain

def main():
    build_all()

def build(name: str, tag: str) -> Result[str, str]:
    """
    Build a Docker image with the specified name and tag.

    Args:
        name: The name of the image
        tag: The tag of the image

    Returns:
        Result[str, str]: Ok with success message or Err with error message
    """
    try:
        image_name = f"enderhostinghq/worker-{name}:{tag}"

        context_path = f"./{name}/{tag}"

        if not os.path.exists(context_path):
            return Err(f"Build context path '{context_path}' does not exist")

        cmd = ["docker", "build", "-t", image_name, context_path]

        print(f"Building Docker image: {image_name}")
        print(f"Build context: {context_path}")
        print(f"Command: {' '.join(cmd)}")

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True
        )

        return Ok(f"Docker image '{image_name}' built successfully")

    except subprocess.CalledProcessError as e:
        error_msg = f"Docker build failed: {e.stderr if e.stderr else e.stdout}"
        return Err(error_msg)
    except Exception as e:
        return Err(f"Unexpected error: {str(e)}")

def build_all(builds: List[Tuple[str, str]] = discover_builds()) -> None:
    """
    Build all available Docker images by auto-discovering available configurations.
    """

    if not builds:
        print("No build configurations found!")
        return

    print(f"Found {len(builds)} build configurations:")
    for name, tag in builds:
        print(f"  - worker-{name}:{tag}")

    print("\nStarting builds...\n")

    successful_builds = []
    success_count = 0

    for name, tag in builds:
        print(f"--- Building worker-{name}:{tag} ---")
        result = build(name, tag)

        if is_ok(result):
            print(f"✅ {result.unwrap()}")
            successful_builds.append((name, tag))
            success_count += 1
        else:
            print(f"❌ {result.unwrap_err()}")
        print()

    print(f"Build complete: {success_count}/{len(builds)} succeeded")

    if successful_builds:
        print("\nCreating manifest with successful builds...")
        manifest_result = create_manifest(successful_builds)

        if is_ok(manifest_result):
            print(f"✅ {manifest_result.unwrap()}")
        else:
            print(f"❌ {manifest_result.unwrap_err()}")
    else:
        print("\n⚠️ No successful builds to include in manifest")

def create_manifest(builds: List[Tuple[str, str]] = None) -> Result[str, str]:
    """
    Create a manifest.json file based on available build configurations.

    Args:
        builds: Optional list of (name, tag) tuples. If None, discovers builds automatically.

    Returns:
        Result[str, str]: Ok with success message or Err with error message
    """
    try:
        if builds is None:
            builds = discover_builds()

        if not builds:
            return Err("No build configurations found to create manifest")

        manifest = {}

        for name, tag in builds:
            config_path = os.path.join(os.path.dirname(__file__), name, tag, "config.json")

            if not os.path.exists(config_path):
                print(f"Warning: Config file not found for {name}:{tag}")
                continue

            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)

                if f"worker-{name}" not in manifest:
                    manifest[f"worker-{name}"] = {}

                domain = get_domain()
                manifest_entry = {
                    "config": f"https://{domain}/Dockerfile/{name}/{tag}/config.json",
                    "end_of_life": config.get('end_of_life'),
                    "flavor": config.get('flavor'),
                    "base": config.get('base')
                }

                manifest[f"worker-{name}"][tag] = manifest_entry

                dist_config_dir = get_project_root("dist", "Dockerfile", name, tag)
                os.makedirs(dist_config_dir, exist_ok=True)

                dist_config_path = os.path.join(dist_config_dir, "config.json")
                shutil.copy2(config_path, dist_config_path)
                print(f"Copied config: {config_path} -> {dist_config_path}")

            except (json.JSONDecodeError, Exception) as e:
                print(f"Warning: Could not process config for {name}:{tag}: {e}")
                continue

        manifest_path = get_project_root("dist", "Dockerfile", "manifest.json")
        with open(manifest_path, 'w', encoding='utf-8') as f:
            json.dump(manifest, f, indent=4, ensure_ascii=False)

        return Ok(f"Manifest created successfully at {manifest_path} with {sum(len(tags) for tags in manifest.values())} configurations")

    except Exception as e:
        return Err(f"Failed to create manifest: {str(e)}")

if __name__ == "__main__":
    main()
