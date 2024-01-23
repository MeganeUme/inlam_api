import asyncio
import httpx

async def fetch_openlibrary(author_name):
    """Get the authors most known work from openlibrary api"""
    search_url = f"https://openlibrary.org/search.json?author={author_name.replace(' ', '+')}"
    async with httpx.AsyncClient() as client:
        response = await client.get(search_url)
        data = response.json()

        if "docs" not in data or len(data["docs"]) == 0:
            return None
        result = data["docs"][0]
        known_work = result.get("title", "Unknown")
        return known_work

async def fetch_wikipedia(author_name):
    """Scrape the top part of wikipedia articles to get
    information of the Author with the wikipedia api"""

    base_url = "https://en.wikipedia.org/w/api.php"
    params = {
        "action": "query",
        "format": "json",
        "titles": author_name,
        "prop": "extracts",
        "exintro": True,
        "explaintext": True
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(base_url, params=params)
        data = response.json()

        page = next(iter(data["query"]["pages"].values()), None)
        if page:
            return page["extract"]
        else:
            return "Summary not found."

async def get_author_info(author_name):
    wikipedia_task = fetch_wikipedia(author_name)
    openlibrary_task = fetch_openlibrary(author_name)
    known_work, summary = await asyncio.gather(openlibrary_task, wikipedia_task)
    return {"known_work": known_work, "summary": summary}
