import sys
import os

# Assuming this script is in the tests directory
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, project_root)

from app.author_api import get_author_info
import pytest

@pytest.mark.asyncio
async def test_get_author_info():
    # test to see if the api calls actually return results
    author_name = "J.K. Rowling"

    result = await get_author_info(author_name)


    assert "known_work" in result
    assert "summary" in result
    assert isinstance(result["known_work"], str)
    assert isinstance(result["summary"], str)
