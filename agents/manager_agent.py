from crewai import Agent

from utils import get_llm_client


def make_manager_agent() -> Agent:
    """Build the quality-control judge used to gate every task's output.

    executor.py attaches this agent to each task as a CrewAI ``guardrail``
    (see guardrails.py): once a specialist agent produces an output, this
    judge checks it against that task's own expected_output before the
    pipeline is allowed to treat it as done, sending it back for a bounded
    number of retries if it falls short.
    """
    return Agent(
        role="Research Quality Judge",
        goal=(
            "Judge whether a completed task's output actually satisfies "
            "what was asked of it. Be strict about missing, off-topic, or "
            "fabricated content. Be lenient about style, phrasing, and length."
        ),
        backstory=(
            "You are the last checkpoint before a research team's work ships. "
            "You never do the research yourself — you only decide whether a "
            "finished piece of work is good enough to pass, and if not, say "
            "exactly what's missing so it can be redone correctly."
        ),
        allow_delegation=False,
        llm=get_llm_client(),
    )
