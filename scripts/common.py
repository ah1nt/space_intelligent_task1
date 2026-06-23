from __future__ import annotations

import json
import os
import shlex
import subprocess
from pathlib import Path
from typing import Iterable


def load_config(config_path: str) -> dict:
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)


def project_root_from_config(config: dict) -> Path:
    return Path(config["project_root"]).resolve()


def resolve_path(project_root: Path, raw_path: str) -> Path | None:
    if not raw_path:
        return None
    candidate = Path(raw_path)
    if candidate.is_absolute():
        return candidate
    return (project_root / candidate).resolve()


def resolve_command(project_root: Path, raw_value: str, default: str) -> str:
    if not raw_value:
        return default
    candidate = Path(raw_value)
    if candidate.is_absolute():
        return str(candidate)
    if any(sep in raw_value for sep in ("/", "\\")):
        return str((project_root / candidate).resolve())
    return raw_value


def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def print_block(title: str, lines: Iterable[str]) -> None:
    print(f"\n=== {title} ===")
    for line in lines:
        print(line)


def quote_command(parts: Iterable[os.PathLike[str] | str]) -> str:
    return " ".join(shlex.quote(str(part)) for part in parts)


def run_command(
    parts: list[str | os.PathLike[str]],
    cwd: Path | None = None,
    env_extra: dict[str, str] | None = None,
) -> None:
    printable = quote_command(parts)
    print(f"[run] {printable}")
    env = os.environ.copy()
    if env_extra:
        env.update(env_extra)
    subprocess.run([str(p) for p in parts], cwd=cwd, check=True, env=env)


def check_exists(path: Path | None, label: str, missing: list[str]) -> None:
    if path is None or not path.exists():
        missing.append(label)
