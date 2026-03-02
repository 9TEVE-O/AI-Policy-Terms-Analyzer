#!/usr/bin/env python3
"""
Key Point Condenser

A long-text summarization assistant that creates summaries, abstracts, and
structured outlines from policy documents and other long-form text.
"""

import re
import json
from typing import Dict, List


class KeyPointCondenser:
    """Summarizes text and generates abstracts and structured outlines."""

    # Words to ignore when scoring sentence importance
    _STOP_WORDS = {
        'a', 'an', 'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
        'of', 'with', 'by', 'from', 'up', 'about', 'into', 'through', 'is',
        'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had',
        'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might',
        'shall', 'can', 'that', 'this', 'these', 'those', 'it', 'its', 'we',
        'you', 'he', 'she', 'they', 'us', 'our', 'your', 'their', 'which',
        'who', 'whom', 'what', 'when', 'where', 'how', 'if', 'as', 'not',
        'also', 'such', 'any', 'all', 'both', 'each', 'more', 'most', 'other',
        'than', 'then', 'so', 'no', 'nor', 'yet', 'only', 'just', 'very',
    }

    # Heading detection: ALL-CAPS lines or lines ending with a colon (short)
    _HEADING_RE = re.compile(
        r'^(?:[A-Z][A-Z\s&/()\-]{2,}[A-Z]|[A-Z][^\n.!?]{0,60}:)\s*$',
        re.MULTILINE,
    )

    def __init__(self):
        # Split on sentence-ending punctuation followed by whitespace
        self._sentence_re = re.compile(r'(?<=[.!?])\s+')

    def _split_sentences(self, text: str) -> List[str]:
        """Split text into individual sentences, filtering very short fragments.

        Heading lines are removed before splitting so that section titles do not
        appear as part of extracted sentences.
        """
        # Strip heading-like lines so they don't pollute sentence extraction
        clean_text = self._HEADING_RE.sub(' ', text)
        sentences = self._sentence_re.split(clean_text)
        return [s.strip() for s in sentences if s.strip() and len(s.split()) >= 4]

    def _word_frequencies(self, text: str) -> Dict[str, int]:
        """Calculate word frequencies, excluding stop words."""
        words = re.findall(r'\b[a-z]+\b', text.lower())
        freq: Dict[str, int] = {}
        for word in words:
            if word not in self._STOP_WORDS:
                freq[word] = freq.get(word, 0) + 1
        return freq

    def _score_sentences(self, sentences: List[str], freq: Dict[str, int]) -> List[float]:
        """Score sentences by summing frequency scores of their meaningful words.

        Scores are normalized by sentence length to avoid bias toward long sentences.
        """
        scores = []
        for sentence in sentences:
            words = re.findall(r'\b[a-z]+\b', sentence.lower())
            score = sum(freq.get(w, 0) for w in words if w not in self._STOP_WORDS)
            scores.append(score / max(len(words), 1))
        return scores

    def summarize(self, text: str, num_sentences: int = 5) -> str:
        """Create an extractive summary of the text.

        Selects the highest-scoring sentences and returns them in the order
        they appear in the original text.

        Args:
            text: The text to summarize.
            num_sentences: Number of sentences to include in the summary.

        Returns:
            A string containing the top sentences in original order.
        """
        sentences = self._split_sentences(text)
        if not sentences:
            return ""
        num_sentences = min(num_sentences, len(sentences))
        freq = self._word_frequencies(text)
        scores = self._score_sentences(sentences, freq)
        ranked = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)
        top_indices = sorted(ranked[:num_sentences])
        return ' '.join(sentences[i] for i in top_indices)

    def generate_abstract(self, text: str) -> str:
        """Generate a short abstract (3-sentence summary) of the text.

        Args:
            text: The text to abstract.

        Returns:
            A concise abstract of the text.
        """
        return self.summarize(text, num_sentences=3)

    def generate_outline(self, text: str) -> List[Dict]:
        """Generate a structured outline from the text.

        Detects section headings and extracts the top key sentences per section.
        When no headings are detected, a single 'Main Points' section is returned.

        Args:
            text: The text to outline.

        Returns:
            List of dicts, each with 'heading' (str) and 'key_points' (List[str]).
        """
        headings = self._HEADING_RE.findall(text)
        parts = self._HEADING_RE.split(text)

        if not headings:
            sentences = self._split_sentences(text)
            freq = self._word_frequencies(text)
            scores = self._score_sentences(sentences, freq)
            ranked = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)
            key_points = [sentences[i] for i in ranked[:3] if i < len(sentences)]
            return [{'heading': 'Main Points', 'key_points': key_points}]

        outline = []
        for i, heading in enumerate(headings):
            section_text = parts[i + 1] if i + 1 < len(parts) else ''
            sentences = self._split_sentences(section_text)
            if not sentences:
                continue
            freq = self._word_frequencies(section_text)
            scores = self._score_sentences(sentences, freq)
            ranked = sorted(range(len(scores)), key=lambda j: scores[j], reverse=True)
            key_points = [sentences[j] for j in ranked[:2] if j < len(sentences)]
            outline.append({
                'heading': heading.strip().rstrip(':'),
                'key_points': key_points,
            })
        return outline

    def condense(self, text: str, title: str = "Document") -> Dict:
        """Perform full condensing: abstract, summary, and structured outline.

        Args:
            text: The text to condense.
            title: Title or name for the document.

        Returns:
            Dictionary with keys 'title', 'word_count', 'abstract', 'summary',
            and 'outline'.
        """
        return {
            'title': title,
            'word_count': len(text.split()),
            'abstract': self.generate_abstract(text),
            'summary': self.summarize(text),
            'outline': self.generate_outline(text),
        }

    def format_report(self, condensed: Dict) -> str:
        """Format the condensed output as a human-readable report.

        Args:
            condensed: The output of condense().

        Returns:
            A human-readable string report.
        """
        report = []
        report.append("=" * 80)
        report.append(f"KEY POINT CONDENSER REPORT: {condensed['title']}")
        report.append("=" * 80)
        report.append(f"Original word count: {condensed['word_count']:,}")
        report.append("")

        report.append("ABSTRACT")
        report.append("-" * 40)
        report.append(condensed['abstract'] or "(No abstract generated)")
        report.append("")

        report.append("SUMMARY")
        report.append("-" * 40)
        report.append(condensed['summary'] or "(No summary generated)")
        report.append("")

        if condensed['outline']:
            report.append("OUTLINE")
            report.append("-" * 40)
            for section in condensed['outline']:
                report.append(f"\n  {section['heading']}")
                for point in section['key_points']:
                    report.append(f"    • {point}")
            report.append("")

        report.append("=" * 80)
        return "\n".join(report)


