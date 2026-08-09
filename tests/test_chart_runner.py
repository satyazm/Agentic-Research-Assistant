"""Tests for chart_runner.extract_and_run_chart.

chart_runner has no third-party imports, so these run anywhere with no API keys.
"""

import os

from chart_runner import extract_and_run_chart


def test_returns_none_when_no_code_block():
    assert extract_and_run_chart("Just a qualitative summary, no code here.") is None


def test_returns_none_for_non_matplotlib_code():
    # A python block that imports something other than matplotlib is rejected.
    output = "```python\nimport os\nos.system('echo hi')\n```"
    assert extract_and_run_chart(output) is None


def test_runs_matplotlib_and_returns_path(tmp_path, monkeypatch):
    # Execute in a temp dir so we don't litter the repo with chart.png.
    monkeypatch.chdir(tmp_path)
    output = (
        "Here is the chart:\n"
        "```python\n"
        "import matplotlib\n"
        "matplotlib.use('Agg')\n"
        "import matplotlib.pyplot as plt\n"
        "plt.bar(['a', 'b'], [1, 2])\n"
        "plt.savefig('chart.png')\n"
        "plt.close()\n"
        "```"
    )
    result = extract_and_run_chart(output)
    assert result == "chart.png"
    assert os.path.exists(tmp_path / "chart.png")


def test_returns_none_when_code_raises(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    output = "```python\nimport matplotlib\nraise ValueError('boom')\n```"
    assert extract_and_run_chart(output) is None
