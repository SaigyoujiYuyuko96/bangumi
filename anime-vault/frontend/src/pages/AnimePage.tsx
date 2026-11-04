import { useState } from 'react'
import { useParams } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import {
  getAnimeDetail,
  getAnimeEpisodes,
  getAnimeCharacters,
  getAnimePersons,
  getAnimeRelations,
} from '@/services/anime'
import { Star, Calendar, Tv, Info, Users, Play, Link2 } from 'lucide-react'

type TabType = 'info' | 'episodes' | 'characters' | 'persons' | 'relations'

export default function AnimePage() {
  const { id } = useParams<{ id: string }>()
  const [activeTab, setActiveTab] = useState<TabType>('info')

  const { data: anime, isLoading } = useQuery({
    queryKey: ['anime', id],
    queryFn: () => getAnimeDetail(Number(id)),
    enabled: !!id,
  })

  const { data: episodes } = useQuery({
    queryKey: ['anime-episodes', id],
    queryFn: () => getAnimeEpisodes(Number(id)),
    enabled: !!id && activeTab === 'episodes',
  })

  const { data: characters } = useQuery({
    queryKey: ['anime-characters', id],
    queryFn: () => getAnimeCharacters(Number(id)),
    enabled: !!id && activeTab === 'characters',
  })

  const { data: persons } = useQuery({
    queryKey: ['anime-persons', id],
    queryFn: () => getAnimePersons(Number(id)),
    enabled: !!id && activeTab === 'persons',
  })

  const { data: relations } = useQuery({
    queryKey: ['anime-relations', id],
    queryFn: () => getAnimeRelations(Number(id)),
    enabled: !!id && activeTab === 'relations',
  })

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-20">
        <div className="text-muted-foreground">加载中...</div>
      </div>
    )
  }

  if (!anime) {
    return <div className="text-center py-20 text-muted-foreground">未找到该动漫</div>
  }

  const tabs: { key: TabType; label: string; count?: number }[] = [
    { key: 'info', label: '详情' },
    { key: 'episodes', label: '剧集', count: anime.total_episodes },
    { key: 'characters', label: '角色' },
    { key: 'persons', label: '制作人员' },
    { key: 'relations', label: '关联' },
  ]

  const roleMap: Record<string, string> = {
    protagonist: '主角',
    deuteragonist: '配角',
    supporting: '配角',
    appears: '登场角色',
    cameo: '客串',
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row gap-6">
        <div className="w-full md:w-56 flex-shrink-0">
          <div className="aspect-[3/4] rounded-xl overflow-hidden bg-muted border border-border sticky top-4">
            {anime.image?.large ? (
              <img src={anime.image.large} alt={anime.name_cn || anime.name} className="w-full h-full object-cover" />
            ) : (
              <div className="w-full h-full flex items-center justify-center text-muted-foreground">
                暂无封面
              </div>
            )}
          </div>
        </div>

        <div className="flex-1 space-y-4">
          <div>
            <h1 className="text-2xl md:text-3xl font-bold">{anime.name_cn || anime.name}</h1>
            {anime.name !== anime.name_cn && (
              <p className="text-muted-foreground mt-1">{anime.name}</p>
            )}
          </div>

          <div className="flex flex-wrap gap-4 text-sm">
            {anime.rating_score && (
              <div className="flex items-center gap-1 text-yellow-500">
                <Star className="w-4 h-4 fill-current" />
                <span className="font-semibold">{(anime.rating_score / 10).toFixed(1)}</span>
                <span className="text-muted-foreground">({anime.rating_total || 0}人评分)</span>
              </div>
            )}
            {anime.rating_rank && (
              <div className="flex items-center gap-1">
                <span className="text-muted-foreground">排名:</span>
                <span className="font-medium">#{anime.rating_rank}</span>
              </div>
            )}
            {anime.year && (
              <div className="flex items-center gap-1">
                <Calendar className="w-4 h-4 text-muted-foreground" />
                <span>{anime.year}年</span>
              </div>
            )}
            {anime.total_episodes > 0 && (
              <div className="flex items-center gap-1">
                <Tv className="w-4 h-4 text-muted-foreground" />
                <span>共 {anime.total_episodes} 集</span>
              </div>
            )}
          </div>

          {anime.tags && anime.tags.length > 0 && (
            <div className="flex flex-wrap gap-2">
              {anime.tags.slice(0, 10).map((tag: any) => (
                <span
                  key={tag.name}
                  className="px-3 py-1 bg-secondary text-secondary-foreground rounded-full text-xs"
                >
                  {tag.name}
                </span>
              ))}
            </div>
          )}

          <div className="flex gap-3 pt-2">
            <button className="px-4 py-2 rounded-lg bg-primary text-primary-foreground font-medium hover:bg-primary/90 transition-colors text-sm">
              想看
            </button>
            <button className="px-4 py-2 rounded-lg bg-secondary text-secondary-foreground font-medium hover:bg-secondary/80 transition-colors text-sm">
              在看
            </button>
            <button className="px-4 py-2 rounded-lg border border-border font-medium hover:bg-secondary transition-colors text-sm">
              看过
            </button>
          </div>
        </div>
      </div>

      <div className="border-b border-border">
        <nav className="flex gap-1 -mb-px overflow-x-auto">
          {tabs.map((tab) => (
            <button
              key={tab.key}
              onClick={() => setActiveTab(tab.key)}
              className={`px-4 py-3 font-medium text-sm whitespace-nowrap border-b-2 transition-colors ${
                activeTab === tab.key
                  ? 'border-primary text-primary'
                  : 'border-transparent text-muted-foreground hover:text-foreground hover:border-border'
              }`}
            >
              {tab.label}
              {tab.count !== undefined && tab.count > 0 && (
                <span className="ml-1 text-xs text-muted-foreground">({tab.count})</span>
              )}
            </button>
          ))}
        </nav>
      </div>

      <div className="min-h-[300px]">
        {activeTab === 'info' && (
          <div className="space-y-6">
            {anime.summary && (
              <div>
                <h3 className="font-semibold mb-2 flex items-center gap-2">
                  <Info className="w-4 h-4" />
                  简介
                </h3>
                <p className="text-muted-foreground whitespace-pre-wrap text-sm leading-relaxed">
                  {anime.summary}
                </p>
              </div>
            )}

            {anime.infobox && anime.infobox.length > 0 && (
              <div>
                <h3 className="font-semibold mb-3">基本信息</h3>
                <div className="bg-card rounded-lg border border-border overflow-hidden">
                  <table className="w-full text-sm">
                    <tbody>
                      {anime.infobox.map((item: any, index: number) => (
                        <tr key={index} className={index !== 0 ? 'border-t border-border' : ''}>
                          <td className="px-4 py-2 text-muted-foreground w-24">{item.key}</td>
                          <td className="px-4 py-2" dangerouslySetInnerHTML={{ __html: item.value }} />
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}

            {anime.genres && anime.genres.length > 0 && (
              <div>
                <h3 className="font-semibold mb-2">题材分类</h3>
                <div className="flex flex-wrap gap-2">
                  {anime.genres.map((genre: any) => (
                    <span key={genre.id} className="px-3 py-1 bg-secondary rounded-full text-xs">
                      {genre.name}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {anime.studios && anime.studios.length > 0 && (
              <div>
                <h3 className="font-semibold mb-2">制作公司</h3>
                <div className="flex flex-wrap gap-2">
                  {anime.studios.map((studio: any) => (
                    <span key={studio.id} className="px-3 py-1 bg-secondary rounded-full text-xs">
                      {studio.name}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {activeTab === 'episodes' && (
          <div>
            {episodes && episodes.length > 0 ? (
              <div className="grid gap-2">
                {episodes.map((ep) => (
                  <div key={ep.id} className="flex items-center gap-4 p-3 bg-card rounded-lg border border-border hover:border-primary/30 transition-colors">
                    <div className="w-16 text-center text-sm text-muted-foreground">
                      {ep.ep !== null ? `第 ${ep.ep} 话` : ep.sort !== null ? `#${ep.sort}` : '-'}
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="font-medium text-sm truncate">{ep.name_cn || ep.name || '暂无标题'}</div>
                      {ep.name && ep.name !== ep.name_cn && (
                        <div className="text-xs text-muted-foreground truncate">{ep.name}</div>
                      )}
                    </div>
                    {ep.duration && (
                      <div className="text-xs text-muted-foreground">{ep.duration}</div>
                    )}
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-12 text-muted-foreground">暂无剧集信息</div>
            )}
          </div>
        )}

        {activeTab === 'characters' && (
          <div>
            {characters && characters.length > 0 ? (
              <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-4">
                {characters.map((char) => (
                  <div key={char.id} className="bg-card rounded-lg border border-border overflow-hidden">
                    <div className="aspect-[3/4] bg-muted">
                      {char.image?.medium ? (
                        <img src={char.image.medium} alt={char.name} className="w-full h-full object-cover" />
                      ) : (
                        <div className="w-full h-full flex items-center justify-center text-muted-foreground text-sm">
                          暂无图片
                        </div>
                      )}
                    </div>
                    <div className="p-3">
                      <div className="font-medium text-sm truncate">{char.name_cn || char.name}</div>
                      {char.name !== char.name_cn && (
                        <div className="text-xs text-muted-foreground truncate">{char.name}</div>
                      )}
                      {char.role && (
                        <div className="text-xs text-primary mt-1">{roleMap[char.role] || char.role}</div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-12 text-muted-foreground">暂无角色信息</div>
            )}
          </div>
        )}

        {activeTab === 'persons' && (
          <div>
            {persons && persons.length > 0 ? (
              <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-4">
                {persons.map((person) => (
                  <div key={person.id} className="bg-card rounded-lg border border-border overflow-hidden">
                    <div className="aspect-square bg-muted">
                      {person.image?.medium ? (
                        <img src={person.image.medium} alt={person.name} className="w-full h-full object-cover" />
                      ) : (
                        <div className="w-full h-full flex items-center justify-center text-muted-foreground text-sm">
                          暂无图片
                        </div>
                      )}
                    </div>
                    <div className="p-3">
                      <div className="font-medium text-sm truncate">{person.name_cn || person.name}</div>
                      {person.name !== person.name_cn && (
                        <div className="text-xs text-muted-foreground truncate">{person.name}</div>
                      )}
                      {person.position && (
                        <div className="text-xs text-primary mt-1">{person.position}</div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-12 text-muted-foreground">暂无制作人员信息</div>
            )}
          </div>
        )}

        {activeTab === 'relations' && (
          <div>
            {relations && relations.length > 0 ? (
              <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-4">
                {relations.map((rel) => (
                  <div key={`${rel.type}-${rel.id}`} className="bg-card rounded-lg border border-border overflow-hidden">
                    <div className="aspect-[3/4] bg-muted">
                      {rel.image?.common ? (
                        <img src={rel.image.common} alt={rel.name} className="w-full h-full object-cover" />
                      ) : (
                        <div className="w-full h-full flex items-center justify-center text-muted-foreground text-sm">
                          暂无图片
                        </div>
                      )}
                    </div>
                    <div className="p-3">
                      <div className="font-medium text-sm truncate">{rel.name_cn || rel.name}</div>
                      {rel.name !== rel.name_cn && (
                        <div className="text-xs text-muted-foreground truncate">{rel.name}</div>
                      )}
                      {rel.relation && (
                        <div className="text-xs text-primary mt-1">{rel.relation}</div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-12 text-muted-foreground">暂无关联条目</div>
            )}
          </div>
        )}
      </div>
    </div>
  )
}
