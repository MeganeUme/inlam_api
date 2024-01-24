import sys
import os

# Assuming this script is in the tests directory
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, project_root)

# Now you should be able to import your modules
from app.author_api import get_author_info
import pytest

@pytest.mark.asyncio
async def test_get_author_info():
    author_name = "J.K. Rowling"  # Replace with a valid author name for testing

    result = await get_author_info(author_name)

    # Add your assertions based on the expected results from the API calls
    assert "known_work" in result
    assert "summary" in result
    assert isinstance(result["known_work"], str)
    assert isinstance(result["summary"], str)
