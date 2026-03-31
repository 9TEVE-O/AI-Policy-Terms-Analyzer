#!/usr/bin/env python3
"""
AI Policy Researcher

Analyses policy, terms-of-service, and privacy documents specifically for
clauses that relate to artificial intelligence — covering how AI is used, how
user data feeds AI systems, and what rights and protections are offered.

This complements the generic ``PolicyAnalyzer`` (which focuses on technology
stack and third-party services) by zooming in on the *conditions* and
*obligations* that govern AI use.

Detection categories
--------------------
* **AI training data** — Does the company train AI/ML models on user content?
* **Automated decisions** — Automated or algorithmic decisions affecting users
* **AI-generated content** — Disclosures about AI-generated text/images/audio
* **AI opt-out** — Mechanisms for users to opt out of AI processing
* **Algorithmic profiling** — Profiling, scoring, and personalisation by AI
* **AI transparency** — Disclosure of how AI/ML systems work
* **Regulatory references** — EU AI Act, GDPR Article 22, US Executive Orders,
  and similar regulatory frameworks
* **Known AI policy frameworks** — References to responsible-AI frameworks
  such as NIST AI RMF, IEEE standards, Partnership on AI, etc.

Research context
----------------
A selection of publicly discussed AI policy analysis tools and frameworks is
embedded in ``KNOWN_AI_POLICY_TOOLS`` for informational purposes.
"""

import re
from datetime import datetime
from typing import Dict, List


# ---------------------------------------------------------------------------
# Informational catalogue of AI policy tools / frameworks
# ---------------------------------------------------------------------------

KNOWN_AI_POLICY_TOOLS: List[Dict] = [
    {
        'name': 'NIST AI Risk Management Framework (AI RMF)',
        'type': 'Framework',
        'url': 'https://www.nist.gov/system/files/documents/2023/01/26/AI%20RMF%201.0.pdf',
        'description': (
            'A voluntary framework from the US National Institute of Standards and '
            'Technology to help organisations manage AI risks across the AI lifecycle.'
        ),
    },
    {
        'name': 'EU AI Act',
        'type': 'Regulation',
        'url': 'https://artificialintelligenceact.eu/',
        'description': (
            'The European Union\'s binding regulation classifying AI systems by risk '
            'level and imposing obligations on providers and deployers.'
        ),
    },
    {
        'name': 'GDPR Article 22 (Automated Decision-Making)',
        'type': 'Regulation',
        'url': 'https://gdpr-info.eu/art-22-gdpr/',
        'description': (
            'EU data-protection right not to be subject to a solely automated '
            'decision that has legal or similarly significant effects.'
        ),
    },
    {
        'name': 'Partnership on AI',
        'type': 'Industry body',
        'url': 'https://partnershiponai.org/',
        'description': (
            'A multi-stakeholder organisation that develops tools and guidance for '
            'the responsible development of AI.'
        ),
    },
    {
        'name': 'AlgorithmWatch',
        'type': 'Research / advocacy',
        'url': 'https://algorithmwatch.org/',
        'description': (
            'A non-profit that analyses and explains algorithmic decision-making '
            'systems and their societal impacts.'
        ),
    },
    {
        'name': 'AI Now Institute',
        'type': 'Research',
        'url': 'https://ainowinstitute.org/',
        'description': (
            'An applied research institute studying the social implications of '
            'artificial intelligence and algorithmic systems.'
        ),
    },
    {
        'name': 'OpenAI Usage Policies Analyzer (community tools)',
        'type': 'Community tool',
        'url': 'https://openai.com/policies/usage-policies',
        'description': (
            'Various community scripts exist to check OpenAI policy compliance; '
            'the authoritative source is OpenAI\'s own usage policy documentation.'
        ),
    },
    {
        'name': 'PrivacyTerms.io / ToS;DR',
        'type': 'Consumer tool',
        'url': 'https://tosdr.org/',
        'description': (
            '"Terms of Service; Didn\'t Read" rates and summarises terms of service '
            'agreements, including AI-related clauses.'
        ),
    },
    {
        'name': 'Future of Privacy Forum — AI Policy Resources',
        'type': 'Policy hub',
        'url': 'https://fpf.org/focus-area/artificial-intelligence/',
        'description': (
            'Policy briefs, guidance, and analysis on AI privacy and data governance '
            'from a non-profit focused on privacy leadership.'
        ),
    },
]


# ---------------------------------------------------------------------------
# AIPolicyResearcher
# ---------------------------------------------------------------------------

