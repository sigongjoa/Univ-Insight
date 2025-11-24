import { create } from 'zustand'
import { User } from '../types'
import { userService } from '../services/userService'

/**
 * Auth Store
 * Manages user authentication state
 */
interface AuthStore {
  user: User | null
  isAuthenticated: boolean
  isLoading: boolean
  error: string | null

  // Actions
  setUser: (user: User | null) => void
  setLoading: (loading: boolean) => void
  setError: (error: string | null) => void
  logout: () => void
  loadUserFromStorage: () => void
}

export const useAuthStore = create<AuthStore>((set) => ({
  user: null,
  isAuthenticated: false,
  isLoading: false,
  error: null,

  setUser: (user) => {
    set({
      user,
      isAuthenticated: !!user,
      error: null,
    })
    if (user) {
      userService.saveAuthData('', user)
    }
  },

  setLoading: (loading) => set({ isLoading: loading }),

  setError: (error) => set({ error }),

  logout: () => {
    set({
      user: null,
      isAuthenticated: false,
      error: null,
    })
    userService.clearAuthData()
  },

  loadUserFromStorage: () => {
    const savedUser = userService.getSavedUser()
    if (savedUser) {
      set({
        user: savedUser,
        isAuthenticated: true,
      })
    }
  },
}))
