# Importing Python Libraries.
from typing import Any, List, Tuple
from typing_extensions import TypedDict
# Importing LangGraph Libraries.
from langgraph.graph import StateGraph, START
from langgraph.checkpoint.memory import MemorySaver

from src.agents import UnderstandingAgent, QuestionAgent, PlatformAgent


class AnalyticState(TypedDict):
    messages: List[Tuple[str, Any]] = []

    initial_question: str
    current_understanding: str
    final_question: str

    answer: str


def generate_understanding(state: AnalyticState):
    initial_question = state["initial_question"]
    messages = state["messages"] if "messages" in state else list()

    understanding_agent = UnderstandingAgent()
    current_understanding = understanding_agent.update_understanding(question = initial_question, messages = messages)

    return {
        "current_understanding": current_understanding.current_understanding
    }


def get_question(state: AnalyticState):
    initial_question = state["initial_question"]
    current_understanding = state["current_understanding"]

    question_agent = QuestionAgent()
    final_question = question_agent.generate_question(question = initial_question, current_understanding = current_understanding)

    return {
        "final_question": final_question.question
    }


def get_answer(state: AnalyticState):
    question = state["final_question"]
    messages = state["messages"] if "messages" in state else list()

    platform_agent = PlatformAgent(question = question, messages = messages)
    answer = platform_agent.acknowledge(question)

    messages.append((question, answer))

    return {
        "question": question,
        "answer": answer,
        "messages": messages
    }


workflow = StateGraph(AnalyticState)

workflow.add_node("generate_understanding", generate_understanding)
workflow.add_node("get_question", get_question)
workflow.add_node("get_answer", get_answer)


workflow.add_edge(START, "generate_understanding")
workflow.add_edge("generate_understanding", "get_question")
workflow.add_edge("get_question", "get_answer")

checkpointer = MemorySaver()

graph = workflow.compile(checkpointer = checkpointer)