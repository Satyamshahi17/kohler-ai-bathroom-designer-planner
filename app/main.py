"""Flask application entry point for the Kohler AI Bathroom Designer POC."""
from __future__ import annotations

from flask import Flask, render_template

from app.api.routes import api


def create_app(test_config=None, *, pipeline=None) -> Flask:
    app = Flask(__name__, template_folder="../frontend/templates", static_folder="../frontend/static")
    app.config.from_mapping(MAX_CONTENT_LENGTH=12 * 1024 * 1024)
    if test_config:
        app.config.update(test_config)
    app.register_blueprint(api)
    if pipeline is not None:
        app.extensions["design_pipeline"] = pipeline

    @app.get("/")
    def index():
        return render_template("index.html")

    @app.get("/health")
    def health():
        return {"status": "ok"}

    return app


app = create_app()


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
