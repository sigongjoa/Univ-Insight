import apiClient from './api'

/**
 * Report Service
 * Handles report generation and retrieval
 */
export const reportService = {
  /**
   * Generate a personalized report for user
   */
  generateReport: async (userId: string): Promise<{
    status: string
    report_id: string
    papers: Array<{
      paper_id: string
      title: string
      summary: string
    }>
  }> => {
    const response = await apiClient.post('/reports/generate', null, {
      params: { user_id: userId },
    })
    return response.data
  },
}
