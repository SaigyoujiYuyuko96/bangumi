import { useState, useRef, useEffect } from 'react'
import { Send, Sparkles, Plus, Trash2, MessageSquare, Menu, X, Bot, User } from 'lucide-react'
import { useChatStore } from '@/stores/chat'
import { sendMessage, sendMessageStream, getSessions, deleteSession, ChatSession } from '@/services/chat'
import { useAuthStore } from '@/stores/auth'
import { Link } from 'react-router-dom'

export default function ChatPage() {
  const { messages, isLoading, addMessage, setLoading, sessionId, setSessionId, clearMessages } = useChatStore()
  const { isAuthenticated } = useAuthStore()
  const [input, setInput] = useState('')
  const [sessions, setSessions] = useState<ChatSession[]>([])
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  useEffect(() => {
    if (isAuthenticated) {
      loadSessions()
    }
  }, [isAuthenticated])

  const loadSessions = async () => {
    try {
      const data = await getSessions()
      setSessions(data.sessions || [])
    } catch (error) {
      console.error('Failed to load sessions:', error)
    }
  }

  const handleSend = async () => {
    if (!input.trim() || isLoading || !isAuthenticated) return

    const userMessage = input.trim()
    setInput('')
    addMessage('user', userMessage)
    setLoading(true)

    let assistantMessage = ''
    let currentSessionId = sessionId || ''

    try {
      await sendMessageStream(
        userMessage,
        sessionId || undefined,
        (chunk) => {
          assistantMessage += chunk
          const lastIndex = messages.length
          if (lastIndex > 0 && messages[lastIndex - 1].role === 'assistant') {
            messages[lastIndex - 1].content = assistantMessage
          } else {
            addMessage('assistant', chunk)
          }
        },
        (fullMessage, sessId) => {
          setSessionId(sessId)
          currentSessionId = sessId
          setLoading(false)
          loadSessions()
        },
        (error) => {
          addMessage('assistant', '抱歉，出了点问题，请稍后再试。')
          setLoading(false)
        }
      )
    } catch (error) {
      addMessage('assistant', '抱歉，出了点问题，请稍后再试。')
      setLoading(false)
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  const handleNewChat = () => {
    clearMessages()
    setSidebarOpen(false)
  }

  const handleDeleteSession = async (sessId: string, e: React.MouseEvent) => {
    e.stopPropagation()
    try {
      await deleteSession(sessId)
      if (sessionId === sessId) {
        clearMessages()
      }
      loadSessions()
    } catch (error) {
      console.error('Failed to delete session:', error)
    }
  }

  if (!isAuthenticated) {
    return (
      <div className="text-center py-20">
        <Sparkles className="w-16 h-16 mx-auto text-primary mb-4" />
        <h2 className="text-2xl font-bold mb-2">AI 找番助手</h2>
        <p className="text-muted-foreground mb-6">登录后即可体验智能找番功能</p>
        <Link
          to="/login"
          className="inline-flex items-center gap-2 px-6 py-3 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 transition-colors"
        >
          去登录
        </Link>
      </div>
    )
  }

  const quickQuestions = [
    '推荐几部2024年的科幻番',
    '有什么治愈系的日常番吗',
    '帮我找评分最高的战斗番',
    '有什么搞笑番推荐吗',
  ]

  return (
    <div className="flex h-[calc(100vh-8rem)] gap-4">
      {/* 移动端菜单按钮 */}
      <button
        onClick={() => setSidebarOpen(!sidebarOpen)}
        className="lg:hidden fixed top-4 left-4 z-50 p-2 bg-background border border-border rounded-lg shadow-md"
      >
        {sidebarOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
      </button>

      {/* 侧边栏 */}
      <div className={`
        fixed lg:relative inset-y-0 left-0 z-40
        w-64 bg-background border-r border-border
        transform transition-transform duration-300 ease-in-out
        ${sidebarOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'}
        flex flex-col
      `}>
        <div className="p-4 border-b border-border">
          <button
            onClick={handleNewChat}
            className="w-full flex items-center justify-center gap-2 px-4 py-2.5 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 transition-colors text-sm font-medium"
          >
            <Plus className="w-4 h-4" />
            新建对话
          </button>
        </div>

        <div className="flex-1 overflow-y-auto p-2 space-y-1">
          {sessions.length === 0 ? (
            <div className="text-center py-8 text-muted-foreground text-sm">
              <MessageSquare className="w-8 h-8 mx-auto mb-2 opacity-50" />
              暂无对话
            </div>
          ) : (
            sessions.map((session) => (
              <div
                key={session.session_id}
                className={`
                  group flex items-center gap-2 px-3 py-2 rounded-lg cursor-pointer
                  ${sessionId === session.session_id ? 'bg-secondary' : 'hover:bg-secondary/50'}
                `}
              >
                <MessageSquare className="w-4 h-4 text-muted-foreground flex-shrink-0" />
                <span className="flex-1 text-sm truncate">{session.title || '新对话'}</span>
                <button
                  onClick={(e) => handleDeleteSession(session.session_id, e)}
                  className="opacity-0 group-hover:opacity-100 p-1 hover:bg-destructive/10 rounded text-muted-foreground hover:text-destructive transition-all"
                >
                  <Trash2 className="w-3.5 h-3.5" />
                </button>
              </div>
            ))
          )}
        </div>
      </div>

      {/* 遮罩层 */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 bg-black/50 z-30 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* 主聊天区域 */}
      <div className="flex-1 flex flex-col min-w-0">
        <div className="mb-4 flex items-center gap-3">
          <h1 className="text-xl font-bold flex items-center gap-2">
            <Sparkles className="w-5 h-5 text-primary" />
            AI 找番助手
          </h1>
          <p className="text-muted-foreground text-sm hidden sm:block">
            用自然语言描述你想看的番
          </p>
        </div>

        <div className="flex-1 overflow-y-auto rounded-xl border border-border bg-card p-4 mb-4 space-y-4">
          {messages.length === 0 && (
            <div className="text-center py-12">
              <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-primary/10 flex items-center justify-center">
                <Bot className="w-8 h-8 text-primary" />
              </div>
              <h2 className="text-lg font-semibold mb-2">你好！我是 AnimeVault AI 助手</h2>
              <p className="text-muted-foreground text-sm mb-6 max-w-md mx-auto">
                我可以帮你找番、推荐番剧、管理收藏。试试下面的问题，或者直接告诉我你想看什么～
              </p>
              <div className="flex flex-wrap justify-center gap-2">
                {quickQuestions.map((q) => (
                  <button
                    key={q}
                    onClick={() => {
                      setInput(q)
                    }}
                    className="px-4 py-2 text-sm bg-secondary text-secondary-foreground rounded-full hover:bg-secondary/80 transition-colors"
                  >
                    {q}
                  </button>
                ))}
              </div>
            </div>
          )}

          {messages.map((msg, idx) => (
            <div
              key={idx}
              className={`flex gap-3 ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              {msg.role === 'assistant' && (
                <div className="w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center flex-shrink-0">
                  <Bot className="w-4 h-4 text-primary" />
                </div>
              )}
              <div
                className={`max-w-[75%] px-4 py-3 rounded-2xl ${
                  msg.role === 'user'
                    ? 'bg-primary text-primary-foreground rounded-br-sm'
                    : 'bg-secondary text-secondary-foreground rounded-bl-sm'
                }`}
              >
                <p className="text-sm whitespace-pre-wrap leading-relaxed">{msg.content}</p>
              </div>
              {msg.role === 'user' && (
                <div className="w-8 h-8 rounded-full bg-primary/20 flex items-center justify-center flex-shrink-0">
                  <User className="w-4 h-4 text-primary" />
                </div>
              )}
            </div>
          ))}

          {isLoading && (
            <div className="flex gap-3 justify-start">
              <div className="w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center flex-shrink-0">
                <Bot className="w-4 h-4 text-primary" />
              </div>
              <div className="bg-secondary text-secondary-foreground px-4 py-3 rounded-2xl rounded-bl-sm">
                <div className="flex gap-1.5">
                  <span className="w-2 h-2 bg-foreground/40 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                  <span className="w-2 h-2 bg-foreground/40 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                  <span className="w-2 h-2 bg-foreground/40 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
                </div>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        <div className="relative">
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault()
                handleSend()
              }
            }}
            placeholder="输入你想找的番，比如：推荐几部2024年的科幻番"
            className="w-full px-4 py-3 pr-12 rounded-xl border border-border bg-card focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all resize-none text-sm"
            disabled={isLoading}
            rows={1}
          />
          <button
            onClick={handleSend}
            disabled={!input.trim() || isLoading}
            className="absolute right-2 bottom-2 p-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            <Send className="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  )
}
