"""
RAG Exercise — Helper Utilities
================================

This module provides plotting, display, and data-wrangling utilities for the
RAG pipeline exercise.  Students import it as::

    import helper
    from helper import format_docs

All RAG logic (embeddings, retrieval, LLM calls) is left to the student.
This file only handles visualisation, pretty-printing, and convenience
formatting so that students can focus on the core RAG concepts.

Requirements: matplotlib, numpy  (both pre-installed in the exercise env).
"""

from __future__ import annotations

import textwrap
from typing import TYPE_CHECKING, Any, Dict, List

import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
import numpy as np

if TYPE_CHECKING:
    from langchain_core.documents import Document

# ---------------------------------------------------------------------------
# Matplotlib style
# ---------------------------------------------------------------------------
plt.rcParams.update(
    {
        "figure.facecolor": "#fafafa",
        "axes.facecolor": "#fafafa",
        "axes.edgecolor": "#cccccc",
        "axes.grid": True,
        "grid.color": "#e0e0e0",
        "grid.linestyle": "--",
        "grid.alpha": 0.7,
        "font.size": 11,
        "axes.titlesize": 13,
        "axes.titleweight": "bold",
        "figure.figsize": (9, 4.5),
        "figure.dpi": 100,
    }
)

_COLORS = ["#4C72B0", "#55A868", "#C44E52", "#8172B3", "#CCB974", "#64B5CD"]


# ───────────────────────────────────────────────────────────────────────────
# Plotting
# ───────────────────────────────────────────────────────────────────────────


def plot_document_length_distribution(documents: List[str]) -> None:
    """Plot a histogram of document lengths (in characters).

    Args:
        documents: List of document strings.

    Example::

        helper.plot_document_length_distribution(documents)
    """
    lengths = [len(d) for d in documents]

    fig, ax = plt.subplots()
    ax.hist(lengths, bins=40, color=_COLORS[0], edgecolor="white", linewidth=0.6)
    ax.yaxis.set_major_locator(MaxNLocator(integer=True))
    ax.set_xlabel("Document length (characters)")
    ax.set_ylabel("Count")
    ax.set_title("Document Length Distribution")
    ax.axvline(np.mean(lengths), color=_COLORS[2], linestyle="--",
               label=f"Mean = {np.mean(lengths):.0f}")
    ax.axvline(np.median(lengths), color=_COLORS[1], linestyle="--",
               label=f"Median = {np.median(lengths):.0f}")
    ax.legend()
    plt.tight_layout()
    plt.show()

    print(f"\n{'─' * 50}")
    print(f"  Documents : {len(documents)}")
    print(f"  Mean len  : {np.mean(lengths):.0f} chars")
    print(f"  Median    : {np.median(lengths):.0f} chars")
    print(f"  Min / Max : {min(lengths)} / {max(lengths)} chars")
    print(f"{'─' * 50}")


def plot_chunk_length_distribution(chunks: List[Any]) -> None:
    """Plot a histogram of chunk lengths (in characters).

    Accepts plain strings or LangChain Document objects.

    Args:
        chunks: List of chunk strings or Document objects.

    Example::

        helper.plot_chunk_length_distribution(chunks)
    """
    lengths = [
        len(c.page_content) if hasattr(c, "page_content") else len(str(c))
        for c in chunks
    ]

    fig, ax = plt.subplots()
    ax.hist(lengths, bins=40, color=_COLORS[1], edgecolor="white", linewidth=0.6)
    ax.yaxis.set_major_locator(MaxNLocator(integer=True))
    ax.set_xlabel("Chunk length (characters)")
    ax.set_ylabel("Count")
    ax.set_title("Chunk Length Distribution")
    ax.axvline(np.mean(lengths), color=_COLORS[2], linestyle="--",
               label=f"Mean = {np.mean(lengths):.0f}")
    ax.axvline(np.median(lengths), color=_COLORS[3], linestyle="--",
               label=f"Median = {np.median(lengths):.0f}")
    ax.legend()
    plt.tight_layout()
    plt.show()

    print(f"\n{'─' * 50}")
    print(f"  Chunks    : {len(chunks)}")
    print(f"  Mean len  : {np.mean(lengths):.0f} chars")
    print(f"  Median    : {np.median(lengths):.0f} chars")
    print(f"  Min / Max : {min(lengths)} / {max(lengths)} chars")
    print(f"{'─' * 50}")


