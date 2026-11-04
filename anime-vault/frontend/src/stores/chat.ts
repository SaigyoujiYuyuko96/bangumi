import { create } from 'zustand'

interface ChatState {
  sessionId: string | null
  messages: Array<{ role: string; content: string }>
  isLoading: boolean
  setSessionId: (id: string | null) => void
  addMessage: (role: string, content: string) => void
  setLoading: (loading: boolean) => void
  clearMessages: () => void
}

export const useChatStore = create<ChatState>((set) => ({
  sessionId: null,
  messages: [],
  isLoading: false,
  setSessionId: (id) => set({ sessionId: id }),
  addMessage: (role, content) =>
    set((state) => ({
      messages: [...state.messages, { role, content }],
    })),
  setLoading: (loading) => set({ isLoading: loading }),
  clearMessages: () => set({ messages: [], sessionId: null }),
}))
