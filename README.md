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