def plot_evaluation_results(results_dict: Dict[str, float]) -> None:
    """Plot a bar chart of evaluation metrics.

    Args:
        results_dict: Mapping of metric name to score (0-1 or 0-100).

    Example::

        helper.plot_evaluation_results({"RAG Accuracy": 0.75, "Naive Accuracy": 0.40})
    """
    labels = list(results_dict.keys())
    values = list(results_dict.values())

    max_val = max(values) if values else 0
    is_fraction = max_val <= 1.0
    display_values = [v * 100 if is_fraction else v for v in values]

    fig, ax = plt.subplots()
    bars = ax.bar(labels, display_values, color=_COLORS[: len(labels)],
                  edgecolor="white", linewidth=0.8)

    for bar, val in zip(bars, display_values):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 1,
                f"{val:.1f}%", ha="center", va="bottom",
                fontweight="bold", fontsize=10)

    ax.set_ylabel("Score (%)")
    ax.set_title("Evaluation Results")
    ax.set_ylim(0, max(display_values) * 1.18 if display_values else 100)
    plt.tight_layout()
    plt.show()

    print(f"\n{'─' * 40}")
    for label, val in zip(labels, display_values):
        print(f"  {label:<25s} {val:6.1f}%")
    print(f"{'─' * 40}")


# ───────────────────────────────────────────────────────────────────────────
# Display / pretty-print
# ───────────────────────────────────────────────────────────────────────────


def display_retrieval_results(
    query: str,
    results: List[Any],
    max_preview: int = 300,
) -> None:
    """Pretty-print retrieval results from a similarity search.

    Args:
        query: The query string.
        results: List of ``(Document, score)`` tuples or ``Document`` objects.
        max_preview: Maximum characters to show per chunk.

    Example::

        results = vectorstore.similarity_search_with_score(query, k=4)
        helper.display_retrieval_results(query, results)
    """
    print(f"\n╔{'═' * 70}╗")
    print(f"║  Query: {query[:62]:<62s}║")
    print(f"╠{'═' * 70}╣")

    for i, item in enumerate(results, 1):
        if isinstance(item, tuple) and len(item) == 2:
            doc, score = item
            text = doc.page_content if hasattr(doc, "page_content") else str(doc)
            score_str = f"  (score: {score:.4f})"
        else:
            doc = item
            text = doc.page_content if hasattr(doc, "page_content") else str(doc)
            score_str = ""

        preview = text[:max_preview].replace("\n", " ")
        if len(text) > max_preview:
            preview += " …"

        wrapped = textwrap.fill(preview, width=66,
                                initial_indent="    ", subsequent_indent="    ")
        print(f"║  [{i}]{score_str}")
        print(f"║{wrapped}")
        if i < len(results):
            print(f"║{'─' * 70}║")

    print(f"╚{'═' * 70}╝\n")


