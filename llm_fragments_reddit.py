"""LLM fragments plugin for Reddit comment threads.

Usage examples:

    # Summarize a Reddit thread by URL
    llm -f reddit:https://www.reddit.com/r/Python/comments/abc123/my_thread/ "summarize key ideas"

    # Or by submission ID
    llm -f reddit:abc123 "extract main arguments"

The plugin fetches the thread as JSON from Reddit and converts it into a
Markdown comment tree where each line starts with the author and is indented
(two spaces per nesting level). The entire tree (including the submission
title and self-text) is returned as a single fragment string so it can be
cleanly concatenated with other fragments in the final prompt.
"""

import re
from typing import List

import llm
import requests

__all__ = ["register_fragment_loaders"]

# Identify ourselves to the Reddit API
HEADERS = {
    "User-Agent": "llm-fragments-reddit/0.1 (+https://github.com/banteg/llm-fragments-reddit)"
}

MAX_COMMENTS = 1000  # Reddit caps at 500 per request, but we'll keep for clarity.


@llm.hookimpl
def register_fragment_loaders(register):
    register("reddit", reddit_loader)


def reddit_loader(arg: str):
    """Loads a full Reddit thread URL or just the submission ID as a fragment containing the submission title, self-text and the full nested comment tree."""

    # Resolve the argument to a Reddit JSON API URL
    submission_id, api_url = _reddit_api_url(arg)

    # Fetch submission + comments JSON (two‑element list)
    try:
        response = requests.get(api_url, headers=HEADERS, timeout=30)
        response.raise_for_status()
        json_data = response.json()
    except Exception as e:  # pragma: no cover – let llm show message to user
        raise ValueError(f"Could not fetch Reddit thread: {e}") from e

    # First element: submission; second: comment tree
    submission = json_data[0]["data"]["children"][0]["data"]
    title = submission["title"]
    self_text = submission.get("selftext", "").strip()

    lines: List[str] = [f"# {title}", ""]
    if self_text:
        lines.append(self_text)
        lines.extend(["", "---", ""])

    # Recursively render comment tree
    comments = json_data[1]["data"].get("children", [])
    for comment in comments:
        _render_comment(comment, lines, depth=0)

    return llm.Fragment("\n".join(lines), api_url)


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------


def _reddit_api_url(arg: str) -> tuple[str, str]:
    """Return *(submission_id, JSON API URL)* for the given ``arg``."""

    if arg.startswith("http://") or arg.startswith("https://"):
        # Strip trailing slash for consistency
        arg = arg.rstrip("/")
        # Extract ID from URL (/comments/<id>/)
        m = re.search(r"/comments/([a-z0-9]+)/", arg)
        if not m:
            raise ValueError("Could not extract submission ID from URL")
        submission_id = m.group(1)
        api_url = f"{arg}.json?limit={MAX_COMMENTS}"
    else:
        submission_id = arg
        api_url = (
            f"https://www.reddit.com/comments/{submission_id}.json?limit={MAX_COMMENTS}"
        )
    return submission_id, api_url


def _render_comment(node: dict, lines: List[str], *, depth: int) -> None:
    """Append a single comment (and its children) to *lines* list."""

    kind = node.get("kind")
    if kind == "more":  # Skip "load more comments" placeholders
        return

    if kind != "t1":  # Only process actual comments
        return

    data = node.get("data", {})
    author = data.get("author") or "[deleted]"
    body = data.get("body", "").strip().replace("\n", "\n\n")

    indent_prefix = " " * (depth * 2)
    comment_md = f"{indent_prefix}- **u/{author}**: {body}"
    lines.append(comment_md)

    replies = data.get("replies")
    if replies and isinstance(replies, dict):
        children = replies.get("data", {}).get("children", [])
        for child in children:
            _render_comment(child, lines, depth=depth + 1)
