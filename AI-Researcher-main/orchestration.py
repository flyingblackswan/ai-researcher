import argparse
import asyncio
import os
from dotenv import load_dotenv

# Define the project root absolute path to resolve paths consistently.
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

def get_args_research():
    parser = argparse.ArgumentParser()
    parser.add_argument("--instance_path", type=str, default="benchmark/gnn.json")
    parser.add_argument('--container_name', type=str, default='paper_eval')
    parser.add_argument("--task_level", type=str, default="task1")
    parser.add_argument("--model", type=str, default="gpt-4o-2024-08-06")
    parser.add_argument("--workplace_name", type=str, default="workplace")
    parser.add_argument("--cache_path", type=str, default="cache")
    parser.add_argument("--port", type=int, default=12345)
    parser.add_argument("--max_iter_times", type=int, default=0)
    parser.add_argument("--category", type=str, default="recommendation")
    # Use parse_known_args to avoid conflicts with other arg parsers
    args, _ = parser.parse_known_args()
    return args

def get_args_paper():
    parser = argparse.ArgumentParser()
    parser.add_argument("--research_field", type=str, default="vq")
    parser.add_argument("--instance_id", type=str, default="rotation_vq")
    args, _ = parser.parse_known_args()
    return args

def _setup_research_args(category, instance_id, task_level, container_name, workplace_name, cache_path, port, max_iter_times):
    """Helper function to set up arguments for the research agent."""
    from research_agent.constant import COMPLETION_MODEL

    args = get_args_research()

    args.instance_path = os.path.join(PROJECT_ROOT, "benchmark", "final", category, f"{instance_id}.json")
    args.task_level = task_level
    args.model = COMPLETION_MODEL
    args.container_name = container_name
    args.workplace_name = workplace_name
    args.cache_path = cache_path
    args.port = port
    args.max_iter_times = max_iter_times
    args.category = category

    return args

def _get_result_paths(args, instance_id):
    """Helper function to compute paths for research artifacts."""
    from research_agent.constant import COMPLETION_MODEL

    model_norm = COMPLETION_MODEL.replace("/", "__")
    workplace_root = os.path.join(PROJECT_ROOT, "workplace_paper", f"task_{instance_id}_{model_norm}")

    local_root = os.path.join(workplace_root, args.workplace_name)
    cache_dir = os.path.join(PROJECT_ROOT, f"cache_{instance_id}_{model_norm}")
    metachain_log = os.path.join(PROJECT_ROOT, f"log_{instance_id}")

    return {
        "workplace_name": args.workplace_name,
        "workplace_root": local_root,
        "cache_dir": cache_dir,
        "metachain_log": metachain_log,
    }

from research_agent.config import settings
import logging
from research_agent.logger_config import setup_logging

def run_ai_researcher(input_data, reference, mode):
    if not logging.getLogger().hasHandlers():
        setup_logging()

    if mode == 'Detailed Idea Description':
        from research_agent import run_infer_plan

        args = _setup_research_args(
            settings.CATEGORY,
            settings.INSTANCE_ID,
            settings.TASK_LEVEL,
            settings.CONTAINER_NAME,
            settings.WORKPLACE_NAME,
            settings.CACHE_PATH,
            settings.PORT,
            settings.MAX_ITER_TIMES
        )

        run_infer_plan.main(args, input_data, reference)

        result = {
            "summary": "Ran Detailed Idea Description pipeline",
            "mode": "detailed_idea",
            "inputs": {"input": input_data},
            "paths": _get_result_paths(args, settings.INSTANCE_ID),
            "metrics": {},
        }
        return result

    elif mode == 'Reference-Based Ideation':
        from research_agent import run_infer_idea

        args = _setup_research_args(
            settings.CATEGORY,
            settings.INSTANCE_ID,
            settings.TASK_LEVEL,
            settings.CONTAINER_NAME,
            settings.WORKPLACE_NAME,
            settings.CACHE_PATH,
            settings.PORT,
            settings.MAX_ITER_TIMES
        )

        run_infer_idea.main(args, reference)

        result = {
            "summary": "Ran Reference-Based Ideation pipeline",
            "mode": "reference_based",
            "inputs": {"references": reference},
            "paths": _get_result_paths(args, settings.INSTANCE_ID),
            "metrics": {},
        }
        return result

    elif mode == 'Paper Generation Agent':
        from paper_agent import writing

        args = get_args_paper()

        research_field = settings.CATEGORY
        args.research_field = research_field
        args.instance_id = settings.INSTANCE_ID

        asyncio.run(writing.writing(args.research_field, args.instance_id))

        result = {
            "summary": "Ran Paper Generation Agent",
            "mode": "paper_generation",
            "inputs": {"research_field": research_field, "instance_id": settings.INSTANCE_ID},
            "paths": {"workspace": PROJECT_ROOT},
            "metrics": {},
        }
        return result
    else:
        raise ValueError(f"Invalid mode: {mode}")

# Placeholder for a potential init function if needed in the future.
def init_ai_researcher():
    pass
