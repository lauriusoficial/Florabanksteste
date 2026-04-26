from flask import Flask, send_from_directory
from core.database import init_db
from api.routes import api
import os

app = Flask(__name__, static_folder="frontend/static")
app.register_blueprint(api, url_prefix="/api")

@app.route("/")
def index():
    return send_from_directory("frontend", "index.html")

@app.route("/<path:path>")
def static_files(path):
    try:
        return send_from_directory("frontend", path)
    except Exception:
        return send_from_directory("frontend", "index.html")

if __name__ == "__main__":
    init_db()
    port = int(os.environ.get("PORT", 5000))
    print(f"\n🌿 Flora Banks rodando em http://localhost:{port}\n")
    app.run(host="0.0.0.0", port=port, debug=False)
