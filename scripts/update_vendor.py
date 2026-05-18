#!/usr/bin/env python3

from __future__ import annotations

import json
import shutil
import sys
import tarfile
import tempfile
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

try:
    import tomllib  # Python 3.11+
except ModuleNotFoundError:
    print("Python 3.11+ required, or install tomli and adjust script.", file=sys.stderr)
    raise


ROOT = Path(__file__).resolve().parents[1]
VENDOR_DIR = ROOT / "vendor"
CONFIG = VENDOR_DIR / "vendor.toml"


def github_tarball_url(repo: str, commit: str) -> str:
    # https://github.com/OWNER/REPO/archive/<commit>.tar.gz
    return f"{repo.rstrip('/')}/archive/{commit}.tar.gz"


def download(url: str, dest: Path) -> None:
    print(f"Downloading {url}")
    urllib.request.urlretrieve(url, dest)


def extract_single_root(tar_path: Path, dest: Path) -> Path:
    with tarfile.open(tar_path, "r:gz") as tar:
        tar.extractall(dest)

    roots = [p for p in dest.iterdir() if p.is_dir()]
    if len(roots) != 1:
        raise RuntimeError(f"Expected one extracted root, got: {roots}")

    return roots[0]


def update_source(source: dict) -> None:
    name = source["name"]
    repo = source["repo"]
    commit = source["commit"]
    files = source["files"]

    if commit == "<commit-sha>":
        raise RuntimeError(f"{name}: replace <commit-sha> with a real commit SHA")

    target_dir = VENDOR_DIR / name
    target_dir.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        tar_path = tmp_path / f"{name}.tar.gz"

        download(github_tarball_url(repo, commit), tar_path)
        extracted_root = extract_single_root(tar_path, tmp_path / "src")

        copied = []

        for file_name in files:
            src = extracted_root / file_name
            dst = target_dir / Path(file_name).name

            if not src.exists():
                raise FileNotFoundError(f"{name}: missing upstream file: {file_name}")

            shutil.copy2(src, dst)
            copied.append(
                {
                    "upstream_path": file_name,
                    "local_path": str(dst.relative_to(ROOT)),
                }
            )

        info = {
            "name": name,
            "repo": repo,
            "commit": commit,
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "files": copied,
        }

        (target_dir / ".vendor-info.json").write_text(
            json.dumps(info, indent=2) + "\n",
            encoding="utf-8",
        )

    print(f"Updated {name}")


def main() -> int:
    config = tomllib.loads(CONFIG.read_text(encoding="utf-8"))

    for source in config["source"]:
        update_source(source)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
