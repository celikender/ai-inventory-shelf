from pathlib import Path

from flask import Flask, jsonify, send_from_directory

from .models import init_db, get_all_bins, insert_demo_bin

app = Flask(__name__)

BASE_DIR = Path(__file__).resolve().parents[1]
WEB_DIR = BASE_DIR / "web"


# Initialize DB once when the app module is imported
init_db()



@app.route("/")
def index():
    # Serve the simple HTML dashboard
    return send_from_directory(WEB_DIR, "index.html")


@app.route("/health")
def health():
    return jsonify({"status": "ok"})


@app.route("/bins")
def list_bins():
    return jsonify(get_all_bins())


@app.route("/bins/add-demo")
def add_demo_bin():
    insert_demo_bin()
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
