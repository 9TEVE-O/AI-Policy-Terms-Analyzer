"""Tests for pyproject.toml configuration.

Validates the structure and content of the pyproject.toml build configuration
file added in this PR.
"""

import os
import re
import tomllib

import pytest

PYPROJECT_PATH = os.path.join(os.path.dirname(__file__), "pyproject.toml")


@pytest.fixture(scope="module")
def config():
    with open(PYPROJECT_PATH, "rb") as f:
        return tomllib.load(f)


# ---------------------------------------------------------------------------
# File validity
# ---------------------------------------------------------------------------


def test_pyproject_toml_exists():
    assert os.path.isfile(PYPROJECT_PATH), "pyproject.toml must exist in the project root"


def test_pyproject_toml_is_valid_toml(config):
    """File must parse without errors (fixture load validates this)."""
    assert isinstance(config, dict)


# ---------------------------------------------------------------------------
# Build system
# ---------------------------------------------------------------------------


def test_build_system_section_present(config):
    assert "build-system" in config


def test_build_backend_is_setuptools(config):
    assert config["build-system"]["build-backend"] == "setuptools.build_meta"


def test_build_backend_is_not_legacy_alias(config):
    """Regression: must use setuptools.build_meta, not the legacy alias."""
    backend = config["build-system"]["build-backend"]
    assert "__legacy__" not in backend, (
        "build-backend must not use the legacy setuptools alias"
    )


def test_build_system_requires_setuptools(config):
    requires = config["build-system"]["requires"]
    assert any("setuptools" in req for req in requires)


def test_build_system_setuptools_minimum_version(config):
    """Ensure setuptools minimum version is >= 68."""
    requires = config["build-system"]["requires"]
    setuptools_req = next(r for r in requires if "setuptools" in r)
    match = re.search(r">=\s*(\d+)", setuptools_req)
    assert match, f"Expected a >= version constraint in: {setuptools_req}"
    assert int(match.group(1)) >= 68


# ---------------------------------------------------------------------------
# Project metadata
# ---------------------------------------------------------------------------


def test_project_section_present(config):
    assert "project" in config


def test_project_name(config):
    assert config["project"]["name"] == "ai-policy-terms-analyzer"


def test_project_version(config):
    assert config["project"]["version"] == "0.1.0"


def test_project_version_is_semver(config):
    version = config["project"]["version"]
    assert re.match(r"^\d+\.\d+\.\d+$", version), (
        f"Version {version!r} does not match MAJOR.MINOR.PATCH semver format"
    )


def test_project_description(config):
    desc = config["project"]["description"]
    assert "AI policies" in desc or "ai policies" in desc.lower(), (
        "Description should reference AI policies"
    )


def test_project_description_mentions_terms_of_service(config):
    desc = config["project"]["description"].lower()
    assert "terms of service" in desc or "terms" in desc


def test_requires_python(config):
    assert config["project"]["requires-python"] == ">=3.9"


def test_requires_python_minimum_is_3_9(config):
    spec = config["project"]["requires-python"]
    match = re.search(r">=\s*(\d+)\.(\d+)", spec)
    assert match, f"Expected >= version specifier, got: {spec}"
    major, minor = int(match.group(1)), int(match.group(2))
    assert (major, minor) >= (3, 9), f"requires-python must be >= 3.9, got {major}.{minor}"


def test_license_is_mit(config):
    license_field = config["project"]["license"]
    assert license_field.get("text") == "MIT"


# ---------------------------------------------------------------------------
# Optional dependencies
# ---------------------------------------------------------------------------


def test_optional_dependencies_section_present(config):
    assert "optional-dependencies" in config["project"]


def test_optional_deps_web_group_exists(config):
    assert "web" in config["project"]["optional-dependencies"]


def test_optional_deps_pdf_group_exists(config):
    assert "pdf" in config["project"]["optional-dependencies"]


def test_optional_deps_all_group_exists(config):
    assert "all" in config["project"]["optional-dependencies"]


