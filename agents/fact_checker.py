"""Fact checking agent using LlmAgent pattern.

This module provides fact-checking capabilities using LLM's knowledge base
to validate research claims and assess credibility.
"""

from google.adk.agents import LlmAgent
from google.genai.types import GenerateContentConfig


class FactCheckAgent(LlmAgent):
    """
    Validates research claims for accuracy and credibility.

    Uses the LLM's training data to evaluate claims and identify
    potential inaccuracies or areas needing verification.

    Pattern: LlmAgent for validation tasks
    """

    def __init__(self, model: str = "gemini-2.0-flash"):
        """Initialize the fact check agent.

        Args:
            model: Gemini model name
        """
        instruction = """You are a fact-checking specialist for research content.

Your role:
1. Extract specific factual claims from research answers
2. Evaluate each claim against your knowledge base
3. Assess credibility and identify potential issues
4. Provide evidence-based verdicts

Claim extraction:
- Identify testable, specific statements
- Focus on key findings and conclusions
- Ignore opinions or subjective assessments

Verdict categories:
- verified: Consistent with established knowledge (high confidence)
- plausible: Likely accurate but needs verification (moderate confidence)
- uncertain: Insufficient information to assess (low confidence)
- questionable: Potentially inaccurate or misleading (flag for review)

Output format (JSON):
{
  "claims_extracted": 5,
  "claim_results": [
    {
      "claim": "Specific factual statement extracted",
      "verdict": "verified/plausible/uncertain/questionable",
      "confidence": 0.0-1.0,
      "reasoning": "Evidence or reasoning for verdict",
      "supporting_facts": ["fact1", "fact2"]
    }
  ],
  "overall_credibility": 0.0-1.0,
  "concerns": ["List", "of", "concerns"],
  "verification_needed": ["Claims", "needing", "external", "verification"]
}

Be rigorous but acknowledge the limits of knowledge-based verification."""

        super().__init__(
            name="fact_checker",
            model=model,
            instruction=instruction,
            generate_content_config=GenerateContentConfig(
                temperature=0.2,
                max_output_tokens=1024,
                response_mime_type="application/json"
            )
        )
