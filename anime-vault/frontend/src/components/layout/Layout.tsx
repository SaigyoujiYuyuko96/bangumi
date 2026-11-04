import { Link, Outlet, useLocation, useNavigate } from 'react-router-dom'
import { Home, Search, BookMarked, MessageSquare, LogOut, User } from 'lucide-react'
import { useAuthStore } from '@/stores/auth'

export default function Layout() {
  const location = useLocation()
  const navigate = useNavigate()
  const { isAuthenticated, user, logout } = useAuthStore()

  const navItems = [
    { path: '/', label: '首页', icon: Home },
    { path: '/search', label: '搜索', icon: Search },
    { path: '/collection', label: '追番', icon: BookMarked },
    { path: '/chat', label: 'AI 助手', icon: MessageSquare },
  ]

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  return (
    <div className="min-h-screen bg-background">
      <header className="sticky top-0 z-50 border-b border-border bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
        <div className="container flex h-16 items-center justify-between">
          <Link to="/" className="flex items-center gap-2 font-bold text-xl">
            <span className="text-primary">🎬</span>
            <span>AnimeVault</span>
          </Link>

          <nav className="flex items-center gap-1">
            {navItems.map((item) => {
              const Icon = item.icon
              const isActive = location.pathname === item.path
              return (
                <Link
                  key={item.path}
                  to={item.path}
                  className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-colors ${
                    isActive
                      ? 'bg-primary/10 text-primary font-medium'
                      : 'text-muted-foreground hover:text-foreground hover:bg-secondary'
                  }`}
                >
                  <Icon className="w-4 h-4" />
                  <span className="hidden sm:inline">{item.label}</span>
                </Link>
              )
            })}
          </nav>

          <div className="flex items-center gap-2">
            {isAuthenticated ? (
              <div className="flex items-center gap-3">
                <span className="text-sm text-muted-foreground hidden sm:inline">
                  {user?.username}
                </span>
                <button
                  onClick={handleLogout}
                  className="p-2 rounded-lg hover:bg-secondary text-muted-foreground hover:text-foreground"
                  title="退出登录"
                >
                  <LogOut className="w-5 h-5" />
                </button>
              </div>
            ) : (
              <Link
                to="/login"
                className="flex items-center gap-2 px-4 py-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 transition-colors"
              >
                <User className="w-4 h-4" />
                <span className="hidden sm:inline">登录</span>
              </Link>
            )}
          </div>
        </div>
      </header>

      <main className="container py-6">
        <Outlet />
      </main>

      <footer className="border-t border-border py-6 mt-12">
        <div className="container text-center text-sm text-muted-foreground">
          <p>AnimeVault © 2024 — 动漫知识库 Agent 平台</p>
          <p className="mt-1">数据来源：Bangumi.tv</p>
        </div>
      </footer>
    </div>
  )
}
