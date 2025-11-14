#!/usr/bin/env python3
"""
Documentation verification script for CIE project.

This script checks that the documentation aligns with the actual implementation.
"""

import re
import sys
from pathlib import Path


def check_textual_version_consistency():
    """Check that Textual version is consistent across files."""
    print("🔍 Checking Textual version consistency...")

    pyproject_path = Path("pyproject.toml")
    with open(pyproject_path) as f:
        pyproject_content = f.read()

    match = re.search(r"textual>=([0-9.]+)", pyproject_content)
    textual_version_pyproject = match.group(1) if match else None

    ui_app_path = Path("cie/ui/app.py")
    with open(ui_app_path) as f:
        app_content = f.read()

    uses_modern_api = "CSS_PATH" in app_content or "Binding(" in app_content

    print(f"  📄 pyproject.toml: textual>={textual_version_pyproject or 'NOT FOUND'}")
    print(f"  📄 cie/ui/app.py: Uses modern API = {uses_modern_api}")

    if (
        textual_version_pyproject
        and textual_version_pyproject.startswith("0.47")
        and uses_modern_api
    ):
        print("  ✅ Version consistency: PASS")
        return True

    print("  ❌ Version consistency: FAIL")
    return False


def check_file_structure():
    """Check that documented file structure matches reality."""
    print("\n🔍 Checking file structure...")

    expected_files = {
        "main.py": "Legacy entrypoint",
        "pyproject.toml": "Project configuration",
        "README.md": "Project documentation",
        "AGENTS.md": "Developer guide",
        "cie/core/backend.py": "Backend implementation",
        "cie/ui/app.py": "Textual application",
        "cie/ui/theme.tcss": "Shared design system",
        "cie/evaluators/text_match.py": "Real evaluator implementation",
        "tests/test_backend.py": "Backend tests",
        "tests/test_optimizers.py": "Optimizer tests",
        "tests/test_end_to_end.py": "End-to-end tests",
    }

    all_present = True
    for file_path, description in expected_files.items():
        path = Path(file_path)
        if path.exists():
            print(f"  ✅ {file_path}: {description}")
        else:
            print(f"  ❌ {file_path}: {description} - MISSING")
            all_present = False

    return all_present


def check_main_py_structure():
    """Confirm main.py simply proxies to the packaged UI."""
    print("\n🔍 Checking main.py structure...")

    content = Path("main.py").read_text()
    has_proxy_import = "cie.ui.app" in content
    has_backend_reexport = "from cie.core.backend import CIEBackend" in content
    has_main_guard = 'if __name__ == "__main__":' in content

    print(f"  🔁 Proxy import present: {has_proxy_import}")
    print(f"  🔁 Backend re-export: {has_backend_reexport}")
    print(f"  🔁 Main guard: {has_main_guard}")

    return has_proxy_import and has_backend_reexport and has_main_guard


def check_documentation_references():
    """Check that documentation references are valid."""
    print("\n🔍 Checking documentation references...")

    readme_content = Path("README.md").read_text()
    has_uv_instructions = "uv sync" in readme_content
    has_evaluator_docs = "cie evaluators" in readme_content
    has_test_commands = "pytest" in readme_content

    print(f"  🛠️ README mentions uv: {has_uv_instructions}")
    print(f"  🧮 README mentions evaluator CLI: {has_evaluator_docs}")
    print(f"  🧪 README mentions pytest: {has_test_commands}")

    return has_uv_instructions and has_evaluator_docs and has_test_commands


def main():
    """Run all verification checks."""
    print("🚀 CIE Documentation Verification")
    print("=" * 40)

    results = []

    # Run checks
    results.append(check_textual_version_consistency())
    results.append(check_file_structure())
    results.append(check_main_py_structure())
    results.append(check_documentation_references())

    print("\n" + "=" * 40)
    print("📋 Summary")

    if all(results):
        print("✅ All checks passed! Documentation aligns with implementation.")
        return 0
    else:
        print("❌ Some checks failed. Review the output above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
