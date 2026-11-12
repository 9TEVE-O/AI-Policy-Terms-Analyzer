#!/usr/bin/env python3
"""Offline, evidence-first wrapper for the repository's PolicyAnalyzer."""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from urllib.parse import urlsplit

MAX_BYTES = 2 * 1024 * 1024


def repository_root(explicit):
    candidates = [Path(explicit)] if explicit else [Path.cwd(), Path(__file__).resolve().parents[2]]
    for candidate in candidates:
        root = candidate.expanduser().resolve()
        if (root / "policy_analyzer.py").is_file() and (root / "extraction_modules.py").is_file():
            return root
    raise ValueError("PolicyAnalyzer source not found. Run in repository or pass --repo-root.")


def read_input(path):
    if not path.is_file():
        raise ValueError("Input must be an existing UTF-8 text file")
    with path.open("rb") as stream:
        raw = stream.read(MAX_BYTES + 1)
    if len(raw) > MAX_BYTES:
        raise ValueError("Input exceeds the 2 MiB limit")
    try:
        content = raw.decode("utf-8-sig")
    except UnicodeError as error:
        raise ValueError("Input is not UTF-8 text") from error
    if not content.strip() or "\x00" in content:
        raise ValueError("Input is empty or appears binary")
    return content, raw


def validate_source_url(url):
    if url is None:
        return None
    parsed = urlsplit(url)
    if parsed.scheme not in ("http", "https") or not parsed.hostname or parsed.username or parsed.password:
        raise ValueError("--source-url must be HTTP(S) without credentials")
    return url


def report(text, raw, company, file_name, source_url, root):
    # Import from this authorised source checkout, not a similarly named package.
    sys.path.insert(0, str(root))
    from policy_analyzer import PolicyAnalyzer
    return {
        "schema_version": "policy-skill-evidence/v1",
        "method": "repository extractor; contextual review NOT performed",
        "review_status": "HUMAN_REVIEW_REQUIRED",
        "source": {
            "name": file_name,
            "source_url": source_url,
            "sha256": hashlib.sha256(raw).hexdigest(),
            "bytes": len(raw),
            "complete_document_verified": False
        },
        "candidate_extraction": PolicyAnalyzer().analyze(text, company),
        "limitations": [
            "Detections are candidates and do not establish actual deployment.",
            "Document version, applicability, context and completeness are not verified.",
            "Human comparison with source passages is required for consequential findings.",
            "This is not legal advice, compliance certification, or a safety verdict."
        ]
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description="Offline policy analysis, evidence-gated")
    parser.add_argument("--input", required=True, help="Authorised local UTF-8 document")
    parser.add_argument("--company", required=True)
    parser.add_argument("--source-url", help="Reference only; never fetched")
    parser.add_argument("--repo-root", help="Path to trusted source repository checkout")
    parser.add_argument("--output", help="New JSON file; never overwritten")
    args = parser.parse_args(argv)
    try:
        text, raw = read_input(Path(args.input))
        url = validate_source_url(args.source_url)
        root = repository_root(args.repo_root)
        result = report(text, raw, args.company, Path(args.input).name, url, root)
        data = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
        if args.output:
            with Path(args.output).open("x", encoding="utf-8") as out:
                out.write(data)
        else:
            sys.stdout.write(data)
        return 0
    except (OSError, ValueError, ImportError) as error:
        print(f"policy-skill: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
