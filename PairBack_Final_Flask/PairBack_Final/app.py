from flask import Flask, render_template, request, redirect, url_for, flash, send_file
from pairback import PairBack, FIELDS
from pathlib import Path
import io, csv

app = Flask(__name__)
app.secret_key = "pairback-local-demo-secret"
store = PairBack()

@app.context_processor
def inject_globals():
    return {"undo_count":len(store.history)}

@app.get("/")
def dashboard():
    records = store.all_records()
    lost = sum(r["report_type"]=="Lost" for r in records)
    found = sum(r["report_type"]=="Found" for r in records)
    available = sum(r["report_type"]=="Found" and r["status"]=="available" for r in records)
    released = sum(r["status"] in ("released","resolved") for r in records)
    return render_template("dashboard.html", records=records[-6:][::-1],
                           stats={"total":len(records),"lost":lost,"found":found,
                                  "available":available,"released":released})

@app.get("/records")
def records():
    q=request.args.get("q","").strip().casefold()
    kind=request.args.get("type","")
    status=request.args.get("status","")
    items=store.all_records()
    if q: items=[r for r in items if q in " ".join(str(v) for v in r.values()).casefold()]
    if kind: items=[r for r in items if r["report_type"]==kind]
    if status: items=[r for r in items if r["status"]==status]
    items=sorted(items,key=lambda r:r["report_id"])
    return render_template("records.html", records=items, q=q, kind=kind, status=status)

@app.route("/reports/new", methods=["GET","POST"])
def new_report():
    if request.method=="POST":
        try:
            record=store.add(request.form)
            flash(f"Report {record['report_id']} added successfully.","success")
            return redirect(url_for("records"))
        except ValueError as e: flash(str(e),"error")
    return render_template("new_report.html")

@app.get("/matching")
def matching():
    lost=[r for r in store.all_records() if r["report_type"]=="Lost"]
    selected=request.args.get("lost_id","")
    results=[]
    if selected:
        try: results=store.matches(selected)
        except ValueError as e: flash(str(e),"error")
    return render_template("matching.html", lost=lost, selected=selected, results=results)

@app.get("/search")
def search():
    query=request.args.get("id","").strip()
    result=store.find(query) if query else None
    return render_template("search.html", query=query, result=result, searched=bool(query))

@app.post("/records/<report_id>/status")
def update_status(report_id):
    try:
        changed=store.set_status(report_id,request.form.get("status",""))
        flash("Status updated." if changed else "No change was needed.","success")
    except ValueError as e: flash(str(e),"error")
    return redirect(request.referrer or url_for("records"))

@app.post("/undo")
def undo():
    change=store.undo()
    flash(f"Restored {change['report_id']} to {change['previous']}." if change else "There is nothing to undo.",
          "success" if change else "error")
    return redirect(request.referrer or url_for("dashboard"))

@app.get("/export")
def export():
    output=io.StringIO()
    writer=csv.DictWriter(output,fieldnames=FIELDS)
    writer.writeheader(); writer.writerows(store.all_records())
    mem=io.BytesIO(output.getvalue().encode("utf-8-sig")); mem.seek(0)
    return send_file(mem,mimetype="text/csv",as_attachment=True,download_name="pairback_records.csv")

@app.get("/health")
def health(): return {"status":"ok","records":len(store.records)}

if __name__=="__main__":
    app.run(debug=True)
