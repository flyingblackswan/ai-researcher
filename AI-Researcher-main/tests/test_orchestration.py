import unittest
from unittest.mock import patch
import os

# Set dummy environment variables for testing
os.environ["CATEGORY"] = "test_cat"
os.environ["INSTANCE_ID"] = "test_id"
os.environ["TASK_LEVEL"] = "test_level"
os.environ["CONTAINER_NAME"] = "test_container"
os.environ["WORKPLACE_NAME"] = "test_workplace"
os.environ["CACHE_PATH"] = "test_cache"
os.environ["PORT"] = "12345"
os.environ["MAX_ITER_TIMES"] = "1"
os.environ["COMPLETION_MODEL"] = "test_model"

from orchestration import run_ai_researcher

class TestOrchestration(unittest.TestCase):

    @patch('research_agent.run_infer_plan.main')
    def test_run_ai_researcher_detailed_idea(self, mock_main):
        """Test the 'Detailed Idea Description' mode."""
        run_ai_researcher("test input", [], "Detailed Idea Description")
        mock_main.assert_called_once()

    @patch('research_agent.run_infer_idea.main')
    def test_run_ai_researcher_reference_based(self, mock_main):
        """Test the 'Reference-Based Ideation' mode."""
        run_ai_researcher(None, ["ref1", "ref2"], "Reference-Based Ideation")
        mock_main.assert_called_once()

    @patch('paper_agent.writing.writing')
    @patch('asyncio.run')
    def test_run_ai_researcher_paper_generation(self, mock_asyncio_run, mock_writing):
        """Test the 'Paper Generation Agent' mode."""
        async def dummy_coro(*args, **kwargs):
            pass
        mock_writing.return_value = dummy_coro()

        run_ai_researcher(None, [], "Paper Generation Agent")

        mock_writing.assert_called_once()
        mock_asyncio_run.assert_called_once()

    def test_run_ai_researcher_invalid_mode(self):
        """Test that an invalid mode raises a ValueError."""
        with self.assertRaises(ValueError):
            run_ai_researcher(None, [], "Invalid Mode")

if __name__ == '__main__':
    unittest.main()
