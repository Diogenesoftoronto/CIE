#!/usr/bin/env python3
"""
Documentation verification script for CIE project.

This script checks that the documentation aligns with the actual implementation.
"""

import ast
import re
import sys
from pathlib import Path


def check_textual_version_consistency():
    """Check that Textual version is consistent across files."""
    print("🔍 Checking Textual version consistency...")
    
    # Check pyproject.toml
    pyproject_path = Path("pyproject.toml")
    with open(pyproject_path) as f:
        pyproject_content = f.read()
    
    textual_version_pyproject = None
    version_match = re.search(r'textual>=([0-9.]+)', pyproject_content)
    if version_match:
        textual_version_pyproject = version_match.group(1)
    
    # Check main.py imports
    main_path = Path("main.py")
    with open(main_path) as f:
        main_content = f.read()
    
    # Check for ModalScreen import pattern (indicates older API)
    uses_modal_alias = "ModalScreen as Modal" in main_content
    
    print(f"  📄 pyproject.toml: textual>={textual_version_pyproject or 'NOT FOUND'}")
    print(f"  📄 main.py: Uses ModalScreen alias = {uses_modal_alias} (indicates ≥0.47 API)")
    
    if textual_version_pyproject and textual_version_pyproject.startswith("0.47"):
        print("  ✅ Version consistency: PASS")
        return True
    else:
        print("  ❌ Version consistency: FAIL")
        return False


def check_file_structure():
    """Check that documented file structure matches reality."""
    print("\n🔍 Checking file structure...")
    
    expected_files = {
        "main.py": "Single-file application",
        "pyproject.toml": "Project configuration",
        "README.md": "Project documentation",
        "AGENTS.md": "Developer guide",
        "skills/textual.md": "Textual framework guide",
        "skills/index.md": "Skills overview",
        "tests/test_backend.py": "Backend tests",
        "tests/test_optimizers.py": "Optimizer tests",
        "tests/conftest.py": "Test configuration",
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
    """Check main.py structure against documentation."""
    print("\n🔍 Checking main.py structure...")
    
    with open("main.py") as f:
        content = f.read()
    
    # Count lines
    line_count = len(content.splitlines())
    print(f"  📊 Line count: {line_count} lines")
    
    # Check for key components
    components = {
        "Policy dataclass": r"@dataclass\s+class Policy:",
        "Trial dataclass": r"@dataclass\s+class Trial:",
        "Optimizer protocol": r"class Optimizer\(Protocol\):",
        "Evaluator protocol": r"class Evaluator\(Protocol\):",
        "MockDspyOptimizer": r"class MockDspyOptimizer:",
        "MockHillClimb": r"class MockHillClimb:",
        "MockBandit": r"class MockBandit:",
        "MockEvaluator": r"class MockEvaluator:",
        "CIEBackend": r"class CIEBackend:",
        "WeightsModal": r"class WeightsModal\(Modal\):",
        "OptimizersPanel": r"class OptimizersPanel\(Static\):",
        "EvalsPanel": r"class EvalsPanel\(Static\):",
        "ExperimentsPanel": r"class ExperimentsPanel\(Static\):",
        "CIEOptimEvalsApp": r"class CIEOptimEvalsApp\(App\):",
    }
    
    all_found = True
    for component, pattern in components.items():
        if re.search(pattern, content):
            print(f"  ✅ {component}")
        else:
            print(f"  ❌ {component} - NOT FOUND")
            all_found = False
    
    return all_found


def check_documentation_references():
    """Check that documentation references are valid."""
    print("\n🔍 Checking documentation references...")
    
    # Check README.md
    readme_path = Path("README.md")
    with open(readme_path) as f:
        readme_content = f.read()
    
    # Check for screenshot placeholder
    has_screenshot_placeholder = "<!-- Screenshot placeholder" in readme_content
    print(f"  📸 README screenshot: {'Placeholder (OK)' if has_screenshot_placeholder else 'Missing placeholder'}")
    
    # Check for test references
    has_test_commands = "pytest" in readme_content
    print(f"  🧪 README test commands: {'Present' if has_test_commands else 'Missing'}")
    
    # Check skills/index.md exists
    skills_index = Path("skills/index.md")
    print(f"  📚 Skills index: {'Present' if skills_index.exists() else 'Missing'}")
    
    return has_test_commands and skills_index.exists()


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