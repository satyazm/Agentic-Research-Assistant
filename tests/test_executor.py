"""Tests for the input-resolution logic that wires task outputs together."""

from executor import resolve_inputs


def test_literal_values_pass_through():
    resolved = resolve_inputs({"query": "diffusion models"}, context={})
    assert resolved == {"query": "diffusion models"}


def test_reference_is_replaced_from_context():
    context = {"task_1_output": "search results text"}
    resolved = resolve_inputs({"query": "$task_1_output"}, context)
    assert resolved == {"query": "search results text"}


def test_unresolved_reference_is_left_as_is():
    # A dangling $reference with no matching context key stays verbatim
    # so the failure is visible rather than silently becoming empty.
    resolved = resolve_inputs({"query": "$task_9_output"}, context={})
    assert resolved == {"query": "$task_9_output"}


def test_mixed_literal_and_reference():
    context = {"task_2_output": "paper id 1234"}
    resolved = resolve_inputs(
        {"paper_id": "$task_2_output", "focus": "results"}, context
    )
    assert resolved == {"paper_id": "paper id 1234", "focus": "results"}
