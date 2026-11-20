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
report ID. It uses a middle pivot, an in-place three-way partition, and an
explicit partition stack. Processing the smaller partition immediately keeps
the stack bounded and avoids Python recursion-limit failures.

- Average time: O(n log n)
- Worst-case time: O(n^2)
- Additional space: O(n) for the returned copy plus O(log n) partition-stack
  space when the smaller partition is processed first

### 2. Heap Sort

The heap_sort function uses the student-built MaxHeap class to rank possible
matches. It constructs the candidate heap bottom-up according to match score.
Repeated removal returns the highest-scoring candidate first. A smaller report
ID wins when scores are equal.

- Bottom-up heap construction: O(k)
- Remove all ranked candidates: O(k log k)
- Peek at strongest candidate: O(1)
- Additional space: O(k)

### 3. Linear Search / Traversal (retained from Coding Assignment 2)

Exact report-ID lookup scans the ArrayList and returns the matching record,
or None when absent. It takes O(n) worst-case time and O(1) auxiliary space.
Record filtering and matching also traverse records sequentially. Matching
scans all n reports and stores k eligible candidates: O(n) scan time and
O(k) candidate storage before Heap Sort ranks them.

Quick Sort and Heap Sort remain the two new final-project algorithms.
Linear Search / Traversal is the retained supporting algorithm.
Merge Sort and Binary Search are not used.

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

    py -m unittest discover -p "*test*.py" -v

The tests cover:

- ArrayList growth and bounds
- UndoStack LIFO behavior
- Quick Sort ordering
- Quick Sort empty, duplicate, and adversarial 1,100-item limits
- Heap Sort ranking and tie-breaking
- Heap Sort empty and 5,001-item input limits
- Duplicate report prevention and JSON persistence
- DSWS intake rules
- Matching weights
- Verified release requirements
- Released-item exclusion
- Undo restoration

## Validation record

`TEST_RESULTS.txt` records the current reproducible validation command and
result.

## Prototype assumptions

MVP 101 release and intake validation are prototype workflow choices based on the supplied DSWS context, not an official policy certification. Online forms and email are recorded as intake channels only; no integration or messages are sent. Existing records with missing time or custody retain unknown values. Exact opening hours are not enforced because they were not supplied. Confirm Quick Sort and Heap Sort eligibility against the course slides before submission.
