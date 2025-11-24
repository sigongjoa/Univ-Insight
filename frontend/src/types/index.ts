/**
 * API Response Types
 */
export interface User {
  id: string
  name: string
  role: 'student' | 'parent'
  interests: string[]
  notion_page_id?: string
  created_at: string
}

export interface ResearchPaper {
  id: string
  title: string
  university: string
  date?: string
  pub_date?: string
  summary_preview: string
  university_tier?: number
}

export interface CareerPath {
  companies?: string[]
  related_companies?: string[]
  job_title?: string
  salary_hint?: string
}

export interface ActionItem {
  subjects?: string[]
  research_topic?: string
}

export interface Analysis {
  paper_id?: string
  title?: string
  university?: string
  analysis?: string
  easy_summary?: string
  career_path?: CareerPath
  action_items?: ActionItem
}

export interface PlanBSuggestion {
  paper_id: string
  title: string
  university: string
  university_tier: number
  summary: string
  similarity_score: number
  reason: string
}

export interface Report {
  id: string
  user_id?: string
  papers?: ResearchPaper[]
  papers_count?: number
  sent_at?: string
  created_at?: string
  status: 'pending' | 'sent' | 'failed' | 'completed'
  notion_page_url?: string
}

/**
 * API Request Types
 */
export interface LoginRequest {
  user_id: string
  name: string
  role: 'student' | 'parent'
  interests?: string[]
}

export interface UpdateProfileRequest {
  user_id: string
  name: string
  role: string
  interests: string[]
}

export interface GenerateReportRequest {
  user_id: string
}

/**
 * List Response Types
 */
export interface ListResponse<T> {
  total_count: number
  items: T[]
}

/**
 * Generic API Response
 */
export interface ApiResponse<T = any> {
  status: string
  data?: T
  message?: string
  error?: string
}

/**
 * Auth Types
 */
export interface AuthToken {
  access_token: string
  token_type: string
}

export interface AuthState {
  user: User | null
  isLoading: boolean
  error: string | null
}
