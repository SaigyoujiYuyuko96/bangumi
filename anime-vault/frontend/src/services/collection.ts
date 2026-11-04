import api from './api'

export interface Collection {
  id: number
  user_id: number
  subject_id: number
  status: 'wish' | 'doing' | 'collect' | 'on_hold' | 'dropped'
  rate: number | null
  ep_status: number
  vol_status: number
  comment: string | null
  private: boolean
  created_at: string
  updated_at: string
  subject?: {
    id: number
    bgm_id: number
    name: string
    name_cn: string | null
    image: Record<string, any> | null
    total_episodes: number
    year: number | null
    rating_score: number | null
  }
}

export interface CollectionCreate {
  status: 'wish' | 'doing' | 'collect' | 'on_hold' | 'dropped'
  rate?: number | null
  ep_status?: number
  vol_status?: number
  comment?: string | null
  private?: boolean
}

export interface PageResult<T> {
  data: T[]
  total: number
  page: number
  page_size: number
}

export interface CollectionStats {
  wish: number
  doing: number
  collect: number
  on_hold: number
  dropped: number
}

export async function getCollections(params?: {
  page?: number
  page_size?: number
  status?: string
}) {
  const { data } = await api.get<PageResult<Collection>>('/collections', { params })
  return data
}

export async function getCollectionStats() {
  const { data } = await api.get<CollectionStats>('/collections/stats')
  return data
}

export async function getCollectionBySubject(subjectId: number) {
  const { data } = await api.get<Collection>(`/collections/${subjectId}`)
  return data
}

export async function upsertCollection(subjectId: number, collection: CollectionCreate) {
  const { data } = await api.put<Collection>(`/collections/${subjectId}`, collection)
  return data
}

export async function updateProgress(subjectId: number, progress: { ep_status?: number; vol_status?: number }) {
  const { data } = await api.patch<Collection>(`/collections/${subjectId}/progress`, progress)
  return data
}

export async function deleteCollection(subjectId: number) {
  await api.delete(`/collections/${subjectId}`)
}
