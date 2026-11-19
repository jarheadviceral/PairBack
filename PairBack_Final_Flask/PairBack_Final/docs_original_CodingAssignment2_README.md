# PairBack — Coding Assignment 2

## Run
Extract this folder, open a terminal there, and run:

```sh
python TanlimcoViceral_Code.py
python TanlimcoViceral_Code.py --test
```

On Windows, use `py` if `python` is unavailable; on macOS/Linux use `python3`.
Open the .py file in VS Code, IDLE, or any text editor to inspect the code.
The normal command prints a deterministic demonstration. It does not request input.
To try another dataset, edit the ID/description pairs in demo(), or call
PairBack.add() with additional unique IDs. All data is synthetic and in memory.

## Two implemented data structures
- ArrayList: stores report objects using allocated slots, a size counter and capacity doubling. Indexing is O(1); insertion is amortized O(1), with O(n) resizing. Storage is O(n). Negative/out-of-range indexes raise a clear IndexError.
- UndoStack: exposes push, pop, peek and isEmpty, backed by ArrayList. Push is amortized O(1); pop/peek are O(1). Empty pop/peek return None. Changes are reversed in LIFO order. Storage is O(u) for u changes.

The application uses linear ID lookup, so release and undo are O(n) overall.
This does not change the stack operation complexities. Binary search and merge
sort are planned for the final project, not implemented in this milestone.
The final product remains a web app; this file demonstrates its backend structures.
Matching, browser screens, persistence and CSV export are outside this assignment build.

## Validation
Four automated tests cover growth to 1,000 entries, order preservation, stack
LIFO behavior, peek without removal, empty operations, invalid indexes,
duplicate IDs, blank fields, missing records, repeated releases and undo.
