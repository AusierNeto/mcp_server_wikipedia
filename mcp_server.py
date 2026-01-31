import wikipedia

from pathlib import Path
from mcp.server.fastmcp import FastMCP


mcp = FastMCP("WikipediaSearch")

@mcp.tool()
def fetch_wikipedia_info(query:str) -> dict:
    """
    Returns title, summary and url information from 
    wikipedia for a given query.
    
    :param query: Description
    :type query: str
    :return: Description    
    :rtype: dict
    """
    try:
        search_results = wikipedia.search(query)

        if not search_results:
            return {"error": "No results found for your query"}
        
        first_result = search_results[0]

        return {"info": first_result}

        # wiki_page = first_result.page

        # return {
        #     "title": wiki_page.title,
        #     "summary": wiki_page.summary,
        #     "url": wiki_page.url
        # }
    except wikipedia.DisambiguationError as e:
        return {"error": f"Ambiguous Topic. Try one of these {', '.join(e.options[:5])}"}
    except wikipedia.PageError as e:
        return {"error": "No wikipedia page could be loaded for this query"}


@mcp.tool()
def list_wikipedia_sections(query:str) -> dict:
    """
    Returns a list of available sections in wikipedia 
    for a given query.
    
    :return: Description
    :rtype: dict
    """
    try:
        page = wikipedia.page(query)
        sections = page.sections
        return {"sections": sections}
    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
def get_section_content(topic: str, section_title: str) -> dict:
    """
    Return the content of a specific section in a Wikipedia article.
    """
    try:
        page = wikipedia.page(topic)
        content = page.section(section_title)
        if content:
            return {"content": content}
        else:
            return {"error": f"Section '{section_title}' not found in article '{topic}'."}
    except Exception as e:
        return {"error": str(e)}

@mcp.prompt()
def highlight_sections_prompt(topic: str) -> str:
    """
    Identifies the most important sections from a Wikipedia article on the given topic.
    """
    return f"""
    The user is exploring the Wikipedia article on "{topic}".

    Given the list of section titles from the article, choose the 3–5 most important or interesting sections 
    that are likely to help someone learn about the topic.

    Return a bullet list of these section titles, along with 1-line explanations of why each one matters.
    """

@mcp.resource("file://suggested_titles")
def suggested_titles() -> list[str]:
    """
    Read and return suggested Wikipedia topics from a local file.
    """
    try:
        path = Path("suggested_titles.txt")
        if not path.exists():
            return ["File not found"]
        return path.read_text(encoding="utf-8").strip().splitlines()
    except Exception as e:
        return [f"Error reading file: {str(e)}"]


if __name__ == '__main__':
    print("Starting Wikipedia search MCP Server")
    mcp.run('stdio')

