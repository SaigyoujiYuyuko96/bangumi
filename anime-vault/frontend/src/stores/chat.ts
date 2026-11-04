import { create } from 'zustand'

interface ChatState {
  sessionId: string | null
  messages: Array<{ role: string; content: string }>
  isLoading: boolean
  setSessionId: (id: string | null) => void
  addMessage: (role: string, content: string) => void
  appendAssistantChunk: (chunk: string) => void
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
  // Streaming arrives one token at a time. Doing the decision inside the updater
  // keeps it reading current messages; a component that reads `messages` from its
  // render closure sees a stale array and opens a fresh bubble on every chunk.
  appendAssistantChunk: (chunk) =>
    set((state) => {
      const last = state.messages[state.messages.length - 1]
      if (last && last.role === 'assistant') {
        const messages = state.messages.slice()
        messages[messages.length - 1] = { ...last, content: last.content + chunk }
        return { messages }
      }
      return { messages: [...state.messages, { role: 'assistant', content: chunk }] }
    }),
  setLoading: (loading) => set({ isLoading: loading }),
  clearMessages: () => set({ messages: [], sessionId: null }),
}))
