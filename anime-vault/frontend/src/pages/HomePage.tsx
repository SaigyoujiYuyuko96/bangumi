import { useQuery } from '@tanstack/react-query'
import { getTrendingAnime } from '@/services/anime'
import { TrendingUp, Sparkles, Search as SearchIcon } from 'lucide-react'
import { Link } from 'react-router-dom'

export default function HomePage() {
  const { data: trending = [] } = useQuery({
    queryKey: ['trending'],
    queryFn: () => getTrendingAnime(8),
  })

  return (
    <div className="space-y-12">
      <section className="text-center py-16 bg-gradient-to-b from-primary/5 to-transparent rounded-2xl -mx-4 px-4">
        <div className="max-w-2xl mx-auto">
          <h1 className="text-4xl md:text-5xl font-bold mb-4 bg-gradient-to-r from-primary to-purple-500 bg-clip-text text-transparent">
            发现你的下一部番
          </h1>
          <p className="text-lg text-muted-foreground mb-8">
            基于 AI 的动漫知识库，智能推荐、追番管理、自然语言问答
          </p>
          <div className="flex gap-3 justify-center flex-wrap">
            <Link
              to="/chat"
              className="inline-flex items-center gap-2 px-6 py-3 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 transition-colors font-medium"
            >
              <Sparkles className="w-5 h-5" />
              AI 找番助手
            </Link>
            <Link
              to="/search"
              className="inline-flex items-center gap-2 px-6 py-3 bg-secondary text-secondary-foreground rounded-lg hover:bg-secondary/80 transition-colors font-medium"
            >
              <SearchIcon className="w-5 h-5" />
              搜索动漫
            </Link>
          </div>
        </div>
      </section>

      <section>
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-2xl font-bold flex items-center gap-2">
            <TrendingUp className="w-6 h-6 text-primary" />
            热门趋势
          </h2>
          <Link to="/search" className="text-primary hover:underline text-sm">
            查看更多 →
          </Link>
        </div>
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-4">
          {trending.map((anime) => (
            <Link
              key={anime.id}
              to={`/anime/${anime.id}`}
              className="group relative overflow-hidden rounded-xl bg-card border border-border hover:border-primary/50 transition-all hover:shadow-lg"
            >
              <div className="aspect-[3/4] bg-muted overflow-hidden">
                {anime.image?.common ? (
                  <img
                    src={anime.image.common}
                    alt={anime.name_cn || anime.name}
                    className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                  />
                ) : (
                  <div className="w-full h-full flex items-center justify-center text-muted-foreground">
                    暂无封面
                  </div>
                )}
              </div>
              <div className="p-3">
                <h3 className="font-medium text-sm line-clamp-2 leading-tight">
                  {anime.name_cn || anime.name}
                </h3>
                <div className="flex items-center justify-between mt-2 text-xs text-muted-foreground">
                  <span>{anime.year || '未知'}</span>
                  {anime.rating_score && (
                    <span className="text-yellow-500 font-medium">
                      ★ {anime.rating_score.toFixed(1)}
                    </span>
                  )}
                </div>
              </div>
            </Link>
          ))}
        </div>
      </section>

      <section className="grid md:grid-cols-3 gap-6">
        {[
          {
            icon: '🤖',
            title: 'AI 智能问答',
            desc: '用自然语言找番，比如「推荐几部2024年的科幻番」',
          },
          {
            icon: '📺',
            title: '追番管理',
            desc: '记录观看进度，评分短评，自定义标签整理',
          },
          {
            icon: '🎯',
            title: '个性化推荐',
            desc: '基于你的收藏历史，智能推荐你可能喜欢的番',
          },
        ].map((feature) => (
          <div
            key={feature.title}
            className="p-6 rounded-xl border border-border bg-card hover:border-primary/30 transition-colors"
          >
            <div className="text-3xl mb-3">{feature.icon}</div>
            <h3 className="font-semibold text-lg mb-2">{feature.title}</h3>
            <p className="text-muted-foreground text-sm">{feature.desc}</p>
          </div>
        ))}
      </section>
    </div>
  )
}
