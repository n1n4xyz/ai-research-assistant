import time
from typing import Dict, Any
from google import genai
from agents.researcher import execute_research_loop
from agents.source_gatherer import execute_source_gathering
from agents.other_agents import (
    DomainClassifierAgent,
    FactCheckAgent,
    SynthesisAgent,
    CitationAgent
)
from agents.evaluator import PerformanceEvaluator


async def execute_research_workflow(
    client: genai.Client,
    query: str,
    max_iterations: int = 3,
    model: str = "gemini-2.0-flash"
) -> Dict[str, Any]:
    """
    Execute complete research assistant workflow.

    This function implements the SequentialAgent pattern:
    - Stage 1: Domain Classification 
    - Stage 2: Source Gathering 
    - Stage 3: Research Refinement
    - Stage 4: Fact Checking (LlmAgent)
    - Stage 5: Synthesis (LlmAgent)
    - Stage 6: Citation Generation (LlmAgent)

    Args:
        client: Configured genai.Client
        query: Research question
        max_iterations: Max iterations for research loop
        model: Gemini model name

    Returns:
        Complete research report with all stages
    """
    print("\n" + "="*80)
    print("AI RESEARCH ASSISTANT - EXECUTION")
    print("="*80)
    print(f"\n Research Query: {query}")
    print(f"   Pattern: SequentialAgent")
    print(f"   Execution: (ADK agents + agent.run_async())")
    print(f"   Model: {model}")

    # Track execution time for performance evaluation
    start_time = time.time()

    workflow_results = {
        'query': query,
        'model': model,
        'pattern': 'SequentialAgent',
        'execution_mode': 'direct'
    }

    # ========================================================================
    # STAGE 1: Domain Classification
    # ========================================================================
    print("\n" + "-"*80)
    print("STAGE 1: Domain Classification ")
    print("-"*80)

    domain_classifier = DomainClassifierAgent(model=model)
    classification = domain_classifier.classify(client=client, query=query)

    print(f"   ✓ Domain: {classification.get('domain', 'unknown')}")
    print(f"   ✓ Confidence: {classification.get('confidence', 0):.2f}")
    print(f"   ✓ Complexity: {classification.get('complexity', 'unknown')}")
    print(f"   ✓ Recommended sources: {', '.join(classification.get('recommended_sources', []))}")

    workflow_results['stage_1_classification'] = classification

    # ========================================================================
    # STAGE 2: Source Gathering
    # ========================================================================
    print("\n" + "-"*80)
    print("STAGE 2: Source Gathering")
    print("-"*80)

    sources = await execute_source_gathering(client=client, query=query, model=model)
    workflow_results['stage_2_sources'] = sources

    # ========================================================================
    # STAGE 3: Research Refinement
    # ========================================================================
    print("\n" + "-"*80)
    print("STAGE 3: Research Refinement")
    print("-"*80)

    research = await execute_research_loop(
        client=client,
        query=query,
        max_iterations=max_iterations,
        model=model
    )
    workflow_results['stage_3_research'] = research

    # ========================================================================
    # STAGE 4: Fact Checking (LlmAgent)
    # ========================================================================
    print("\n" + "-"*80)
    print("STAGE 4: Fact Checking (LlmAgent)")
    print("-"*80)

    fact_checker = FactCheckAgent(model=model)
    fact_check = fact_checker.check(
        client=client,
        answer=research['final_answer'],
        sources=sources
    )

    print(f"   ✓ Credibility Score: {fact_check.get('credibility_score', 0):.2f}")
    print(f"   ✓ Verified Claims: {len(fact_check.get('verified_claims', []))}")
    print(f"   ✓ Questionable Claims: {len(fact_check.get('questionable_claims', []))}")

    workflow_results['stage_4_fact_check'] = fact_check

    # ========================================================================
    # STAGE 5: Synthesis (LlmAgent)
    # ========================================================================
    print("\n" + "-"*80)
    print("STAGE 5: Synthesis (LlmAgent)")
    print("-"*80)

    synthesizer = SynthesisAgent(model=model)
    synthesis = synthesizer.synthesize(
        client=client,
        query=query,
        answer=research['final_answer'],
        fact_check=fact_check,
        sources=sources
    )

    print(f"   ✓ Synthesis completed")
    print(f"   ✓ Key Insights: {len(synthesis.get('key_insights', []))}")
    print(f"   ✓ Themes: {len(synthesis.get('themes', []))}")
    print(f"   ✓ Coherence Score: {synthesis.get('coherence_score', 0):.2f}")

    workflow_results['stage_5_synthesis'] = synthesis

    # ========================================================================
    # STAGE 6: Citation Generation (LlmAgent)
    # ========================================================================
    print("\n" + "-"*80)
    print("STAGE 6: Citation Generation (LlmAgent)")
    print("-"*80)

    citation_formatter = CitationAgent(model=model)
    citations = citation_formatter.format_citations(client=client, sources=sources)

    print(f"   ✓ Citations formatted")
    print(f"   ✓ Total Citations: {citations.get('total_citations', 0)}")
    print(f"   ✓ Style: {citations.get('citation_style', 'APA')}")

    workflow_results['stage_6_citations'] = citations

    # ========================================================================
    # WORKFLOW SUMMARY
    # ========================================================================
    print("\n" + "="*80)
    print("WORKFLOW COMPLETED")
    print("="*80)
    print(f"\n. All 7 stages executed successfully")
    print(f"\n. Results Summary:")
    print(f"   • Query: {query}")
    print(f"   • Domain: {classification.get('domain', 'unknown')}")
    print(f"   • Sources Found: {sources['aggregated_sources'].get('total_sources', 0)}")
    print(f"   • Research Iterations: {research['iterations_run']}")
    print(f"   • Credibility Score: {fact_check.get('credibility_score', 0):.2f}")
    print(f"   • Citations: {citations.get('total_citations', 0)}")
    print(f"\n  Execution Method:")
    print(f"   ✓ All agents inherit from ADK base classes")
    print(f"   ✓ Executed via agent.run_async() with genai.Client")
    print(f"   ✓ No ADK server deployment required")
    print(f"   ✓ Real LLM output from Vertex AI Gemini")

    # ========================================================================
    # STAGE 7: Performance Evaluation
    # ========================================================================
    # TODO 8: Track workflow performance metrics 
    #
    # Instantiate PerformanceEvaluator and record the workflow results.
    #
    # Steps:
    # 1. Calculate execution time
    # 2. Create evaluator
    # 3. Record metrics
    # 4. Get summary
    # 5. Add to workflow_results
   
    print("\n" + "-"*80)
    print("STAGE 7: Performance Evaluation")
    print("-"*80)

    # TODO 8: Implement performance evaluation here
    # Replace the None values below with actual implementation

    execution_time = None  # REPLACE: Calculate execution time
    evaluator = None       # REPLACE: Create PerformanceEvaluator instance
    performance_summary = None  # REPLACE: Get performance summary after recording metrics

    # This section will work once you complete TODO 8
    if execution_time and evaluator and performance_summary:
        print(f"   ✓ Execution Time: {execution_time:.2f}s")
        print(f"   ✓ Performance Score: {performance_summary['performance_score']:.2f}")
        print(f"   ✓ Health Status: {performance_summary['health_status']}")
        print(f"   ✓ Queries Processed: {evaluator.metrics.queries_processed}")

        if performance_summary['bottlenecks']:
            print(f"   ⚠️  Bottlenecks Identified:")
            for bottleneck in performance_summary['bottlenecks']:
                print(f"      • {bottleneck}")

        workflow_results['stage_7_performance'] = {
            'execution_time': execution_time,
            'performance_summary': performance_summary,
            'evaluator': evaluator
        }
    else:
        print(f"   ⚠️  Performance evaluation not implemented (complete TODO 8)")
        workflow_results['stage_7_performance'] = None

    return workflow_results


