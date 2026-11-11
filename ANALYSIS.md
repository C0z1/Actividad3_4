# Analysis, Interpretation & Reflection

This document covers the written deliverables for **Activity 3** (proof-of-operation
comments and organizational reflection) and **Activity 4** (ground-truth table,
metrics table, interpretation, Q&A, and the organizational-value reflection /
infographic content). All numbers come from the actual runs captured in
`proof_of_operation.txt`.

---

# PART A — ACTIVITY 3

## A.1 Proof of operation — the three tests

### Test 1 — Seed from *Policy/Process*: `DOC001` (Remote Work Policy)

| Rank | Doc | Score | Category | Title |
|------|-----|-------|----------|-------|
| 1 | DOC016 | 0.114 | FAQ | Connecting to the Company VPN |
| 2 | DOC011 | 0.104 | Support/Incidents | VPN Disconnection Issues |
| 3 | DOC031 | 0.092 | News/Article | The Rise of Remote and Hybrid Work |
| 4 | DOC005 | 0.078 | Policy/Process | Information Security Policy |
| 5 | DOC028 | 0.076 | News/Article | Company Opens New Regional Office |

**Comment — coherent?** Yes. The remote-work policy requires the **VPN** and
**secure remote access**, so the VPN FAQ, the VPN ticket and the security policy
are logically connected, and the "rise of remote work" article shares the same
theme. The scores are low in absolute terms because the documents are short and
the overlap is thematic rather than literal, but the *ranking* is sensible.

### Test 2 — Seed from *Support/Incidents*: `DOC011` (VPN Disconnection)

| Rank | Doc | Score | Category | Title |
|------|-----|-------|----------|-------|
| 1 | DOC016 | 0.294 | FAQ | Connecting to the Company VPN |
| 2 | DOC013 | 0.116 | Support/Incidents | Password Reset Request |
| 3 | DOC001 | 0.104 | Policy/Process | Remote Work Policy |
| 4 | DOC010 | 0.071 | Support/Incidents | Email Delivery Failure |
| 5 | DOC015 | 0.050 | Support/Incidents | Software Installation Access Denied |

**Comment — coherent?** Strongly. The top hit (0.294) is the **VPN FAQ** — exactly
the document a support agent would want next to a VPN ticket. The rest are other
help-desk tickets and the remote-work policy (which mandates the VPN). This is the
ideal behaviour for a "related knowledge" recommender.

### Test 3 — Free text query: *"I forgot my password and I am locked out of my account"*

| Rank | Doc | Score | Category | Title |
|------|-----|-------|----------|-------|
| 1 | DOC020 | 0.413 | FAQ | Recovering Account Access |
| 2 | DOC013 | 0.237 | Support/Incidents | Password Reset Request |
| 3 | DOC015 | 0.039 | Support/Incidents | Software Installation Access Denied |
| 4 | DOC010 | 0.036 | Support/Incidents | Email Delivery Failure |
| 5 | DOC016 | 0.036 | FAQ | Connecting to the Company VPN |

**Comment — coherent?** Excellent. The two top results (0.413 and 0.237) are the
account-recovery FAQ and the password-reset ticket — precisely the right answers.
The sharp drop to ~0.04 afterwards shows the model cleanly separates the two truly
relevant documents from the rest.

## A.2 Organizational reflection — talking points (for the ≤5-minute video)

Use these three answers as your script.

**1. Why does this reduce rework and speed up decisions?**
Knowledge in organizations is scattered across policies, tickets, FAQs and minutes.
When someone hits a VPN problem, the recommender instantly surfaces the VPN FAQ, the
matching policy and past tickets — so people **reuse existing answers instead of
re-solving solved problems** or re-writing documents that already exist. That shortens
time-to-answer, keeps responses consistent, and lets decisions rest on prior knowledge
rather than starting from a blank page.

**2. What limitations do you observe?**
- **Synonyms / vocabulary gap:** TF-IDF matches *words*, not *meaning*. "Laptop" vs
  "notebook", or "sign-in" vs "login", look unrelated to it.
- **Ambiguity:** a word like "access" spans VPN access, building access and data
  access; the model cannot disambiguate.
- **Short documents:** little text means few shared terms and low scores, so weak
  matches look similar to strong ones.
- **Corpus bias:** topics with many documents (support tickets) dominate; rare topics
  are under-recommended.

**3. What would you improve for a real environment?**
Add **metadata** (date, author, product, status) and **role-based filters** so a new
hire and a security engineer see different results; enforce **security / access
control** so recommendations never leak documents a user shouldn't see; move to
**semantic embeddings** (Path B) to handle synonyms; and run **continuous evaluation**
(the metrics below, tracked over time) so quality is monitored as the corpus grows.

---

# PART B — ACTIVITY 4 (Evaluation)

**Scenario evaluated:** seed document `DOC011` (VPN Disconnection ticket).
**Information need (ground truth):** documents in the same category,
`Support/Incidents`. **Top-K = 5.**

Of the 32 candidate documents (seed excluded), **7 are relevant** (the other
Support/Incidents documents).

## B.1 Identification of relevant results — ground-truth vs retrieved

