import api from './api'

export interface AnimeSubject {
  id: number
  bgm_id: number
  name: string
  name_cn: string | null
  name_en: string | null
  summary: string | null
  subject_type: number
  platform: string | null
  total_episodes: number
  status: string | null
  air_date: string | null
  end_date: string | null
  season: string | null
  year: number | null
  rating_score: number | null
  rating_rank: number | null
  rating_total: number | null
  image: Record<string, any> | null
  tags: Array<Record<string, any>> | null
  infobox: Array<Record<string, any>> | null
  genres: Array<Record<string, any>> | null
  studios: Array<Record<string, any>> | null
  relations: Array<Record<string, any>> | null
  url: string | null
  created_at: string
  updated_at: string
}

export interface AnimeListItem {
  id: number
  bgm_id: number
  name: string
  name_cn: string | null
  subject_type: number
  year: number | null
  rating_score: number | null
  rating_rank: number | null
  image: Record<string, any> | null
  tags: Array<Record<string, any>> | null
}

export interface AnimeEpisode {
  id: number
  bgm_id: number
  name: string | null
  name_cn: string | null
  ep: number | null
  sort: number | null
  episode_type: number
  duration: string | null
  airdate: string | null
  comment: number
  desc: string | null
}

export interface AnimeCharacter {
  id: number
  bgm_id: number
  name: string
  name_cn: string | null
  role: string | null
  image: Record<string, any> | null
  summary: string | null
}

export interface AnimePerson {
  id: number
  bgm_id: number
  name: string
  name_cn: string | null
  position: string | null
  career: string[] | null
  image: Record<string, any> | null
  summary: string | null
}

export interface AnimeRelation {
  id: number
  relation: string
  type: number
  name: string
  name_cn: string | null
  image: Record<string, any> | null
}

export interface PageResult<T> {
  data: T[]
  total: number
  page: number
  page_size: number
}

export interface CalendarItem {
  weekday: string
  id: number
  name: string
  name_cn: string | null
  image: string | null
}

export async function getAnimeList(params: {
  page?: number
  page_size?: number
  subject_type?: number
  status?: string
  year?: number
  season?: string
  sort_by?: string
}) {
  const { data } = await api.get<PageResult<AnimeListItem>>('/anime', { params })
  return data
}

export async function getAnimeDetail(id: number) {
  const { data } = await api.get<AnimeSubject>(`/anime/${id}`)
  return data
}

export async function getTrendingAnime(limit = 10) {
  const { data } = await api.get<AnimeListItem[]>('/anime/trending', { params: { limit } })
  return data
}

export async function getAnimeEpisodes(animeId: number) {
  const { data } = await api.get<AnimeEpisode[]>(`/anime/${animeId}/episodes`)
  return data
}

export async function getAnimeCharacters(animeId: number) {
  const { data } = await api.get<AnimeCharacter[]>(`/anime/${animeId}/characters`)
  return data
}

export async function getAnimePersons(animeId: number) {
  const { data } = await api.get<AnimePerson[]>(`/anime/${animeId}/persons`)
  return data
}

export async function getAnimeRelations(animeId: number) {
  const { data } = await api.get<AnimeRelation[]>(`/anime/${animeId}/relations`)
  return data
}

export async function getCalendar() {
  const { data } = await api.get<CalendarItem[]>('/anime/calendar')
  return data
}

export async function searchAnime(params: {
  keyword?: string
  page?: number
  page_size?: number
  subject_type?: number
  year?: number
  season?: string
  status?: string
  sort_by?: string
  tag?: string
  min_score?: number
}) {
  const { data } = await api.get<PageResult<AnimeListItem>>('/search/subjects', { params })
  return data
}

export interface SearchSuggestion {
  id: number
  bgm_id: number
  name: string
  name_cn: string | null
  image: string | null
  type: string
  score: number | null
}

export async function getSearchSuggestions(keyword: string) {
  const { data } = await api.get<{ suggestions: SearchSuggestion[] }>('/search/suggest', {
    params: { keyword, limit: 10 },
  })
  return data
}

export interface Tag {
  name: string
  count: number
}

export async function getPopularTags(subjectType?: number) {
  const { data } = await api.get<{ tags: Tag[] }>('/search/tags', {
    params: { subject_type: subjectType, limit: 50 },
  })
  return data
}

export async function getAvailableYears(subjectType?: number) {
  const { data } = await api.get<{ years: number[] }>('/search/years', {
    params: { subject_type: subjectType },
  })
  return data
}

export async function getAvailableSeasons() {
  const { data } = await api.get<{ seasons: { value: string; label: string }[] }>('/search/seasons')
  return data
}
