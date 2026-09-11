"""Synthesis and citation agents using LlmAgent pattern.

This module provides research synthesis and citation generation using LlmAgents.
"""

from google.adk.agents import LlmAgent
from google.genai.types import GenerateContentConfig


class SynthesisAgent(LlmAgent):
    """
    Synthesizes research findings into coherent narratives.

    Combines research answers, source information, and fact-checking results
    into comprehensive research reports.

    Pattern: LlmAgent for knowledge synthesis
    """

    def __init__(self, model: str = "gemini-2.0-flash"):
        """Initialize the synthesis agent.

        Args:
            model: Gemini model name
        """
        instruction = """You are a research synthesis specialist that creates comprehensive reports.

Your role:
1. Combine research findings from multiple sources into coherent narratives
2. Identify main findings, patterns, and themes
3. Highlight contradictions or knowledge gaps
4. Create executive summaries

Input: You'll receive:
- Research answer with key points
- List of sources consulted
- Fact-checking results
- Quality assessments

Output format (JSON):
{
  "executive_summary": "2-3 paragraph summary covering findings, limitations, and future directions",
  "main_findings": ["finding1", "finding2", "finding3", "finding4", "finding5"],
  "patterns_identified": ["pattern1", "pattern2", "pattern3"],
  "contradictions": ["contradiction1 if any"],
  "knowledge_gaps": [
    "Gap 1: Specific research question or limitation",
    "Gap 2: Area needing further investigation",
    "Gap 3: Methodological limitation"
  ],
  "synthesis_confidence": 0.0-1.0,
  "narrative": "Comprehensive synthesis narrative (3-5 paragraphs) integrating all findings"
}

Create publication-quality research syntheses that are clear, accurate, and insightful."""

        super().__init__(
            name="synthesizer",
            model=model,
            instruction=instruction,
            generate_content_config=GenerateContentConfig(
                temperature=0.5,
                max_output_tokens=2048,
                response_mime_type="application/json"
            )
        )


class CitationAgent(LlmAgent):
    """
    Generates properly formatted citations for sources.

    Creates APA-style citations from source metadata.

    Pattern: LlmAgent for formatting tasks
    """

    def __init__(self, model: str = "gemini-2.0-flash"):
        """Initialize the citation agent.

        Args:
            model: Gemini model name
        """
        instruction = """You are a citation formatting specialist focused on APA style.

Your role:
1. Generate properly formatted APA citations from source metadata
2. Handle various source types (articles, papers, websites, books)
3. Ensure consistency and accuracy in formatting

Source types:
- Web: Website title, URL, access date
- ArXiv: Paper title, authors, arXiv ID, publication date
- Scholar: Article title, authors, journal/venue, year, DOI/URL

APA format examples:
- Web: Author. (Year). Title. Site Name. URL
- ArXiv: Authors. (Year). Paper Title. arXiv. https://arxiv.org/abs/####.#####
- Journal: Authors. (Year). Article Title. Journal Name, Volume(Issue), pages. DOI/URL

Output format (JSON):
{
  "citations": [
    {
      "formatted": "Complete APA citation",
      "source_type": "web/arxiv/scholar",
      "order": 1
    }
  ],
  "citation_count": 10,
  "citation_format": "APA"
}

Generate accurate, properly formatted citations for all sources."""

        super().__init__(
            name="citation_formatter",
            model=model,
            instruction=instruction,
            generate_content_config=GenerateContentConfig(
                temperature=0.1,
                max_output_tokens=1024,
                response_mime_type="application/json"
            )
        )
