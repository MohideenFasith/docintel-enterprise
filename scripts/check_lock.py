from __future__ import annotations

import re
import tomllib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PIN = re.compile(r"^([A-Za-z0-9_.-]+)==([^;\\s]+)$")


def normalized(name: str) -> str:
    return name.lower().replace("_", "-").replace(".", "-")


def lock_pins(path: Path) -> dict[str, str]:
    pins: dict[str, str] = {}
    for line in path.read_text().splitlines():
        match = PIN.match(line.strip())
        if match:
            pins[normalized(match.group(1))] = match.group(2)
    return pins


def direct_pin(requirement: str) -> tuple[str, str] | None:
    match = PIN.match(requirement)
    if not match:
        return None
    return normalized(match.group(1)), match.group(2)


def main() -> int:
    project = tomllib.loads((ROOT / "pyproject.toml").read_text())
    runtime = lock_pins(ROOT / "requirements.lock")
    dev = lock_pins(ROOT / "requirements-dev.lock")
    missing: list[str] = []

    for requirement in project["project"]["dependencies"]:
        direct = direct_pin(requirement)
        if direct is None:
            missing.append(f"runtime requirement is not exactly pinned: {requirement}")
            continue
        name, version = direct
        if runtime.get(name) != version:
            missing.append(f"runtime lock mismatch: {name}=={version}")

    for requirement in project["project"]["optional-dependencies"]["dev"]:
        direct = direct_pin(requirement)
        if direct is None:
            missing.append(f"dev requirement is not exactly pinned: {requirement}")
            continue
        name, version = direct
        if dev.get(name) != version:
            missing.append(f"dev lock mismatch: {name}=={version}")

    if missing:
        print("\n".join(missing))
        return 1
    print("lock files match direct pyproject pins")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
