from crewai import Agent

from utils import get_llm_client


def make_manager_agent(available_agents: list) -> Agent:
    """
    Called by executor.py after the task list is built.
    Receives only the agents actually participating in this run,
    so the manager never tries to delegate to a non-existent agent.
    """

    # Build a readable roster from the live agent list
    agent_roster = "\n".join([
        f"- {agent.role}: {agent.goal}"
        for agent in available_agents
    ])

    return Agent(
        role="Research Operations Director",
        goal=(
            "Oversee task execution. Delegate every task to the correct agent "
            "from the roster below. Review outputs before marking tasks complete.\n\n"
            "Rules:\n"
            "- NEVER perform tasks yourself\n"
            "- ONLY delegate to agents listed in your roster\n"
            "- Validate each output before proceeding to the next task\n"
        ),
        backstory=(
            "You are a strict research dispatcher. You assign work and validate results.\n\n"
            f"Agents available to you right now:\n{agent_roster}\n\n"
            "You must only delegate to agents on this list."
        ),
        allow_delegation=True,
        llm=get_llm_client(),
    )