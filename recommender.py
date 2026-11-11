"""
recommender.py
--------------
A document recommender system (Activity 3, Path A: TF-IDF + cosine similarity).

The system reads a corpus of documents from `corpus.csv`, converts the text into
TF-IDF vectors, and recommends the Top-N most similar documents either to:

  * a SEED DOCUMENT identified by its id  (e.g. DOC001), or
  * a FREE-TEXT QUERY pasted by the user  (e.g. "my vpn keeps disconnecting").

Design notes / best practices applied here
-------------------------------------------
* The logic lives in a small, testable class (`DocumentRecommender`) so it can be
  imported by the evaluation script (evaluate.py) without duplicating code.
* Text cleaning, vectorization, and similarity are separated into clear methods.
* A command-line interface (argparse) exposes both required modalities.
* Type hints and docstrings document intent; no global state is mutated.

Command-line usage
------------------
    # Recommend by seed document id:
    python recommender.py --id DOC001

    # Recommend from a free-text query:
    python recommender.py --query "the vpn keeps disconnecting at home"

    # Change how many results are returned (default 5):
    python recommender.py --id DOC008 --top 5

    # Interactive menu (pick mode at runtime):
    python recommender.py
"""

from __future__ import annotations

import argparse
import re
from dataclasses import dataclass

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Default location of the corpus and default number of recommendations.
DEFAULT_CORPUS = "corpus.csv"
DEFAULT_TOP_N = 5


# ---------------------------------------------------------------------------
# A simple container for one recommendation, so results are self-documenting.
# ---------------------------------------------------------------------------
@dataclass
class Recommendation:
    """One recommended document and its similarity score to the input."""

    doc_id: str
    title: str
    category: str
    score: float


def clean_text(text: str) -> str:
    """Minimal, transparent text cleaning for TF-IDF.

    Steps (kept deliberately simple so results are easy to reason about):
      1. Lowercase everything.
      2. Replace any character that is not a letter, digit or whitespace with a
         space (removes punctuation and special characters).
      3. Collapse repeated whitespace into single spaces.

    Stop-word removal is NOT done here; it is delegated to the TfidfVectorizer
    (`stop_words="english"`), which is the idiomatic place for it.
    """
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


class DocumentRecommender:
    """TF-IDF based content recommender over a corpus of text documents."""

    def __init__(self, corpus_path: str = DEFAULT_CORPUS) -> None:
        """Load the corpus and build the TF-IDF matrix once, up front."""
        self.corpus_path = corpus_path
        self.df = self._load_corpus(corpus_path)

        # Map a document id -> its row position, for fast seed lookups.
        self.id_to_index = {
            doc_id: pos for pos, doc_id in enumerate(self.df["id"])
        }

        # Fit the vectorizer on the cleaned corpus text. Using the title plus the
        # body gives the title terms extra weight, which is realistic for search.
        cleaned = (self.df["title"] + " " + self.df["text"]).apply(clean_text)

        self.vectorizer = TfidfVectorizer(
            stop_words="english",   # remove common English stop-words
            ngram_range=(1, 2),     # unigrams + bigrams capture short phrases
            min_df=1,               # keep rare terms (small corpus)
        )
        self.tfidf_matrix = self.vectorizer.fit_transform(cleaned)

    # ---- loading -----------------------------------------------------------
    @staticmethod
    def _load_corpus(corpus_path: str) -> pd.DataFrame:
        """Read corpus.csv and validate the required columns are present."""
        df = pd.read_csv(corpus_path)
        required = {"id", "title", "text"}
        missing = required - set(df.columns)
        if missing:
            raise ValueError(
                f"Corpus is missing required column(s): {sorted(missing)}"
            )
        # A missing optional 'category' column is tolerated (filled as "Unknown").
        if "category" not in df.columns:
            df["category"] = "Unknown"
        df = df.reset_index(drop=True)
        return df

    # ---- core recommendation logic ----------------------------------------
    def _top_from_scores(
        self,
        scores,
        top_n: int,
        exclude_index: int | None = None,
    ) -> list[Recommendation]:
        """Turn a similarity-score vector into the Top-N recommendations.

        `exclude_index`, when given, removes the seed document from its own
        results (requirement 2.e).
        """
        # Pair each row position with its score, then sort by score descending.
        ranked = sorted(
            enumerate(scores),
            key=lambda pair: pair[1],
            reverse=True,
        )

        results: list[Recommendation] = []
        for index, score in ranked:
            if exclude_index is not None and index == exclude_index:
                continue  # never recommend the seed document itself
            row = self.df.iloc[index]
            results.append(
                Recommendation(
                    doc_id=row["id"],
                    title=row["title"],
                    category=row["category"],
                    score=float(score),
                )
            )
            if len(results) >= top_n:
                break
        return results

    def recommend_by_id(
        self, doc_id: str, top_n: int = DEFAULT_TOP_N
    ) -> list[Recommendation]:
        """Recommend the Top-N documents most similar to a seed document id."""
        if doc_id not in self.id_to_index:
            raise KeyError(
                f"Document id '{doc_id}' not found in the corpus. "
                f"Valid ids look like: {', '.join(self.df['id'].head(3))} ..."
            )
        index = self.id_to_index[doc_id]
        # Cosine similarity of the seed vector against every document.
        scores = cosine_similarity(
            self.tfidf_matrix[index], self.tfidf_matrix
        ).flatten()
        return self._top_from_scores(scores, top_n, exclude_index=index)

    def recommend_by_text(
        self, query: str, top_n: int = DEFAULT_TOP_N
    ) -> list[Recommendation]:
        """Recommend the Top-N documents most similar to a free-text query."""
        cleaned = clean_text(query)
        # Transform the query with the SAME fitted vocabulary as the corpus.
        query_vector = self.vectorizer.transform([cleaned])
        scores = cosine_similarity(query_vector, self.tfidf_matrix).flatten()
        # No seed document to exclude when the input is free text.
        return self._top_from_scores(scores, top_n, exclude_index=None)


