# PairBack - Final Flask Application

PairBack is a single-user web application for a campus lost-and-found desk.
It records lost and found reports, creates explainable candidate scores, and
supports a staff-controlled item-release process.

The prototype follows the stated DSWS workflow:

- The DSWS Lost & Found desk is at MVP 101.
- A student may report a lost item in person, through the online Lost Items
  Report Form, or through the DSWS lost-and-found email.
- A found item must be surrendered at MVP 101 or turned over through OADSA at
  Xavier Hall.
- A match score only creates a shortlist. It does not prove ownership.
- Before releasing a found item at MVP 101, staff must verify ownership using a valid ID or
  sufficient proof of ownership.

## Final-project algorithms

The two algorithms counted for the final project are different from the
algorithms submitted in the earlier coding assignments.

### 1. Quick Sort

The quick_sort function in data_structures.py arranges the record directory by
report ID. It uses a middle pivot and separates values into lower, equal, and
higher groups.

- Average time: O(n log n)
- Worst-case time: O(n^2)
- Additional space: O(n) on balanced partitions; O(n^2) worst case for this recursive copying implementation

### 2. Heap Sort

The heap_sort function uses the student-built MaxHeap class to rank possible
matches. Every candidate is inserted according to its match score. Repeated
removal returns the highest-scoring candidate first. A smaller report ID wins
when scores are equal.

- Build through repeated insertion: O(k log k)
- Remove all ranked candidates: O(k log k)
- Peek at strongest candidate: O(1)
- Additional space: O(k)

Merge Sort and Binary Search from Coding Assignment 1 are no longer used by
the final application. The Linear Search demonstrated in Coding Assignment 2
is also not used for exact report retrieval; PairBack maintains a report-ID
dictionary index with average O(1) access.

## Data structures

- ArrayList: stores all report records and grows by doubling capacity.
- UndoStack: stores status changes using Last-In, First-Out behavior.
- MaxHeap: stores match candidates according to priority.
- Report-ID dictionary: supports exact record retrieval.

## Matching rule

Each exact, non-empty, case-insensitive match receives a fixed weight:

- Category: 30
- Color: 25
- Brand: 20
- Location: 15
- Date lost/found: 10

The weights total 100. The score is a transparent project-defined heuristic,
not an AI prediction and not proof of ownership.

## Main features

- Dashboard for lost, found, available, released, and resolved reports
- Lost and found report intake with date, time, and channel validation
- Automatic report IDs and duplicate prevention
- DSWS-aligned intake and custody validation
- Explainable weighted matching
- Heap-Sort candidate ranking
- Quick-Sort record directory
- Verified release at MVP 101
- Undo for status changes and releases
- JSON persistence
- CSV export
- Search and filtering
- Automated unit tests

## Run on Windows

Open the folder containing app.py in VS Code, then run:

    py -m venv .venv
    .venv\Scripts\activate
    py -m pip install -r requirements.txt
    py app.py

Open http://127.0.0.1:5000 in a browser.

## Run the tests

    py -m unittest -v

The tests cover:

- ArrayList growth and bounds
- UndoStack LIFO behavior
- Quick Sort ordering
- Heap Sort ranking and tie-breaking
- Duplicate report prevention and JSON persistence
- DSWS intake rules
- Matching weights
- Verified release requirements
- Released-item exclusion
- Undo restoration

## Files to replace

Replace these files in PairBack_Final_Flask/PairBack_Final/:

- data_structures.py
- pairback.py
- app.py
- tests.py
- README.md
- templates/new_report.html
- templates/matching.html
- templates/records.html

The remaining files, including base.html, dashboard.html, search.html,
style.css, requirements.txt, and the run scripts, can remain unchanged.

## Prototype assumptions

MVP 101 release and intake validation are prototype workflow choices based on the supplied DSWS context, not an official policy certification. Online forms and email are recorded as intake channels only; no integration or messages are sent. Existing records with missing time or custody retain unknown values. Exact opening hours are not enforced because they were not supplied. Confirm Quick Sort and Heap Sort eligibility against the course slides before submission.
