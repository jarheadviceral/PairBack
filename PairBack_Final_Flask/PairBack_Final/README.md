# PairBack — Final Flask Application

A single-user campus lost-and-found matching tool. Built with Flask, HTML/CSS, JSON persistence, and CSV export.

## Run on Windows
1. Extract the ZIP.
2. Open the `PairBack_Final` folder in VS Code.
3. Open Terminal in that folder.
4. Run:
   ```bash
   py -m venv .venv
   .venv\Scripts\activate
   py -m pip install -r requirements.txt
   py app.py
   ```
5. Open http://127.0.0.1:5000 in your browser.

You can also double-click `run.bat` if Python is installed and available on PATH.

## Run on macOS / Linux
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python3 app.py
```

## Features
- Dashboard counts for total, lost, found, available, and released/resolved records.
- Add lost and found reports with required-field and ISO date validation.
- Automatic IDs (`L001`, `F001`, etc.) and duplicate-ID prevention.
- Attribute matching across category (30%), color (25%), brand (20%), location (15%), and date (10%).
- Explainable match candidates showing each attribute, its compared values, and score contribution.
- Released found records are excluded from subsequent candidate lists.
- Recursive merge sort ranks matches by descending score, then ascending report ID.
- Iterative binary search retrieves exact IDs from an ID-sorted index.
- ArrayList and UndoStack are explicitly implemented in `data_structures.py`.
- Status updates push previous values onto UndoStack; Undo restores the latest change.
- JSON persistence in `data/records.json`.
- CSV export from the records page or sidebar.
- Search and filtering in the records directory.
- Responsive blue-and-white interface.

## Matching rule
Each exact, non-empty, case-insensitive field match receives its fixed weight:
- Category: 30
- Color: 25
- Brand: 20
- Location: 15
- Date: 10

The five weights total 100. This is a transparent project-defined heuristic, not an AI prediction or proof of ownership. Staff must independently verify ownership before releasing an item.

## Algorithms and complexity
Let `n` be total records, `f` available found records, `k` candidates, and `u` undo entries.
- Candidate scan and scoring: O(f)
- Candidate merge sort: O(k log k), O(k) auxiliary space
- ID index merge sort: O(n log n); binary search after index creation: O(log n)
- ArrayList append: amortized O(1), O(n) on resize
- UndoStack push: amortized O(1); pop/peek: O(1)
- JSON save: O(n)
- CSV export: O(n)

The ID index is rebuilt for each lookup in this straightforward prototype, so end-to-end lookup including index construction is O(n log n) + O(log n). The binary-search operation itself is O(log n).

## Test
```bash
python -m unittest -v
```
Tests cover array growth and bounds, stack LIFO behavior, merge sort, binary search, duplicate validation, JSON persistence, matching weights, released-item exclusion, and Undo.

## Data
The application creates `data/records.json` with synthetic sample records on first run. Back up this file before manually editing it. No real student personal data is included.
