from agents.base_agent import BaseReviewAgent, call_ollama


class FinalReviewAgent(BaseReviewAgent):
    """
    Takes the three specialist reviews (security, performance, style) for a
    single file and merges/de-duplicates/prioritizes them into one final
    verdict. This is the "debate/merge" step in the architecture diagram.
    """

    name = "FinalReviewAgent"
    system_prompt = """You are the lead reviewer on a pull request, synthesizing feedback from three
specialist reviewers: a Security reviewer, a Performance reviewer, and a
Code Quality/Style reviewer.

You will be given their three raw reviews for one file. Your job:
1. Merge them into a single, coherent review.
2. Remove duplicate or overlapping points.
3. If two reviewers seem to disagree or trade off against each other
   (e.g. Performance wants caching, Security flags the cache as a leak risk),
   call that out explicitly as a "trade-off to consider".
4. Order findings by severity (HIGH first).
5. End with one-line overall verdict: APPROVE, APPROVE WITH COMMENTS, or
   REQUEST CHANGES.

Keep the final output under 250 words. Use clear markdown-style bullets.
"""

    def merge(self, filename: str, security_review: str, performance_review: str, style_review: str) -> str:
        user_prompt = (
            f"File: {filename}\n\n"
            f"--- SECURITY REVIEW ---\n{security_review}\n\n"
            f"--- PERFORMANCE REVIEW ---\n{performance_review}\n\n"
            f"--- STYLE REVIEW ---\n{style_review}\n\n"
            f"Produce the merged final review now."
        )
        result = call_ollama(self.system_prompt, user_prompt, self.model, self.temperature)
        if result.startswith("ERROR calling Ollama"):
            return f"[{self.name}] {result}"
        return result