import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { useMutation } from '@tanstack/react-query'
import { login, register, getCurrentUser } from '@/services/auth'
import { useAuthStore } from '@/stores/auth'
import { LogIn, UserPlus, Sparkles } from 'lucide-react'

export default function LoginPage() {
  const [isRegister, setIsRegister] = useState(false)
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [email, setEmail] = useState('')
  const [error, setError] = useState('')
  const navigate = useNavigate()
  const { login: setAuth } = useAuthStore()

  const loginMutation = useMutation({
    mutationFn: () => login(username, password),
    onSuccess: async (data) => {
      try {
        const user = await getCurrentUser()
        setAuth(data.access_token, user)
        navigate('/')
      } catch {
        setAuth(data.access_token, {
          id: 0,
          username,
          email: null,
          avatar_url: null,
          bio: null,
          bgm_username: null,
          is_admin: false,
          created_at: new Date().toISOString(),
        })
        navigate('/')
      }
    },
    onError: (err: any) => {
      setError(err.response?.data?.detail || '登录失败，请检查用户名和密码')
    },
  })

  const registerMutation = useMutation({
    mutationFn: () => register(username, password, email || undefined),
    onSuccess: () => {
      setIsRegister(false)
      setError('')
    },
    onError: (err: any) => {
      setError(err.response?.data?.detail || '注册失败')
    },
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    if (isRegister) {
      registerMutation.mutate()
    } else {
      loginMutation.mutate()
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-primary/5 via-background to-purple-500/5 p-4">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <Link to="/" className="inline-flex items-center gap-2 font-bold text-2xl">
            <Sparkles className="text-primary" />
            <span>AnimeVault</span>
          </Link>
          <p className="text-muted-foreground mt-2">
            {isRegister ? '创建一个新账号' : '登录你的账号'}
          </p>
        </div>

        <div className="bg-card border border-border rounded-2xl p-6 shadow-sm">
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium mb-1.5">用户名</label>
              <input
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                className="w-full px-4 py-2.5 rounded-lg border border-border bg-background focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all"
                placeholder="请输入用户名"
                required
                minLength={3}
              />
            </div>

            {isRegister && (
              <div>
                <label className="block text-sm font-medium mb-1.5">邮箱（可选）</label>
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="w-full px-4 py-2.5 rounded-lg border border-border bg-background focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all"
                  placeholder="请输入邮箱"
                />
              </div>
            )}

            <div>
              <label className="block text-sm font-medium mb-1.5">密码</label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full px-4 py-2.5 rounded-lg border border-border bg-background focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all"
                placeholder="请输入密码"
                required
                minLength={6}
              />
            </div>

            {error && (
              <div className="text-sm text-red-500 bg-red-50 dark:bg-red-950/30 px-3 py-2 rounded-lg">
                {error}
              </div>
            )}

            <button
              type="submit"
              disabled={loginMutation.isPending || registerMutation.isPending}
              className="w-full py-2.5 bg-primary text-primary-foreground rounded-lg font-medium hover:bg-primary/90 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
            >
              {isRegister ? (
                <>
                  <UserPlus className="w-4 h-4" />
                  {registerMutation.isPending ? '注册中...' : '注册'}
                </>
              ) : (
                <>
                  <LogIn className="w-4 h-4" />
                  {loginMutation.isPending ? '登录中...' : '登录'}
                </>
              )}
            </button>
          </form>

          <div className="mt-6 text-center text-sm">
            <span className="text-muted-foreground">
              {isRegister ? '已有账号？' : '还没有账号？'}
            </span>
            <button
              onClick={() => {
                setIsRegister(!isRegister)
                setError('')
              }}
              className="text-primary hover:underline ml-1"
            >
              {isRegister ? '去登录' : '去注册'}
            </button>
          </div>
        </div>

        <p className="text-center text-xs text-muted-foreground mt-6">
          登录即表示同意 AnimeVault 的服务条款和隐私政策
        </p>
      </div>
    </div>
  )
}
