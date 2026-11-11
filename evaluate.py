"""
evaluate.py
-----------
Evaluation of the recommender system (Activity 4).

The goal here is NOT to change the recommender, but to measure the quality of
the results it produces for a chosen seed document, using standard information
retrieval metrics computed with scikit-learn:

    * Precision      (sklearn.metrics.precision_score)
    * Recall         (sklearn.metrics.recall_score)
    * F1-score       (sklearn.metrics.f1_score)
    * Confusion matrix (sklearn.metrics.confusion_matrix)
    * A simple bar/heatmap visualization (matplotlib) saved as PNG.

How "relevant" is defined (the ground truth)
--------------------------------------------
For an automatic, reproducible evaluation we treat the seed document's CATEGORY
as the information need: a candidate document is RELEVANT (ground-truth positive)
when it belongs to the same category as the seed, and NOT relevant otherwise.
The seed itself is excluded from the evaluation.

This gives, for every other document in the corpus, two labels:
    y_true  = 1 if it shares the seed's category        (ground truth)
    y_pred  = 1 if it appears in the Top-K recommendations (retrieved)

Precision, recall and F1 are then computed on these binary vectors, which is
exactly precision@K / recall@K for the retrieval task.

Usage
-----
    python evaluate.py                 # default seed DOC011, K=5
    python evaluate.py --id DOC001 --k 5
    python evaluate.py --id DOC008 --k 5 --out confusion_matrix.png
"""

from __future__ import annotations

import argparse

import matplotlib

# Use a non-interactive backend so the script runs headless (no display needed).
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402  (import after backend is set)
import numpy as np  # noqa: E402
from sklearn.metrics import (  # noqa: E402
    ConfusionMatrixDisplay,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)

from recommender import DocumentRecommender  # reuse the Activity 3 system

DEFAULT_SEED = "DOC011"   # a Support/Incidents ticket makes a clear example
DEFAULT_K = 5
DEFAULT_OUT = "confusion_matrix.png"


def build_labels(
    recommender: DocumentRecommender,
    seed_id: str,
    k: int,
) -> tuple[np.ndarray, np.ndarray, list[str], str]:
    """Produce aligned y_true / y_pred arrays for every non-seed document.

    Returns
    -------
    y_true : np.ndarray  -> 1 if the document is relevant (same category as seed)
    y_pred : np.ndarray  -> 1 if the document was retrieved in the Top-K
    doc_ids: list[str]   -> the document ids, in the same order as the arrays
    seed_category : str  -> the seed document's category (the "information need")
    """
    df = recommender.df
    seed_row = df.loc[df["id"] == seed_id].iloc[0]
    seed_category = seed_row["category"]

    # Which documents did the system actually retrieve (Top-K, seed excluded)?
    recommendations = recommender.recommend_by_id(seed_id, top_n=k)
    retrieved_ids = {rec.doc_id for rec in recommendations}

    y_true: list[int] = []
    y_pred: list[int] = []
    doc_ids: list[str] = []

    for _, row in df.iterrows():
        if row["id"] == seed_id:
            continue  # the seed is never part of its own evaluation
        doc_ids.append(row["id"])
        # Ground truth: relevant if it shares the seed's category.
        y_true.append(1 if row["category"] == seed_category else 0)
        # Prediction: relevant if the system put it in the Top-K.
        y_pred.append(1 if row["id"] in retrieved_ids else 0)

    return np.array(y_true), np.array(y_pred), doc_ids, seed_category


def print_ground_truth_table(
    recommender: DocumentRecommender,
    seed_id: str,
    y_true: np.ndarray,
    y_pred: np.ndarray,
    doc_ids: list[str],
) -> None:
    """Print the per-document ground-truth vs retrieved comparison table.

    To keep the console output readable, we show every retrieved document plus
    every relevant document (the rows that drive the metrics), which is the
    interesting part of the table.
    """
    df = recommender.df
    title_by_id = dict(zip(df["id"], df["title"]))

    print("\nGround truth vs. retrieved (relevant OR retrieved rows shown):")
    print(f"{'Document':<9}{'Ground Truth':<16}{'Retrieved':<12}Title")
    print("-" * 78)
    for doc_id, truth, pred in zip(doc_ids, y_true, y_pred):
        if truth == 0 and pred == 0:
            continue  # skip the many true-negatives for a compact table
        gt = "Relevant" if truth == 1 else "Not Relevant"
        rt = "Yes" if pred == 1 else "No"
        print(f"{doc_id:<9}{gt:<16}{rt:<12}{title_by_id[doc_id]}")


def summarize_confusion(y_true: np.ndarray, y_pred: np.ndarray) -> dict[str, int]:
    """Return TP/FP/FN/TN counts from the confusion matrix for clear reporting."""
    # labels=[0, 1] fixes the orientation: rows = actual, cols = predicted.
    tn, fp, fn, tp = confusion_matrix(y_true, y_pred, labels=[0, 1]).ravel()
    return {"TP": int(tp), "FP": int(fp), "FN": int(fn), "TN": int(tn)}


