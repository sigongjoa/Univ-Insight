import apiClient from './api'
import type { User, UpdateProfileRequest } from '../types'

/**
 * User Service
 * Handles user-related API calls
 */
export const userService = {
  /**
   * Get user profile
   */
  getProfile: async (userId: string): Promise<User> => {
    const response = await apiClient.get(`/users/${userId}`)
    return response.data
  },

  /**
   * Update user profile
   */
  updateProfile: async (data: UpdateProfileRequest): Promise<{ status: string; user_id: string }> => {
    const response = await apiClient.post('/users/profile', {
      user_id: data.user_id,
      name: data.name,
      role: data.role,
      interests: data.interests,
    })
    return response.data
  },

  /**
   * Save auth token and user to localStorage
   */
  saveAuthData: (token: string, user: User) => {
    localStorage.setItem('auth_token', token)
    localStorage.setItem('user', JSON.stringify(user))
  },

  /**
   * Get saved user from localStorage
   */
  getSavedUser: (): User | null => {
    const user = localStorage.getItem('user')
    return user ? JSON.parse(user) : null
  },

  /**
   * Clear auth data
   */
  clearAuthData: () => {
    localStorage.removeItem('auth_token')
    localStorage.removeItem('user')
  },
}
