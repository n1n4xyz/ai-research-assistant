import json
import asyncio
from typing import Dict, Any, List
from google.adk.agents import LlmAgent, ParallelAgent, SequentialAgent
from google import genai
from google.genai.types import GenerateContentConfig


class WebSearchAgent(LlmAgent):
    """Simulates web search using LLM (ADK LlmAgent)."""

    def __init__(self, model: str = "gemini-2.0-flash"):
        instruction = """You are a web search specialist that finds relevant online sources.

Generate 5-10 realistic web search results with:
- Diverse source types (blogs, documentation, news, tutorials, forums)
- Authentic-looking titles and URLs
- Relevant 2-3 sentence snippets
- Relevance scores (0-1)

Output format (JSON):
{
  "source_type": "web",
  "results": [
    {
      "title": "Descriptive article title",
      "url": "https://example.com/realistic-url",
      "snippet": "2-3 sentence preview that's relevant to the query",
      "relevance": 0.95,
      "source": "website name"
    }
  ],
  "total_found": 10,
  "search_time": 0.5
}"""

        # Initialize ADK LlmAgent 
        super().__init__(
            name="web_search",
            model=model,
            instruction=instruction,
            generate_content_config=GenerateContentConfig(
                temperature=0.8,
                max_output_tokens=1024,
                response_mime_type="application/json"
            )
        )

    def search(self, client: genai.Client, query: str) -> Dict[str, Any]:
        """Execute search using direct genai.Client call (execution)."""
        prompt = f"{self.instruction}\n\nuser: Search query: {query}\n\nGenerate realistic web search results for this query."

        response = client.models.generate_content(
            model=self.model,
            contents=prompt,
            config=self.generate_content_config
        )

        try:
            result = json.loads(response.text)
            result['_metadata'] = {
                'agent': self.name,
                'source_type': 'web',
                'execution': 'direct_genai_client'
            }
            return result
        except json.JSONDecodeError:
            return {
                'source_type': 'web',
                'results': [],
                'total_found': 0,
                'search_time': 0.0,
                '_metadata': {'agent': self.name, 'error': 'json_parse_error'}
            }


class ArxivSearchAgent(LlmAgent):
    """Simulates arXiv academic paper search using LLM (ADK LlmAgent)."""

    def __init__(self, model: str = "gemini-2.0-flash"):
        instruction = """You are an arXiv academic paper search specialist.

Generate 5-8 realistic arXiv papers with:
- Academic paper titles
- Realistic author names
- arXiv URLs (https://arxiv.org/abs/YYMM.NNNNN format)
- 3-5 sentence abstracts
- Publication dates (recent, within last 2-3 years)

Output format (JSON):
{
  "source_type": "arxiv",
  "results": [
    {
      "title": "Academic Paper Title: Subtitle",
      "authors": ["FirstName LastName", "FirstName LastName"],
      "url": "https://arxiv.org/abs/2401.12345",
      "abstract": "3-5 sentence academic abstract describing the research",
      "published": "2024-01-15",
      "relevance": 0.92
    }
  ],
  "total_found": 8,
  "search_time": 0.3
}"""

        # Initialize ADK LlmAgent 
        super().__init__(
            name="arxiv_search",
            model=model,
            instruction=instruction,
            generate_content_config=GenerateContentConfig(
                temperature=0.8,
                max_output_tokens=1024,
                response_mime_type="application/json"
            )
        )

    def search(self, client: genai.Client, query: str) -> Dict[str, Any]:
        """Execute search using direct genai.Client call (execution)."""
        prompt = f"{self.instruction}\n\nuser: Search query: {query}\n\nGenerate realistic arXiv papers for this query."

        response = client.models.generate_content(
            model=self.model,
            contents=prompt,
            config=self.generate_content_config
        )

        try:
            result = json.loads(response.text)
            result['_metadata'] = {
                'agent': self.name,
                'source_type': 'arxiv',
                'execution': 'direct_genai_client'
            }
            return result
        except json.JSONDecodeError:
            return {
                'source_type': 'arxiv',
                'results': [],
                'total_found': 0,
                'search_time': 0.0,
                '_metadata': {'agent': self.name, 'error': 'json_parse_error'}
            }