def display_comparison_table(
    questions: List[str],
    rag_answers: List[str],
    naive_answers: List[str],
    gold_answers: List[str],
) -> None:
    """Print a side-by-side comparison of RAG vs. naive LLM answers.

    Args:
        questions: List of question strings.
        rag_answers: Answers from the RAG chain.
        naive_answers: Answers from the naive (no-retrieval) chain.
        gold_answers: Ground-truth answers.

    Example::

        helper.display_comparison_table(questions, rag_answers, naive_answers, gold_answers)
    """
    q_w, a_w = 30, 28

    def _trunc(s: str, w: int) -> str:
        s = s.replace("\n", " ").strip()
        return s[: w - 1] + "…" if len(s) > w else s

    header = (
        f"│ {'#':>2} │ {'Question':<{q_w}} │ {'RAG Answer':<{a_w}} │ "
        f"{'Naive Answer':<{a_w}} │ {'Gold Answer':<{a_w}} │"
    )
    sep = f"├{'─' * 4}┼{'─' * (q_w + 2)}┼{'─' * (a_w + 2)}┼{'─' * (a_w + 2)}┼{'─' * (a_w + 2)}┤"
    top = f"┌{'─' * 4}┬{'─' * (q_w + 2)}┬{'─' * (a_w + 2)}┬{'─' * (a_w + 2)}┬{'─' * (a_w + 2)}┐"
    bot = f"└{'─' * 4}┴{'─' * (q_w + 2)}┴{'─' * (a_w + 2)}┴{'─' * (a_w + 2)}┴{'─' * (a_w + 2)}┘"

    print(f"\n{top}")
    print(header)
    print(sep)

    for i, (q, ra, na, ga) in enumerate(
        zip(questions, rag_answers, naive_answers, gold_answers), 1
    ):
        rag_correct = ga.lower() in ra.lower()
        naive_correct = ga.lower() in na.lower()
        rag_mark = "✓" if rag_correct else "✗"
        naive_mark = "✓" if naive_correct else "✗"

        print(
            f"│ {i:>2} │ {_trunc(q, q_w):<{q_w}} │ {rag_mark} {_trunc(ra, a_w - 2):<{a_w - 2}} │ "
            f"{naive_mark} {_trunc(na, a_w - 2):<{a_w - 2}} │ {_trunc(ga, a_w):<{a_w}} │"
        )

    print(bot)

    n = len(questions)
    rag_acc = sum(1 for ra, ga in zip(rag_answers, gold_answers)
                  if ga.lower() in ra.lower()) / n * 100
    naive_acc = sum(1 for na, ga in zip(naive_answers, gold_answers)
                    if ga.lower() in na.lower()) / n * 100
    print(f"\n  RAG accuracy:   {rag_acc:.1f}%")
    print(f"  Naive accuracy: {naive_acc:.1f}%\n")


# ───────────────────────────────────────────────────────────────────────────
# Formatting utilities
# ───────────────────────────────────────────────────────────────────────────


def format_docs(docs: List[Any]) -> str:
    """Concatenate LangChain Document objects into a single string.

    Intended for use inside an LCEL chain::

        {"context": retriever | format_docs, "question": RunnablePassthrough()}

    Args:
        docs: List of Document objects (or strings).

    Returns:
        A single string with documents joined by ``---``.
    """
    return "\n---\n".join(
        d.page_content if hasattr(d, "page_content") else str(d) for d in docs
    )


def build_eval_set(
    dataset: Any,
    documents: List[str],
    n: int = 50,
) -> List[Dict[str, str]]:
    """Build an evaluation set by matching SQuAD questions to indexed documents.

    Args:
        dataset: A HuggingFace Dataset (SQuAD v2 validation split).
        documents: The document strings that were indexed.
        n: Maximum number of examples to return.

    Returns:
        List of dicts with keys ``"question"``, ``"answer"``, ``"context"``.

    Example::

        eval_set = helper.build_eval_set(squad, documents, n=50)
    """
    doc_set = set(documents)
    eval_examples: List[Dict[str, str]] = []

    for row in dataset:
        ctx = row["context"]
        answers = row.get("answers", {})
        answer_texts = answers.get("text", [])

        if ctx in doc_set and answer_texts:
            eval_examples.append(
                {
                    "question": row["question"],
                    "answer": answer_texts[0],
                    "context": ctx,
                }
            )
            if len(eval_examples) >= n:
                break

    print(f"  Built evaluation set: {len(eval_examples)} examples "
          f"(requested {n})")
    return eval_examples
