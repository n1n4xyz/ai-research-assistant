# AI Research Assistant with Multi-Agent Workflows

A hands-on project demonstrating **agentic AI workflow patterns** using **Google's Agent Development Kit (ADK)**.


## Testing Your Implementation

### Run the Complete Workflow

```bash
python main.py
```

### Test with Custom Research Queries

```bash
export RESEARCH_QUERY="What are the smartest birds on the planet?"
python main.py
```

Or edit the `queries` list in `main.py` to add your own research topics.

### Expected Output

If your implementation is correct, you should see:

1. All 7 stages execute successfully
2. LoopAgent, ParallelAgent, and SequentialAgent objects created
3. LLM output from Gemini
4. Performance evaluation metrics displayed
5. A generated `research_report.md` file with comprehensive findings

---

## Project Submission

### Custom research query

```
How does retrieval-augmented generation reduce hallucinations in enterprise LLM systems?
```

```bash
export RESEARCH_QUERY="How does retrieval-augmented generation reduce hallucinations in enterprise LLM systems?"
python main.py 2>&1 | tee run.log
```

Model: `gemini-2.5-flash-lite` on Vertex AI, region `us-central1`. The starter default `gemini-2.0-flash` was discontinued on Vertex AI on June 1, 2026, so `MODEL_NAME` is set in `.env`.

### Final run

| Metric | Result |
|---|---|
| Domain | computer_science, confidence 0.95, complexity moderate |
| Sources | 22 total (web 8, arXiv 6, Scholar 8), 14 top sources passed to the research loop |
| Research iterations | 3 (critic scores 0.85, 0.85, 0.85), max iterations reached |
| Fact check | credibility 0.95, 5 verified claims, 1 questionable |
| Citations | 10, APA |
| Execution time | 38.90 s |
| Performance | score 0.85, health status excellent |

### Observations

**Router.** Across 4 runs of this query the classifier returned computer_science with confidence 0.95 every time. Temperature 0.3 and JSON output kept the routing stable.

**Parallel source gathering.** All three searches start before any of them finishes. The aggregator runs only after all three return. The parallel stage took between 4.7 and 6.8 seconds. The starter wrapped blocking calls in `asyncio.gather`, which runs them one after another, so the searches now run through `asyncio.to_thread`.

**Silent source failures.** The first two runs found 0 and 5 sources. The search agents asked for up to 10 results with snippets inside a 1024 token limit. The JSON got cut off and the parse fallback returned an empty list without any log line. Raising the limits to 4096 for searches and 8192 for the aggregator fixed it. A failed parse now prints the finish reason.

**Critic calibration.** With the starter critic the first draft scored 0.95 and the loop stopped after one iteration in every run. The critic now requires at least 3 named sources, concrete evidence and a discussion of limitations for 0.90 or higher, and the loop stops only at 0.90. A minimum of 2 iterations is enforced as well, so every first draft gets at least one round of feedback. In the final run that rule did not fire because the first draft scored 0.85 on its own.

**Score plateau.** The researcher revised the answer twice based on the feedback, yet the critic scored all three drafts at 0.85 and the loop returned the last draft after max_iterations. Feedback and revisions did not converge. Two changes for a next version: pass the critic's `weaknesses` list to the researcher as an explicit checklist, and run the critic on a stronger model than the generator.

**Limits of the simulated tools.** The search agents generate plausible sources instead of querying real APIs, so titles, authors and URLs in the bibliography are not verified. The fact checker compares claims against model knowledge only. A credibility score of 0.95 reflects internal consistency, not independent verification.

**Metrics.** The stricter critic lowered the performance score from 0.95 to 0.85, although the final answer went through two more revision rounds. The evaluator counts 0.85 as excellent, so the health status did not change. The performance score tracks the critic's calibration as much as the answer quality.

### Changes beyond the TODOs

- `orchestrator.py` imported `DomainClassifierAgent` from `other_agents.py`. It now uses `agents/router.py`, which got a `classify()` method.
- Stage 2 sources are passed into `execute_research_loop` and seed the researcher's context.
- The WORKFLOW COMPLETED summary prints after Stage 7 and includes the performance metrics.
- Higher `max_output_tokens` for searches, aggregator, researcher, fact check, synthesis and citations.
- Stricter critic prompt, `QUALITY_THRESHOLD = 0.90` and `MIN_ITERATIONS = 2`.

### Screenshots

`screenshots/` holds the initialization with agent types, the router and research loop logs, and the completion summary of the final run.
