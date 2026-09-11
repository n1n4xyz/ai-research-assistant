import json
from typing import Dict, Any, List
from google.adk.agents import LlmAgent, LoopAgent
from google import genai
from google.genai.types import GenerateContentConfig


class ResearcherAgent(LlmAgent):
    """
    Generator agent: Answers research questions or refines based on feedback.

    """

    def __init__(self, model: str = "gemini-2.0-flash"):
        """Initialize the researcher agent.

        Args:
            model: Gemini model name
        """
        instruction = """You are a research assistant that answers questions accurately and thoroughly.

Your role:
1. Answer the research question clearly and comprehensively
2. If you receive feedback from the critic, improve your previous answer addressing all concerns
3. Cite reasoning and provide evidence where possible
4. Include 3-5 key points with supporting details
5. Mention relevant sources or areas of research

Output format (JSON):
{
  "answer": "Your comprehensive answer here with evidence and reasoning",
  "key_points": ["point1 with evidence", "point2 with evidence", "point3 with evidence"],
  "sources_mentioned": ["source1", "source2", "source3"],
  "confidence": "high/medium/low",
  "iteration_notes": "What you improved this iteration (if applicable)"
}

Focus on accuracy, clarity, and continuous improvement. Each iteration should show measurable progress."""

        # Initialize ADK LlmAgent
        super().__init__(
            name="researcher",
            model=model,
            instruction=instruction,
            generate_content_config=GenerateContentConfig(
                temperature=0.7,
                max_output_tokens=1024,
                response_mime_type="application/json"
            )
        )

    def generate(self, client: genai.Client, query: str, context: List[Dict[str, str]] = None) -> Dict[str, Any]:
        """Generate research answer using direct genai.Client call.

        This is the execution part - use agent's config but execute directly.

        Args:
            client: Configured genai.Client
            query: Research question
            context: Previous conversation history (for refinement)

        Returns:
            Dictionary with answer and metadata
        """
        # Build prompt with context (mimics ADK context passing)
        if context:
            prompt = f"{self.instruction}\n\nConversation history:\n"
            for msg in context:
                prompt += f"\n{msg['role']}: {msg['content']}"
            prompt += f"\n\nuser: {query}"
        else:
            prompt = f"{self.instruction}\n\nuser: {query}"

        # Direct execution using genai.Client (part)
        response = client.models.generate_content(
            model=self.model,
            contents=prompt,
            config=self.generate_content_config
        )

        # Parse JSON response
        try:
            result = json.loads(response.text)
            result['_metadata'] = {
                'agent': self.name,
                'model': self.model,
                'execution': 'direct_genai_client'
            }
            return result
        except json.JSONDecodeError:
            return {
                'answer': response.text,
                'key_points': [],
                'sources_mentioned': [],
                'confidence': 'low',
                'iteration_notes': 'JSON parsing failed',
                '_metadata': {
                    'agent': self.name,
                    'error': 'json_parse_error'
                }
            }


