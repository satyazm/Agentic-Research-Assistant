"""Top-level entrypoint for the agentic research assistant.

The flow is a two-stage plan → execute pipeline:

  1. ``planner.plan`` asks an LLM to turn a free-form user request into a
     minimal, ordered JSON execution plan drawn from ``task_registry``.
  2. ``executor.execute_plan`` builds only the CrewAI tasks named in that
     plan, wires each task's context to the outputs of the prior ones, and
     runs them sequentially.
"""

from executor import execute_plan
from planner import plan


def run(user_input: str, file_name: str = None) -> str:
    """Plan and execute a research workflow for a single user request.

    Args:
        user_input: The natural-language research request.
        file_name: Optional name of a PDF the user uploaded, made available
            to the planner and to any file-reading task.

    Returns:
        The final crew output as a string.
    """
    # Step 1 — the LLM decides which tasks are needed.
    execution_plan = plan(user_input, file_name=file_name)

    print("\nExecution Plan:")
    for step in execution_plan["tasks"]:
        print(f"   {step['task_id']}. {step['name']} → {step['reason']}")

    # Step 2 — build and run only those tasks.
    initial_context = {}
    if file_name:
        initial_context["uploaded_file"] = file_name

    return execute_plan(execution_plan, initial_context)


if __name__ == "__main__":
    # A few representative requests. Each produces a different plan:
    #   • upload + summarize   → read_local_file → explain_paper
    #   • targeted search      → search_arxiv
    #   • full pipeline        → search_arxiv → download_paper → … → analyze
    #   • composed request     → generate_hypotheses → search_arxiv → analyze
    print(run(
        user_input="find recent papers on LoRA fine-tuning",
    ))
