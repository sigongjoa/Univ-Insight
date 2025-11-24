import apiClient from './api'
import { ResearchPaper, Analysis, PlanBSuggestion, ListResponse } from '../types'

/**
 * Paper Service
 * Handles research paper related API calls
 */
export const paperService = {
  /**
   * Get list of research papers
   */
  listPapers: async (params?: {
    university?: string
    topic?: string
    limit?: number
    offset?: number
  }): Promise<ListResponse<ResearchPaper>> => {
    const response = await apiClient.get('/research', { params })
    return response.data
  },

  /**
   * Get detailed analysis of a paper
   */
  getPaperAnalysis: async (paperId: string): Promise<Analysis> => {
    const response = await apiClient.get(`/research/${paperId}/analysis`)
    return response.data
  },

  /**
   * Get Plan B suggestions for a paper
   */
  getPlanBSuggestions: async (paperId: string): Promise<{
    original_paper: {
      title: string
      university: string
      university_tier: number
    }
    plan_b_suggestions: PlanBSuggestion[]
  }> => {
    const response = await apiClient.get(`/research/${paperId}/plan-b`)
    return response.data
  },
}
