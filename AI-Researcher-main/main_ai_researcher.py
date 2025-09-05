import argparse
from orchestration import run_ai_researcher

def main():
    """
    Command-line interface for the AI Researcher.
    This is a simple wrapper around the core orchestration logic.
    """
    parser = argparse.ArgumentParser(description="AI Researcher CLI")
    parser.add_argument("mode", choices=['Detailed Idea Description', 'Reference-Based Ideation', 'Paper Generation Agent'])
    parser.add_argument("--input", type=str, help="Detailed idea description.")
    parser.add_argument("--reference", type=str, help="Reference papers (comma-separated).")
    
    args = parser.parse_args()

    references = args.reference.split(',') if args.reference else []

    run_ai_researcher(args.input, references, args.mode)

if __name__ == "__main__":
    main()
