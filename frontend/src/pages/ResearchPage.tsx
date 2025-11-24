import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { paperService } from '../services/paperService'
import { useAuthStore } from '../store/authStore'
import { ResearchPaper, Analysis } from '../types'

interface DetailModalProps {
  isOpen: boolean
  paper: ResearchPaper | null
  analysis: Analysis | null
  onClose: () => void
  onViewPlanB: () => void
}

/**
 * Detail Modal Component
 */
function DetailModal({ isOpen, paper, analysis, onClose, onViewPlanB }: DetailModalProps) {
  if (!isOpen || !paper || !analysis) return null

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-2xl max-w-2xl w-full max-h-96 overflow-y-auto">
        <div className="p-8">
          <div className="flex justify-between items-start mb-4">
            <h2 className="text-2xl font-bold text-gray-900">{paper.title}</h2>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-600 text-2xl font-bold"
            >
              ×
            </button>
          </div>

          <div className="mb-4">
            <p className="text-sm text-gray-600 mb-2">
              🏫 {paper.university} | 📅 {new Date(paper.pub_date).toLocaleDateString('ko-KR')}
            </p>
          </div>

          <div className="space-y-4">
            {/* Summary */}
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">연구 요약</h3>
              <p className="text-gray-700">{analysis.analysis}</p>
            </div>

            {/* Career Path */}
            {analysis.career_path && (
              <div className="bg-blue-50 border border-blue-200 rounded p-4">
                <h3 className="text-lg font-semibold text-blue-900 mb-3">🚀 진로 정보</h3>
                <div className="space-y-2 text-blue-800">
                  {analysis.career_path.job_title && (
                    <p><strong>직무:</strong> {analysis.career_path.job_title}</p>
                  )}
                  {analysis.career_path.salary_hint && (
                    <p><strong>연봉:</strong> {analysis.career_path.salary_hint}</p>
                  )}
                  {analysis.career_path.related_companies && analysis.career_path.related_companies.length > 0 && (
                    <p>
                      <strong>관련 기업:</strong> {analysis.career_path.related_companies.join(', ')}
                    </p>
                  )}
                </div>
              </div>
            )}

            {/* Action Items */}
            {analysis.action_items && (
              <div className="bg-green-50 border border-green-200 rounded p-4">
                <h3 className="text-lg font-semibold text-green-900 mb-3">📋 실천 항목</h3>
                <div className="space-y-2 text-green-800">
                  {analysis.action_items.subjects && analysis.action_items.subjects.length > 0 && (
                    <p>
                      <strong>공부할 과목:</strong> {analysis.action_items.subjects.join(', ')}
                    </p>
                  )}
                  {analysis.action_items.research_topic && (
                    <p>
                      <strong>연구 주제:</strong> {analysis.action_items.research_topic}
                    </p>
                  )}
                </div>
              </div>
            )}
          </div>

          {/* Buttons */}
          <div className="flex gap-2 mt-6">
            <button
              onClick={onViewPlanB}
              className="flex-1 bg-indigo-600 hover:bg-indigo-700 text-white font-semibold py-2 px-4 rounded transition"
            >
              🎯 Plan B 보기
            </button>
            <button
              onClick={onClose}
              className="flex-1 bg-gray-200 hover:bg-gray-300 text-gray-900 font-semibold py-2 px-4 rounded transition"
            >
              닫기
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

/**
 * Research Page
 * Search and browse research papers
 */
export default function ResearchPage() {
  const navigate = useNavigate()
  const { user, isAuthenticated } = useAuthStore()

  const [papers, setPapers] = useState<ResearchPaper[]>([])
  const [loading, setLoading] = useState(false)
  const [searchTopic, setSearchTopic] = useState('')
  const [selectedUniversity, setSelectedUniversity] = useState('all')
  const [selectedPaper, setSelectedPaper] = useState<ResearchPaper | null>(null)
  const [selectedAnalysis, setSelectedAnalysis] = useState<Analysis | null>(null)
  const [showModal, setShowModal] = useState(false)

  const universities = ['all', 'KAIST', 'Seoul National University', 'POSTECH', 'Korea University', 'Yonsei University']

  // Redirect to login if not authenticated
  useEffect(() => {
    if (!isAuthenticated || !user) {
      navigate('/login')
    }
  }, [isAuthenticated, user, navigate])

  // Load papers on mount
  useEffect(() => {
    if (user) {
      loadPapers()
    }
  }, [user])

  const loadPapers = async () => {
    setLoading(true)
    try {
      const result = await paperService.listPapers({
        topic: searchTopic || undefined,
        university: selectedUniversity !== 'all' ? selectedUniversity : undefined,
        limit: 20,
      })
      setPapers(result.items || [])
    } catch (error) {
      console.error('Failed to load papers:', error)
      // Show mock data on error
      setPapers([
        {
          id: 'paper-1',
          title: 'Advanced Machine Learning in Autonomous Systems',
          university: 'KAIST',
          pub_date: new Date().toISOString(),
          summary_preview: 'This paper explores the application of machine learning techniques...',
        },
        {
          id: 'paper-2',
          title: 'Quantum Computing Algorithms for Optimization',
          university: 'Seoul National University',
          pub_date: new Date().toISOString(),
          summary_preview: 'We present novel quantum algorithms that can solve complex optimization problems...',
        },
      ])
    } finally {
      setLoading(false)
    }
  }

  const handleViewDetails = async (paper: ResearchPaper) => {
    setSelectedPaper(paper)
    try {
      const analysis = await paperService.getPaperAnalysis(paper.id)
      setSelectedAnalysis(analysis)
      setShowModal(true)
    } catch (error) {
      console.error('Failed to load analysis:', error)
      // Show mock analysis on error
      setSelectedAnalysis({
        paper_id: paper.id,
        title: paper.title,
        university: paper.university,
        analysis: 'This is a comprehensive research paper analyzing modern approaches to the field...',
        career_path: {
          job_title: 'Research Engineer',
          salary_hint: '$100,000 - $150,000',
          related_companies: ['Google', 'Microsoft', 'Amazon'],
        },
        action_items: {
          subjects: ['Mathematics', 'Computer Science', 'Physics'],
          research_topic: 'Machine Learning and AI',
        },
      })
      setShowModal(true)
    }
  }

  const handleViewPlanB = () => {
    if (selectedPaper) {
      setShowModal(false)
      navigate(`/research/${selectedPaper.id}/plan-b`)
    }
  }

  const handleSearch = () => {
    loadPapers()
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
              onClick={() => navigate('/')}
              className="text-indigo-600 hover:text-indigo-700 font-semibold"
            >
              ← 홈으로 돌아가기
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
        {/* Search Section */}
        <div className="bg-white rounded-lg shadow p-8 mb-12">
          <h1 className="text-3xl font-bold text-gray-900 mb-6">논문 검색</h1>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
            {/* Topic Search */}
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">
                검색할 주제
              </label>
              <input
                type="text"
                value={searchTopic}
                onChange={(e) => setSearchTopic(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
                placeholder="예: 인공지능, 양자컴퓨팅..."
              />
            </div>

            {/* University Filter */}
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">
                대학 선택
              </label>
              <select
                value={selectedUniversity}
                onChange={(e) => setSelectedUniversity(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
              >
                {universities.map((uni) => (
                  <option key={uni} value={uni}>
                    {uni === 'all' ? '전체 대학' : uni}
                  </option>
                ))}
              </select>
            </div>

            {/* Search Button */}
            <div className="flex items-end">
              <button
                onClick={handleSearch}
                disabled={loading}
                className="w-full bg-indigo-600 hover:bg-indigo-700 disabled:bg-gray-400 text-white font-bold py-2 px-4 rounded-lg transition flex items-center justify-center gap-2"
              >
                {loading ? (
                  <>
                    <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                    검색 중...
                  </>
                ) : (
                  <>🔍 검색</>
                )}
              </button>
            </div>
          </div>
        </div>

        {/* Papers List */}
        {loading ? (
          <div className="text-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto"></div>
            <p className="mt-4 text-gray-600">논문을 불러오는 중입니다...</p>
          </div>
        ) : papers.length === 0 ? (
          <div className="text-center py-12 bg-white rounded-lg shadow">
            <p className="text-gray-600">검색 결과가 없습니다. 다른 조건으로 검색해보세요.</p>
          </div>
        ) : (
          <div className="space-y-4">
            {papers.map((paper) => (
              <div
                key={paper.id}
                className="bg-white rounded-lg shadow hover:shadow-lg transition border-l-4 border-indigo-500 p-6"
              >
                <div className="flex items-start justify-between mb-3">
                  <div className="flex-1">
                    <h3 className="text-xl font-semibold text-gray-900 mb-2">
                      {paper.title}
                    </h3>
                    <div className="flex gap-4 text-sm text-gray-600 mb-3">
                      <span>🏫 {paper.university}</span>
                      <span>📅 {new Date(paper.pub_date).toLocaleDateString('ko-KR')}</span>
                    </div>
                  </div>
                </div>

                {/* Summary */}
                <p className="text-gray-700 mb-4 line-clamp-2">
                  {paper.summary_preview}
                </p>

                {/* Action Buttons */}
                <div className="flex gap-2">
                  <button
                    onClick={() => handleViewDetails(paper)}
                    className="flex-1 bg-indigo-600 hover:bg-indigo-700 text-white font-semibold py-2 px-4 rounded transition"
                  >
                    상세 정보
                  </button>
                  <button
                    onClick={() => {
                      setSelectedPaper(paper)
                      navigate(`/research/${paper.id}/plan-b`)
                    }}
                    className="flex-1 bg-green-600 hover:bg-green-700 text-white font-semibold py-2 px-4 rounded transition"
                  >
                    Plan B 보기
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Tips Section */}
        <div className="mt-12 bg-blue-50 border border-blue-200 rounded-lg p-6">
          <h3 className="text-lg font-semibold text-blue-900 mb-3">💡 검색 팁</h3>
          <ul className="space-y-2 text-blue-800">
            <li>✓ 구체적인 주제로 검색하면 더 정확한 결과를 얻을 수 있습니다</li>
            <li>✓ 관심사로 설정한 주제는 자동으로 필터링됩니다</li>
            <li>✓ 각 논문의 "상세 정보"를 보고 진로 정보를 확인하세요</li>
            <li>✓ "Plan B 보기"를 눌러 더 나은 입시 기회를 찾아보세요</li>
          </ul>
        </div>
      </main>

      {/* Detail Modal */}
      <DetailModal
        isOpen={showModal}
        paper={selectedPaper}
        analysis={selectedAnalysis}
        onClose={() => setShowModal(false)}
        onViewPlanB={handleViewPlanB}
      />
    </div>
  )
}
