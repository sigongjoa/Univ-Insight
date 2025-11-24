import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { userService } from '../services/userService'
import { useAuthStore } from '../store/authStore'

/**
 * Profile Page
 * User profile management and settings
 */
export default function ProfilePage() {
  const navigate = useNavigate()
  const { user, isAuthenticated, logout } = useAuthStore()

  const [name, setName] = useState('')
  const [interests, setInterests] = useState<string[]>([])
  const [newInterest, setNewInterest] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState<string | null>(null)

  // Redirect to login if not authenticated
  useEffect(() => {
    if (!isAuthenticated || !user) {
      navigate('/login')
    } else {
      setName(user.name)
      setInterests(user.interests || [])
    }
  }, [isAuthenticated, user, navigate])

  const handleAddInterest = () => {
    if (newInterest.trim() && !interests.includes(newInterest.trim())) {
      setInterests([...interests, newInterest.trim()])
      setNewInterest('')
    }
  }

  const handleRemoveInterest = (interest: string) => {
    setInterests(interests.filter((i) => i !== interest))
  }

  const handleSaveProfile = async () => {
    setLoading(true)
    setError(null)
    setSuccess(null)

    try {
      // For now, just update local state and show success
      // In a real app, this would call an API endpoint to update the backend
      userService.saveAuthData('', {
        ...user!,
        name,
        interests,
      })

      // Update auth store
      useAuthStore.setState({
        user: {
          ...user!,
          name,
          interests,
        },
      })

      setSuccess('프로필이 저장되었습니다!')
      setTimeout(() => setSuccess(null), 3000)
    } catch (err) {
      console.error('Failed to save profile:', err)
      setError('프로필 저장에 실패했습니다.')
    } finally {
      setLoading(false)
    }
  }

  const handleLogout = () => {
    if (window.confirm('정말 로그아웃하시겠습니까?')) {
      logout()
      navigate('/login')
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
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        {/* User Info Header */}
        <div className="bg-gradient-to-r from-blue-600 to-cyan-600 text-white rounded-lg shadow-lg p-8 mb-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold mb-2">{user.name}</h1>
              <p className="text-blue-100 mb-1">👤 역할: {user.role === 'student' ? '학생' : '부모'}</p>
              <p className="text-blue-100">🆔 ID: {user.id}</p>
            </div>
            <div className="text-right">
              <p className="text-blue-100 mb-2">
                가입일:{' '}
                {new Date(user.created_at).toLocaleDateString('ko-KR', {
                  year: 'numeric',
                  month: 'long',
                  day: 'numeric',
                })}
              </p>
            </div>
          </div>
        </div>

        {/* Error and Success Messages */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-8 text-red-800">
            {error}
          </div>
        )}
        {success && (
          <div className="bg-green-50 border border-green-200 rounded-lg p-4 mb-8 text-green-800">
            {success}
          </div>
        )}

        {/* Profile Form */}
        <div className="bg-white rounded-lg shadow p-8 mb-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">프로필 설정</h2>

          {/* Name */}
          <div className="mb-6">
            <label className="block text-sm font-semibold text-gray-700 mb-2">이름</label>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
              placeholder="이름을 입력하세요"
            />
          </div>

          {/* Role Display */}
          <div className="mb-6">
            <label className="block text-sm font-semibold text-gray-700 mb-2">역할</label>
            <div className="px-4 py-2 bg-gray-100 rounded-lg text-gray-700 font-semibold">
              {user.role === 'student' ? '👤 학생' : '👨‍👩‍👧 부모'}
            </div>
            <p className="text-xs text-gray-500 mt-2">역할은 변경할 수 없습니다.</p>
          </div>

          {/* Interests */}
          <div className="mb-6">
            <label className="block text-sm font-semibold text-gray-700 mb-2">관심사</label>
            <div className="flex gap-2 mb-3">
              <input
                type="text"
                value={newInterest}
                onChange={(e) => setNewInterest(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleAddInterest()}
                className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
                placeholder="새로운 관심사를 입력하세요"
              />
              <button
                onClick={handleAddInterest}
                className="bg-indigo-600 hover:bg-indigo-700 text-white font-semibold py-2 px-4 rounded-lg transition"
              >
                추가
              </button>
            </div>

            {/* Interest Tags */}
            {interests.length > 0 ? (
              <div className="flex flex-wrap gap-2">
                {interests.map((interest) => (
                  <div
                    key={interest}
                    className="bg-indigo-100 text-indigo-800 px-3 py-2 rounded-full text-sm font-semibold flex items-center gap-2"
                  >
                    {interest}
                    <button
                      onClick={() => handleRemoveInterest(interest)}
                      className="text-indigo-600 hover:text-indigo-900 font-bold"
                    >
                      ×
                    </button>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-sm text-gray-500">아직 관심사가 없습니다. 위에서 추가해보세요!</p>
            )}
          </div>

          {/* Save Button */}
          <button
            onClick={handleSaveProfile}
            disabled={loading}
            className="w-full bg-indigo-600 hover:bg-indigo-700 disabled:bg-gray-400 text-white font-bold py-3 px-4 rounded-lg transition flex items-center justify-center gap-2"
          >
            {loading ? (
              <>
                <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                저장 중...
              </>
            ) : (
              <>💾 프로필 저장</>
            )}
          </button>
        </div>

        {/* Preferences Section */}
        <div className="bg-white rounded-lg shadow p-8 mb-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">설정</h2>

          {/* Notifications */}
          <div className="mb-6 pb-6 border-b border-gray-200">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">알림 설정</h3>
            <div className="space-y-3">
              <label className="flex items-center gap-3 cursor-pointer">
                <input
                  type="checkbox"
                  defaultChecked
                  className="w-5 h-5 text-indigo-600 rounded focus:ring-2 focus:ring-indigo-500"
                />
                <span className="text-gray-700">주간 리포트 이메일 알림</span>
              </label>
              <label className="flex items-center gap-3 cursor-pointer">
                <input
                  type="checkbox"
                  defaultChecked
                  className="w-5 h-5 text-indigo-600 rounded focus:ring-2 focus:ring-indigo-500"
                />
                <span className="text-gray-700">새로운 논문 추천 알림</span>
              </label>
              <label className="flex items-center gap-3 cursor-pointer">
                <input
                  type="checkbox"
                  className="w-5 h-5 text-indigo-600 rounded focus:ring-2 focus:ring-indigo-500"
                />
                <span className="text-gray-700">Notion 자동 저장</span>
              </label>
            </div>
          </div>

          {/* Integrations */}
          <div className="mb-6 pb-6 border-b border-gray-200">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">연동 서비스</h3>
            <div className="space-y-3">
              <div className="flex items-center justify-between p-4 border border-gray-200 rounded-lg">
                <div>
                  <p className="font-semibold text-gray-900">Notion</p>
                  <p className="text-sm text-gray-500">자동으로 리포트를 저장합니다</p>
                </div>
                <button className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded font-semibold">
                  연동하기
                </button>
              </div>
              <div className="flex items-center justify-between p-4 border border-gray-200 rounded-lg">
                <div>
                  <p className="font-semibold text-gray-900">Kakao Talk</p>
                  <p className="text-sm text-gray-500">새로운 논문을 메시지로 받습니다</p>
                </div>
                <button className="bg-yellow-400 hover:bg-yellow-500 text-black px-4 py-2 rounded font-semibold">
                  연동하기
                </button>
              </div>
            </div>
          </div>

          {/* Danger Zone */}
          <div>
            <h3 className="text-lg font-semibold text-red-600 mb-4">위험한 작업</h3>
            <button
              onClick={handleLogout}
              className="w-full bg-red-600 hover:bg-red-700 text-white font-bold py-3 px-4 rounded-lg transition"
            >
              🚪 로그아웃
            </button>
          </div>
        </div>

        {/* Info Section */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-6 mb-8">
          <h3 className="text-lg font-semibold text-blue-900 mb-3">ℹ️ 계정 정보</h3>
          <ul className="space-y-2 text-blue-800 text-sm">
            <li>
              • 프로필 변경은 자동으로 저장되며, 새로운 리포트 생성에 바로 반영됩니다
            </li>
            <li>
              • 관심사 추가/제거 후 다음 주 자동 리포트에 반영됩니다
            </li>
            <li>
              • 연동 서비스는 언제든지 설정에서 해제할 수 있습니다
            </li>
          </ul>
        </div>
      </main>
    </div>
  )
}