class ResearchCriticAgent(LlmAgent):
    """
    Validator agent: Evaluates answer quality and provides feedback.

    """

    def __init__(self, model: str = "gemini-2.0-flash"):
        """Initialize the critic agent.

        Args:
            model: Gemini model name
        """
        instruction = """You are a research quality critic that evaluates answers.

Your role:
1. Evaluate the answer for accuracy, completeness, and clarity
2. Assign a quality level: excellent, good, needs_improvement, or poor
3. Provide specific, actionable feedback for improvement
4. Decide if answer is good enough to stop, or needs another iteration
5. Calculate a quality score (0-1) based on your assessment

Quality criteria:
- Excellent (0.90-1.00): Thorough, accurate, well-structured, comprehensive evidence
- Good (0.80-0.89): Accurate and complete, all key points covered
- Needs Improvement (0.50-0.79): Missing key points, needs more evidence or clarity
- Poor (0.00-0.49): Incomplete, unclear, or potentially inaccurate

Output format (JSON):
{
  "quality": "excellent/good/needs_improvement/poor",
  "quality_score": 0.85,
  "feedback": "Specific feedback for improvement",
  "strengths": ["strength1", "strength2"],
  "weaknesses": ["weakness1", "weakness2"],
  "should_stop": true/false,
  "reasoning": "Why to stop or continue"
}

Set should_stop=true ONLY if quality_score >= 0.80.
Otherwise set should_stop=false to trigger another iteration."""

        # Initialize ADK LlmAgent
        super().__init__(
            name="critic",
            model=model,
            instruction=instruction,
            generate_content_config=GenerateContentConfig(
                temperature=0.3,
                max_output_tokens=768,
                response_mime_type="application/json"
            )
        )

    def evaluate(self, client: genai.Client, question: str, answer: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate research answer quality using direct genai.Client call.

        This is the execution part - use agent's config but execute directly.

        Args:
            client: Configured genai.Client
            question: Original research question
            answer: Answer dictionary from researcher

        Returns:
            Evaluation dictionary with should_stop flag
        """
        prompt = f"""{self.instruction}

user: Please evaluate this research answer:

Question: {question}

Answer: {answer.get('answer', 'No answer provided')}
Key Points: {json.dumps(answer.get('key_points', []))}
Confidence: {answer.get('confidence', 'unknown')}"""

        response = client.models.generate_content(
            model=self.model,
            contents=prompt,
            config=self.generate_content_config
        )

        try:
            result = json.loads(response.text)
            result['_metadata'] = {
                'agent': self.name,
                'model': self.model,
                'execution': 'direct_genai_client'
            }
            return result
        except json.JSONDecodeError:
            return {
                'quality': 'needs_improvement',
                'quality_score': 0.5,
                'feedback': 'Unable to parse evaluation',
                'strengths': [],
                'weaknesses': ['Evaluation failed'],
                'should_stop': False,
                'reasoning': 'JSON parsing failed',
                '_metadata': {
                    'agent': self.name,
                    'error': 'json_parse_error'
                }
            }


def create_research_loop_agent(model: str = "gemini-2.0-flash",
                                max_iterations: int = 3) -> LoopAgent:
    """
    Creates a LoopAgent for iterative research refinement.

    Args:
        model: Gemini model to use
        max_iterations: Maximum loop iterations (safety limit)

    Returns:
        LoopAgent configured for research refinement
    """
    # TODO 1: Create the two agents for the LoopAgent
    #
    # Create the generator and validator agents:
    # - ResearcherAgent: The generator that creates/improves answers
    # - ResearchCriticAgent: The validator that evaluates quality

    researcher = None  # REPLACE: Create ResearcherAgent here
    critic = None      # REPLACE: Create ResearchCriticAgent here

    # TODO 2: Compose agents into LoopAgent
    #
    # Create a LoopAgent that will run the researcher and critic iteratively.
    #

    refinement_loop = None  # REPLACE: Create LoopAgent here

    return refinement_loop


async def execute_research_loop(
    client: genai.Client,
    query: str,
    max_iterations: int = 3,
    model: str = "gemini-2.0-flash"
) -> Dict[str, Any]:
    """
    Execute iterative research refinement using ADK LoopAgent.

    Args:
        client: Configured genai.Client
        query: Research question
        max_iterations: Maximum loop iterations
        model: Gemini model name

    Returns:
        Dictionary with final answer and iteration history
    """
    print(f"\n Research Loop: {query[:60]}...")
    print(f"   Max Iterations: {max_iterations}")

    # Create LoopAgent
    loop_agent = create_research_loop_agent(model=model, max_iterations=max_iterations)

    print(f"   Created LoopAgent: {loop_agent.name}")
    print(f"   Type: {type(loop_agent).__name__}")
    print(f"   Sub-agents: {len(loop_agent.sub_agents)} (researcher + critic)")

    # Get the sub-agents from the LoopAgent
    researcher = loop_agent.sub_agents[0]
    critic = loop_agent.sub_agents[1]

    print(f"\n   🔄 Executing LoopAgent logic (execution)...")

    # Manually execute the loop logic (part - can't use ADK deployment)
    context = []
    iteration_history = []
    final_answer = None

    for iteration in range(1, max_iterations + 1):
        print(f"\n   Iteration {iteration}/{max_iterations}")

        # Researcher generates/improves answer
        print(f"      → {researcher.name} generating answer...")
        answer = researcher.generate(client, query, context=context if context else None)

        context.append({
            'role': 'researcher',
            'content': json.dumps(answer)
        })

        print(f"      ✓ Answer generated (confidence: {answer.get('confidence', 'unknown')})")

        # Critic evaluates quality
        print(f"      → {critic.name} evaluating quality...")
        evaluation = critic.evaluate(client, question=query, answer=answer)

        context.append({
            'role': 'critic',
            'content': json.dumps(evaluation)
        })

        quality_score = evaluation.get('quality_score', 0.5)
        should_stop = evaluation.get('should_stop', False)

        print(f"      ✓ Quality: {evaluation.get('quality', 'unknown')} (score: {quality_score:.2f})")

        # Record iteration
        iteration_history.append({
            'iteration': iteration,
            'answer': answer,
            'evaluation': evaluation,
            'should_stop': should_stop
        })

        # Check termination (mimics ADK LoopAgent escalate logic)
        if should_stop:
            print(f"      Quality threshold met - Loop terminated")
            final_answer = answer
            break
        else:
            print(f"      Quality below threshold - Continue refining...")
            if iteration < max_iterations:
                print(f"      Feedback: {evaluation.get('feedback', 'No feedback')[:80]}...")

    # If loop exhausted without should_stop
    if not final_answer:
        print(f"\n   Max iterations reached - Returning best attempt")
        final_answer = iteration_history[-1]['answer'] if iteration_history else {}

    print(f"   LoopAgent execution completed ({len(iteration_history)} iterations)")

    return {
        'query': query,
        'final_answer': final_answer,
        'iterations_run': len(iteration_history),
        'iteration_history': iteration_history,
        'loop_agent': loop_agent,  # Include the actual LoopAgent object
        'pattern': 'ADK LoopAgent',
        'execution_mode': 'direct'
    }
