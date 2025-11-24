import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuthStore } from '../store/authStore'
import type { User } from '../types'

/**
 * Login Page
 * Handles user authentication and registration
 */
export default function LoginPage() {
  const navigate = useNavigate()
  const { setUser, setLoading, setError } = useAuthStore()

  const [formData, setFormData] = useState({
    userId: '',
    name: '',
    role: 'student' as const,
    interests: '',
  })
  const [isLoading, setIsLoading] = useState(false)

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }))
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsLoading(true)
    setLoading(true)

    try {
      // Create user object
      const newUser: User = {
        id: formData.userId,
        name: formData.name,
        role: formData.role,
        interests: formData.interests.split(',').filter((i) => i.trim()),
        created_at: new Date().toISOString(),
      }

      // Save to auth store
      setUser(newUser)

      // Navigate to home
      navigate('/')
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Login failed'
      setError(message)
    } finally {
      setIsLoading(false)
      setLoading(false)
    }
  }

  const handleKakaoLogin = () => {
    // Kakao 로그인은 추후 구현
    alert('Kakao login will be implemented soon')
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
      <div className="bg-white rounded-lg shadow-xl p-8 max-w-md w-full">
        <h1 className="text-3xl font-bold text-center mb-2 text-gray-900">
          Univ-Insight
        </h1>
        <p className="text-center text-gray-600 mb-8">
          대학 연구로 미래 설계하기
        </p>

        {/* Kakao Login Button */}
        <button
          onClick={handleKakaoLogin}
          className="w-full bg-yellow-400 hover:bg-yellow-500 text-gray-800 font-semibold py-3 px-4 rounded-lg mb-6 transition"
        >
          카카오로 시작하기
        </button>

        <div className="relative mb-6">
          <div className="absolute inset-0 flex items-center">
            <div className="w-full border-t border-gray-300"></div>
          </div>
          <div className="relative flex justify-center text-sm">
            <span className="px-2 bg-white text-gray-500">또는</span>
          </div>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              사용자 ID
            </label>
            <input
              type="text"
              name="userId"
              value={formData.userId}
              onChange={handleChange}
              placeholder="user123"
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              이름
            </label>
            <input
              type="text"
              name="name"
              value={formData.name}
              onChange={handleChange}
              placeholder="김학생"
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              역할
            </label>
            <select
              name="role"
              value={formData.role}
              onChange={handleChange}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
            >
              <option value="student">학생</option>
              <option value="parent">학부모</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              관심사 (쉼표로 구분)
            </label>
            <input
              type="text"
              name="interests"
              value={formData.interests}
              onChange={handleChange}
              placeholder="AI, 로봇공학, 생명공학"
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
            />
          </div>

          <button
            type="submit"
            disabled={isLoading}
            className="w-full bg-indigo-600 hover:bg-indigo-700 text-white font-semibold py-3 px-4 rounded-lg transition disabled:opacity-50"
          >
            {isLoading ? '로그인 중...' : '시작하기'}
          </button>
        </form>

        <p className="text-center text-gray-600 text-sm mt-4">
          모든 학생과 학부모를 환영합니다 👋
        </p>
      </div>
    </div>
  )
}
