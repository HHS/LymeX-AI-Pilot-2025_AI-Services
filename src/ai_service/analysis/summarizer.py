"""
app.analysis.summarizer
-----------------------
Create an ≤ `max_words` summary for a product‑profile PDF.

Priority of back‑ends
---------------------
1.  **OpenAI GPT‑4o**            – highest quality if OPENAI_API_KEY set.
2.  **Local TextRank (sumy)**    – zero‑cost fallback if OpenAI not available.

Usage
-----
>>> from tool_a.extractor import TextExtractor
>>> from tool_a.analysis import summarizer
>>> pages = TextExtractor().extract("uploads/K240287.pdf")
>>> print(summarizer.summarize(pages))
"""

from __future__ import annotations

import os
import re
import textwrap
from typing import List, Sequence, Union

#from ai_service.extractor import Page
from ai_service.extractor.text_extractor import TextExtractor

# import and ownload nltk tokenizer
import nltk
nltk.download('punkt_tab')

# --------------------------------------------------------------------------- helpers

def _pages_to_text(pages: Sequence[Page]) -> str:
    """Concatenate page text with form‑feed separators (useful for GPT)."""
    return "\f\n".join(p.text.strip() for p in pages if p.text.strip())


def _trim_to_chars(txt: str, max_chars: int = 16_000) -> str:
    """Hard‑limit prompt length for the LLM backend."""
    if len(txt) <= max_chars:
        return txt
    # keep first and last blocks – gives model context + conclusion
    head = txt[: max_chars // 2]
    tail = txt[-max_chars // 2 :]
    return f"{head}\n\n[...omitted...]\n\n{tail}"


# --------------------------------------------------------------------------- OpenAI backend

def _openai_summarize(text: str, max_words: int, model: str = "gpt-4o") -> str:
    from openai import OpenAI
    api_key = "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"

    client = OpenAI(api_key= api_key) #os.getenv("OPENAI_API_KEY")
    text = _trim_to_chars(text, 16_000)

    messages = [
        {
            "role": "system",
            "content": (
                "You are an FDA document analyst. Provide an accurate, "
                f"neutral summary of no more than {max_words} words."
            ),
        },
        {"role": "user", "content": text},
    ]

    resp = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0.3,
        max_tokens=max_words * 2,  # generous; GPT will usually stop earlier
    )
    summary = resp.choices[0].message.content.strip()

    # post‑trim in case GPT overshoots word limit
    summary_words = summary.split()
    if len(summary_words) > max_words:
        summary = " ".join(summary_words[:max_words]) + "…"
    return summary


# --------------------------------------------------------------------------- Local TextRank fallback

def _textrank_summarize(text: str, max_words: int) -> str:
    """
    Quick local fallback using Sumy's TextRank. Requires:
        pip install sumy nltk
    """
    from sumy.parsers.plaintext import PlaintextParser
    from sumy.nlp.tokenizers import Tokenizer
    from sumy.summarizers.text_rank import TextRankSummarizer

    # heuristic: 1 sentence ≈ 20 words
    sentence_limit = max(3, max_words // 18)

    parser = PlaintextParser.from_string(text, Tokenizer("english"))
    summarizer = TextRankSummarizer()
    sentences = summarizer(parser.document, sentence_limit)
    summary = " ".join(str(s) for s in sentences)

    # enforce hard word cap
    words = summary.split()
    if len(words) > max_words:
        summary = " ".join(words[:max_words]) + "…"
    return summary


# --------------------------------------------------------------------------- public API

def summarize(
    doc: Union[str, Sequence[Page]],
    *,
    max_words: int = 250,
) -> str:
    """
    Parameters
    ----------
    doc
        Either a list/tuple of `Page` objects (preferred) **or** a raw text string.
    max_words
        Word cap for the summary (hard limit).

    Returns
    -------
    str  – summary ≤ `max_words` words.
    """

    # 1) canonicalize input
    if isinstance(doc, str):
        text = doc
    else:
        text = _pages_to_text(doc)

    # 2) choose backend
    if os.getenv("OPENAI_API_KEY"):
        print("Summarizer backend: OpenAI GPT‑4o")
        try:
            return _openai_summarize(text, max_words)
        except Exception as e:  # noqa: BLE001
            # log & fall through to local summarizer
            print("[summarizer] OpenAI backend failed:", e)
    else:
        print("Summarizer backend: TextRank fallback")
        return _textrank_summarize(text, max_words)

#print('Run Succesfull')