
from crewai import Agent
from pydantic import BaseModel

from utils import get_llm_client

llm_client = get_llm_client()

class Theme(BaseModel):
    name: str
    papers: list[str]
    description: str

class AnalysisOutput(BaseModel):
    themes: list[Theme]
    trends: list[str]
    gaps: list[str]


analyst_agent = Agent(
    role="research_analyst",
    goal="Synthesize multiple research papers into insights, trends, and gaps",
    backstory=(
        "You are an expert researcher who compares papers, identifies patterns, "
        "and extracts deep insights across multiple works."
    ),
    verbose=True , 
    llm=llm_client 
)

