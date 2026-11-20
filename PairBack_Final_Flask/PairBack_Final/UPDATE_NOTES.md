# PairBack UI and intake update — 20 November 2026

Built on `origin/pairback-algorithms-dsws` (33c7459), which is separate from main. Flask, Quick Sort, Insertion Sort, ArrayList, and UndoStack remain in place.

## Changes

- Compact responsive top navigation with restrained hover/focus styling and reduced-motion support. Secondary actions live in Tools.
- Blue eagle dashboard illustration, inspired by the campus identity, and a new soft PairBack logo.
- Intake page: downloadable CSV template, validation and preview before import, exact duplicate skipping, 500-row / 2 MB limits, all-or-nothing batch persistence. Preview expires after 30 minutes or restart.
- Email intake shortcut: opens the existing report form with Email selected. It does not connect to Gmail or send email.
- DSWS information page: supplied hours, location, email/form links, claiming instructions, and non-valuable versus valuable item guidance. Current hours and office designations need confirmation with DSWS.

## How records enter the system

1. Staff with access to the Google Form response Sheet export it to CSV.
2. Copy item details into the downloadable template's columns. Remove the synthetic example. Use the loss date/time, not the submission timestamp. Unknown required details need staff follow-up; do not invent them.
3. Upload, inspect the preview, and confirm. PairBack records the source as Online Lost Items Report Form.
4. For student email, staff read the authorized DSWS inbox separately and choose Record an email. Check for an existing report first.
5. Record surrendered items separately, with their actual custody location.

CSV import is for new lost reports, not backup restoration: it does not preserve uploaded statuses or IDs. Duplicate detection compares all imported item fields after trimming and case-folding; it is not fuzzy or cross-channel identity verification. All matching remains staff-reviewed.

## Future direct integrations

The public form URL cannot supply private responses. Automatic polling requires authorized access to the response Sheet (Sheets API or an owner-installed Apps Script), a stable response ID and last-sync checkpoint. Gmail intake requires permission for the actual DSWS mailbox, least-privilege OAuth and message-ID deduplication. Both should create reviewable drafts before accepted reports. Neither connector has been implemented or simulated here.

## Run

From this folder:

```sh
python -m pip install -r requirements.txt
python app.py
```

Open http://127.0.0.1:5000. This retains the existing single-operator local demo configuration; do not expose its debug server publicly.

## Validation and boundaries

Run `python -m unittest discover -p '*test*.py'`. Includes existing algorithm/service checks plus CSV validation, atomic rejection, duplicate import after reload, page rendering, preview/commit and expired token checks. Browser visual QA was not performed.

The earlier branch's release-at-MVP-only and persisted undo semantics are unchanged. They require a separate policy review before operational use, particularly for items held at Xavier Hall. No real student data or account access is included.
