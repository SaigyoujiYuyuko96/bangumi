import api from './api'

export interface User {
  id: number
  username: string
  email: string | null
  avatar_url: string | null
  bio: string | null
  bgm_username: string | null
  is_admin: boolean
  created_at: string
}

export interface Token {
  access_token: string
  token_type: string
}

export async function login(username: string, password: string) {
  const formData = new FormData()
  formData.append('username', username)
  formData.append('password', password)
  const { data } = await api.post<Token>('/auth/login', formData)
  return data
}

export async function register(username: string, password: string, email?: string) {
  const { data } = await api.post<User>('/auth/register', { username, password, email })
  return data
}

export async function getCurrentUser() {
  const { data } = await api.get<User>('/auth/me')
  return data
}
