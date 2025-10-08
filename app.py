from flask import Flask, render_template, request, redirect, url_for
import json
from pathlib import Path
from datetime import datetime

app = Flask(__name__)
app.secret_key = "supersecretkey"  # Still needed if sessions are later required

BASE_DIR = Path(__file__).parent
DATA_FEEDBACK = BASE_DIR / "feedback.json"
DATA_TICKETS = BASE_DIR / "tickets.json"
DATA_HOUSING = BASE_DIR / "housing.json"


def ensure_data_files():
    """Create data files if missing."""
    if not DATA_FEEDBACK.exists():
        DATA_FEEDBACK.write_text("[]", encoding="utf-8")
    if not DATA_TICKETS.exists():
        DATA_TICKETS.write_text("[]", encoding="utf-8")
    if not DATA_HOUSING.exists():
        # Provide a starter list of housing blocks
        DATA_HOUSING.write_text(json.dumps([
            "Block A", "Block B", "Block C", "Block D"
        ], indent=2), encoding="utf-8")


def load_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return []


def append_json(path: Path, record: dict):
    data = load_json(path)
    data.append(record)
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")


@app.route("/")
def home():
    """Home page with navigation choices."""
    return render_template("index.html")


@app.route("/feedback", methods=["GET", "POST"])
def feedback():
    ensure_data_files()
    if request.method == "POST":
        rating = request.form.get("rating")
        description = request.form.get("description", "").strip()
        try:
            rating_int = int(rating)
        except (TypeError, ValueError):
            rating_int = None
        if rating_int is not None and 1 <= rating_int <= 5 and description:
            append_json(DATA_FEEDBACK, {
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "rating": rating_int,
                "description": description
            })
        return redirect(url_for('home'))
    return render_template("feedback.html")


@app.route("/ticket", methods=["GET", "POST"])
def ticket():
    ensure_data_files()
    housing_blocks = load_json(DATA_HOUSING)
    if request.method == "POST":
        problem = request.form.get("problem", "").strip()
        housing = request.form.get("housing")
        room = request.form.get("room", "").strip()
        time_available = request.form.get("time_available", "").strip()
        if problem and housing in housing_blocks and room:
            append_json(DATA_TICKETS, {
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "problem": problem,
                "housing": housing,
                "room": room,
                "time_available": time_available
            })
        return redirect(url_for('home'))
    return render_template("ticket.html", housing_blocks=housing_blocks)


if __name__ == "__main__":
    ensure_data_files()
    app.run(debug=True)
