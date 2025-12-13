from __future__ import annotations

from importlib import resources
from pathlib import Path
import os
import shutil
import subprocess
import sys


def main() -> int:
    root_dir = Path(__file__).resolve().parent.parent
    config_path = root_dir / "config.yaml"
    litellm_executable = shutil.which("litellm")
    if not litellm_executable:
        print("litellm CLI is not installed or not on PATH.", file=sys.stderr)
        return 1

    schema_resource: Path | None = None
    for package_name in ("litellm_proxy_extras", "litellm.proxy.db"):
        try:
            candidate = resources.files(package_name) / "schema.prisma"
        except (ModuleNotFoundError, AttributeError):
            continue
        else:
            schema_resource = candidate
            break

    if schema_resource is None:
        print(
            "Could not locate a schema.prisma file in litellm packages.",
            file=sys.stderr,
        )
        return 1

    try:
        schema_path_context = resources.as_file(schema_resource)
    except FileNotFoundError:
        print(
            "Prisma schema not found in litellm installation.",
            file=sys.stderr,
        )
        return 1

    with schema_path_context as schema_path:
        schema_file = str(schema_path)
        generate_cmd = [
            sys.executable,
            "-m",
            "prisma",
            "generate",
            "--schema",
            schema_file,
        ]
        try:
            subprocess.run(generate_cmd, check=True)
        except FileNotFoundError:
            print(
                "Prisma CLI not found. Ensure the 'prisma' package is installed in this environment.",
                file=sys.stderr,
            )
            return 1
        except subprocess.CalledProcessError as exc:
            print(
                f"Prisma generate failed with exit code {exc.returncode}.",
                file=sys.stderr,
            )
            return exc.returncode

    result = subprocess.run(
        [
            litellm_executable,
            "--config",
            str(config_path),
        ],
        check=False,
    )
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
