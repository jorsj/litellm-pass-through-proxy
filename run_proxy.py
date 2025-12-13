from __future__ import annotations

from pathlib import Path
import subprocess
import sys


def main() -> int:
    config_path = Path(__file__).resolve().parent / "config.yaml"
    try:
        result = subprocess.run([
            sys.executable,
            "-m",
            "litellm",
            "--config",
            str(config_path),
        ], check=False)
    except FileNotFoundError:
        print("litellm CLI is not installed.", file=sys.stderr)
        return 1
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