def generate_research_report(workflow_results: Dict[str, Any]) -> str:
    """Generate formatted research report from workflow results.

    Args:
        workflow_results: Complete workflow results

    Returns:
        Formatted markdown report
    """
    query = workflow_results['query']
    classification = workflow_results['stage_1_classification']
    sources = workflow_results['stage_2_sources']
    research = workflow_results['stage_3_research']
    fact_check = workflow_results['stage_4_fact_check']
    synthesis = workflow_results['stage_5_synthesis']
    citations = workflow_results['stage_6_citations']

    report = f"""
# Research Report: {query}

## Executive Summary
{synthesis.get('executive_summary', 'No summary available')}

**Domain:** {classification.get('domain', 'Unknown')}
**Credibility Score:** {fact_check.get('credibility_score', 0):.2f}/1.00
**Sources Consulted:** {sources['aggregated_sources'].get('total_sources', 0)}
**Research Iterations:** {research['iterations_run']}

---

## Research Findings

{synthesis.get('synthesis', research['final_answer'].get('answer', 'No findings available'))}

---

## Key Insights

{chr(10).join(f"{i+1}. {insight}" for i, insight in enumerate(synthesis.get('key_insights', [])))}

---

## Major Themes

{chr(10).join(f"- {theme}" for theme in synthesis.get('themes', []))}

---

## Recommendations

{chr(10).join(f"{i+1}. {rec}" for i, rec in enumerate(synthesis.get('recommendations', [])))}

---

## Quality Assessment

**Research Quality Score:** {research.get('final_answer', {}).get('confidence', 'unknown')}
**Credibility Score:** {fact_check.get('credibility_score', 0):.2f}/1.00
**Coherence Score:** {synthesis.get('coherence_score', 0):.2f}/1.00

### Verified Claims
{chr(10).join(f"✓ {claim}" for claim in fact_check.get('verified_claims', [])[:5])}

### Areas for Further Investigation
{chr(10).join(f"⚠️  {claim}" for claim in fact_check.get('questionable_claims', [])[:3])}

---

## Sources

**Total Sources:** {sources['aggregated_sources'].get('total_sources', 0)}
**Unique Sources:** {sources['aggregated_sources'].get('unique_sources', 0)}

### Source Distribution
- Web: {sources['aggregated_sources'].get('sources_by_type', {}).get('web', 0)}
- ArXiv: {sources['aggregated_sources'].get('sources_by_type', {}).get('arxiv', 0)}
- Google Scholar: {sources['aggregated_sources'].get('sources_by_type', {}).get('scholar', 0)}

---

## Bibliography

{citations.get('bibliography', 'No bibliography available')}

---

## Methodology

This research report was generated using an ADK-based multi-agent system with the following workflow:

1. **Domain Classification** 
2. **Parallel Source Gathering** 
3. **Iterative Research Refinement** 
4. **Fact Checking** (LlmAgent validation)
5. **Synthesis** (LlmAgent integration)
6. **Citation Formatting** (LlmAgent academic standards)

**Model:** {workflow_results['model']}

---

*Report generated by AI Research Assistant
"""

    return report
