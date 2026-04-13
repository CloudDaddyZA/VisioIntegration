"""Build the Azure Visio AI Assistant desktop app with PyInstaller.

Usage:
    python scripts/build_desktop.py          # build only
    python scripts/build_desktop.py --run    # build then launch

Prerequisites (install once):
    pip install .[desktop]
"""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SPEC = ROOT / "desktop.spec"
DIST = ROOT / "dist" / "AzureVisioAssistant"


def build() -> None:
    print("=" * 60)
    print("  Building Azure Visio AI Assistant")
    print("=" * 60)

    # Sanity checks
    if not SPEC.exists():
        sys.exit(f"ERROR: spec file not found: {SPEC}")
    try:
        import PyInstaller  # noqa: F401
    except ImportError:
        sys.exit("ERROR: PyInstaller not installed. Run: pip install .[desktop]")
    try:
        import webview  # noqa: F401
    except ImportError:
        sys.exit("ERROR: pywebview not installed. Run: pip install .[desktop]")

    # Clean previous build
    for d in [ROOT / "build", DIST]:
        if d.exists():
            print(f"  Cleaning {d} ...")
            shutil.rmtree(d)

    # Run PyInstaller
    print(f"  Running PyInstaller with {SPEC.name} ...")
    result = subprocess.run(
        [sys.executable, "-m", "PyInstaller", str(SPEC), "--noconfirm"],
        cwd=str(ROOT),
    )
    if result.returncode != 0:
        sys.exit(f"ERROR: PyInstaller failed (exit code {result.returncode})")

    exe = DIST / "AzureVisioAssistant.exe"
    if exe.exists():
        print()
        print(f"  Build successful!")
        print(f"  Output: {DIST}")
        print(f"  Executable: {exe}")
        print(f"  Size: {sum(f.stat().st_size for f in DIST.rglob('*') if f.is_file()) / 1024 / 1024:.1f} MB")
    else:
        sys.exit("ERROR: Build completed but executable not found.")


def main() -> None:
    build()
    if "--run" in sys.argv:
        exe = DIST / "AzureVisioAssistant.exe"
        print(f"\n  Launching {exe.name} ...")
        subprocess.Popen([str(exe)])


if __name__ == "__main__":
    main()
