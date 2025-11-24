import { useState, useEffect } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { paperService } from '../services/paperService'
import type { PlanBSuggestion } from '../types'
import { useAuthStore } from '../store/authStore'

/**
 * Plan B Page
 * Shows alternative universities with similar research
 */
export default function PlanBPage() {
  const navigate = useNavigate()
  const { paperId } = useParams<{ paperId: string }>()
  const { user, isAuthenticated } = useAuthStore()

  const [originalPaper, setOriginalPaper] = useState<any>(null)
  const [suggestions, setSuggestions] = useState<PlanBSuggestion[]>([])
  const [loading, setLoading] = useState(false)

  // Redirect to login if not authenticated
  useEffect(() => {
    if (!isAuthenticated || !user) {
      navigate('/login')
    }
  }, [isAuthenticated, user, navigate])

  // Load Plan B suggestions
  useEffect(() => {
    if (paperId) {
      loadPlanB()
    }
  }, [paperId])

  const loadPlanB = async () => {
    setLoading(true)
    try {
      const result = await paperService.getPlanBSuggestions(paperId!)
      setOriginalPaper(result.original_paper)
      setSuggestions(result.plan_b_suggestions)
    } catch (error) {
      console.error('Failed to load Plan B suggestions:', error)
    } finally {
      setLoading(false)
    }
  }

  if (!user) {
    return <div className="flex items-center justify-center h-screen">로딩 중...</div>
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex justify-between items-center">
          <button
            onClick={() => navigate('/')}
            className="text-2xl font-bold text-gray-900 hover:text-indigo-600"
          >
            Univ-Insight
          </button>
          <div className="flex items-center gap-4">
            <button
              onClick={() => navigate('/research')}
              className="text-indigo-600 hover:text-indigo-700 font-semibold"
            >
              ← 논문 검색으로 돌아가기
            </button>
            <button
              onClick={() => navigate('/profile')}
              className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded"
            >
              프로필
            </button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        {loading ? (
          <div className="text-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto"></div>
            <p className="mt-4 text-gray-600">Plan B 제안을 불러오는 중입니다...</p>
          </div>
        ) : (
          <>
            {/* Original Paper */}
            {originalPaper && (
              <div className="bg-gradient-to-r from-indigo-600 to-indigo-700 text-white rounded-lg shadow-lg p-8 mb-12">
                <h1 className="text-3xl font-bold mb-4">Plan B 대안 찾기</h1>
                <div className="space-y-2">
                  <p className="text-lg font-semibold">{originalPaper.title}</p>
                  <p className="text-indigo-100">
                    🏫 {originalPaper.university} (Tier {originalPaper.university_tier})
                  </p>
                  <p className="text-indigo-100 mt-4">
                    아래의 대학들에서도 유사한 연구를 진행 중입니다. 더 나은 입시 기회를 찾아보세요!
                  </p>
                </div>
              </div>
            )}

            {/* Plan B Suggestions */}
            {suggestions.length === 0 ? (
              <div className="text-center py-12 bg-white rounded-lg shadow">
                <p className="text-gray-600">유사한 연구를 찾을 수 없습니다.</p>
              </div>
            ) : (
              <div className="space-y-6">
                {suggestions.map((suggestion, index) => (
                  <div
                    key={suggestion.paper_id}
                    className="bg-white rounded-lg shadow hover:shadow-lg transition p-6 border-l-4 border-green-500"
                  >
                    <div className="flex items-start justify-between mb-4">
                      <div className="flex-1">
                        <div className="flex items-center gap-3 mb-2">
                          <span className="inline-block bg-green-100 text-green-800 px-3 py-1 rounded-full text-sm font-semibold">
                            Plan B #{index + 1}
                          </span>
                          <span className="text-sm text-gray-600">
                            유사도: {(suggestion.similarity_score * 100).toFixed(1)}%
                          </span>
                        </div>
                        <h3 className="text-xl font-semibold text-gray-900 mb-2">
                          {suggestion.title}
                        </h3>
                        <div className="flex gap-4 text-sm text-gray-600 mb-3">
                          <span>🏫 {suggestion.university}</span>
                          <span>📊 Tier {suggestion.university_tier}</span>
                        </div>
                      </div>
                      {/* Similarity Bar */}
                      <div className="ml-4">
                        <div className="text-right mb-2">
                          <span className="text-sm font-semibold text-gray-700">
                            {(suggestion.similarity_score * 100).toFixed(0)}%
                          </span>
                        </div>
                        <div className="w-32 h-3 bg-gray-200 rounded-full overflow-hidden">
                          <div
                            className="h-full bg-gradient-to-r from-green-400 to-green-600 transition-all duration-300"
                            style={{
                              width: `${suggestion.similarity_score * 100}%`,
                            }}
                          ></div>
                        </div>
                      </div>
                    </div>

                    {/* Summary */}
                    <p className="text-gray-700 mb-4 line-clamp-3">
                      {suggestion.summary}
                    </p>

                    {/* Reason */}
                    <div className="bg-green-50 border border-green-200 rounded p-3 mb-4">
                      <p className="text-sm text-green-800">
                        <strong>💡 이유:</strong> {suggestion.reason}
                      </p>
                    </div>

                    {/* Action Buttons */}
                    <div className="flex gap-2">
                      <button
                        onClick={() => navigate(`/research/${suggestion.paper_id}`)}
                        className="flex-1 bg-indigo-600 hover:bg-indigo-700 text-white font-semibold py-2 px-4 rounded transition"
                      >
                        상세 정보
                      </button>
                      <button
                        onClick={() => navigate('/research')}
                        className="flex-1 bg-gray-200 hover:bg-gray-300 text-gray-900 font-semibold py-2 px-4 rounded transition"
                      >
                        다른 논문 보기
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}

            {/* Tips Section */}
            <div className="mt-12 bg-blue-50 border border-blue-200 rounded-lg p-6">
              <h3 className="text-lg font-semibold text-blue-900 mb-3">
                💡 Plan B 선택 팁
              </h3>
              <ul className="space-y-2 text-blue-800">
                <li>
                  ✓ <strong>유사도가 높을수록</strong> 더 유사한 연구를 진행 중입니다
                </li>
                <li>
                  ✓ <strong>Tier가 높을수록</strong> 입시 난이도가 낮습니다
                </li>
                <li>
                  ✓ <strong>여러 대학을 비교</strong>하여 최적의 진로를 선택하세요
                </li>
                <li>
                  ✓ 각 대학의 <strong>입시 정보를 확인</strong>하고 준비하세요
                </li>
              </ul>
            </div>
          </>
        )}
      </main>
    </div>
  )
}
