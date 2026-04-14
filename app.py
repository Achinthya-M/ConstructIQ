import csv
import io
import json
import os
import re
import uuid
from datetime import datetime

import joblib
import pandas as pd
from flask import Flask, jsonify, request, send_from_directory
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATASET_PATH = os.path.join(BASE_DIR, "dataset", "construction_data.csv")
DATA_DIR = os.path.join(BASE_DIR, "data")
DB_PATH = os.path.join(DATA_DIR, "db.json")
MODEL_PATH = os.path.join(BASE_DIR, "model.pkl")
VECTORIZER_PATH = os.path.join(BASE_DIR, "vectorizer.pkl")

ALLOWED_CATEGORIES = ["Material", "Labor", "Travel", "Equipment"]

app = Flask(__name__, static_folder=BASE_DIR)

model = None
vectorizer = None


def clean_text(text):
    text = str(text or "").lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def normalize_category(value):
    text = str(value or "").strip().lower()
    if "material" in text:
        return "Material"
    if "labor" in text or "labour" in text or "worker" in text:
        return "Labor"
    if "travel" in text or "transport" in text or "fuel" in text:
        return "Travel"
    if "equipment" in text or "machine" in text or "tool" in text:
        return "Equipment"
    return "Material"


def ensure_storage():
    os.makedirs(DATA_DIR, exist_ok=True)
    if not os.path.exists(DB_PATH):
        with open(DB_PATH, "w", encoding="utf-8") as f:
            json.dump({"projects": [], "expenses": []}, f, indent=2)


