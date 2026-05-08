import http from '../../shared/api/client'

export interface GameSearchResult {
  externalGameId: string
  name: string
  nameZh: string | null
  coverUrl: string | null
  released: string | null
  rating: number | null
  platforms: string[]
  genres: string[]
  summary: string | null
  summaryZh: string | null
}

interface GameSearchResponse {
  results: GameSearchResult[]
}

export function searchGames(query: string) {
  return http.get<GameSearchResponse>('/games/search', {
    params: { q: query },
  })
}
