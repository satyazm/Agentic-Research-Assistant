"""Judge-and-retry: wires the manager agent into per-task output validation.

CrewAI Task supports a ``guardrail`` callable of type
``TaskOutput -> tuple[bool, Any]``: once a task's own agent produces an
output, CrewAI calls the guardrail before accepting it. Returning
``(False, feedback)`` sends the task back to the *same* agent with that
feedback added to its context and reruns it, up to
``Task.guardrail_max_retries`` times; ``(True, result)`` accepts the output
and moves on. See executor.py for where this gets attached to every task.
"""

from typing import Any

from crewai import Agent
from crewai.tasks.task_output import TaskOutput
from pydantic import BaseModel, Field


class JudgeVerdict(BaseModel):
    passed: bool = Field(
        description="Whether the output satisfies the task's expected_output."
    )
    feedback: str = Field(
        default="",
        description="If not passed, precise instructions for what to fix.",
    )


def make_output_guardrail(judge: Agent, description: str, expected_output: str):
    """Build a guardrail closure that has `judge` review a task's output."""

    def _guardrail(task_output: TaskOutput) -> tuple[bool, Any]:
        query = (
            "Judge whether the TASK RESULT below actually satisfies the "
            "EXPECTED OUTPUT requirements for the TASK.\n\n"
            f"TASK:\n{description}\n\n"
            f"EXPECTED OUTPUT:\n{expected_output}\n\n"
            f"TASK RESULT:\n{task_output.raw}\n\n"
            "Fail it only if it's empty, off-topic, refuses without reason, "
            "or is missing something the expected output explicitly "
            "requires. Do not fail it for style, phrasing, or length alone."
        )
        try:
            verdict = judge.kickoff(query, response_format=JudgeVerdict)
            result = verdict.pydantic
        except Exception as e:
            # A broken judge call should never take down an otherwise-good
            # output — fail open rather than blocking the whole pipeline.
            print(f"  ⚠ Guardrail check errored, passing output through: {e}")
            return True, task_output.raw

        if not isinstance(result, JudgeVerdict):
            return True, task_output.raw

        if result.passed:
            return True, task_output.raw
        return False, result.feedback or "Output did not satisfy the expected_output requirements."

    return _guardrail
