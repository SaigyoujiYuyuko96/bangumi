import { useState } from 'react'
import { Link } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { BookMarked, LogIn, Star, Play } from 'lucide-react'
import { useAuthStore } from '@/stores/auth'
import { getCollections, getCollectionStats, Collection } from '@/services/collection'

type StatusKey = 'wish' | 'doing' | 'collect' | 'on_hold' | 'dropped'

const statusLabels: Record<StatusKey, string> = {
  wish: '想看',
  doing: '在看',
  collect: '看过',
  on_hold: '搁置',
  dropped: '抛弃',
}

export default function CollectionPage() {
  const { isAuthenticated } = useAuthStore()
  const [status, setStatus] = useState<StatusKey>('wish')

  const { data: stats } = useQuery({
    queryKey: ['collection-stats'],
    queryFn: getCollectionStats,
    enabled: isAuthenticated,
  })

  const { data: collections, isLoading } = useQuery({
    queryKey: ['collections', status],
    queryFn: () => getCollections({ status, page_size: 50 }),
    enabled: isAuthenticated,
  })

  if (!isAuthenticated) {
    return (
      <div className="text-center py-20">
        <BookMarked className="w-16 h-16 mx-auto text-muted-foreground mb-4" />
        <h2 className="text-2xl font-bold mb-2">追番管理</h2>
        <p className="text-muted-foreground mb-6">登录后即可管理你的追番列表</p>
        <Link
          to="/login"
          className="inline-flex items-center gap-2 px-6 py-3 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 transition-colors"
        >
          <LogIn className="w-5 h-5" />
          去登录
        </Link>
      </div>
    )
  }

  const tabs: { key: StatusKey; label: string; count: number }[] = [
    { key: 'wish', label: '想看', count: stats?.wish || 0 },
    { key: 'doing', label: '在看', count: stats?.doing || 0 },
    { key: 'collect', label: '看过', count: stats?.collect || 0 },
    { key: 'on_hold', label: '搁置', count: stats?.on_hold || 0 },
    { key: 'dropped', label: '抛弃', count: stats?.dropped || 0 },
  ]

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">我的追番</h1>

      <div className="flex gap-2 flex-wrap">
        {tabs.map((tab) => (
          <button
            key={tab.key}
            onClick={() => setStatus(tab.key)}
            className={`px-4 py-2 rounded-lg transition-colors text-sm ${
              status === tab.key
                ? 'bg-primary text-primary-foreground'
                : 'bg-secondary text-secondary-foreground hover:bg-secondary/80'
            }`}
          >
            {tab.label} ({tab.count})
          </button>
        ))}
      </div>

      {isLoading ? (
        <div className="text-center py-20 text-muted-foreground">加载中...</div>
      ) : collections && collections.data.length > 0 ? (
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-4">
          {collections.data.map((item) => (
            <Link
              key={item.id}
              to={`/anime/${item.subject_id}`}
              className="group relative overflow-hidden rounded-xl bg-card border border-border hover:border-primary/50 transition-all hover:shadow-lg"
            >
              <div className="aspect-[3/4] bg-muted overflow-hidden">
                {item.subject?.image?.common ? (
                  <img
                    src={item.subject.image.common}
                    alt={item.subject.name_cn || item.subject.name}
                    className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                  />
                ) : (
                  <div className="w-full h-full flex items-center justify-center text-muted-foreground">
                    暂无封面
                  </div>
                )}
                {item.status === 'doing' && item.subject?.total_episodes && (
                  <div className="absolute bottom-0 left-0 right-0 bg-black/70 text-white text-xs p-1">
                    <div className="flex items-center justify-center gap-1">
                      <Play className="w-3 h-3" />
                      {item.ep_status || 0} / {item.subject.total_episodes}
                    </div>
                  </div>
                )}
              </div>
              <div className="p-3">
                <h3 className="font-medium text-sm line-clamp-2 leading-tight">
                  {item.subject?.name_cn || item.subject?.name || '未知'}
                </h3>
                <div className="flex items-center justify-between mt-2 text-xs text-muted-foreground">
                  <span>{item.subject?.year || '未知'}</span>
                  {item.rate && (
                    <span className="text-yellow-500 font-medium flex items-center gap-1">
                      <Star className="w-3 h-3 fill-current" />
                      {item.rate}
                    </span>
                  )}
                </div>
              </div>
            </Link>
          ))}
        </div>
      ) : (
        <div className="text-center py-20 text-muted-foreground">
          <BookMarked className="w-12 h-12 mx-auto mb-3 opacity-50" />
          <p>暂无{statusLabels[status]}的番剧</p>
          <p className="text-sm mt-1">去搜索页面添加你想看的番吧～</p>
        </div>
      )}
    </div>
  )
}
