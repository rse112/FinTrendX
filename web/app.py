from flask import Flask, render_template, request, jsonify
import pandas as pd
import os

app = Flask(__name__)

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "result_out", "240625")


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/get_data", methods=["GET"])
def get_data():
    subcategory = request.args.get("subcategory")
    keyword = request.args.get("keyword")

    # Load the data from CSV files
    graph_df = pd.read_csv(os.path.join(DATA_DIR, "graph_240625_in.csv"))
    info_df = pd.read_csv(os.path.join(DATA_DIR, "info_240625_in.csv"))

    # Rename columns to unify the data format
    graph_df.columns = ["Reference_Date", "Category", "Keyword", "Date", "Value"]
    info_df.columns = [
        "Reference_Date",
        "Category",
        "Keyword",
        "Date",
        "Value",
        "Extra1",
        "Extra2",
        "Extra3",
        "Extra4",
        "Extra5",
        "Extra6",
        "Extra7",
    ]

    # Filter data based on the selected subcategory and keyword
    filtered_graph_df = graph_df[(graph_df["Category"] == subcategory)]
    if keyword:
        filtered_graph_df = filtered_graph_df[filtered_graph_df["Keyword"] == keyword]
        filtered_info_df = info_df[info_df["Keyword"] == keyword]
    else:
        filtered_info_df = info_df[info_df["Category"] == subcategory]

    keywords = filtered_graph_df["Keyword"].unique().tolist()
    graph_data = filtered_graph_df[["Date", "Value"]].to_dict(orient="records")
    info_data = filtered_info_df.to_dict(orient="records")

    return jsonify(
        {"graph_data": graph_data, "info_data": info_data, "keywords": keywords}
    )


if __name__ == "__main__":
    app.run(debug=True)
