from flask import Flask, jsonify
from .models import init_db, get_all_bins, insert_demo_bin

app = Flask(__name__)

# Initialize the database once at startup
init_db()


@app.get("/health")
def health():
    return jsonify({"status": "ok"})


@app.get("/bins")
def bins():
    return jsonify(get_all_bins())

@app.get("/bins/add-demo")
def add_demo_bin():
    insert_demo_bin()
    return jsonify({"status": "demo bin inserted"})



if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
    


