# Document Recommender System (TF-IDF) + Evaluation

Content-based **document recommender** over a corpus of 33 documents, built with
**TF-IDF + cosine similarity** (Path A — chosen for simplicity and transparency),
plus a **scikit-learn evaluation** (precision, recall, F1, confusion matrix).

---

## Objective

Build a recommender that, given a **seed document ID** or a **free-text query**,
returns the **Top-5 most similar documents** from an organizational knowledge base
(policies, support tickets, FAQs, meeting minutes, news). Then **evaluate the quality**
of those recommendations with standard information-retrieval metrics, so the system's
usefulness can be measured objectively rather than assumed.

## Dependencies

- Python 3.9+
- `pandas`, `numpy`, `scikit-learn`, `matplotlib`, `Pillow`

Install everything with:

```bash
pip install -r requirements.txt
```

## Execution steps

```bash
# 1. (Re)build the dataset  ->  corpus.csv
python build_corpus.py

# 2. Run the recommender (Activity 3)
python recommender.py --id DOC011                         # by seed document ID
python recommender.py --query "the vpn keeps disconnecting"   # by free text

# 3. Run the evaluation (Activity 4)  ->  prints metrics, writes the chart
python evaluate.py --id DOC011 --k 5 --out evidencias/confusion_matrix.png
```

No arguments launches a small interactive menu:

```bash
python recommender.py
```

## Usage example

```text
$ python recommender.py --id DOC011

SEED DOCUMENT: DOC011 | Support Ticket: VPN Disconnection Issues | category=Support/Incidents
Top-5 most similar documents:

Rank DocID    Score    Category            Title
------------------------------------------------------------------------------
1    DOC016   0.2939   FAQ                 FAQ: Connecting to the Company VPN
2    DOC013   0.1161   Support/Incidents   Support Ticket: Password Reset Request
3    DOC001   0.1043   Policy/Process      Remote Work Policy
4    DOC010   0.0710   Support/Incidents   Support Ticket: Email Delivery Failure
5    DOC015   0.0499   Support/Incidents   Support Ticket: Software Installation Access Denied
```

---

## Repository structure

```
.
├── README.md                 # this file
├── requirements.txt          # dependencies
├── corpus.csv                # dataset: id, title, text, category (33 docs)
├── build_corpus.py           # regenerates corpus.csv
├── recommender.py            # TF-IDF recommender (Activity 3)
├── evaluate.py               # precision / recall / F1 / confusion matrix (Activity 4)
├── ANALYSIS.md               # full analysis, interpretation, Q&A, infographic content
├── evidencias/               # evidence of the three tests + evaluation
│   ├── test1_policy_DOC001.txt
│   ├── test2_support_DOC011.txt
│   ├── test3_freetext_query.txt
│   ├── evaluation_DOC011.txt
│   └── confusion_matrix.png
└── docs/
    └── reporte.pdf           # 1–2 page report (approach, improvements, video link)
```

## The corpus

33 documents across 5 categories, mixing public-style articles and simulated internal
material. Vocabulary overlaps across categories (VPN, security, password, remote work)
so the recommender must rely on real term statistics, not trivial keyword matches.

| Category | Count |
|----------|-------|
| Policy/Process | 7 |
| Support/Incidents | 8 |
| FAQ | 6 |
| Meeting Minutes | 6 |
| News/Article | 6 |

## Evaluation headline (seed DOC011, Top-5)

**Precision 0.60 · Recall 0.43 · F1 0.50** — TP 3, FP 2, FN 4, TN 23.
A clean "precision > recall" case (Top-5 cannot cover all 7 relevant documents).
Full interpretation in `ANALYSIS.md`.

## Organizational reflection (video)

> **Reflection video:** _[PASTE YOUR VIDEO LINK HERE]_

The talking points and infographic content for the reflection are in `ANALYSIS.md`
(Part A.2 and Part B.4).

---

## Author

Felix (GitHub: [@C0z1](https://github.com/C0z1))
