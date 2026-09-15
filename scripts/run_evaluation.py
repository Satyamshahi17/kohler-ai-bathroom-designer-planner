"""Run the synthetic benchmark suite and save JSON results."""
from app.evaluation.evaluator import Evaluator
from app.pipeline.orchestrator import DesignPipeline

if __name__ == "__main__":
    report = Evaluator(DesignPipeline()).run()
    print("Scenarios:", report["scenario_count"])
    for key, value in report["summary"].items():
        print(f"{key}: {value}")
