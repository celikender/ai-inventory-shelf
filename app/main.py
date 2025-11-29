from pathlib import Path

from flask import Flask, jsonify, send_from_directory, Response

import subprocess
import shutil

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

def _find_camera_cli() -> str | None:
    """Return the path to libcamera-still or rpicam-still, whichever exists."""
    for name in ("libcamera-still", "rpicam-still"):
        cmd = shutil.which(name)
        if cmd is not None:
            return cmd
    return None


@app.route("/camera/snapshot")
def camera_snapshot():
    """
    Grab one frame from the Pi camera using libcamera-still or rpicam-still
    and return it as JPEG.
    """
    from tempfile import NamedTemporaryFile

    cmd = _find_camera_cli()
    if cmd is None:
        return jsonify({"error": "No camera CLI found (libcamera-still or rpicam-still)"}), 500

    tmp = NamedTemporaryFile(suffix=".jpg", delete=False)
    tmp_path = tmp.name
    tmp.close()

    # -n = no preview, -t 200 = 200 ms capture time (both CLIs accept this)
    result = subprocess.run(
        [cmd, "-n", "-t", "200", "-o", tmp_path],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    if result.returncode != 0:
        err = result.stderr.decode(errors="ignore")
        return jsonify({"error": f"{cmd} failed", "details": err}), 500

    data = Path(tmp_path).read_bytes()
    Path(tmp_path).unlink(missing_ok=True)

    return Response(data, mimetype="image/jpeg")



if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
