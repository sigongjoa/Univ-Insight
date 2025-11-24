import { useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuthStore } from '../store/authStore'

/**
 * Home Page
 * Main landing page after login
 */
export default function HomePage() {
  const navigate = useNavigate()
  const { user, isAuthenticated, loadUserFromStorage } = useAuthStore()

  useEffect(() => {
    // Load user from localStorage on mount
    loadUserFromStorage()

    // Redirect to login if not authenticated
    if (!isAuthenticated && !user) {
      navigate('/login')
    }
  }, [isAuthenticated, user, navigate, loadUserFromStorage])

  if (!user) {
    return <div className="flex items-center justify-center h-screen">로딩 중...</div>
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex justify-between items-center">
          <h1 className="text-2xl font-bold text-gray-900">Univ-Insight</h1>
          <div className="flex items-center gap-4">
            <span className="text-gray-700">{user.name}님 환영합니다!</span>
            <button
              onClick={() => {
                const { logout } = useAuthStore.getState()
                logout()
                navigate('/login')
              }}
              className="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded"
            >
              로그아웃
            </button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        {/* Welcome Section */}
        <section className="bg-gradient-to-r from-blue-500 to-indigo-600 rounded-lg p-8 text-white mb-12">
          <h2 className="text-3xl font-bold mb-4">
            {user.role === 'student'
              ? `${user.name}의 대학 연구 여정을 시작하세요! 🎓`
              : `${user.name}님, 자녀의 진로 탐색을 도와주세요! 📚`}
          </h2>
          <p className="text-lg opacity-90 mb-6">
            {user.role === 'student'
              ? '최신 대학 연구를 쉽게 이해하고, 진로를 설계해보세요.'
              : '자녀의 관심사에 맞춘 맞춤형 리포트를 받아보세요.'}
          </p>

          <div className="flex gap-4 flex-wrap">
            <button
              onClick={() => navigate('/research')}
              className="bg-white text-indigo-600 font-semibold px-6 py-3 rounded hover:bg-gray-100 transition"
            >
              연구 논문 탐색 →
            </button>
            <button
              onClick={() => navigate('/reports')}
              className="bg-indigo-700 hover:bg-indigo-800 font-semibold px-6 py-3 rounded transition"
            >
              리포트 보기 →
            </button>
          </div>
        </section>

        {/* Interest Tags */}
        <section className="mb-12">
          <h3 className="text-xl font-bold text-gray-900 mb-4">당신의 관심사</h3>
          <div className="flex flex-wrap gap-2">
            {user.interests.length > 0 ? (
              user.interests.map((interest) => (
                <span
                  key={interest}
                  className="bg-indigo-100 text-indigo-800 px-4 py-2 rounded-full"
                >
                  #{interest}
                </span>
              ))
            ) : (
              <p className="text-gray-600">관심사를 설정해주세요</p>
            )}
          </div>
        </section>

        {/* Quick Actions */}
        <section>
          <h3 className="text-xl font-bold text-gray-900 mb-6">빠른 시작</h3>
          <div className="grid md:grid-cols-3 gap-6">
            {/* Card 1 */}
            <div className="bg-white rounded-lg shadow p-6 hover:shadow-lg transition cursor-pointer">
              <div className="text-4xl mb-4">🔍</div>
              <h4 className="text-lg font-semibold text-gray-900 mb-2">논문 검색</h4>
              <p className="text-gray-600 mb-4">
                대학 연구 논문을 검색하고, 진로와 연결해보세요.
              </p>
              <button
                onClick={() => navigate('/research')}
                className="text-indigo-600 hover:text-indigo-700 font-semibold"
              >
                시작하기 →
              </button>
            </div>

            {/* Card 2 */}
            <div className="bg-white rounded-lg shadow p-6 hover:shadow-lg transition cursor-pointer">
              <div className="text-4xl mb-4">📊</div>
              <h4 className="text-lg font-semibold text-gray-900 mb-2">맞춤 리포트</h4>
              <p className="text-gray-600 mb-4">
                당신의 관심사에 맞춘 주간 리포트를 받아보세요.
              </p>
              <button
                onClick={() => navigate('/reports')}
                className="text-indigo-600 hover:text-indigo-700 font-semibold"
              >
                생성하기 →
              </button>
            </div>

            {/* Card 3 */}
            <div className="bg-white rounded-lg shadow p-6 hover:shadow-lg transition cursor-pointer">
              <div className="text-4xl mb-4">🎓</div>
              <h4 className="text-lg font-semibold text-gray-900 mb-2">플랜 B</h4>
              <p className="text-gray-600 mb-4">
                유사 연구를 다른 대학에서 찾아보세요.
              </p>
              <button
                onClick={() => navigate('/research')}
                className="text-indigo-600 hover:text-indigo-700 font-semibold"
              >
                탐색하기 →
              </button>
            </div>
          </div>
        </section>
      </main>
    </div>
  )
}