class ScholarSearchAgent(LlmAgent):
    """Simulates Google Scholar academic search using LLM (ADK LlmAgent)."""

    def __init__(self, model: str = "gemini-2.0-flash"):
        instruction = """You are a Google Scholar search specialist.

Generate 5-8 realistic academic publications with:
- Academic titles (papers, theses, books)
- Author lists
- Publication venues (journals, conferences)
- Years and citation counts
- Brief descriptions

Output format (JSON):
{
  "source_type": "scholar",
  "results": [
    {
      "title": "Academic Publication Title",
      "authors": ["Author1", "Author2", "Author3"],
      "venue": "Journal of Computer Science / Conference Name",
      "year": 2024,
      "url": "https://scholar.google.com/citations?id=example",
      "snippet": "2-3 sentence description of the work",
      "citations": 45,
      "relevance": 0.88
    }
  ],
  "total_found": 8,
  "search_time": 0.4
}"""

        # Initialize ADK LlmAgent
        super().__init__(
            name="scholar_search",
            model=model,
            instruction=instruction,
            generate_content_config=GenerateContentConfig(
                temperature=0.8,
                max_output_tokens=1024,
                response_mime_type="application/json"
            )
        )

    def search(self, client: genai.Client, query: str) -> Dict[str, Any]:
        """Execute search using direct genai.Client call (execution)."""
        prompt = f"{self.instruction}\n\nuser: Search query: {query}\n\nGenerate realistic Google Scholar results for this query."

        response = client.models.generate_content(
            model=self.model,
            contents=prompt,
            config=self.generate_content_config
        )

        try:
            result = json.loads(response.text)
            result['_metadata'] = {
                'agent': self.name,
                'source_type': 'scholar',
                'execution': 'direct_genai_client'
            }
            return result
        except json.JSONDecodeError:
            return {
                'source_type': 'scholar',
                'results': [],
                'total_found': 0,
                'search_time': 0.0,
                '_metadata': {'agent': self.name, 'error': 'json_parse_error'}
            }