# ---------------------------------------------------------------------------
# Pretty-printing helpers for the console interface.
# ---------------------------------------------------------------------------
def describe_seed(recommender: DocumentRecommender, doc_id: str) -> str:
    """Return a short human-readable description of a seed document."""
    row = recommender.df.loc[recommender.df["id"] == doc_id].iloc[0]
    return f"{row['id']} | {row['title']} | category={row['category']}"


def print_recommendations(results: list[Recommendation]) -> None:
    """Print the Top-N recommendations as a simple aligned table."""
    print(f"{'Rank':<5}{'DocID':<9}{'Score':<9}{'Category':<20}Title")
    print("-" * 78)
    for rank, rec in enumerate(results, start=1):
        print(
            f"{rank:<5}{rec.doc_id:<9}{rec.score:<9.4f}"
            f"{rec.category:<20}{rec.title}"
        )


# ---------------------------------------------------------------------------
# Command-line / interactive entry point.
# ---------------------------------------------------------------------------
def run_cli() -> None:
    """Parse arguments and run the recommender in the requested mode."""
    parser = argparse.ArgumentParser(
        description="TF-IDF document recommender (Top-N by seed id or query).",
    )
    parser.add_argument(
        "--corpus", default=DEFAULT_CORPUS, help="Path to corpus.csv"
    )
    parser.add_argument(
        "--id", dest="doc_id", help="Seed document id, e.g. DOC001"
    )
    parser.add_argument(
        "--query", dest="query", help="Free-text query, e.g. 'reset my password'"
    )
    parser.add_argument(
        "--top", dest="top_n", type=int, default=DEFAULT_TOP_N,
        help=f"How many recommendations to return (default {DEFAULT_TOP_N})",
    )
    args = parser.parse_args()

    recommender = DocumentRecommender(args.corpus)

    # Mode 1: seed document id supplied on the command line.
    if args.doc_id:
        print(f"\nSEED DOCUMENT: {describe_seed(recommender, args.doc_id)}")
        print(f"Top-{args.top_n} most similar documents:\n")
        print_recommendations(recommender.recommend_by_id(args.doc_id, args.top_n))
        return

    # Mode 2: free-text query supplied on the command line.
    if args.query:
        print(f'\nQUERY TEXT: "{args.query}"')
        print(f"Top-{args.top_n} most similar documents:\n")
        print_recommendations(recommender.recommend_by_text(args.query, args.top_n))
        return

    # No flags given -> drop into a tiny interactive menu.
    _interactive_menu(recommender, args.top_n)


def _interactive_menu(recommender: DocumentRecommender, top_n: int) -> None:
    """A minimal interactive loop so the script is usable with no arguments."""
    print("Document Recommender (TF-IDF). Choose a mode:")
    print("  1) Recommend by document id")
    print("  2) Recommend by free text")
    choice = input("Enter 1 or 2: ").strip()

    if choice == "1":
        doc_id = input("Enter a document id (e.g. DOC001): ").strip().upper()
        try:
            print(f"\nSEED DOCUMENT: {describe_seed(recommender, doc_id)}\n")
            print_recommendations(recommender.recommend_by_id(doc_id, top_n))
        except KeyError as error:
            print(error)
    elif choice == "2":
        query = input("Paste your text: ").strip()
        print(f'\nQUERY TEXT: "{query}"\n')
        print_recommendations(recommender.recommend_by_text(query, top_n))
    else:
        print("Unrecognized choice; please run again and enter 1 or 2.")


if __name__ == "__main__":
    run_cli()
