from flask import Flask, render_template, request, jsonify, session
from core import process_query, format_goal, format_explanation
from datetime import datetime
import uuid
import os
from flask_session import Session

app = Flask(__name__)
app.secret_key = "your_secret_key"

# Session config - store session on filesystem to avoid size limit
app.config["SESSION_TYPE"] = "filesystem"
app.config["SESSION_FILE_DIR"] = os.path.join(os.getcwd(), "flask_session_data")
app.config["SESSION_PERMANENT"] = False
Session(app)

# Databases
DATABASES = {
    "Chinook": "sqlite:///Chinook.db",
    "Northwind": "postgresql+psycopg2://postgres:226850@localhost:5433/northwind"
}

@app.route("/")
def chat():
    if "history" not in session:
        session["history"] = {}
    return render_template("chat.html", databases=DATABASES.keys(), history=session["history"])

@app.route("/ask", methods=["POST"])
def ask():
    data = request.json
    db_name = data.get("database")
    question = data.get("question")
    history_id = data.get("history_id") or str(uuid.uuid4())

    db_uri = DATABASES.get(db_name)
    result = process_query(db_uri=db_uri, question=question)

    charts = result.get("chart_base64_list", [])
    goals = result.get("goals", [])
    explanations = result.get("explanation_list", [])

    if not (charts and goals and explanations) or not (len(charts) == len(goals) == len(explanations)):
        return jsonify({
            "final_answer": result.get("final_answer", "No answer."),
            "main_chart": None,
            "main_explanation": None,
            "recommendations": [],
            "history_id": history_id
        })

    main_chart = charts[0]
    main_explanation = format_explanation(explanations[0])
    main_goal = format_goal(goals[0])

    recommendations = []
    for i in range(1, len(charts)):
        recommendations.append({
            "goal": format_goal(goals[i]),
            "chart": charts[i],
            "explanation": format_explanation(explanations[i])
        })

    # Save to session history
    if "history" not in session:
        session["history"] = {}

    history = session["history"]

    if history_id not in history:
        history[history_id] = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "title": question,
            "entries": []
        }

    history[history_id]["entries"].append({
        "question": question,
        "final_answer": result.get("final_answer", "No answer."),
        "main_chart": main_chart,
        "main_explanation": main_explanation,
        "recommendations": recommendations
    })

    session["history"] = history
    session.modified = True

    return jsonify({
        "final_answer": result.get("final_answer", "No answer."),
        "main_chart": main_chart,
        "main_explanation": main_explanation,
        "recommendations": recommendations,
        "history_id": history_id
    })

@app.route("/clear_history", methods=["POST"])
def clear_history():
    session.pop("history", None)
    session.modified = True
    return ("", 204)

if __name__ == "__main__":
    os.makedirs(app.config["SESSION_FILE_DIR"], exist_ok=True)
    app.run(debug=True)
