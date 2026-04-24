import http from '../../shared/api/client'

export type ReviewStatus = 'reviewed' | 'wishlist' | 'played' | 'completed'

export interface GameReview {
  id: number
  externalGameId: string
  gameName: string
  coverUrl: string | null
  platforms: string[]
  genres: string[]
  released: string | null
  externalRating: number | null
  userScore: number
  reviewText: string
  status: ReviewStatus
  createdAt: string
}

export interface CreateReviewPayload {
  externalGameId: string
  gameName: string
  coverUrl: string | null
  platforms: string[]
  genres: string[]
  released: string | null
  externalRating: number | null
  userScore: number
  reviewText: string
  status: ReviewStatus
}

interface ReviewsResponse {
  reviews: GameReview[]
}

interface ReviewResponse {
  review: GameReview
}

export function getMyReviews() {
  return http.get<ReviewsResponse>('/reviews/mine')
}

export function createReview(payload: CreateReviewPayload) {
  return http.post<ReviewResponse>('/reviews', payload)
}
