from __future__ import annotations

import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = ("pyproject.toml", "requirements.lock", "requirements-dev.lock")


def main() -> int:
    missing = [name for name in REQUIRED if not (ROOT / name).is_file()]
    if missing:
        print("missing reproducibility files: " + ", ".join(missing))
        return 1

    tracked = subprocess.run(
        ["git", "ls-files", "--error-unmatch", *REQUIRED],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if tracked.returncode != 0:
        print("lock/build files must be committed to git")
        print(tracked.stderr.strip())
        return 1

    print("reproducibility files are present and tracked")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
