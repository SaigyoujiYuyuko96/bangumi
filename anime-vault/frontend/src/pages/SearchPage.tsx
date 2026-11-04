import { useState, useRef, useEffect } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Search as SearchIcon, Filter, ChevronDown, X, Star, Calendar, TrendingUp, Clock, Tag as TagIcon } from 'lucide-react'
import { searchAnime, getSearchSuggestions, getPopularTags, getAvailableYears } from '@/services/anime'
import { Link, useNavigate } from 'react-router-dom'

export default function SearchPage() {
  const navigate = useNavigate()
  const [keyword, setKeyword] = useState('')
  const [debouncedKeyword, setDebouncedKeyword] = useState('')
  const [subjectType, setSubjectType] = useState<number | undefined>(2)
  const [year, setYear] = useState<number | undefined>()
  const [sortBy, setSortBy] = useState<string>('rank')
  const [selectedTags, setSelectedTags] = useState<string[]>([])
  const [showSuggestions, setShowSuggestions] = useState(false)
  const [showFilters, setShowFilters] = useState(false)
  const [page, setPage] = useState(1)
  const searchRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedKeyword(keyword)
    }, 300)
    return () => clearTimeout(timer)
  }, [keyword])

  useEffect(() => {
    setPage(1)
  }, [keyword, subjectType, year, sortBy, selectedTags])

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (searchRef.current && !searchRef.current.contains(event.target as Node)) {
        setShowSuggestions(false)
      }
    }
    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  const { data, isLoading } = useQuery({
    queryKey: ['search', debouncedKeyword, page, subjectType, year, sortBy, selectedTags],
    queryFn: () => searchAnime({
      keyword: debouncedKeyword,
      page,
      page_size: 24,
      subject_type: subjectType,
      year,
      sort_by: sortBy,
      tag: selectedTags[0] || undefined,
    }),
  })

  const { data: suggestions } = useQuery({
    queryKey: ['search-suggest', debouncedKeyword],
    queryFn: () => getSearchSuggestions(debouncedKeyword),
    enabled: debouncedKeyword.length >= 1 && showSuggestions,
  })

  const { data: tagsData } = useQuery({
    queryKey: ['popular-tags', subjectType],
    queryFn: () => getPopularTags(subjectType),
  })

  const { data: yearsData } = useQuery({
    queryKey: ['available-years', subjectType],
    queryFn: () => getAvailableYears(subjectType),
  })

  const handleSearch = (searchKeyword: string) => {
    setKeyword(searchKeyword)
    setShowSuggestions(false)
  }

  const handleTagClick = (tagName: string) => {
    setSelectedTags((prev) => {
      if (prev.includes(tagName)) {
        return prev.filter((t) => t !== tagName)
      }
      return [tagName]
    })
  }

  const clearFilters = () => {
    setSubjectType(2)
    setYear(undefined)
    setSelectedTags([])
    setSortBy('rank')
  }

  const sortOptions = [
    { value: 'rank', label: '排名', icon: Star },
    { value: 'rating', label: '评分', icon: Star },
    { value: 'popular', label: '人气', icon: TrendingUp },
    { value: 'new', label: '最新', icon: Clock },
  ]

  const typeOptions = [
    { label: '全部', value: undefined },
    { label: '动画', value: 2 },
    { label: '漫画', value: 1 },
    { label: '游戏', value: 4 },
  ]

  const totalPages = Math.ceil((data?.total || 0) / 24)

  return (
    <div className="space-y-6">
      {/* 搜索框 */}
      <div className="relative" ref={searchRef}>
        <SearchIcon className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-muted-foreground" />
        <input
          type="text"
          value={keyword}
          onChange={(e) => {
            setKeyword(e.target.value)
            setShowSuggestions(true)
          }}
          onFocus={() => setShowSuggestions(true)}
          placeholder="搜索动漫、角色、制作人员..."
          className="w-full pl-12 pr-4 py-4 rounded-xl border border-border bg-card text-lg focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all"
        />
        {keyword && (
          <button
            onClick={() => setKeyword('')}
            className="absolute right-4 top-1/2 -translate-y-1/2 p-1 hover:bg-secondary rounded-full transition-colors"
          >
            <X className="w-4 h-4 text-muted-foreground" />
          </button>
        )}

        {/* 搜索建议下拉 */}
        {showSuggestions && suggestions?.suggestions && suggestions.suggestions.length > 0 && (
          <div className="absolute top-full left-0 right-0 mt-2 bg-card border border-border rounded-xl shadow-lg overflow-hidden z-50 max-h-80 overflow-y-auto">
            {suggestions.suggestions.map((item) => (
              <button
                key={item.id}
                onClick={() => navigate(`/anime/${item.id}`)}
                className="w-full flex items-center gap-3 px-4 py-3 hover:bg-secondary transition-colors text-left"
              >
                <div className="w-10 h-14 rounded bg-muted overflow-hidden flex-shrink-0">
                  {item.image ? (
                    <img src={item.image} alt={item.name_cn || item.name} className="w-full h-full object-cover" />
                  ) : (
                    <div className="w-full h-full flex items-center justify-center text-xs text-muted-foreground">
                      无
                    </div>
                  )}
                </div>
                <div className="flex-1 min-w-0">
                  <div className="font-medium text-sm truncate">{item.name_cn || item.name}</div>
                  {item.name !== item.name_cn && (
                    <div className="text-xs text-muted-foreground truncate">{item.name}</div>
                  )}
                </div>
                {item.score && (
                  <div className="text-yellow-500 text-sm font-medium flex items-center gap-1">
                    <Star className="w-3 h-3 fill-current" />
                    {(item.score / 10).toFixed(1)}
                  </div>
                )}
              </button>
            ))}
          </div>
        )}
      </div>

      {/* 筛选栏 */}
      <div className="space-y-4">
        {/* 主筛选 */}
        <div className="flex flex-wrap items-center gap-3">
          <div className="flex items-center gap-2">
            <Filter className="w-4 h-4 text-muted-foreground" />
            <span className="text-sm font-medium">筛选</span>
          </div>

          {/* 类型 */}
          <div className="flex gap-1 flex-wrap">
            {typeOptions.map((item) => (
              <button
                key={item.label}
                onClick={() => {
                  setSubjectType(item.value)
                  setPage(1)
                }}
                className={`px-3 py-1.5 rounded-lg text-sm transition-colors ${
                  subjectType === item.value
                    ? 'bg-primary text-primary-foreground'
                    : 'bg-secondary text-secondary-foreground hover:bg-secondary/80'
                }`}
              >
                {item.label}
              </button>
            ))}
          </div>

          {/* 排序 */}
          <div className="flex gap-1 ml-auto">
            {sortOptions.map((option) => {
              const Icon = option.icon
              return (
                <button
                  key={option.value}
                  onClick={() => {
                    setSortBy(option.value)
                    setPage(1)
                  }}
                  className={`flex items-center gap-1 px-3 py-1.5 rounded-lg text-sm transition-colors ${
                    sortBy === option.value
                      ? 'bg-primary text-primary-foreground'
                      : 'bg-secondary text-secondary-foreground hover:bg-secondary/80'
                  }`}
                >
                  <Icon className="w-3.5 h-3.5" />
                  {option.label}
                </button>
              )
            })}
          </div>

          {/* 高级筛选按钮 */}
          <button
            onClick={() => setShowFilters(!showFilters)}
            className="flex items-center gap-1 px-3 py-1.5 rounded-lg text-sm bg-secondary text-secondary-foreground hover:bg-secondary/80 transition-colors"
          >
            更多筛选
            <ChevronDown className={`w-4 h-4 transition-transform ${showFilters ? 'rotate-180' : ''}`} />
          </button>
        </div>

        {/* 高级筛选面板 */}
        {showFilters && (
          <div className="bg-card border border-border rounded-xl p-4 space-y-4">
            {/* 年份 */}
            <div>
              <div className="text-sm font-medium mb-2 flex items-center gap-2">
                <Calendar className="w-4 h-4 text-muted-foreground" />
                年份
              </div>
              <div className="flex flex-wrap gap-2">
                <button
                  onClick={() => setYear(undefined)}
                  className={`px-3 py-1.5 rounded-lg text-sm transition-colors ${
                    year === undefined
                      ? 'bg-primary text-primary-foreground'
                      : 'bg-secondary text-secondary-foreground hover:bg-secondary/80'
                  }`}
                >
                  全部
                </button>
                {yearsData?.years.slice(0, 10).map((y) => (
                  <button
                    key={y}
                    onClick={() => {
                      setYear(y === year ? undefined : y)
                      setPage(1)
                    }}
                    className={`px-3 py-1.5 rounded-lg text-sm transition-colors ${
                      year === y
                        ? 'bg-primary text-primary-foreground'
                        : 'bg-secondary text-secondary-foreground hover:bg-secondary/80'
                    }`}
                  >
                    {y}
                  </button>
                ))}
              </div>
            </div>

            {/* 标签 */}
            {tagsData?.tags && tagsData.tags.length > 0 && (
              <div>
                <div className="text-sm font-medium mb-2 flex items-center gap-2">
                  <TagIcon className="w-4 h-4 text-muted-foreground" />
                  热门标签
                </div>
                <div className="flex flex-wrap gap-2">
                  {tagsData.tags.slice(0, 20).map((tag) => (
                    <button
                      key={tag.name}
                      onClick={() => handleTagClick(tag.name)}
                      className={`px-3 py-1 rounded-full text-xs transition-colors ${
                        selectedTags.includes(tag.name)
                          ? 'bg-primary text-primary-foreground'
                          : 'bg-secondary text-secondary-foreground hover:bg-secondary/80'
                      }`}
                    >
                      {tag.name}
                      <span className="opacity-70 ml-1">({tag.count})</span>
                    </button>
                  ))}
                </div>
              </div>
            )}

            {/* 清除筛选 */}
            {(year || selectedTags.length > 0 || sortBy !== 'rank') && (
              <div className="flex justify-end">
                <button
                  onClick={clearFilters}
                  className="text-sm text-muted-foreground hover:text-foreground transition-colors flex items-center gap-1"
                >
                  <X className="w-3 h-3" />
                  清除筛选条件
                </button>
              </div>
            )}
          </div>
        )}

        {/* 已选标签 */}
        {selectedTags.length > 0 && (
          <div className="flex flex-wrap items-center gap-2">
            <span className="text-sm text-muted-foreground">已选标签:</span>
            {selectedTags.map((tag) => (
              <button
                key={tag}
                onClick={() => handleTagClick(tag)}
                className="flex items-center gap-1 px-2.5 py-1 bg-primary text-primary-foreground rounded-full text-xs"
              >
                {tag}
                <X className="w-3 h-3" />
              </button>
            ))}
          </div>
        )}
      </div>

      {/* 结果统计 */}
      <div className="text-sm text-muted-foreground">
        {debouncedKeyword ? (
          <>找到 <span className="text-foreground font-medium">{data?.total || 0}</span> 个关于 "{debouncedKeyword}" 的结果</>
        ) : (
          <>共 <span className="text-foreground font-medium">{data?.total || 0}</span> 部作品</>
        )}
      </div>

      {/* 搜索结果 */}
      {isLoading ? (
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-4">
          {Array.from({ length: 12 }).map((_, i) => (
            <div key={i} className="animate-pulse">
              <div className="aspect-[3/4] bg-muted rounded-xl" />
              <div className="mt-2 space-y-1">
                <div className="h-3 bg-muted rounded w-3/4" />
                <div className="h-3 bg-muted rounded w-1/2" />
              </div>
            </div>
          ))}
        </div>
      ) : data && data.data.length > 0 ? (
        <>
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-4">
            {data.data.map((anime) => (
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
                    <div className="w-full h-full flex items-center justify-center text-muted-foreground text-sm">
                      暂无封面
                    </div>
                  )}
                  {anime.rating_rank && (
                    <div className="absolute top-2 left-2 bg-black/70 text-white text-xs px-2 py-0.5 rounded">
                      #{anime.rating_rank}
                    </div>
                  )}
                </div>
                <div className="p-3">
                  <h3 className="font-medium text-sm line-clamp-2 leading-tight min-h-[2.5rem]">
                    {anime.name_cn || anime.name}
                  </h3>
                  <div className="flex items-center justify-between mt-2 text-xs">
                    <span className="text-muted-foreground">{anime.year || '未知'}</span>
                    {anime.rating_score && (
                      <span className="text-yellow-500 font-medium flex items-center gap-0.5">
                        <Star className="w-3 h-3 fill-current" />
                        {(anime.rating_score / 10).toFixed(1)}
                      </span>
                    )}
                  </div>
                </div>
              </Link>
            ))}
          </div>

          {/* 分页 */}
          {totalPages > 1 && (
            <div className="flex justify-center items-center gap-1 pt-4">
              <button
                onClick={() => setPage((p) => Math.max(1, p - 1))}
                disabled={page <= 1}
                className="px-3 py-1.5 rounded-lg border border-border hover:bg-secondary disabled:opacity-50 disabled:cursor-not-allowed text-sm"
              >
                上一页
              </button>

              {Array.from({ length: Math.min(5, totalPages) }, (_, i) => {
                let pageNum
                if (totalPages <= 5) {
                  pageNum = i + 1
                } else if (page <= 3) {
                  pageNum = i + 1
                } else if (page >= totalPages - 2) {
                  pageNum = totalPages - 4 + i
                } else {
                  pageNum = page - 2 + i
                }
                return (
                  <button
                    key={pageNum}
                    onClick={() => setPage(pageNum)}
                    className={`w-9 h-9 rounded-lg text-sm transition-colors ${
                      page === pageNum
                        ? 'bg-primary text-primary-foreground'
                        : 'border border-border hover:bg-secondary'
                    }`}
                  >
                    {pageNum}
                  </button>
                )
              })}

              <button
                onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
                disabled={page >= totalPages}
                className="px-3 py-1.5 rounded-lg border border-border hover:bg-secondary disabled:opacity-50 disabled:cursor-not-allowed text-sm"
              >
                下一页
              </button>
            </div>
          )}
        </>
      ) : (
        <div className="text-center py-20">
          <SearchIcon className="w-12 h-12 mx-auto text-muted-foreground/50 mb-3" />
          <p className="text-muted-foreground">没有找到相关结果</p>
          <p className="text-sm text-muted-foreground mt-1">试试其他关键词或筛选条件</p>
        </div>
      )}
    </div>
  )
}
