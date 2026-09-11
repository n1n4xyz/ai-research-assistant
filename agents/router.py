from google.adk.agents import LlmAgent
from google.genai.types import GenerateContentConfig


class DomainClassifierAgent(LlmAgent):
    """
    Classifies research queries into appropriate domains.

    This agent analyzes queries and routes them to appropriate specialist
    processing based on domain, complexity, and content type.

    """

    def __init__(self, model: str = "gemini-2.0-flash"):
        """Initialize the domain classifier agent.

        Args:
            model: Gemini model name
        """
        instruction = """You are a research query classification specialist.

Your role:
1. Analyze research queries to determine their primary domain
2. Assess query complexity and depth
3. Provide confidence scores for routing decisions
4. Suggest fallback options for ambiguous queries

Supported domains:
- computer_science: AI, ML, software engineering, algorithms, systems
- biology: Life sciences, genetics, ecology, medicine, neuroscience
- physics: Theoretical physics, quantum mechanics, astrophysics, materials
- chemistry: Organic, inorganic, physical chemistry, biochemistry
- medicine: Clinical research, diagnostics, treatments, public health
- economics: Finance, markets, policy, behavioral economics
- psychology: Cognitive, social, clinical, developmental psychology
- mathematics: Pure math, applied math, statistics, optimization
- engineering: Mechanical, electrical, civil, aerospace engineering
- interdisciplinary: Crosses multiple domains

Query complexity levels:
- low: Simple definition or concept explanation
- moderate: Requires synthesis of multiple sources
- high: Deep analysis, cutting-edge research, or complex synthesis

Output format (JSON):
{
  "domain": "primary_domain",
  "confidence": 0.0-1.0,
  "complexity": "low/moderate/high",
  "reasoning": "Why this domain was selected",
  "alternative_domains": ["backup1", "backup2"],
  "recommended_sources": ["web", "arxiv", "scholar"],
  "specialist_agent": "domain_name_specialist"
}

Confidence guidelines:
- >0.9: Very clear domain match
- 0.7-0.9: Strong match with minor ambiguity
- 0.5-0.7: Moderate match, consider alternatives
- <0.5: Unclear, use general/interdisciplinary

Be precise in classification but acknowledge uncertainty when present."""

        # TODO 5: Initialize LlmAgent for domain classification 

        pass  # REPLACE THIS LINE: Initialize LlmAgent with super().__init__() here


class QueryComplexityAgent(LlmAgent):
    """
    Assesses query complexity for resource allocation.

    """

    def __init__(self, model: str = "gemini-2.0-flash"):
        """Initialize the complexity assessment agent.

        Args:
            model: Gemini model name
        """
        instruction = """You are a query complexity assessment specialist.

Your role:
1. Analyze the depth and breadth of research queries
2. Estimate the resources needed to answer thoroughly
3. Recommend processing strategies based on complexity

Complexity factors:
- Scope: Narrow topic vs. broad synthesis
- Depth: Surface-level vs. cutting-edge research
- Interdisciplinarity: Single field vs. multiple domains
- Recency: Historical vs. latest developments
- Specificity: General overview vs. specific techniques

Output format (JSON):
{
  "complexity_score": 0.0-1.0,
  "complexity_level": "low/moderate/high",
  "factors": {
    "scope": "narrow/moderate/broad",
    "depth": "surface/moderate/deep",
    "interdisciplinary": true/false,
    "recency_required": true/false,
    "specificity": "general/moderate/specific"
  },
  "recommended_strategy": "Strategy description",
  "estimated_sources_needed": 10,
  "suggested_iterations": 2
}

Use this to help allocate appropriate resources for each query."""

        super().__init__(
            name="complexity_assessor",
            model=model,
            instruction=instruction,
            generate_content_config=GenerateContentConfig(
                temperature=0.2,
                max_output_tokens=384,
                response_mime_type="application/json"
            )
        )
