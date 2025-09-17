#!/usr/bin/env python3
"""
Generate requirements.txt from pyproject.toml
This script helps create a requirements.txt file for Render deployment
"""

import tomllib
import sys
from pathlib import Path

def generate_requirements():
    """Generate requirements.txt from pyproject.toml dependencies"""

    pyproject_path = Path("pyproject.toml")

    if not pyproject_path.exists():
        print("❌ pyproject.toml not found!")
        return False

    try:
        with open(pyproject_path, "rb") as f:
            data = tomllib.load(f)

        dependencies = data.get("project", {}).get("dependencies", [])

        if not dependencies:
            print("❌ No dependencies found in pyproject.toml")
            return False

        requirements_path = Path("requirements.txt")

        with open(requirements_path, "w") as f:
            for dep in dependencies:
                f.write(f"{dep}\n")

        print(f"✅ Generated requirements.txt with {len(dependencies)} dependencies")
        print("📄 Contents:")
        with open(requirements_path, "r") as f:
            print(f.read())

        return True

    except Exception as e:
        print(f"❌ Error generating requirements.txt: {e}")
        return False

if __name__ == "__main__":
    print("🔧 Generating requirements.txt from pyproject.toml...")
    success = generate_requirements()

    if success:
        print("\n✅ Ready for Render deployment!")
        print("   1. Commit these files to your GitHub repository")
        print("   2. Connect your repo to Render.com")
        print("   3. Render will automatically detect the render.yaml file")
        print("   4. Set your environment variables in Render dashboard")
    else:
        print("\n❌ Failed to generate requirements.txt")
        sys.exit(1)