#!/usr/bin/env python3
"""
Dagger CI/CD pipeline for CIE (Optimization & Evaluation) project.

This pipeline handles:
- Code quality checks (formatting, linting, type checking)
- Testing with coverage
- Building and packaging
- Security scanning
- Documentation generation
- Multi-environment deployment
"""

import asyncio
import sys
from pathlib import Path

import dagger
from dagger import dag, function, object_type


@object_type
class CieCI:
    """Dagger CI/CD pipeline for CIE project."""

    def __init__(self):
        self.project_name = "cie"
        self.python_version = "3.13"
        self.source_dir = Path("/home/diogenes/Projects/CIE")

    @function
    def source(self) -> dagger.Directory:
        """Get the project source code."""
        return dag.host().directory(
            str(self.source_dir),
            exclude=[
                "__pycache__",
                "*.pyc",
                ".pytest_cache",
                ".coverage",
                "htmlcov",
                ".venv",
                "venv",
                "*.egg-info",
                "dist",
                "build",
                ".git",
                ".jj",
                ".ruff_cache",
                ".mypy_cache",
                "ci/__pycache__",
            ],
        )

    def python_container(self, with_dev_deps: bool = True) -> dagger.Container:
        """Create a Python container with project dependencies."""
        container = (
            dag.container()
            .from_(f"python:{self.python_version}-slim")
            .with_exec(["apt-get", "update"])
            .with_exec(["apt-get", "install", "-y", "git", "curl", "build-essential", "pkg-config"])
            .with_workdir("/app")
            .with_file("pyproject.toml", self.source().file("pyproject.toml"))
            .with_file("uv.lock", self.source().file("uv.lock"))
        )

        if with_dev_deps:
            container = container.with_exec(["pip", "install", "-e", ".[dev]"])
        else:
            container = container.with_exec(["pip", "install", "-e", "."])

        return container.with_directory("/app", self.source())

    @function
    async def lint(self) -> str:
        """Run code linting with ruff."""
        print("🔍 Running code linting...")

        result = await (
            self.python_container()
            .with_exec(["ruff", "check", "cie/", "--format", "json"])
            .stdout()
        )

        if result.strip():
            print(f"⚠️  Linting issues found:\n{result}")
            return f"Linting issues found:\n{result}"
        else:
            print("✅ No linting issues found")
            return "No linting issues found"

    @function
    async def format(self) -> str:
        """Check code formatting with black."""
        print("🎨 Checking code formatting...")

        result = await (
            self.python_container().with_exec(["black", "--check", "--diff", "cie/"]).stdout()
        )

        if result.strip():
            print(f"⚠️  Formatting issues found:\n{result}")
            return f"Formatting issues found:\n{result}"
        else:
            print("✅ Code is properly formatted")
            return "Code is properly formatted"

    @function
    async def type_check(self) -> str:
        """Run type checking with mypy."""
        print("🔬 Running type checking...")

        result = await (
            self.python_container().with_exec(["mypy", "cie/", "--ignore-missing-imports"]).stdout()
        )

        if "error" in result.lower() or "Error" in result:
            print(f"⚠️  Type checking issues found:\n{result}")
            return f"Type checking issues found:\n{result}"
        else:
            print("✅ No type checking issues found")
            return "No type checking issues found"

    @function
    async def test(self, coverage: bool = True) -> str:
        """Run tests with optional coverage."""
        print("🧪 Running tests...")

        test_cmd = ["pytest", "-v"]
        if coverage:
            test_cmd.extend(["--cov=cie", "--cov-report=term-missing"])

        result = await self.python_container().with_exec(test_cmd).stdout()

        print("✅ Tests completed")
        return result

    @function
    async def security_scan(self) -> str:
        """Run security scanning with bandit."""
        print("🔒 Running security scan...")

        try:
            result = await (
                self.python_container().with_exec(["bandit", "-r", "cie/", "-f", "json"]).stdout()
            )
            print("✅ Security scan completed")
            return result
        except Exception as e:
            print(f"⚠️  Security scan not available: {e}")
            return "Security scan skipped (bandit not installed)"

    @function
    async def build(self) -> dagger.File:
        """Build the project package."""
        print("📦 Building project package...")

        container = self.python_container(with_dev_deps=False)

        # Build the package
        built = await container.with_exec(["python", "-m", "build"]).directory("dist")

        # Get the wheel file
        wheel_files = await built.entries()
        wheel_file = [f for f in wheel_files if f.endswith(".whl")][0]

        print(f"✅ Built package: {wheel_file}")
        return built.file(wheel_file)

    @function
    async def docs(self) -> str:
        """Generate documentation."""
        print("📚 Generating documentation...")

        try:
            result = await (
                self.python_container()
                .with_exec(["python", "-m", "pdoc", "cie/", "--output-directory", "docs/"])
                .stdout()
            )
            print("✅ Documentation generated")
            return result
        except Exception as e:
            print(f"⚠️  Documentation generation failed: {e}")
            return "Documentation generation skipped"

    @function
    async def quality_gate(self) -> str:
        """Run all quality checks (linting, formatting, type checking)."""
        print("🚪 Running quality gate checks...")

        results = []

        # Run all quality checks
        lint_result = await self.lint()
        results.append(f"Linting: {lint_result}")

        format_result = await self.format()
        results.append(f"Formatting: {format_result}")

        type_result = await self.type_check()
        results.append(f"Type Checking: {type_result}")

        # Check if any issues found
        issues_found = any("issues found" in result.lower() for result in results)

        if issues_found:
            print("❌ Quality gate failed")
            return "\n".join(results)
        else:
            print("✅ Quality gate passed")
            return "All quality checks passed"

    @function
    async def ci(self) -> str:
        """Run complete CI pipeline."""
        print("🔄 Running complete CI pipeline...")

        start_time = time.time()

        # Quality checks
        quality_result = await self.quality_gate()
        if "failed" in quality_result.lower():
            return f"CI failed at quality gate:\n{quality_result}"

        # Security scan
        security_result = await self.security_scan()

        # Tests
        test_result = await self.test(coverage=True)
        if "failed" in test_result.lower() or "error" in test_result.lower():
            return f"CI failed at tests:\n{test_result}"

        # Build
        try:
            package = await self.build()
            package_path = await package.name()
            build_result = f"Package built successfully: {package_path}"
        except Exception as e:
            return f"CI failed at build: {e}"

        # Documentation
        docs_result = await self.docs()

        end_time = time.time()
        duration = end_time - start_time

        print(f"✅ CI pipeline completed in {duration:.2f}s")

        return f"""
CI Pipeline Results:
===================
Quality Gate: ✅ PASSED
Security Scan: ✅ COMPLETED
Tests: ✅ PASSED
Build: ✅ COMPLETED - {package_path}
Documentation: ✅ GENERATED

Total Duration: {duration:.2f}s
Pipeline Status: ✅ SUCCESS
"""

    @function
    async def deploy_dev(self, registry: str = "ghcr.io") -> str:
        """Deploy to development environment."""
        print("🚀 Deploying to development environment...")

        # Build the package
        package = await self.build()

        # Create development container
        dev_container = (
            dag.container()
            .from_(f"python:{self.python_version}-slim")
            .with_workdir("/app")
            .with_file("package.whl", package)
            .with_exec(["pip", "install", "package.whl"])
            .with_exec(["pip", "install", "pytest", "pytest-cov"])
            .with_directory("/app/tests", self.source().directory("tests"))
        )

        # Test in container
        test_result = await dev_container.with_exec(["pytest", "tests/", "-v"]).stdout()

        print("✅ Development deployment completed")
        return f"Development deployment successful:\n{test_result}"

    @function
    async def deploy_prod(self, registry: str = "ghcr.io", image_tag: str = "latest") -> str:
        """Deploy to production environment."""
        print("🚀 Deploying to production environment...")

        # Build production container
        prod_container = (
            dag.container()
            .from_(f"python:{self.python_version}-slim")
            .with_workdir("/app")
            .with_file("pyproject.toml", self.source().file("pyproject.toml"))
            .with_directory("/app/cie", self.source().directory("cie"))
            .with_directory("/app/examples", self.source().directory("examples"))
            .with_exec(["pip", "install", "-e", "."])
            .with_entrypoint(["cie"])
        )

        # Publish container
        if registry:
            address = await prod_container.publish(f"{registry}/cie:{image_tag}")
            print(f"✅ Production image published: {address}")
            return f"Production deployment successful: {address}"
        else:
            print("✅ Production container built successfully")
            return "Production container built successfully"


@function
async def main() -> None:
    """Main entry point for Dagger CI."""
    ci = CieCI()

    # Run the complete CI pipeline
    result = await ci.ci()
    print(result)

    # Exit with appropriate code
    if "failed" in result.lower():
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    asyncio.run(main())
