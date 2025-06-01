# llm-fragments-reddit

A plugin for [llm](https://github.com/simonw/llm) that loads Reddit threads as fragments, making it easy to analyze and summarize Reddit discussions with large language models.

## Features

- Load entire Reddit threads (submission + comments) as LLM fragments
- Support for both Reddit URLs and submission IDs
- Preserves comment hierarchy with proper indentation
- Converts threads to clean Markdown format
- Handles deleted comments and "load more" placeholders gracefully

## Installation

Install using pip:

```bash
llm install llm-fragments-reddit
```

Or for development:

```bash
git clone https://github.com/banteg/llm-fragments-reddit
cd llm-fragments-reddit
pip install -e .
```

## Usage

The plugin adds a `reddit` fragment loader to the `llm` command. You can use it in two ways:

### Using Reddit URLs

```bash
llm -f reddit:https://www.reddit.com/r/Python/comments/abc123/my_thread/ "summarize the key ideas"
```

### Using Submission IDs

```bash
llm -f reddit:abc123 "extract the main arguments from this discussion"
```

## How it works

The plugin:

1. Fetches the Reddit thread using Reddit's JSON API
2. Converts the submission title, self-text, and comment tree into Markdown
3. Preserves comment hierarchy with indentation (2 spaces per nesting level)
4. Each comment is formatted as: `- **u/username**: comment body`
5. Returns the entire thread as a single fragment for LLM processing

## Output Format

The generated fragment includes:

- Thread title as H1 header
- Original post content (if any)
- Nested comment tree with proper indentation
- Author attribution for each comment

Example output structure:
```markdown
# DAE think Reddit is becoming too mainstream?

I've been on Reddit for 7 years (this is my alt account) and I swear the quality of discourse has really declined. Back in my day we had actual discussions instead of just memes and karma farming.

---

- **u/NostalgicRedditor2016**: This. So much this. I remember when you could have nuanced discussions without getting downvoted to oblivion.
  - **u/ActuallyIm14**: OK boomer. Reddit was always trash, you just got older and realized it.
    - **u/NostalgicRedditor2016**: I'm 23 but go off I guess
      - **u/GrammarNaziPatrol**: *you're
        - **u/NostalgicRedditor2016**: No, "you" is correct there. Maybe learn grammar before correcting others?
          - **u/GrammarNaziPatrol**: Edit: Thanks for the gold, kind stranger!
- **u/RedditExpert2024**: Unpopular opinion but Reddit has always been a circlejerk. The real issue is people thinking upvotes = truth
  - **u/PhilosophyUndergrad**: This is a profound observation. As Nietzsche once said... [3000 word comment about nihilism]
    - **u/SkippedTheReading**: TL;DR?
- **u/PowerModerator**: Locked. Y'all can't behave.
```

## Requirements

- Python ≥ 3.12
- [llm](https://github.com/simonw/llm) ≥ 0.26
- requests ≥ 2.32.3

## License

MIT License - see the source code for details.

## Author

Created by [banteg](https://github.com/banteg)
