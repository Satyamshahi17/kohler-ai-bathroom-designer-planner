"""Flask API routes for the interactive designer."""
from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path

from flask import Blueprint, current_app, jsonify, request

from app.llm.vision import validate_spatial_payload
from app.models.result import DesignResult
from app.pipeline.orchestrator import DesignPipeline

api = Blueprint("api", __name__, url_prefix="/api")


def _pipeline() -> DesignPipeline:
    pipeline = current_app.extensions.get("design_pipeline")
    if pipeline is None:
        pipeline = DesignPipeline()
        current_app.extensions["design_pipeline"] = pipeline
    return pipeline


def _json_result(result: DesignResult):
    return jsonify(result.model_dump(mode="json"))


@api.post("/design")
def design():
    """Run the complete design pipeline from requirements + image or structured plan."""
    requirements = request.form.get("requirements")
    payload = request.form.get("payload")
    if payload:
        try:
            data = json.loads(payload)
        except json.JSONDecodeError as exc:
            return jsonify({"status": "error", "error": f"Invalid payload JSON: {exc}"}), 400
        requirements = data.get("requirements", requirements)
        spatial_plan = data.get("spatial_plan")
        top_k = data.get("top_k", 3)
    else:
        data = request.get_json(silent=True) or {}
        requirements = requirements or data.get("requirements")
        spatial_plan = data.get("spatial_plan")
        top_k = data.get("top_k", 3)
    if not requirements:
        return jsonify({"status": "error", "error": "requirements is required"}), 400

    image_path = None
    upload = request.files.get("image")
    if upload and upload.filename:
        suffix = Path(upload.filename).suffix or ".bin"
        fd, image_path = tempfile.mkstemp(prefix="kohler_", suffix=suffix)
        os.close(fd)
        upload.save(image_path)

    try:
        plan = None
        if spatial_plan is not None:
            try:
                plan = validate_spatial_payload({"spatial_plan": spatial_plan}).spatial_plan
            except Exception as exc:
                return jsonify({"status": "error", "error": f"Invalid spatial_plan: {exc}"}), 400
        result = _pipeline().run(requirements=requirements, image_path=image_path,
                                 spatial_plan=plan, top_k=top_k)
        current_app.extensions["latest_result"] = result
        status_code = 200 if result.status in {"success", "provisional", "no_valid_layout"} else 500
        return _json_result(result), status_code
    finally:
        if image_path:
            try:
                os.unlink(image_path)
            except OSError:
                pass


@api.post("/recommend")
def recommend():
    """Return the current product ranking without running layout generation."""
    from app.llm.requirements import RequirementsParser
    from app.products.catalog import load_products
    from app.products.embeddings import ProductEmbeddingIndex
    from app.recommendation.hybrid_ranker import HybridRanker

    data = request.get_json(silent=True) or {}
    requirements = data.get("requirements", "")
    if not requirements:
        return jsonify({"status": "error", "error": "requirements is required"}), 400
    products = load_products()
    constraints = RequirementsParser().parse(requirements)
    ranker = HybridRanker(products, ProductEmbeddingIndex(products), None)
    ranked = ranker.filter_compatible(ranker.rank(constraints))
    return jsonify({"status": "success", "constraints": constraints.model_dump(),
                    "recommendations": {k: [r.as_dict() for r in v] for k, v in ranked.items()}})


@api.post("/layout")
def layout():
    data = request.get_json(silent=True) or {}
    result = data.get("result")
    if not result:
        return jsonify({"status": "error", "error": "result is required"}), 400
    return jsonify({"status": "success", "layout": result.get("layout"), "svg": result.get("svg"),
                    "validation": result.get("validation")})


@api.post("/validate")
def validate():
    data = request.get_json(silent=True) or {}
    result = data.get("result")
    if not result:
        return jsonify({"status": "error", "error": "result is required"}), 400
    return jsonify({"status": "success", "validation": result.get("validation", {})})


@api.post("/replace")
def replace():
    data = request.get_json(silent=True) or {}
    category = data.get("category")
    result_payload = data.get("result")
    if not category or not result_payload:
        return jsonify({"status": "error", "error": "category and result are required"}), 400
    try:
        current = DesignResult.model_validate(result_payload)
        result = _pipeline().replace_product(current_result=current, category=category,
                                              requirements=data.get("requirements"),
                                              spatial_plan=current.spatial_plan)
        current_app.extensions["latest_result"] = result
        return _json_result(result), 200 if result.status == "success" else 422
    except Exception as exc:
        return jsonify({"status": "error", "error": str(exc)}), 500


@api.get("/result")
def result():
    latest = current_app.extensions.get("latest_result")
    if latest is None:
        return jsonify({"status": "empty"}), 404
    return _json_result(latest)
