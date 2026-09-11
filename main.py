import os
import asyncio
from google import genai
from utils.config import config
from agents.orchestrator import execute_research_workflow, generate_research_report


async def main():
    """Main entry point for research assistant."""

    print("\n" + "="*80)
    print("AI RESEARCH ASSISTANT")
    print("="*80)
  
    print(f"\n Configuration:")
    print(f"   Project ID: {config.project_id or 'NOT SET'}")
    print(f"   Location: {config.location}")
    print(f"   Model: {config.model_name}")

    # Initialize genai client
    print(f"\n🔧 Initializing genai.Client...")

    # Try multiple authentication methods (easiest to hardest for students)
    api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")

    try:
        if api_key:
            # Method 1: API Key (EASIEST for students!)
            print(f"   Using Gemini API key authentication...")
            client = genai.Client(api_key=api_key)
            print(f"   ✓ Client initialized with API key")
        elif config.project_id:
            # Method 2: Vertex AI (requires gcloud or service account)
            print(f"   Using Vertex AI authentication...")
            client = genai.Client(
                vertexai=True,
                project=config.project_id,
                location=config.location
            )
            print(f"   ✓ Client initialized with Vertex AI")
        else:
            print("\n❌ No authentication method available")
            return
    except Exception as e:
        print(f"\n❌ Failed to initialize client: {e}")
        return

    # Sample research queries
    queries = [
        "What are the latest advances in quantum computing error correction?",
        "How does machine learning improve code review efficiency?",
        "What are the health impacts of microplastics in marine ecosystems?",
        "What are the latest types of computer memory?"
    ]

    print(f"\n📝 Sample Research Queries:")
    for i, q in enumerate(queries, 1):
        print(f"   {i}. {q}")

    # Allow user to select query or provide custom one
    print(f"\n💡 To research a different topic:")
    print(f"   • Edit queries list in main.py")
    print(f"   • Or set RESEARCH_QUERY environment variable")
    print(f"   • Example: export RESEARCH_QUERY='Your custom question here'")

    # Check for custom query via environment variable
    custom_query = os.getenv("RESEARCH_QUERY")

    if custom_query:
        selected_query = custom_query
        print(f"\n🎯 Running custom research query...")
    else:
        # Select query (default to first one)
        selected_query = queries[0]
        print(f"\n🎯 Running research workflow for query 1...")

    # Execute complete workflow
    try:
        workflow_results = await execute_research_workflow(
            client=client,
            query=selected_query,
            max_iterations=config.max_iterations,
            model=config.model_name
        )

        # Generate formatted report
        print(f"\n📄 Generating research report...")
        report = generate_research_report(workflow_results)

        # Save report
        report_file = os.path.join(os.path.dirname(__file__), "research_report.md")
        with open(report_file, 'w') as f:
            f.write(report)

        print(f"   ✓ Report saved to: {report_file}")

        # Display report preview
        print("\n" + "="*80)
        print("RESEARCH REPORT PREVIEW")
        print("="*80)
        print(report[:2000])  # First 2000 chars
        if len(report) > 2000:
            print(f"\n... (report continues, total {len(report)} characters)")
            print(f"\nFull report saved to: {report_file}")

        # Summary metrics
        print("\n" + "="*80)
        print("EXECUTION SUMMARY")
        print("="*80)
        print(f"\n  Workflow Metrics:")
        print(f"   • Total Stages: 6")
        print(f"   • Research Iterations: {workflow_results['stage_3_research']['iterations_run']}")
        print(f"   • Sources Found: {workflow_results['stage_2_sources']['aggregated_sources'].get('total_sources', 0)}")
        print(f"   • Credibility Score: {workflow_results['stage_4_fact_check'].get('credibility_score', 0):.2f}")
        print(f"   • Citations: {workflow_results['stage_6_citations'].get('total_citations', 0)}")

        print(f"\n Execution successful!")
       
    except Exception as e:
        print(f"\n❌ Error executing workflow: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
