from flask import Flask, render_template, request, jsonify
from core import process_query, format_goal, format_explanation

app = Flask(__name__)

DATABASES = {
    "Chinook": "sqlite:///Chinook.db",
    "Northwind": "postgresql+psycopg2://postgres:226850@localhost:5433/northwind"
}


@app.route("/")
def chat():
    return render_template("chat.html", databases=DATABASES.keys())

@app.route("/ask", methods=["POST"])
@app.route("/ask", methods=["POST"])
@app.route("/ask", methods=["POST"])
def ask():
    data = request.json
    db_name = data.get("database")
    question = data.get("question")
    db_uri = DATABASES.get(db_name)

    result = process_query(db_uri=db_uri, question=question)

    # 空结果时直接返回 final_answer，推荐为空
    if not result["chart_base64_list"]:
        return jsonify({
            "final_answer": result["final_answer"],
            "main_chart": None,
            "main_explanation": None,
            "recommendations": []
        })

    # 正常处理主图 + 推荐图
    main_chart = result["chart_base64_list"][0]
    main_explanation = format_explanation(result["explanation_list"][0])
    main_goal = format_goal(result["goals"][0])

    recommendations = []
    for i in range(1, len(result["chart_base64_list"])):
        recommendations.append({
            "goal": format_goal(result["goals"][i]),
            "chart": result["chart_base64_list"][i],
            "explanation": format_explanation(result["explanation_list"][i])
        })

    return jsonify({
        "final_answer": result["final_answer"],
        "main_chart": main_chart,
        "main_explanation": main_explanation,
        "recommendations": recommendations
    })


if __name__ == "__main__":
    app.run(debug=True)