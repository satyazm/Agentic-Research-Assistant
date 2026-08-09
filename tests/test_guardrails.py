"""Tests for the judge-and-retry guardrail closure.

The judge itself is a duck-typed stub (anything with a `.kickoff()` method),
not a real crewai.Agent, so these run offline with no API key.
"""

from types import SimpleNamespace

from guardrails import JudgeVerdict, make_output_guardrail


class _StubJudge:
    """Stands in for crewai.Agent: only `.kickoff()` is ever called on it."""

    def __init__(self, verdict=None, raises=None):
        self._verdict = verdict
        self._raises = raises

    def kickoff(self, query, response_format=None):
        if self._raises:
            raise self._raises
        return SimpleNamespace(pydantic=self._verdict)


def _task_output(raw="the answer"):
    return SimpleNamespace(raw=raw)


def test_passing_verdict_returns_true_and_raw_output():
    judge = _StubJudge(verdict=JudgeVerdict(passed=True))
    guardrail = make_output_guardrail(judge, "do the thing", "a thing")

    ok, result = guardrail(_task_output("the real answer"))

    assert ok is True
    assert result == "the real answer"


def test_failing_verdict_returns_false_and_feedback():
    judge = _StubJudge(verdict=JudgeVerdict(passed=False, feedback="missing the citation"))
    guardrail = make_output_guardrail(judge, "do the thing", "a thing")

    ok, result = guardrail(_task_output())

    assert ok is False
    assert result == "missing the citation"


def test_failing_verdict_with_no_feedback_gets_a_default_message():
    judge = _StubJudge(verdict=JudgeVerdict(passed=False, feedback=""))
    guardrail = make_output_guardrail(judge, "do the thing", "a thing")

    ok, result = guardrail(_task_output())

    assert ok is False
    assert "did not satisfy" in result


def test_judge_exception_fails_open():
    # A broken judge call must never block an otherwise-fine output.
    judge = _StubJudge(raises=RuntimeError("LLM timeout"))
    guardrail = make_output_guardrail(judge, "do the thing", "a thing")

    ok, result = guardrail(_task_output("still a good answer"))

    assert ok is True
    assert result == "still a good answer"


def test_malformed_judge_result_fails_open():
    judge = _StubJudge(verdict="not a JudgeVerdict")
    guardrail = make_output_guardrail(judge, "do the thing", "a thing")

    ok, result = guardrail(_task_output("still a good answer"))

    assert ok is True
    assert result == "still a good answer"
