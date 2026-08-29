# Controlled URL Analysis

The active v0.1 URL-only workflow is documented in
[`docs/controlled_policy_analysis.md`](docs/controlled_policy_analysis.md).

Run it after installation with:

```bash
analyze-site https://example.com
```

This workflow performs bounded one-hop discovery of qualifying first-party
policy links and feeds successfully fetched HTML documents into the existing
`PolicyAnalyzer`. It does not provide legal advice, compliance validation, or a
safe/unsafe verdict.
