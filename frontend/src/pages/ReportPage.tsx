import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { reportService } from '../services/reportService'
import { useAuthStore } from '../store/authStore'
import type { Report } from '../types'

/**
 * Report Page
 * Shows generated reports and allows users to generate new ones
 */
export default function ReportPage() {
  const navigate = useNavigate()
  const { user, isAuthenticated } = useAuthStore()

  const [reports, setReports] = useState<Report[]>([])
  const [loading, setLoading] = useState(false)
  const [generating, setGenerating] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [expandedReportId, setExpandedReportId] = useState<string | null>(null)

  // Redirect to login if not authenticated
  useEffect(() => {
    if (!isAuthenticated || !user) {
      navigate('/login')
    }
  }, [isAuthenticated, user, navigate])

  // Load reports (mock data for now)
  useEffect(() => {
    if (user) {
      loadReports()
    }
  }, [user])

  const loadReports = async () => {
    setLoading(true)
    try {
      // For now, show mock reports since backend doesn't have list endpoint yet
      const mockReports: Report[] = [
        {
          id: 'report-1',
          created_at: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString(),
          papers_count: 5,
          status: 'completed',
        },
        {
          id: 'report-2',
          created_at: new Date(Date.now() - 14 * 24 * 60 * 60 * 1000).toISOString(),
          papers_count: 8,
          status: 'completed',
        },
      ]
      setReports(mockReports)
    } catch (err) {
      console.error('Failed to load reports:', err)
      setError('리포트를 불러올 수 없습니다.')
    } finally {
      setLoading(false)
    }
  }

  const handleGenerateReport = async () => {
    if (!user) return

    setGenerating(true)
    setError(null)
    try {
      const result = await reportService.generateReport(user.id)
      console.log('Report generated:', result)
      alert(`리포트가 생성되었습니다!\n${result.papers.length}개의 논문이 포함되었습니다.`)
      // Refresh reports list
      loadReports()
    } catch (err) {
      console.error('Failed to generate report:', err)
      setError('리포트 생성에 실패했습니다.')
    } finally {
      setGenerating(false)
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
        {/* Generate Report Section */}
        <div className="bg-gradient-to-r from-purple-600 to-pink-600 text-white rounded-lg shadow-lg p-8 mb-12">
          <h1 className="text-3xl font-bold mb-2">개인 맞춤 리포트</h1>
          <p className="text-purple-100 mb-6">
            당신의 관심사에 맞는 연구 논문들을 분석한 개인 맞춤 리포트를 생성하세요
          </p>
          <button
            onClick={handleGenerateReport}
            disabled={generating}
            className="bg-white text-purple-600 hover:bg-gray-100 disabled:bg-gray-300 text-white font-bold py-3 px-6 rounded-lg transition flex items-center gap-2"
          >
            {generating ? (
              <>
                <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-purple-600"></div>
                생성 중...
              </>
            ) : (
              <>📄 새 리포트 생성</>
            )}
          </button>
        </div>

        {/* Error Message */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-8 text-red-800">
            {error}
          </div>
        )}

        {/* Reports List */}
        {loading ? (
          <div className="text-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto"></div>
            <p className="mt-4 text-gray-600">리포트를 불러오는 중입니다...</p>
          </div>
        ) : reports.length === 0 ? (
          <div className="text-center py-12 bg-white rounded-lg shadow">
            <p className="text-gray-600 mb-4">아직 생성된 리포트가 없습니다.</p>
            <p className="text-sm text-gray-500">위의 버튼을 눌러 첫 번째 리포트를 생성해보세요!</p>
          </div>
        ) : (
          <div className="space-y-4">
            <h2 className="text-2xl font-bold text-gray-900 mb-6">이전 리포트</h2>
            {reports.map((report) => (
              <div
                key={report.id}
                className="bg-white rounded-lg shadow hover:shadow-lg transition border-l-4 border-purple-500"
              >
                <button
                  onClick={() =>
                    setExpandedReportId(expandedReportId === report.id ? null : report.id)
                  }
                  className="w-full p-6 text-left hover:bg-gray-50 transition"
                >
                  <div className="flex items-center justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-2">
                        <span className="inline-block bg-purple-100 text-purple-800 px-3 py-1 rounded-full text-sm font-semibold">
                          리포트 #{report.id.split('-')[1]}
                        </span>
                        <span className="text-sm text-gray-600">
                          {report.created_at && new Date(report.created_at).toLocaleDateString('ko-KR', {
                            year: 'numeric',
                            month: 'long',
                            day: 'numeric',
                          })}
                        </span>
                      </div>
                      <p className="text-gray-600">
                        📊 {report.papers_count}개의 논문 포함
                      </p>
                    </div>
                    <span className="text-gray-400 text-2xl">
                      {expandedReportId === report.id ? '−' : '+'}
                    </span>
                  </div>
                </button>

                {/* Expanded Details */}
                {expandedReportId === report.id && (
                  <div className="px-6 pb-6 bg-gray-50 border-t border-gray-200">
                    <div className="space-y-4">
                      <div className="grid grid-cols-3 gap-4">
                        <div className="bg-white p-4 rounded border border-gray-200">
                          <p className="text-sm text-gray-600 mb-1">상태</p>
                          <p className="text-lg font-semibold text-gray-900">
                            {report.status === 'completed' ? '✅ 완료됨' : '⏳ 진행 중'}
                          </p>
                        </div>
                        <div className="bg-white p-4 rounded border border-gray-200">
                          <p className="text-sm text-gray-600 mb-1">포함된 논문</p>
                          <p className="text-lg font-semibold text-gray-900">
                            {report.papers_count}개
                          </p>
                        </div>
                        <div className="bg-white p-4 rounded border border-gray-200">
                          <p className="text-sm text-gray-600 mb-1">생성일</p>
                          <p className="text-sm font-semibold text-gray-900">
                            {report.created_at && new Date(report.created_at).toLocaleDateString('ko-KR')}
                          </p>
                        </div>
                      </div>

                      <div className="flex gap-2">
                        <button className="flex-1 bg-indigo-600 hover:bg-indigo-700 text-white font-semibold py-2 px-4 rounded transition">
                          📥 다운로드
                        </button>
                        <button className="flex-1 bg-gray-200 hover:bg-gray-300 text-gray-900 font-semibold py-2 px-4 rounded transition">
                          👁️ 상세 보기
                        </button>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}

        {/* Tips Section */}
        <div className="mt-12 bg-blue-50 border border-blue-200 rounded-lg p-6">
          <h3 className="text-lg font-semibold text-blue-900 mb-3">💡 리포트 활용 팁</h3>
          <ul className="space-y-2 text-blue-800">
            <li>✓ <strong>매주 자동 생성</strong>되어 새로운 논문들을 놓치지 않습니다</li>
            <li>✓ <strong>관심사 기반</strong>으로 필터링된 논문들만 포함됩니다</li>
            <li>✓ <strong>PDF 다운로드</strong>해서 언제든지 열람할 수 있습니다</li>
            <li>✓ <strong>Notion</strong>에 자동으로 저장됩니다 (설정 시)</li>
          </ul>
        </div>
      </main>
    </div>
  )
}
