#!/usr/bin/env python3
"""Install the recipes in xcode/ as Xcode 27 saved themes, replacing any with the same name."""

import json
import plistlib
import subprocess
import sys
import time
import uuid
from pathlib import Path

DOMAIN = "com.apple.dt.Xcode"
KEY = "DVTWorkspaceSavedRecipes"
APPLE_EPOCH_OFFSET = 978307200
ROOT = Path(__file__).resolve().parent


def main() -> int:
    xcode = subprocess.run(["pgrep", "-x", "Xcode"], capture_output=True, check=False)
    if xcode.returncode == 0:
        print("Quit Xcode first: it rewrites its settings on quit.", file=sys.stderr)
        return 1

    exported = subprocess.run(
        ["defaults", "export", DOMAIN, "-"], capture_output=True, check=True
    ).stdout
    blob = plistlib.loads(exported).get(KEY)
    saved = json.loads(blob) if blob else []
    ids = {entry["name"]: entry["id"] for entry in saved}

    for path in sorted((ROOT / "xcode").glob("*.json")):
        theme = json.loads(path.read_text())
        entry = {
            "id": ids.get(theme["name"], str(uuid.uuid4()).upper()),
            "lastUsedDate": time.time() - APPLE_EPOCH_OFFSET,
            "name": theme["name"],
            "recipe": theme["recipe"],
        }
        saved = [e for e in saved if e["name"] != theme["name"]] + [entry]
        print(f"Installed {theme['name']}")

    payload = json.dumps(saved, separators=(",", ":")).encode()
    subprocess.run(
        ["defaults", "write", DOMAIN, KEY, "-data", payload.hex()], check=True
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