| Document | Ground Truth | Retrieved by System | Outcome |
|----------|--------------|---------------------|---------|
| DOC016 (VPN FAQ) | Not Relevant* | Yes | False Positive |
| DOC013 (Password Reset ticket) | Relevant | Yes | **True Positive** |
| DOC001 (Remote Work Policy) | Not Relevant | Yes | False Positive |
| DOC010 (Email Delivery ticket) | Relevant | Yes | **True Positive** |
| DOC015 (Software Install ticket) | Relevant | Yes | **True Positive** |
| DOC008 (Login Outage incident) | Relevant | No | False Negative |
| DOC009 (DB Latency incident) | Relevant | No | False Negative |
| DOC012 (Printer ticket) | Relevant | No | False Negative |
| DOC014 (API 500 incident) | Relevant | No | False Negative |
| *(23 other documents)* | Not Relevant | No | True Negatives |

\* **Important nuance:** DOC016 (the VPN FAQ) is counted as a *false positive* only
because our automatic ground truth uses *category* as relevance. In reality it is the
**most useful** document for a VPN ticket. This shows how a strict category-based
ground truth can *understate* a recommender's true usefulness — a point worth raising
in the interpretation.

**Confusion matrix counts:** TP = 3, FP = 2, FN = 4, TN = 23.

## B.2 Evaluation metrics

| Metric | Result | Interpretation |
|--------|--------|----------------|
| **Precision** | **0.60** | Of the 5 documents the system returned, 60% (3/5) were truly relevant. It measures *how clean the results are* — how little noise the user sees. |
| **Recall** | **0.43** | Of the 7 relevant documents that exist, the system found 43% (3/7). It measures *coverage* — how much of the relevant knowledge was actually surfaced. |
| **F1-score** | **0.50** | The harmonic mean of precision and recall — a single balanced score. 0.50 reflects good precision pulled down by limited coverage. |

(See `confusion_matrix.png` for the visual.)

## B.3 Analysis — answers to the required questions

**Does the system display higher precision or higher recall?**
**Higher precision (0.60) than recall (0.43).** This is expected: with Top-K = 5 the
system can return at most 5 documents, but 7 are relevant, so recall is *capped* at
5/7 ≈ 0.71 before the run even starts. The model is **conservative** — it prefers to
return a short, mostly-correct list rather than cast a wide net.

**Is it retrieving an adequate amount of relevant documents?**
**Partially.** It surfaced 3 of 7 relevant documents. For a help-desk "related
articles" panel, returning 3 solid hits at the top is useful, but missing more than
half of the relevant set is a real gap if the goal is thorough knowledge discovery.

**Are there relevant documents that the system missed?**
**Yes — four false negatives:** the Login-Outage, Database-Latency, Printer and
API-500 documents. They belong to the same category but share almost no vocabulary
with a *VPN* ticket, so TF-IDF scored them low. (Note: for the *specific* need "a VPN
problem", several of these are only loosely relevant, which is why category-based
ground truth is a slightly pessimistic yardstick here.)

**What implications would this behavior have in an organizational context?**
A **precision-leaning** system builds **user trust**: people rarely see junk at the
top, so they keep using it. The cost is **residual rework** — relevant material that
never surfaces means some questions still get re-researched or re-answered. For
high-stakes needs (compliance, incident response) the missed documents (low recall)
matter more than a little extra noise, so the precision/recall balance should be tuned
to the use case.

**What improvements could boost recommendation quality?**
- **Semantic embeddings** (Path B, `sentence-transformers`) to catch synonyms and
  paraphrases the keyword model misses → higher recall.
- **Tune K / use a score threshold** so the retrieved-set size adapts to the query.
- **Metadata + role-based filters** (product, recency, permissions) to raise precision
  for a given user.
- **Human-labeled ground truth** instead of category-only, for a fairer measurement.
- **Hybrid retrieval** (lexical TF-IDF + semantic) and **query expansion**.
- **Continuous evaluation**: track precision/recall/F1 as the corpus grows.

## B.4 Reflection on the organizational value of evaluation — infographic content

Ready-to-drop content for your Canva / Miro / Genially infographic.

**Title:** *Why Measuring a Recommender Matters*

**Section 1 — Metrics turn opinion into evidence.**
Precision, recall and F1 replace "it feels good" with numbers you can compare across
versions, teams and time. In this project: **Precision 0.60 · Recall 0.43 · F1 0.50.**

**Section 2 — Each metric answers a business question.**
- *Precision* → "Can I trust the top results?" (low noise)
- *Recall* → "Am I missing important knowledge?" (coverage)
- *F1* → "What's the overall balance?"
- *Confusion matrix* → where errors happen (false positives vs false negatives).

**Section 3 — Better retrieval, better decisions.**
Measured systems can be **tuned on purpose**: raise recall for compliance and incident
response; raise precision for quick self-service. Evaluation makes that trade-off a
deliberate choice, not an accident.

**Section 4 — Why it's vital for knowledge management.**
What gets measured gets improved. Continuous evaluation catches quality drift as the
document base grows, protects trust in the tool, and ties IT/knowledge investment to a
visible outcome: **less rework, faster and more consistent decisions.**

**Key visual:** the two-panel figure in `confusion_matrix.png` (confusion matrix +
metric bars) works directly as the infographic's centerpiece.