def test_web_group_contains_beautifulsoup4(config):
    web_deps = config["project"]["optional-dependencies"]["web"]
    assert any("beautifulsoup4" in dep for dep in web_deps)


def test_web_group_contains_requests(config):
    web_deps = config["project"]["optional-dependencies"]["web"]
    assert any("requests" in dep for dep in web_deps)


def test_web_group_beautifulsoup4_version(config):
    web_deps = config["project"]["optional-dependencies"]["web"]
    bs4 = next(d for d in web_deps if "beautifulsoup4" in d)
    assert "4.12.0" in bs4


def test_web_group_requests_version(config):
    web_deps = config["project"]["optional-dependencies"]["web"]
    req = next(d for d in web_deps if "requests" in d)
    assert "2.31.0" in req


def test_pdf_group_contains_pdfplumber(config):
    pdf_deps = config["project"]["optional-dependencies"]["pdf"]
    assert any("pdfplumber" in dep for dep in pdf_deps)


def test_pdf_group_pdfplumber_version(config):
    pdf_deps = config["project"]["optional-dependencies"]["pdf"]
    pp = next(d for d in pdf_deps if "pdfplumber" in d)
    assert "0.10.0" in pp


def test_all_group_contains_beautifulsoup4(config):
    all_deps = config["project"]["optional-dependencies"]["all"]
    assert any("beautifulsoup4" in dep for dep in all_deps)


def test_all_group_contains_requests(config):
    all_deps = config["project"]["optional-dependencies"]["all"]
    assert any("requests" in dep for dep in all_deps)


def test_all_group_contains_pdfplumber(config):
    all_deps = config["project"]["optional-dependencies"]["all"]
    assert any("pdfplumber" in dep for dep in all_deps)


def test_all_group_is_superset_of_web(config):
    """The [all] group must include every package from [web]."""
    web_pkgs = {
        dep.split(">=")[0].split("==")[0].strip()
        for dep in config["project"]["optional-dependencies"]["web"]
    }
    all_pkgs = {
        dep.split(">=")[0].split("==")[0].strip()
        for dep in config["project"]["optional-dependencies"]["all"]
    }
    assert web_pkgs <= all_pkgs, f"[all] is missing web packages: {web_pkgs - all_pkgs}"


def test_all_group_is_superset_of_pdf(config):
    """The [all] group must include every package from [pdf]."""
    pdf_pkgs = {
        dep.split(">=")[0].split("==")[0].strip()
        for dep in config["project"]["optional-dependencies"]["pdf"]
    }
    all_pkgs = {
        dep.split(">=")[0].split("==")[0].strip()
        for dep in config["project"]["optional-dependencies"]["all"]
    }
    assert pdf_pkgs <= all_pkgs, f"[all] is missing pdf packages: {pdf_pkgs - all_pkgs}"


def test_optional_deps_use_minimum_version_constraints(config):
    """All optional deps should use >= version constraints (not pinned exact versions)."""
    opt_deps = config["project"]["optional-dependencies"]
    for group, deps in opt_deps.items():
        for dep in deps:
            assert ">=" in dep, (
                f"Dependency {dep!r} in [{group}] should use >= constraint, not a pinned version"
            )


# ---------------------------------------------------------------------------
# Entry points / scripts
# ---------------------------------------------------------------------------


def test_scripts_section_present(config):
    assert "scripts" in config["project"]


def test_scripts_analyze_policy_entry_point(config):
    scripts = config["project"]["scripts"]
    assert "analyze-policy" in scripts


def test_scripts_analyze_policy_target(config):
    assert config["project"]["scripts"]["analyze-policy"] == "quick_start:main"


def test_scripts_analyze_policy_module_is_quick_start(config):
    target = config["project"]["scripts"]["analyze-policy"]
    module, func = target.split(":")
    assert module == "quick_start"


def test_scripts_analyze_policy_function_is_main(config):
    target = config["project"]["scripts"]["analyze-policy"]
    module, func = target.split(":")
    assert func == "main"


# ---------------------------------------------------------------------------
# Tool / setuptools py-modules
# ---------------------------------------------------------------------------

