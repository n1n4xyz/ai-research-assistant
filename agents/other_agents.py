import json
from typing import Dict, Any
from google.adk.agents import LlmAgent
from google import genai
from google.genai.types import GenerateContentConfig


class DomainClassifierAgent(LlmAgent):
    """Classifies research queries into domains."""

    def __init__(self, model: str = "gemini-2.0-flash"):
        """Initialize domain classifier.

        Args:
            model: Gemini model name
        """
        instruction = """You are a research query classification specialist.

Your role:
1. Classify research queries into appropriate domains
2. Provide confidence scores for classification
3. Analyze query complexity
4. Recommend appropriate sources

Supported domains:
- computer_science
- biology
- physics
- chemistry
- medicine
- mathematics
- engineering
- social_science
- general

Output format (JSON):
{
  "domain": "computer_science",
  "confidence": 0.95,
  "complexity": "medium/high/low",
  "reasoning": "Brief explanation of classification",
  "recommended_sources": ["web", "arxiv", "scholar"],
  "keywords": ["key1", "key2", "key3"]
}"""

        # Initialize ADK LlmAgent
        super().__init__(
            name="domain_classifier",
            model=model,
            instruction=instruction,
            generate_content_config=GenerateContentConfig(
                temperature=0.3,
                max_output_tokens=512,
                response_mime_type="application/json"
            )
        )

    def classify(self, client: genai.Client, query: str) -> Dict[str, Any]:
        """Classify research query using direct genai.Client call.

        execution: Use the agent's configuration but execute directly.

        Args:
            client: Configured genai.Client
            query: Research question

        Returns:
            Classification results
        """
        # Use agent's instruction and config for execution
        prompt = f"{self.instruction}\n\nuser: Classify this research query: {query}"

        response = client.models.generate_content(
            model=self.model,
            contents=prompt,
            config=self.generate_content_config
        )

        try:
            result = json.loads(response.text)
            result['_metadata'] = {
                'agent': self.name,
                'execution': 'direct_genai_client'
            }
            return result
        except json.JSONDecodeError:
            return {
                'domain': 'general',
                'confidence': 0.5,
                'complexity': 'medium',
                'reasoning': 'Classification failed',
                'recommended_sources': ['web', 'arxiv', 'scholar'],
                'keywords': [],
                '_metadata': {'agent': self.name, 'error': 'json_parse_error'}
            }


class FactCheckAgent(LlmAgent):
    """Validates research claims for accuracy (ADK LlmAgent)."""

    def __init__(self, model: str = "gemini-2.0-flash"):
        """Initialize fact checker.

        Args:
            model: Gemini model name
        """
        instruction = """You are a research fact-checking specialist.

Your role:
1. Verify claims against your knowledge
2. Identify potentially inaccurate or unsupported statements
3. Assess overall credibility
4. Provide verification notes

Output format (JSON):
{
  "verified_claims": ["List of verified statements"],
  "questionable_claims": ["List of claims needing verification"],
  "credibility_score": 0.85,
  "verification_notes": "Brief notes on verification process",
  "sources_checked": ["List of knowledge sources validated against"],
  "recommendations": ["Suggestions for strengthening claims"]
}"""

        # Initialize ADK LlmAgent
        super().__init__(
            name="fact_checker",
            model=model,
            instruction=instruction,
            generate_content_config=GenerateContentConfig(
                temperature=0.3,
                max_output_tokens=1024,
                response_mime_type="application/json"
            )
        )

    def check(self, client: genai.Client, answer: Dict[str, Any],
              sources: Dict[str, Any] = None) -> Dict[str, Any]:
        """Fact-check research answer using direct genai.Client call.

        Args:
            client: Configured genai.Client
            answer: Research answer to check
            sources: Source information

        Returns:
            Fact-check results
        """
        prompt = f"""{self.instruction}

user: Please fact-check this research answer:

Answer: {answer.get('answer', 'No answer provided')}
Key Points: {json.dumps(answer.get('key_points', []))}
"""
        if sources:
            prompt += f"\nSources mentioned: {json.dumps(sources.get('aggregated_sources', {}).get('top_sources', [])[:5], indent=2)}"

        response = client.models.generate_content(
            model=self.model,
            contents=prompt,
            config=self.generate_content_config
        )

        try:
            result = json.loads(response.text)
            result['_metadata'] = {
                'agent': self.name,
                'execution': 'direct_genai_client'
            }
            return result
        except json.JSONDecodeError:
            return {
                'verified_claims': [],
                'questionable_claims': [],
                'credibility_score': 0.5,
                'verification_notes': 'Fact-checking failed',
                'sources_checked': [],
                'recommendations': [],
                '_metadata': {'agent': self.name, 'error': 'json_parse_error'}
            }