def save_confusion_plot(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    metrics: dict[str, float],
    seed_id: str,
    out_path: str,
) -> None:
    """Save a two-panel figure: the confusion matrix + a metrics bar chart."""
    cm = confusion_matrix(y_true, y_pred, labels=[0, 1])

    fig, (ax_cm, ax_bar) = plt.subplots(1, 2, figsize=(11, 4.5))

    # ---- Left panel: confusion matrix heatmap ----
    display = ConfusionMatrixDisplay(
        confusion_matrix=cm,
        display_labels=["Not Relevant", "Relevant"],
    )
    display.plot(ax=ax_cm, cmap="Blues", colorbar=False)
    ax_cm.set_title(f"Confusion Matrix — seed {seed_id}")
    ax_cm.set_xlabel("Predicted (Retrieved)")
    ax_cm.set_ylabel("Actual (Ground Truth)")

    # ---- Right panel: precision / recall / F1 bar chart ----
    names = ["Precision", "Recall", "F1-score"]
    values = [metrics["precision"], metrics["recall"], metrics["f1"]]
    bars = ax_bar.bar(names, values, color=["#2a6fdb", "#47a44b", "#d9772b"])
    ax_bar.set_ylim(0, 1)
    ax_bar.set_title("Evaluation metrics")
    ax_bar.set_ylabel("Score (0–1)")
    # Annotate each bar with its exact value.
    for bar, value in zip(bars, values):
        ax_bar.text(
            bar.get_x() + bar.get_width() / 2,
            value + 0.02,
            f"{value:.2f}",
            ha="center",
            va="bottom",
            fontweight="bold",
        )

    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)
    print(f"\nSaved visualization to: {out_path}")


def evaluate(seed_id: str, k: int, corpus_path: str, out_path: str) -> None:
    """Run the full evaluation for one seed document and report everything."""
    recommender = DocumentRecommender(corpus_path)

    # Build aligned ground-truth / prediction arrays.
    y_true, y_pred, doc_ids, seed_category = build_labels(recommender, seed_id, k)

    seed_title = recommender.df.loc[
        recommender.df["id"] == seed_id, "title"
    ].iloc[0]

    # ---- Inputs (shown clearly, as the assignment requires) ----
    print("=" * 78)
    print("RECOMMENDER SYSTEM EVALUATION (Activity 4)")
    print("=" * 78)
    print(f"Seed document      : {seed_id} — {seed_title}")
    print(f"Information need    : documents in category '{seed_category}'")
    print(f"Top-K evaluated     : {k}")
    print(f"Corpus size         : {len(recommender.df)} documents "
          f"({len(doc_ids)} candidates after excluding the seed)")
    print(f"Relevant in corpus  : {int(y_true.sum())} documents "
          f"(same category as seed)")

    # ---- Show what the recommender returned (the retrieved set) ----
    print("\nTop-K recommendations returned by the system:")
    for rank, rec in enumerate(recommender.recommend_by_id(seed_id, k), start=1):
        flag = "RELEVANT" if rec.category == seed_category else "not relevant"
        print(f"  {rank}. {rec.doc_id}  score={rec.score:.4f}  "
              f"[{rec.category}] {rec.title}  -> {flag}")

    # ---- Ground-truth comparison table ----
    print_ground_truth_table(recommender, seed_id, y_true, y_pred, doc_ids)

    # ---- Metrics via scikit-learn (zero_division=0 guards tiny samples) ----
    precision = precision_score(y_true, y_pred, zero_division=0)
    recall = recall_score(y_true, y_pred, zero_division=0)
    f1 = f1_score(y_true, y_pred, zero_division=0)
    counts = summarize_confusion(y_true, y_pred)

    print("\nConfusion matrix counts:")
    print(f"  True Positives  (relevant & retrieved)     : {counts['TP']}")
    print(f"  False Positives (not relevant but retrieved): {counts['FP']}")
    print(f"  False Negatives (relevant but missed)       : {counts['FN']}")
    print(f"  True Negatives  (not relevant & not retrieved): {counts['TN']}")

    print("\nEvaluation metrics (scikit-learn):")
    print(f"  Precision : {precision:.4f}")
    print(f"  Recall    : {recall:.4f}")
    print(f"  F1-score  : {f1:.4f}")

    # ---- Visualization ----
    save_confusion_plot(
        y_true,
        y_pred,
        {"precision": precision, "recall": recall, "f1": f1},
        seed_id,
        out_path,
    )


def run_cli() -> None:
    parser = argparse.ArgumentParser(
        description="Evaluate the TF-IDF recommender with precision/recall/F1."
    )
    parser.add_argument("--corpus", default="corpus.csv", help="Path to corpus.csv")
    parser.add_argument("--id", dest="seed_id", default=DEFAULT_SEED,
                        help=f"Seed document id (default {DEFAULT_SEED})")
    parser.add_argument("--k", type=int, default=DEFAULT_K,
                        help=f"Top-K to evaluate (default {DEFAULT_K})")
    parser.add_argument("--out", default=DEFAULT_OUT,
                        help=f"Output PNG path (default {DEFAULT_OUT})")
    args = parser.parse_args()
    evaluate(args.seed_id, args.k, args.corpus, args.out)


if __name__ == "__main__":
    run_cli()
