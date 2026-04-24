from modules.games.providers.igdb import GameProviderError, search_games as igdb_search_games


def search_games(query):
    return igdb_search_games(query)


__all__ = ["GameProviderError", "search_games"]