class SourceAggregatorAgent(LlmAgent):
    """Aggregates and ranks sources from multiple search agents."""

    def __init__(self, model: str = "gemini-2.0-flash"):
        """Initialize aggregator agent."""
        instruction = """You are a source aggregation specialist.

Your role:
1. Combine search results from multiple sources (web, arXiv, Google Scholar)
2. Remove duplicates
3. Rank by relevance
4. Provide summary statistics

Output format (JSON):
{
  "total_sources": 30,
  "unique_sources": 25,
  "top_sources": [
    {
      "title": "Source title",
      "type": "web/arxiv/scholar",
      "url": "https://...",
      "relevance_score": 0.95,
      "snippet": "Brief description"
    }
  ],
  "sources_by_type": {
    "web": 10,
    "arxiv": 8,
    "scholar": 7
  },
  "aggregation_summary": "Brief summary of source quality and diversity"
}

Select the top 10-15 most relevant sources."""

        # Initialize ADK LlmAgent
        super().__init__(
            name="source_aggregator",
            model=model,
            instruction=instruction,
            generate_content_config=GenerateContentConfig(
                temperature=0.3,
                max_output_tokens=2048,
                response_mime_type="application/json"
            )
        )

    def aggregate(self, client: genai.Client, search_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Aggregate results from multiple searches using direct genai.Client call (execution)."""
        prompt = f"""{self.instruction}

user: Please aggregate these search results:

{json.dumps(search_results, indent=2)}"""

        response = client.models.generate_content(
            model=self.model,
            contents=prompt,
            config=self.generate_content_config
        )

        try:
            result = json.loads(response.text)
            result['_metadata'] = {
                'agent': self.name,
                'execution': 'direct_genai_client',
                'input_sources': len(search_results)
            }
            return result
        except json.JSONDecodeError:
            total = sum(r.get('total_found', 0) for r in search_results)
            return {
                'total_sources': total,
                'unique_sources': total,
                'top_sources': [],
                'sources_by_type': {'web': 0, 'arxiv': 0, 'scholar': 0},
                'aggregation_summary': 'Aggregation failed - JSON parse error',
                '_metadata': {'agent': self.name, 'error': 'json_parse_error'}
            }


def create_source_gathering_workflow(model: str = "gemini-2.0-flash") -> SequentialAgent:
    """
    Creates a SequentialAgent with ParallelAgent for source gathering.

    Args:
        model: Gemini model to use

    Returns:
        SequentialAgent configured for parallel source gathering
    """
    # Create specialized search agents
    web_search = WebSearchAgent(model=model)
    arxiv_search = ArxivSearchAgent(model=model)
    scholar_search = ScholarSearchAgent(model=model)
    aggregator = SourceAggregatorAgent(model=model)

    # TODO 3: Create ParallelAgent for concurrent searches
    #
    # Create a ParallelAgent that runs all three search agents concurrently.
    # This is the "fan-out" part of the fan-out/fan-in pattern.

    parallel_searches = None  # REPLACE: Create ParallelAgent here

    # TODO 4: Wrap with SequentialAgent
    #
    # Create a SequentialAgent that orchestrates the workflow:
    # 1. First runs the ParallelAgent (fan-out: all searches run concurrently)
    # 2. Then runs the aggregator (fan-in: combines all results)


    source_gathering_workflow = None  # REPLACE: Create SequentialAgent here

    return source_gathering_workflow


async def execute_source_gathering(
    client: genai.Client,
    query: str,
    model: str = "gemini-2.0-flash"
) -> Dict[str, Any]:
    """
    Execute parallel source gathering workflow using ADK ParallelAgent + SequentialAgent.

    EXECUTION:
    - Manually executes workflow logic 
    - Uses genai.Client directly for real LLM output
    - Uses asyncio.gather for true parallelism

    Args:
        client: Configured genai.Client
        query: Research query
        model: Gemini model name

    Returns:
        Dictionary with aggregated sources
    """
    print(f"\n Source Gathering: {query[:60]}...")
    print(f"   Pattern: ADK ParallelAgent + SequentialAgent")

    # Create SequentialAgent with ParallelAgent 
    workflow = create_source_gathering_workflow(model=model)

    print(f"   Created SequentialAgent: {workflow.name}")
    print(f"   Type: {type(workflow).__name__}")
    print(f"   Sub-agents: {len(workflow.sub_agents)}")

    # Get the sub-agents from SequentialAgent
    parallel_stage = workflow.sub_agents[0]  # ParallelAgent
    aggregator = workflow.sub_agents[1]      # AggregatorAgent

    print(f"   Stage 1 (ParallelAgent): {parallel_stage.name}")
    print(f"      → Type: {type(parallel_stage).__name__}")
    print(f"      → Sub-agents: {len(parallel_stage.sub_agents)} parallel searches")

    print(f"   Stage 2 (Aggregator): {aggregator.name}")

    # Manually execute the workflow logic 
    print(f"\n   Executing workflow logic (execution)...")

    # STAGE 1: Execute parallel searches (fan-out)
    print(f"\n   Stage 1: ParallelAgent (fan-out)")

    web_search = parallel_stage.sub_agents[0]
    arxiv_search = parallel_stage.sub_agents[1]
    scholar_search = parallel_stage.sub_agents[2]

    async def run_web():
        print(f"      → {web_search.name} running...")
        result = web_search.search(client, query)
        print(f"      ✓ {web_search.name}: Found {result.get('total_found', 0)} sources")
        return result

    async def run_arxiv():
        print(f"      → {arxiv_search.name} running...")
        result = arxiv_search.search(client, query)
        print(f"      ✓ {arxiv_search.name}: Found {result.get('total_found', 0)} sources")
        return result

    async def run_scholar():
        print(f"      → {scholar_search.name} running...")
        result = scholar_search.search(client, query)
        print(f"      ✓ {scholar_search.name}: Found {result.get('total_found', 0)} sources")
        return result

    # Run all searches in parallel (parallel execution with asyncio.gather)
    search_results = await asyncio.gather(run_web(), run_arxiv(), run_scholar())

    # STAGE 2: Aggregate results (fan-in)
    print(f"\n   Stage 2: Aggregator (fan-in)")
    print(f"      → {aggregator.name} aggregating results...")

    aggregated = aggregator.aggregate(client, list(search_results))

    print(f"      ✓ Total: {aggregated.get('total_sources', 0)} sources")
    print(f"      ✓ Unique: {aggregated.get('unique_sources', 0)} sources")
    print(f"      ✓ Top sources: {len(aggregated.get('top_sources', []))}")

    print(f"   ✅ Workflow execution completed")

    return {
        'query': query,
        'raw_searches': list(search_results),
        'aggregated_sources': aggregated,
        'workflow': workflow,  # Include the actual SequentialAgent object
        'parallel_agent': parallel_stage,  # Include the actual ParallelAgent object
        'pattern': 'ADK ParallelAgent + SequentialAgent',
        'execution_mode': 'direct'
    }
