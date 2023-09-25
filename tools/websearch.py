from itertools import islice
from duckduckgo_search import DDGS

# for r in DDGS().news("weather seattle"):
# for r in DDGS().suggestions("weather"):
# for r in DDGS().videos("weather"):
# for r in DDGS().images("weather"):

SEARCH_COUNT = 5


def web_search(query):
    ddg_gen = DDGS().text(query)
    return list(islice(ddg_gen, SEARCH_COUNT))


def news_search(query):
    ddg_gen = DDGS().news(query)
    return list(islice(ddg_gen, SEARCH_COUNT))


def places_search(query: str, place: str):
    ddg_gen = DDGS().maps(query, place)
    return list(islice(ddg_gen, SEARCH_COUNT))


if __name__ == "__main__":
    print(places_search("restaurants", "California"))
