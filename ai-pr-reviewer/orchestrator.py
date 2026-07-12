"""
orchestrator.py

Wires SecurityAgent, PerformanceAgent, and StyleAgent together using
LangGraph, then routes their output into FinalReviewAgent for merging.

Graph shape (matches the architecture diagram in the project plan):

            PR CODE
               |
      -------------------
      |        |        |
   Security  Perf     Style     <- run in parallel (fan-out)
      |        |        |
      -------------------
               |
          Final Review          <- fan-in / merge node
               |
          FINAL PR REVIEW

Requires: pip install langgraph

IMPLEMENTATION NOTE:
`filename` and `code` are constant for the whole run -- they're never
re-written by any node. Under concurrent execution, LangGraph rebuilds
each node's state view from whichever channels have been written so far
in the current superstep; values that are never re-written can drop out
of that view for whichever parallel node happens to run last, causing a
KeyError. Rather than fight that, we bake filename/code into each node
via closures (built fresh per review_file() call) so no node ever needs
to read them from shared graph state -- only the three review outputs
(which ARE written by nodes) live in the state schema.
"""

from typing import TypedDict
from langgraph.graph import StateGraph, START, END

from agents.security_agent import SecurityAgent
from agents.performance_agent import PerformanceAgent
from agents.style_agent import StyleAgent
from agents.final_agent import FinalReviewAgent


class ReviewState(TypedDict, total=False):
    security_review: str
    performance_review: str
    style_review: str
    final_review: str


# Instantiate agents once (they're stateless per-call, safe to reuse
# across every file/PR review).
security_agent = SecurityAgent()
performance_agent = PerformanceAgent()
style_agent = StyleAgent()
final_agent = FinalReviewAgent()


def _build_graph_for(filename: str, code: str):
    """
    Builds (and compiles) a small graph for one specific file review.
    filename/code are captured via closures instead of being threaded
    through shared graph state -- see module docstring for why.
    """

    def run_security(state: ReviewState) -> dict:
        print(f"   -> SecurityAgent reviewing {filename}...")
        return {"security_review": security_agent.review(filename, code)}

    def run_performance(state: ReviewState) -> dict:
        print(f"   -> PerformanceAgent reviewing {filename}...")
        return {"performance_review": performance_agent.review(filename, code)}

    def run_style(state: ReviewState) -> dict:
        print(f"   -> StyleAgent reviewing {filename}...")
        return {"style_review": style_agent.review(filename, code)}

    def run_final_merge(state: ReviewState) -> dict:
        print(f"   -> FinalReviewAgent merging findings for {filename}...")
        merged = final_agent.merge(
            filename=filename,
            security_review=state["security_review"],
            performance_review=state["performance_review"],
            style_review=state["style_review"],
        )
        return {"final_review": merged}

    graph = StateGraph(ReviewState)

    graph.add_node("security", run_security)
    graph.add_node("performance", run_performance)
    graph.add_node("style", run_style)
    graph.add_node("final_merge", run_final_merge)

    # Fan-out: all three specialist agents run independently from START.
    graph.add_edge(START, "security")
    graph.add_edge(START, "performance")
    graph.add_edge(START, "style")

    # Fan-in: final_merge only runs once ALL three specialists have written
    # their review into state (LangGraph waits for all incoming edges
    # before executing a node).
    graph.add_edge("security", "final_merge")
    graph.add_edge("performance", "final_merge")
    graph.add_edge("style", "final_merge")

    graph.add_edge("final_merge", END)

    return graph.compile()


def review_file(filename: str, code: str) -> dict:
    """
    Runs one file through the full multi-agent pipeline and returns a dict
    with filename, code, and all three specialist reviews + the merged
    final review.
    """
    graph = _build_graph_for(filename, code)
    result = graph.invoke({})
    return {
        "filename": filename,
        "code": code,
        "security_review": result["security_review"],
        "performance_review": result["performance_review"],
        "style_review": result["style_review"],
        "final_review": result["final_review"],
    }


if __name__ == "__main__":
    sample_code = """
def get_user(user_id):
    query = "SELECT * FROM users WHERE id = " + user_id
    return db.execute(query)
"""
    result = review_file("demo-test/test1.py", sample_code)
    print("\n=== FINAL REVIEW ===")
    print(result["final_review"])