EXPECTED_MODULES = {
    "ai_operator_os",
    "ai_policy_researcher",
    "batch_analyzer",
    "document_scanner",
    "example_usage",
    "extraction_modules",
    "key_point_condenser",
    "policy_analyzer",
    "quick_start",
}


def test_tool_setuptools_section_present(config):
    assert "tool" in config
    assert "setuptools" in config["tool"]


def test_py_modules_key_present(config):
    assert "py-modules" in config["tool"]["setuptools"]


def test_py_modules_count(config):
    modules = config["tool"]["setuptools"]["py-modules"]
    assert len(modules) == 9, f"Expected 9 py-modules, got {len(modules)}: {modules}"


def test_py_modules_no_duplicates(config):
    modules = config["tool"]["setuptools"]["py-modules"]
    assert len(modules) == len(set(modules)), (
        f"Duplicate modules found: {[m for m in modules if modules.count(m) > 1]}"
    )


def test_py_modules_contains_all_expected(config):
    modules = set(config["tool"]["setuptools"]["py-modules"])
    assert modules == EXPECTED_MODULES, (
        f"Module mismatch.\n  Missing: {EXPECTED_MODULES - modules}\n  Extra: {modules - EXPECTED_MODULES}"
    )


def test_py_modules_ai_operator_os(config):
    assert "ai_operator_os" in config["tool"]["setuptools"]["py-modules"]


def test_py_modules_ai_policy_researcher(config):
    assert "ai_policy_researcher" in config["tool"]["setuptools"]["py-modules"]


def test_py_modules_batch_analyzer(config):
    assert "batch_analyzer" in config["tool"]["setuptools"]["py-modules"]


def test_py_modules_document_scanner(config):
    assert "document_scanner" in config["tool"]["setuptools"]["py-modules"]


def test_py_modules_example_usage(config):
    assert "example_usage" in config["tool"]["setuptools"]["py-modules"]


def test_py_modules_extraction_modules(config):
    assert "extraction_modules" in config["tool"]["setuptools"]["py-modules"]


def test_py_modules_key_point_condenser(config):
    assert "key_point_condenser" in config["tool"]["setuptools"]["py-modules"]


def test_py_modules_policy_analyzer(config):
    assert "policy_analyzer" in config["tool"]["setuptools"]["py-modules"]


def test_py_modules_quick_start(config):
    assert "quick_start" in config["tool"]["setuptools"]["py-modules"]


def test_py_modules_script_module_is_listed(config):
    """The module referenced in [project.scripts] must be in py-modules."""
    script_target = config["project"]["scripts"]["analyze-policy"]
    script_module = script_target.split(":")[0]
    assert script_module in config["tool"]["setuptools"]["py-modules"], (
        f"Script module {script_module!r} is not listed in [tool.setuptools] py-modules"
    )


def test_py_modules_source_files_exist(config):
    """Every module in py-modules must have a corresponding .py file in the project root."""
    root = os.path.dirname(PYPROJECT_PATH)
    modules = config["tool"]["setuptools"]["py-modules"]
    missing = [m for m in modules if not os.path.isfile(os.path.join(root, f"{m}.py"))]
    assert not missing, f"Missing source files for modules: {missing}"


# ---------------------------------------------------------------------------
# Cross-section consistency checks
# ---------------------------------------------------------------------------


def test_no_install_requires_in_project(config):
    """Core project should have no mandatory dependencies (all are optional)."""
    project = config["project"]
    assert "dependencies" not in project or project.get("dependencies") == [], (
        "Core project should not declare mandatory dependencies; use optional-dependencies instead"
    )


def test_all_optional_group_package_count(config):
    """[all] group must have at least as many packages as web + pdf combined."""
    web = config["project"]["optional-dependencies"]["web"]
    pdf = config["project"]["optional-dependencies"]["pdf"]
    all_deps = config["project"]["optional-dependencies"]["all"]
    # All packages in web and pdf should be covered in all
    assert len(all_deps) >= len(web) + len(pdf) - 0, (
        "[all] group should cover all web and pdf packages"
    )