
import apiClient from './api'

export interface University {
    id: string
    name: string
    name_ko: string
    location: string
    ranking?: number
    tier?: string
    url?: string
    description?: string
    established_year?: number
    college_count?: number
}

export interface Paper {
    id: string
    title: string
    url?: string
    abstract?: string
    crawled_at?: string
    keywords?: string[]
}

export interface PapersListResponse {
    total_count: number
    items: Paper[]
}

export interface UniversityListResponse {
    total_count: number
    items: University[]
}

export interface CrawlResponse {
    status: string
    university_id: string
    target_url: string
    message: string
}

export const universityService = {
    /**
     * Get list of universities
     */
    getUniversities: async (): Promise<UniversityListResponse> => {
        const response = await apiClient.get('/universities')
        return response.data
    },

    /**
     * Get university details
     */
    getUniversity: async (id: string): Promise<University> => {
        const response = await apiClient.get(`/universities/${id}`)
        return response.data
    },

    /**
     * Get papers for a university
     */
    getPapers: async (id: string): Promise<PapersListResponse> => {
        const response = await apiClient.get(`/universities/${id}/papers`)
        return response.data
    },

    /**
     * Trigger crawling for a university
     */
    crawlUniversity: async (id: string, targetUrl?: string): Promise<CrawlResponse> => {
        const response = await apiClient.post('/admin/crawl', {
            university_id: id,
            target_url: targetUrl
        })
        return response.data
    }
}