def load_db():
    ensure_storage()
    with open(DB_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    data.setdefault("projects", [])
    data.setdefault("expenses", [])
    return data


def save_db(data):
    with open(DB_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def train_model_from_dataset():
    global model, vectorizer
    if not os.path.exists(DATASET_PATH):
        raise FileNotFoundError(f"Dataset not found: {DATASET_PATH}")

    df = pd.read_csv(DATASET_PATH)
    if "Description" not in df.columns or "Task Group" not in df.columns:
        raise ValueError("Dataset must include Description and Task Group columns.")

    df["Description"] = df["Description"].fillna("").astype(str).map(clean_text)
    df["Task Group"] = df["Task Group"].fillna("").astype(str).map(normalize_category)
    df = df[(df["Description"] != "") & (df["Task Group"] != "")]

    vectorizer = TfidfVectorizer(ngram_range=(1, 2), max_features=5000)
    X = vectorizer.fit_transform(df["Description"])
    y = df["Task Group"]

    model = MultinomialNB()
    model.fit(X, y)

    joblib.dump(model, MODEL_PATH)
    joblib.dump(vectorizer, VECTORIZER_PATH)


def load_or_train_model():
    global model, vectorizer
    if os.path.exists(MODEL_PATH) and os.path.exists(VECTORIZER_PATH):
        model = joblib.load(MODEL_PATH)
        vectorizer = joblib.load(VECTORIZER_PATH)
    else:
        train_model_from_dataset()


def rule_based_category(description):
    text = clean_text(description)
    rules = {
        "Material": ["cement", "sand", "brick", "bricks"],
        "Labor": ["worker", "labour", "labor"],
        "Travel": ["fuel", "bus"],
        "Equipment": ["machine", "tools", "tool"],
    }
    for category, keywords in rules.items():
        if any(keyword in text for keyword in keywords):
            return category
    return None


def ml_category(description):
    if model is None or vectorizer is None:
        return "Material", 0.0
    cleaned = clean_text(description)
    if not cleaned:
        return "Material", 0.0

    vector = vectorizer.transform([cleaned])
    predicted = normalize_category(model.predict(vector)[0])
    confidence = 0.0
    if hasattr(model, "predict_proba"):
        confidence = float(model.predict_proba(vector).max())
    return predicted, confidence


def category_totals(expenses):
    totals = {key: 0.0 for key in ALLOWED_CATEGORIES}
    for expense in expenses:
        category = normalize_category(expense.get("category"))
        totals[category] += float(expense.get("amount", 0))
    return totals


@app.route("/", methods=["GET"])
def home():
    return send_from_directory(BASE_DIR, "index.html")


@app.route("/add_project", methods=["POST"])
def add_project():
    payload = request.get_json(silent=True) or {}
    project_name = str(payload.get("project_name", "")).strip()
    location = str(payload.get("location", "")).strip()

    if not project_name or not location:
        return jsonify({"success": False, "error": "project_name and location are required"}), 400

    db = load_db()
    project = {
        "id": str(uuid.uuid4()),
        "project_name": project_name,
        "location": location,
        "created_at": datetime.utcnow().isoformat(),
    }
    db["projects"].append(project)
    save_db(db)
    return jsonify({"success": True, "project": project})


@app.route("/get_projects", methods=["GET"])
def get_projects():
    db = load_db()
    projects = db["projects"]
    expenses = db["expenses"]
    enriched = []

    for project in projects:
        project_expenses = [e for e in expenses if e.get("projectId") == project["id"]]
        totals = category_totals(project_expenses)
        total_expense = sum(totals.values())
        enriched.append({**project, "total_expense": total_expense, "category_summary": totals})

    return jsonify({"success": True, "projects": enriched})


@app.route("/add_expense", methods=["POST"])
def add_expense():
    payload = request.get_json(silent=True) or {}
    project_id = str(payload.get("projectId", "")).strip()
    description = str(payload.get("description", "")).strip()

    amount_raw = payload.get("amount")
    try:
        amount = float(amount_raw)
    except (TypeError, ValueError):
        return jsonify({"success": False, "error": "Amount must be a valid number"}), 400

    if not project_id or not description or amount <= 0:
        return jsonify({"success": False, "error": "projectId, description and positive amount are required"}), 400

    db = load_db()
    if not any(project["id"] == project_id for project in db["projects"]):
        return jsonify({"success": False, "error": "Project not found"}), 404

    category = rule_based_category(description)
    method = "rule-based"
    confidence = 1.0
    if category is None:
        category, confidence = ml_category(description)
        method = "ml"

    expense = {
        "id": str(uuid.uuid4()),
        "projectId": project_id,
        "description": description,
        "amount": amount,
        "category": normalize_category(category),
        "date": datetime.utcnow().date().isoformat(),
        "method": method,
    }
    db["expenses"].append(expense)
    save_db(db)

    return jsonify({"success": True, "expense": expense, "confidence": confidence})


@app.route("/get_expenses/<project_id>", methods=["GET"])
def get_expenses(project_id):
    db = load_db()
    project_exists = any(project["id"] == project_id for project in db["projects"])
    if not project_exists:
        return jsonify({"success": False, "error": "Project not found"}), 404
    project_expenses = [e for e in db["expenses"] if e.get("projectId") == project_id]
    return jsonify({"success": True, "expenses": project_expenses})


@app.route("/dashboard", methods=["GET"])
def dashboard():
    db = load_db()
    projects = db["projects"]
    expenses = db["expenses"]
    totals_by_category = category_totals(expenses)
    total_expense = sum(totals_by_category.values())

    project_totals = []
    for project in projects:
        value = sum(float(e.get("amount", 0)) for e in expenses if e.get("projectId") == project["id"])
        project_totals.append({"projectId": project["id"], "project_name": project["project_name"], "total": value})

    return jsonify(
        {
            "success": True,
            "total_expense": total_expense,
            "category_totals": totals_by_category,
            "project_totals": project_totals,
        }
    )


@app.route("/predict", methods=["POST"])
def predict():
    payload = request.get_json(silent=True) or {}
    description = str(payload.get("description", "")).strip()
    if not description:
        return jsonify({"success": False, "error": "description is required"}), 400

    category = rule_based_category(description)
    method = "rule-based"
    confidence = 1.0
    if category is None:
        category, confidence = ml_category(description)
        method = "ml"

    return jsonify(
        {
            "success": True,
            "category": normalize_category(category),
            "confidence": confidence,
            "method": method,
        }
    )


@app.route("/export/json", methods=["GET"])
def export_json():
    db = load_db()
    return jsonify({"success": True, "data": db})


@app.route("/export/csv", methods=["GET"])
def export_csv():
    db = load_db()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["id", "projectId", "description", "amount", "category", "date"])
    for item in db["expenses"]:
        writer.writerow(
            [
                item.get("id"),
                item.get("projectId"),
                item.get("description"),
                item.get("amount"),
                item.get("category"),
                item.get("date"),
            ]
        )
    content = output.getvalue()
    return app.response_class(content, mimetype="text/csv", headers={"Content-Disposition": "attachment; filename=expenses.csv"})


if __name__ == "__main__":
    ensure_storage()
    load_or_train_model()
    app.run(debug=True, host="0.0.0.0", port=5000)