class AIPolicyResearcher:
    """
    Analyses policy documents for AI-specific clauses and conditions.

    Usage::

        researcher = AIPolicyResearcher()
        result = researcher.research(policy_text, company_name="Acme Corp")
        print(researcher.format_report(result))
    """

    # ------------------------------------------------------------------
    # Compiled detection patterns
    # ------------------------------------------------------------------

    # AI training data — user content used to train or improve AI/ML models
    _TRAINING_PATTERNS = [
        re.compile(p, re.IGNORECASE | re.DOTALL)
        for p in [
            r'(?:train|improve|develop|fine.?tun).{0,80}?(?:model|algorithm|AI|machine learning|neural)',
            r'(?:your|user|customer).{0,60}?(?:content|data|input).{0,80}?'
            r'(?:train|improve|develop).{0,60}?(?:AI|ML|model|algorithm)',
            r'(?:AI|machine learning|model).{0,80}?(?:train|learn).{0,60}?'
            r'(?:your|user|customer).{0,60}?(?:content|data|input)',
            r'use.{0,60}?(?:content|data|information).{0,60}?'
            r'(?:train|improve|enhance).{0,60}?(?:AI|model|algorithm|service)',
        ]
    ]

    # Automated / algorithmic decision-making
    _AUTO_DECISION_PATTERNS = [
        re.compile(p, re.IGNORECASE | re.DOTALL)
        for p in [
            r'automated?.{0,80}?decision',
            r'algorithmic.{0,80}?(?:decision|scoring|ranking|selection)',
            r'(?:without|no).{0,40}?human.{0,40}?(?:review|oversight|intervention)',
            r'solely.{0,80}?automated',
            r'automatic.{0,80}?(?:process|moderat|terminat|suspend|ban)',
            r'(?:AI|algorithm|system).{0,80}?(?:determin|decid|assess|evaluat)',
        ]
    ]

    # AI-generated content disclosures
    _AI_GENERATED_PATTERNS = [
        re.compile(p, re.IGNORECASE | re.DOTALL)
        for p in [
            r'AI.?generated',
            r'generated.{0,40}?(?:by|using|with).{0,40}?(?:AI|artificial intelligence|model|algorithm)',
            r'(?:synthetic|machine.?generated).{0,60}?(?:content|text|image|audio|video)',
            r'(?:language model|LLM|GPT|generative AI).{0,80}?(?:generat|creat|produc)',
        ]
    ]

    # AI opt-out provisions
    _OPT_OUT_PATTERNS = [
        re.compile(p, re.IGNORECASE | re.DOTALL)
        for p in [
            r'opt.out.{0,80}?(?:AI|automated|algorithmic|training|profil)',
            r'(?:disable|turn off|object to).{0,80}?(?:AI|automated|algorithmic|profil)',
            r'right.{0,60}?(?:object|refuse|opt.out).{0,60}?(?:automated|AI|algorithmic)',
            r'(?:AI|automated).{0,80}?opt.out',
        ]
    ]

    # Algorithmic profiling and personalisation
    _PROFILING_PATTERNS = [
        re.compile(p, re.IGNORECASE | re.DOTALL)
        for p in [
            r'(?:profil|personalise|personalize|tailor).{0,80}?(?:AI|algorithm|automated|machine learning)',
            r'(?:AI|algorithm|machine learning).{0,80}?(?:profil|personaliz|recommend|predict)',
            r'(?:behaviour|behavioral).{0,60}?(?:analys|target|track|monitor)',
            r'(?:infer|predict).{0,80}?(?:interest|preference|behaviour|characteristic)',
        ]
    ]

    # AI transparency disclosures
    _TRANSPARENCY_PATTERNS = [
        re.compile(p, re.IGNORECASE | re.DOTALL)
        for p in [
            r'(?:explain|explainab|transparent|disclosure).{0,80}?(?:AI|algorithm|automated|decision)',
            r'(?:AI|algorithm).{0,80}?(?:explainab|transparent|accountab)',
            r'how.{0,60}?(?:AI|algorithm|automated system).{0,60}?work',
            r'(?:human|manual).{0,60}?review.{0,60}?(?:AI|automated|algorithmic)',
        ]
    ]

    # Regulatory and framework references
    _REGULATORY_PATTERNS = [
        re.compile(p, re.IGNORECASE)
        for p in [
            r'\bEU AI Act\b',
            r'\bAI Act\b',
            r'GDPR.{0,40}?article.{0,20}?22',
            r'article.{0,20}?22.{0,40}?GDPR',
            r'\bGDPR\b',
            r'\bCCPA\b',
            r'\bCPRA\b',
            r'executive order.{0,40}?(?:AI|artificial intelligence)',
            r'(?:AI|artificial intelligence).{0,40}?executive order',
            r'NIST AI',
            r'AI Risk Management',
            r'IEEE.{0,40}?(?:AI|ethic)',
            r'(?:responsible|trustworthy|ethical).{0,40}?AI',
            r'AI safety',
            r'AI governance',
        ]
    ]

    # Keywords used to quickly check whether a document mentions AI at all
    _AI_SIGNAL_WORDS = [
        'artificial intelligence', 'machine learning', 'ai system',
        'algorithm', 'automated', 'chatbot', 'large language model', 'llm',
        'generative ai', 'neural network', 'deep learning', 'nlp',
        'natural language processing', 'computer vision', 'recommendation',
    ]

    def __init__(self):
        pass

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def research(self, text: str, company_name: str = "Unknown") -> Dict:
        """
        Perform comprehensive AI policy research on a document.

        Args:
            text: The full text of the policy document.
            company_name: Name of the company (optional, used in reports).

        Returns:
            Dictionary with research findings.
        """
        return {
            'company_name': company_name,
            'analysis_date': datetime.now().isoformat(),
            'ai_signals_detected': self._detect_ai_signals(text),
            'training_data_clauses': self._extract_matches(
                self._TRAINING_PATTERNS, text, context_chars=150),
            'automated_decision_clauses': self._extract_matches(
                self._AUTO_DECISION_PATTERNS, text, context_chars=150),
            'ai_generated_content_clauses': self._extract_matches(
                self._AI_GENERATED_PATTERNS, text, context_chars=150),
            'ai_opt_out_clauses': self._extract_matches(
                self._OPT_OUT_PATTERNS, text, context_chars=150),
            'profiling_clauses': self._extract_matches(
                self._PROFILING_PATTERNS, text, context_chars=150),
            'transparency_clauses': self._extract_matches(
                self._TRANSPARENCY_PATTERNS, text, context_chars=150),
            'regulatory_references': self._extract_regulatory_refs(text),
            'known_ai_policy_tools': KNOWN_AI_POLICY_TOOLS,
            'risk_summary': self._compute_risk_summary(text),
            'document_length': len(text),
            'word_count': len(text.split()),
        }

    def format_report(self, result: Dict) -> str:
        """
        Format research results as a human-readable report.

        Args:
            result: The output of ``research()``.

        Returns:
            Formatted report string.
        """
        lines = []
        sep = "=" * 80
        sub = "-" * 40

        lines.append(sep)
        lines.append(f"AI POLICY RESEARCH REPORT: {result['company_name']}")
        lines.append(sep)
        lines.append(f"Analysis date : {result['analysis_date']}")
        lines.append(f"Document size : {result['document_length']:,} chars / "
                     f"{result['word_count']:,} words")
        lines.append("")

        # Risk summary
        risk = result['risk_summary']
        lines.append("RISK SUMMARY")
        lines.append(sub)
        lines.append(f"  Overall risk level : {risk['level']}")
        lines.append(f"  AI signals detected: {risk['ai_signal_count']}")
        lines.append(f"  Concern categories : {risk['concern_count']}")
        lines.append(f"  Opt-out provisions : "
                     f"{'Yes' if risk['has_opt_out'] else 'Not found'}")
        lines.append(f"  Transparency notes : "
                     f"{'Yes' if risk['has_transparency'] else 'Not found'}")
        lines.append("")

        # AI signals
        signals = result['ai_signals_detected']
        if signals:
            lines.append(f"AI SIGNALS DETECTED ({len(signals)})")
            lines.append(sub)
            for s in signals:
                lines.append(f"  • {s}")
            lines.append("")

        def _append_section(title: str, clauses: List[str]) -> None:
            if clauses:
                lines.append(f"{title} ({len(clauses)})")
                lines.append(sub)
                for clause in clauses[:5]:
                    snippet = clause.replace('\n', ' ').strip()
                    lines.append(f"  • …{snippet[:120]}…")
                if len(clauses) > 5:
                    lines.append(f"  … and {len(clauses) - 5} more")
                lines.append("")

        _append_section("TRAINING DATA CLAUSES", result['training_data_clauses'])
        _append_section("AUTOMATED DECISION-MAKING", result['automated_decision_clauses'])
        _append_section("AI-GENERATED CONTENT", result['ai_generated_content_clauses'])
        _append_section("AI OPT-OUT PROVISIONS", result['ai_opt_out_clauses'])
        _append_section("ALGORITHMIC PROFILING", result['profiling_clauses'])
        _append_section("AI TRANSPARENCY", result['transparency_clauses'])

        # Regulatory references
        regs = result['regulatory_references']
        if regs:
            lines.append(f"REGULATORY REFERENCES ({len(regs)})")
            lines.append(sub)
            for ref in regs:
                lines.append(f"  • {ref}")
            lines.append("")

        # Known AI policy tools
        lines.append("KNOWN AI POLICY & ANALYSIS TOOLS (for reference)")
        lines.append(sub)
        for tool in result['known_ai_policy_tools']:
            lines.append(f"  [{tool['type']}] {tool['name']}")
            lines.append(f"    {tool['description']}")
            lines.append(f"    {tool['url']}")
            lines.append("")

        lines.append(sep)
        return "\n".join(lines)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _detect_ai_signals(self, text: str) -> List[str]:
        """Return AI-related signal words present in the text."""
        text_lower = text.lower()
        return [w for w in self._AI_SIGNAL_WORDS if w in text_lower]

    def _extract_matches(
        self, patterns: List[re.Pattern], text: str, context_chars: int = 150
    ) -> List[str]:
        """
        Return unique context snippets for all pattern matches.

        For each compiled pattern, extract surrounding context rather than the
        raw regex match, so reports are human-readable.
        """
        snippets = set()
        for pattern in patterns:
            for match in pattern.finditer(text):
                start = max(0, match.start() - 20)
                end = min(len(text), match.end() + context_chars)
                snippet = text[start:end].strip()
                snippets.add(snippet)
        # Return in document order (approximate) using start position
        ordered = sorted(
            snippets,
            key=lambda s: text.find(s) if s in text else len(text)
        )
        return ordered[:20]  # cap at 20 per category

    def _extract_regulatory_refs(self, text: str) -> List[str]:
        """Extract unique regulatory/framework references."""
        refs: List[str] = []
        seen: set = set()
        for pattern in self._REGULATORY_PATTERNS:
            for match in pattern.finditer(text):
                key = match.group(0).lower()
                if key not in seen:
                    seen.add(key)
                    start = max(0, match.start() - 10)
                    end = min(len(text), match.end() + 60)
                    refs.append(text[start:end].strip())
        return refs[:15]

    def _compute_risk_summary(self, text: str) -> Dict:
        """
        Compute a lightweight risk summary.

        Risk level is a simple heuristic:
        - LOW    : few or no AI signals
        - MEDIUM : AI signals present but some protections found
        - HIGH   : AI signals present with no opt-out or transparency clauses
        """
        ai_signals = self._detect_ai_signals(text)
        has_opt_out = bool(self._extract_matches(self._OPT_OUT_PATTERNS, text))
        has_transparency = bool(
            self._extract_matches(self._TRANSPARENCY_PATTERNS, text)
        )

        concern_count = 0
        for patterns in [
            self._TRAINING_PATTERNS,
            self._AUTO_DECISION_PATTERNS,
            self._PROFILING_PATTERNS,
        ]:
            if self._extract_matches(patterns, text):
                concern_count += 1

        signal_count = len(ai_signals)

        if signal_count == 0:
            level = 'LOW — No significant AI signals detected'
        elif has_opt_out and has_transparency:
            level = 'LOW-MEDIUM — AI present; opt-out and transparency noted'
        elif has_opt_out or has_transparency:
            level = 'MEDIUM — AI present; partial protections found'
        elif concern_count >= 2:
            level = 'HIGH — AI concerns found; no opt-out or transparency'
        else:
            level = 'MEDIUM — AI signals present; limited protections found'

        return {
            'level': level,
            'ai_signal_count': signal_count,
            'concern_count': concern_count,
            'has_opt_out': has_opt_out,
            'has_transparency': has_transparency,
        }


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def main():
    """Interactive AI Policy Researcher."""
    print("AI Policy Researcher")
    print("=" * 80)
    print()
    print("Analyzes policy documents for AI-specific clauses and conditions.")
    print()
    print("Usage:")
    print("  1. Paste your policy text when prompted")
    print("  2. Press Ctrl+D (Linux/Mac) or Ctrl+Z (Windows) when done")
    print()

    company = input("Enter company name (optional): ").strip() or "Unknown Company"
    print("\nPaste the policy text below (Ctrl+D or Ctrl+Z when finished):")
    print("-" * 80)

    try:
        lines = []
        while True:
            try:
                lines.append(input())
            except EOFError:
                break

        text = "\n".join(lines)

        if not text.strip():
            print("\nNo text provided. Using example...")
            text = """
            Privacy Policy — TechCorp AI Platform

            AI AND MACHINE LEARNING:
            We use artificial intelligence and machine learning to personalise your
            experience, detect fraud, and improve our services. Your content and usage
            data may be used to train our AI models unless you opt out.

            AUTOMATED DECISIONS:
            Some decisions affecting your account are made automatically by our
            algorithms without human review. You have the right to request human
            oversight for decisions that significantly affect you.

            OPT-OUT:
            You may opt out of AI-based personalisation at any time by visiting
            your privacy settings. Note that some features may be unavailable
            if you disable AI processing.

            REGULATORY COMPLIANCE:
            We comply with GDPR Article 22 regarding automated decision-making
            and are monitoring developments under the EU AI Act.
            """

        researcher = AIPolicyResearcher()
        result = researcher.research(text, company)
        print("\n" + researcher.format_report(result))

    except KeyboardInterrupt:
        print("\n\nCancelled.")


if __name__ == "__main__":
    main()
