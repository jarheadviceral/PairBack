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

The app uses three algorithms: Quick Sort, Insertion Sort, and Linear Search /
Traversal. Quick Sort and Insertion Sort are the two new algorithms; Linear Search
is retained from Coding Assignment 2.

### 1. Quick Sort

The quick_sort function in data_structures.py arranges the record directory by
report ID. It uses a middle pivot, an in-place three-way partition, and an
explicit partition stack. Processing the smaller partition immediately keeps
the stack bounded and avoids Python recursion-limit failures.

- Average time: O(n log n)
- Worst-case time: O(n^2)
- Additional space: O(n) for the returned copy plus O(log n) partition-stack
  space when the smaller partition is processed first

### 2. Insertion Sort

The insertion_sort function shifts lower-priority candidates right to insert
each candidate into its ordered position. Scores are descending; ties use
report ID ascending. Equal-priority entries retain their input order.

- Best time: O(k) for already ordered input
- Average/worst time: O(k^2)
- Additional space: O(k) for the returned copy; O(1) for the insertion loop

### 3. Linear Search / Traversal (retained from Coding Assignment 2)

Exact report-ID lookup scans the ArrayList and returns the matching record,
or None when absent. It takes O(n) worst-case time and O(1) auxiliary space.
Record filtering and matching also traverse records sequentially. Matching
scans all n reports and stores k eligible candidates: O(n) scan time and
O(k) candidate storage before Insertion Sort ranks them.

Quick Sort and Insertion Sort remain the two new final-project algorithms.
Linear Search / Traversal is the retained supporting algorithm.
Merge Sort and Binary Search are not used.

## Two primary data structures

- ArrayList: stores all report records in explicitly allocated slots, with a
  size counter and capacity doubling. Indexed access is O(1); append is
  amortized O(1), with O(n) copying during growth. pop_last is O(1).
- UndoStack: stores status changes and releases in Last-In, First-Out order,
  backed by ArrayList. Push is amortized O(1); pop and peek are O(1).
  Empty pop and peek return None. History is kept for the current session.

There is no report-ID dictionary index: PairBack.find performs Linear Search.

### Implementation map

| Component | Implementation | Application |
| --- | --- | --- |
| Quick Sort | data_structures.quick_sort | PairBack.sorted_records; record directory |
| Insertion Sort | data_structures.insertion_sort | PairBack.matches; score descending, ID ascending |
| Linear Search / Traversal | PairBack.find; app.records; PairBack.matches | Exact ID lookup, filtering, candidate scan |
| ArrayList | data_structures.ArrayList | PairBack.records; backing storage for UndoStack |
| UndoStack | data_structures.UndoStack | PairBack.set_status, release, and undo |

IDs are compared lexicographically as strings. Sorting returns a new list and
does not rearrange the stored ArrayList. A missing ID returns None. The full
matching operation costs O(n + k^2) in the worst case, where n is all stored reports and k
is eligible found reports. Undo is O(n) overall because it searches for the
record, even though the stack pop itself is O(1); saving also processes n
records. The five matching weights are fixed, so scoring one candidate is O(1).

## Matching rule

Each non-empty, case-insensitive match receives a fixed weight. Location uses
the building when recognized; other fields use exact equality:

- Category: 30
- Color: 25
- Brand: 20
- Location: 15
- Date lost/found: 10

New reports select a building and optionally enter a room, floor, or area.
The combined location (for example, MVP · 101) is saved and exported.
CSV imports retain their location column; use the same combined format.
Existing free-text locations are preserved.

Room suggestions come from the team's ranges in locations.py. Intermediate
floors suggest 01–15; the final floor stops at the supplied endpoint. These
are not a verified room inventory, so custom room or area entries are allowed.
Known buildings receive the location weight even when rooms differ. Full
locations remain visible in the comparison for staff review.

The weights total 100. The score is a transparent project-defined heuristic,
not an AI prediction and not proof of ownership.

## Main features

- Dashboard for lost, found, available, released, and resolved reports
- Lost and found report intake with date, time, and channel validation
- Automatic report IDs and duplicate prevention
- DSWS-aligned intake and custody validation
- Explainable weighted matching
- Insertion-Sort candidate ranking
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
- Insertion Sort ranking and tie-breaking
- Insertion Sort empty and 5,001-item input limits
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

MVP 101 release and intake validation are prototype workflow choices based on the supplied DSWS context, not an official policy certification. Online forms and email are recorded as intake channels only; no integration or messages are sent. Existing records with missing time or custody retain unknown values. Exact opening hours are not enforced because they were not supplied. Quick Sort and Insertion Sort are explicitly covered in the supplied course slides. Linear Search remains a supporting operation and is not counted toward the two required algorithms.
