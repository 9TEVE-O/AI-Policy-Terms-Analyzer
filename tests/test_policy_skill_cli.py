"""Real-repository regression tests for the reusable policy skill."""
import hashlib
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skill/scripts/analyze_text.py"
INSTALLER = ROOT / "skill/scripts/install_skill.py"


def run_cli(*args):
    return subprocess.run([sys.executable, str(SCRIPT), *map(str, args)],
                          cwd=ROOT, capture_output=True, text=True, check=False)


def test_extract_keeps_source_fingerprint_and_human_gate(tmp_path):
    raw = b"We use Stripe to process payments. Automated scraping is prohibited."
    source = tmp_path / "terms.txt"
    source.write_bytes(raw)
    result = run_cli("--input", source, "--company", "Example Inc",
                     "--source-url", "https://example.com/terms")
    assert result.returncode == 0, result.stderr
    report = json.loads(result.stdout)
    assert report["schema_version"] == "policy-skill-evidence/v1"
    assert report["review_status"] == "HUMAN_REVIEW_REQUIRED"
    assert "NOT performed" in report["method"]
    assert report["source"]["sha256"] == hashlib.sha256(raw).hexdigest()
    assert report["source"]["source_url"] == "https://example.com/terms"
    assert report["source"]["complete_document_verified"] is False
    assert report["candidate_extraction"]["company_name"] == "Example Inc"


def test_does_not_overwrite_report(tmp_path):
    source = tmp_path / "terms.txt"
    source.write_text("We use Stripe.", encoding="utf-8")
    output = tmp_path / "out.json"
    output.write_text("KEEP", encoding="utf-8")
    result = run_cli("--input", source, "--company", "Example", "--output", output)
    assert result.returncode == 2
    assert output.read_text(encoding="utf-8") == "KEEP"


def test_rejects_empty_binary_and_oversized_input(tmp_path):
    source = tmp_path / "terms.txt"
    for data in (b"", b"\xff\xfe", b"\x00abc", b"x" * (2 * 1024 * 1024 + 1)):
        source.write_bytes(data)
        result = run_cli("--input", source, "--company", "Example")
        assert result.returncode == 2
        assert not result.stdout


def test_does_not_accept_non_http_source_reference(tmp_path):
    source = tmp_path / "terms.txt"
    source.write_text("Some policy text", encoding="utf-8")
    for url in ("file:///etc/passwd", "https://user:password@example.com/terms", "javascript:alert(1)"):
        result = run_cli("--input", source, "--company", "Example", "--source-url", url)
        assert result.returncode == 2
        assert "--source-url" in result.stderr


def test_missing_explicit_repository_does_not_fall_back(tmp_path):
    source = tmp_path / "terms.txt"
    source.write_text("Some policy text", encoding="utf-8")
    result = run_cli("--input", source, "--company", "Example", "--repo-root", tmp_path)
    assert result.returncode == 2
    assert "source not found" in result.stderr


def test_installer_previews_without_write_and_refuses_overwrite(tmp_path):
    spec = importlib.util.spec_from_file_location("policy_skill_installer", INSTALLER)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    target = module.install(agent="codex", scope="project", project_root=str(tmp_path), execute=False)
    assert str(target).endswith(".agents/skills/analyzing-policy-and-terms")
    assert not target.exists()
    target = module.install(agent="claude", scope="project", project_root=str(tmp_path), execute=True)
    assert (target / "SKILL.md").is_file()
    assert (target / "scripts/analyze_text.py").is_file()
    assert (target / "references/extraction-schema.md").is_file()
    assert "name: analyzing-policy-and-terms" in (target / "SKILL.md").read_text()
    try:
        module.install(agent="claude", scope="project", project_root=str(tmp_path), execute=True)
        assert False, "Existing install must be protected"
    except FileExistsError:
        pass
