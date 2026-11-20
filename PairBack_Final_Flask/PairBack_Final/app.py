import csv
import io

from flask import (
    Flask,
    flash,
    redirect,
    render_template,
    request,
    send_file,
    url_for,
)

from pairback import FIELDS, PairBack
from locations import LOCATIONS


app = Flask(__name__)
app.secret_key = "pairback-local-demo-secret"
store = PairBack()


@app.context_processor
def inject_globals():
    return {"undo_count": len(store.history)}


@app.get("/")
def dashboard():
    records = store.all_records()
    lost = sum(record["report_type"] == "Lost" for record in records)
    found = sum(record["report_type"] == "Found" for record in records)
    available = sum(
        record["report_type"] == "Found"
        and record["status"] == "available"
        for record in records
    )
    completed = sum(
        record["status"] in {"released", "resolved"}
        for record in records
    )
    return render_template(
        "dashboard.html",
        records=records[-6:][::-1],
        stats={
            "total": len(records),
            "lost": lost,
            "found": found,
            "available": available,
            "released": completed,
        },
    )


@app.get("/records")
def records():
    query = request.args.get("q", "").strip().casefold()
    report_type = request.args.get("type", "")
    status = request.args.get("status", "")
    items = store.all_records()

    if query:
        items = [
            record
            for record in items
            if query
            in " ".join(str(value) for value in record.values()).casefold()
        ]
    if report_type:
        items = [
            record
            for record in items
            if record["report_type"] == report_type
        ]
    if status:
        items = [
            record for record in items if record["status"] == status
        ]

    # Final-project algorithm 1: student-implemented Quick Sort.
    items = store.sorted_records(items)
    return render_template(
        "records.html",
        records=items,
        q=query,
        kind=report_type,
        status=status,
    )


@app.route("/reports/new", methods=["GET", "POST"])
def new_report():
    if request.method == "POST":
        try:
            record = store.add(request.form)
            flash(
                f"Report {record['report_id']} added successfully.",
                "success",
            )
            return redirect(url_for("records"))
        except ValueError as error:
            flash(str(error), "error")
    return render_template("new_report.html", campus_locations=LOCATIONS)


@app.get("/matching")
def matching():
    lost_reports = [
        record
        for record in store.sorted_records()
        if record["report_type"] == "Lost"
        and record["status"] == "open"
    ]
    selected = request.args.get("lost_id", "")
    results = []
    if selected:
        try:
            # Final-project algorithm 2: Insertion Sort candidate ranking.
            results = store.matches(selected)
        except ValueError as error:
            flash(str(error), "error")
    return render_template(
        "matching.html",
        lost=lost_reports,
        selected=selected,
        results=results,
    )


@app.get("/search")
def search():
    query = request.args.get("id", "").strip()
    result = store.find(query) if query else None
    return render_template(
        "search.html",
        query=query,
        result=result,
        searched=bool(query),
    )


@app.post("/records/<report_id>/status")
def update_status(report_id):
    try:
        changed = store.set_status(
            report_id,
            request.form.get("status", ""),
        )
        flash(
            "Status updated."
            if changed
            else "No change was needed.",
            "success",
        )
    except ValueError as error:
        flash(str(error), "error")
    return redirect(request.referrer or url_for("records"))


@app.post("/records/<report_id>/release")
def release_item(report_id):
    try:
        store.release(
            report_id=report_id,
            valid_id_confirmed=request.form.get("valid_id") == "yes",
            proof_confirmed=(
                request.form.get("proof_of_ownership") == "yes"
            ),
            release_location=request.form.get("release_location", ""),
        )
        flash(
            f"{report_id} was released through the verified MVP 101 process.",
            "success",
        )
    except ValueError as error:
        flash(str(error), "error")
    return redirect(request.referrer or url_for("matching"))


@app.post("/undo")
def undo():
    change = store.undo()
    if change:
        flash(
            f"Restored {change['report_id']} to {change['previous']}.",
            "success",
        )
    else:
        flash("There is nothing to undo.", "error")
    return redirect(request.referrer or url_for("dashboard"))


@app.get("/export")
def export():
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=FIELDS)
    writer.writeheader()
    writer.writerows(store.all_records())

    memory_file = io.BytesIO(output.getvalue().encode("utf-8-sig"))
    memory_file.seek(0)
    return send_file(
        memory_file,
        mimetype="text/csv",
        as_attachment=True,
        download_name="pairback_records.csv",
    )


@app.get("/health")
def health():
    return {"status": "ok", "records": len(store.records)}


# Intake is local and staff-reviewed; this does not connect to Google accounts.
from flask import session
from intake import parse_csv, prepare_batch, commit_batch, IMPORT_FIELDS
import secrets
import time

app.config["MAX_CONTENT_LENGTH"] = 2 * 1024 * 1024
_pending_imports = {}

@app.get("/dsws")
def dsws():
    return render_template("dsws.html")

@app.route("/intake", methods=["GET", "POST"])
def intake():
    preview = None
    skipped = 0
    token = None
    for key, pending in list(_pending_imports.items()):
        if time.time() - pending[0] > 1800:
            _pending_imports.pop(key, None)
    if request.method == "POST":
        try:
            if request.form.get("action") == "commit":
                token = request.form.get("token", "")
                if not token or token != session.get("import_token") or token not in _pending_imports:
                    raise ValueError("Preview expired. Upload the CSV again.")
                _, rows = _pending_imports[token]
                count, skipped = commit_batch(store, rows)
                _pending_imports.pop(token)
                session.pop("import_token", None)
                flash(f"Imported {count} reports; skipped {skipped} exact duplicates.", "success")
                return redirect(url_for("records"))
            upload = request.files.get("file")
            if not upload or not upload.filename.lower().endswith(".csv"):
                raise ValueError("Choose a UTF-8 CSV file.")
            rows = parse_csv(upload.read().decode("utf-8-sig"))
            preview, skipped = prepare_batch(store, rows)
            old_token = session.get("import_token")
            _pending_imports.pop(old_token, None)
            token = secrets.token_urlsafe(24)
            session["import_token"] = token
            _pending_imports[token] = (time.time(), rows)
        except (ValueError, UnicodeError, csv.Error) as error:
            flash(str(error), "error")
    return render_template("intake.html", preview=preview, skipped=skipped, token=token)

@app.get("/intake/template")
def intake_template():
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=IMPORT_FIELDS)
    writer.writeheader()
    writer.writerow(dict(item_name="Blue bottle",category="Bottle",color="Blue",brand="",location="Library",report_date="2026-11-19",report_time="14:30",description="Synthetic example: remove before importing"))
    return send_file(io.BytesIO(output.getvalue().encode("utf-8-sig")),mimetype="text/csv",as_attachment=True,download_name="pairback_intake_template.csv")

@app.errorhandler(413)
def upload_too_large(error):
    return "CSV exceeds the 2 MB upload limit. Return to Intake and choose a smaller file.", 413


if __name__ == "__main__":
    app.run(debug=True)