class SynthesisAgent(LlmAgent):
    """Synthesizes research findings into coherent narrative (ADK LlmAgent)."""

    def __init__(self, model: str = "gemini-2.0-flash"):
        """Initialize synthesis agent.

        Args:
            model: Gemini model name
        """
        instruction = """You are a research synthesis specialist.

Your role:
1. Combine findings from multiple sources
2. Create coherent narrative structure
3. Identify key themes and insights
4. Maintain academic tone
5. Provide actionable recommendations

Output format (JSON):
{
  "synthesis": "Comprehensive narrative combining all findings (3-5 paragraphs)",
  "key_insights": ["Main insight 1", "Main insight 2", "Main insight 3"],
  "themes": ["Major theme 1", "Major theme 2"],
  "recommendations": ["Actionable recommendation 1", "Actionable recommendation 2"],
  "coherence_score": 0.9,
  "executive_summary": "1-2 sentence summary"
}"""

        # Initialize ADK LlmAgent
        super().__init__(
            name="synthesizer",
            model=model,
            instruction=instruction,
            generate_content_config=GenerateContentConfig(
                temperature=0.7,
                max_output_tokens=2048,
                response_mime_type="application/json"
            )
        )

    def synthesize(self, client: genai.Client, query: str, answer: Dict[str, Any],
                    fact_check: Dict[str, Any], sources: Dict[str, Any]) -> Dict[str, Any]:
        """Synthesize research findings using direct genai.Client call.

        Args:
            client: Configured genai.Client
            query: Original question
            answer: Research answer
            fact_check: Fact-check results
            sources: Source information

        Returns:
            Synthesized findings
        """
        prompt = f"""{self.instruction}

user: Synthesize these research findings:

Question: {query}

Answer: {answer.get('answer', 'No answer')}

Key Points: {json.dumps(answer.get('key_points', []))}

Credibility: {fact_check.get('credibility_score', 0.5)}

Top Sources: {len(sources.get('aggregated_sources', {}).get('top_sources', []))} sources available"""

        response = client.models.generate_content(
            model=self.model,
            contents=prompt,
            config=self.generate_content_config
        )

        try:
            result = json.loads(response.text)
            result['_metadata'] = {
                'agent': self.name,
                'execution': 'direct_genai_client'
            }
            return result
        except json.JSONDecodeError:
            return {
                'synthesis': answer.get('answer', 'Synthesis failed'),
                'key_insights': answer.get('key_points', []),
                'themes': [],
                'recommendations': [],
                'coherence_score': 0.5,
                'executive_summary': 'Synthesis failed',
                '_metadata': {'agent': self.name, 'error': 'json_parse_error'}
            }


class CitationAgent(LlmAgent):
    """Generates properly formatted citations (ADK LlmAgent)."""

    def __init__(self, model: str = "gemini-2.0-flash"):
        """Initialize citation agent.

        Args:
            model: Gemini model name
        """
        instruction = """You are an academic citation specialist.

Your role:
1. Format citations in standard academic styles
2. Generate bibliography
3. Ensure proper attribution

Output format (JSON):
{
  "citations": [
    {
      "source_title": "Source title",
      "citation_apa": "APA formatted citation",
      "citation_mla": "MLA formatted citation",
      "citation_number": 1
    }
  ],
  "bibliography": "Complete bibliography in APA format",
  "total_citations": 10,
  "citation_style": "APA"
}"""

        # Initialize ADK LlmAgent
        super().__init__(
            name="citation_formatter",
            model=model,
            instruction=instruction,
            generate_content_config=GenerateContentConfig(
                temperature=0.1,
                max_output_tokens=1536,
                response_mime_type="application/json"
            )
        )

    def format_citations(self, client: genai.Client, sources: Dict[str, Any]) -> Dict[str, Any]:
        """Format citations for sources using direct genai.Client call.

        Args:
            client: Configured genai.Client
            sources: Source information

        Returns:
            Formatted citations
        """
        top_sources = sources.get('aggregated_sources', {}).get('top_sources', [])

        prompt = f"""{self.instruction}

user: Generate citations for these sources:

{json.dumps(top_sources[:10], indent=2)}"""

        response = client.models.generate_content(
            model=self.model,
            contents=prompt,
            config=self.generate_content_config
        )

        try:
            result = json.loads(response.text)
            result['_metadata'] = {
                'agent': self.name,
                'execution': 'direct_genai_client'
            }
            return result
        except json.JSONDecodeError:
            return {
                'citations': [],
                'bibliography': '',
                'total_citations': 0,
                'citation_style': 'APA',
                '_metadata': {'agent': self.name, 'error': 'json_parse_error'}
            }