def main():
    """Interactive Key Point Condenser."""
    print("Key Point Condenser")
    print("=" * 80)
    print()
    print("Usage:")
    print("  1. Paste your text when prompted")
    print("  2. Press Ctrl+D (Linux/Mac) or Ctrl+Z (Windows) when done")
    print()

    title = input("Enter document title (optional): ").strip() or "Document"
    print("\nPaste the text below (Ctrl+D or Ctrl+Z when finished):")
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
            Privacy Policy - TechCorp Inc.

            DATA COLLECTION:
            We collect personal information including your name, email address, and
            usage data when you interact with our services. This information helps us
            improve our products and provide a better experience.

            DATA SHARING:
            We may share your data with trusted third-party service providers who
            assist us in operating our website, conducting our business, or servicing you.
            All third parties are required to keep your information confidential.

            SECURITY:
            We implement industry-standard security measures to protect your data from
            unauthorized access, alteration, disclosure, or destruction. However, no
            method of transmission over the Internet is 100% secure.
            """

        condenser = KeyPointCondenser()
        result = condenser.condense(text, title)
        print("\n" + condenser.format_report(result))

        save = input("\nSave results as JSON? (y/n): ").strip().lower()
        if save == 'y':
            safe_title = re.sub(r'[^\w\s-]', '', title).strip()
            safe_title = re.sub(r'[-\s]+', '_', safe_title)
            filename = f"{safe_title}_condensed.json"
            try:
                with open(filename, 'w') as f:
                    json.dump(result, f, indent=2)
                print(f"Results saved to {filename}")
            except (PermissionError, OSError) as e:
                print(f"Could not save results to '{filename}': {e}")

    except KeyboardInterrupt:
        print("\n\nCancelled.")


if __name__ == "__main__":
    main()
