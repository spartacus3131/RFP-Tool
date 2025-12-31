import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Quick Scan API
export const quickScan = {
  scan: async (url: string) => {
    const response = await api.post('/api/quick-scan/', { url })
    return response.data
  },
  getSupportedDomains: async () => {
    const response = await api.get('/api/quick-scan/supported-domains')
    return response.data
  },
}

// RFP API
export const rfpApi = {
  upload: async (file: File) => {
    const formData = new FormData()
    formData.append('file', file)
    const response = await api.post('/api/rfp/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    return response.data
  },
  get: async (id: string) => {
    const response = await api.get(`/api/rfp/${id}`)
    return response.data
  },
  getDetail: async (id: string) => {
    const response = await api.get(`/api/rfp/${id}/detail`)
    return response.data
  },
  extract: async (id: string) => {
    const response = await api.post(`/api/rfp/${id}/extract`)
    return response.data
  },
  getEvidence: async (id: string, fieldName: string) => {
    const response = await api.get(`/api/rfp/${id}/evidence/${fieldName}`)
    return response.data
  },
  update: async (id: string, updates: Record<string, any>) => {
    const response = await api.patch(`/api/rfp/${id}`, updates)
    return response.data
  },
  decide: async (id: string, decision: 'go' | 'no_go', notes?: string) => {
    const response = await api.post(`/api/rfp/${id}/decide`, { decision, notes })
    return response.data
  },
}

// Dashboard API
export const dashboardApi = {
  get: async () => {
    const response = await api.get('/api/dashboard/')
    return response.data
  },
  listRfps: async (params?: { status?: string; client?: string }) => {
    const response = await api.get('/api/dashboard/rfps', { params })
    return response.data
  },
}

// Budget API
export const budgetApi = {
  upload: async (file: File, municipality: string, fiscalYear: string) => {
    const formData = new FormData()
    formData.append('file', file)
    const response = await api.post(
      `/api/budgets/upload?municipality=${encodeURIComponent(municipality)}&fiscal_year=${encodeURIComponent(fiscalYear)}`,
      formData,
      { headers: { 'Content-Type': 'multipart/form-data' } }
    )
    return response.data
  },
  extract: async (budgetId: string) => {
    const response = await api.post(`/api/budgets/${budgetId}/extract`)
    return response.data
  },
  list: async () => {
    const response = await api.get('/api/budgets/')
    return response.data
  },
  getItems: async (budgetId: string) => {
    const response = await api.get(`/api/budgets/${budgetId}/items`)
    return response.data
  },
  matchToRfp: async (rfpId: string) => {
    const response = await api.get(`/api/budgets/match/${rfpId}`)
    return response.data
  },
}

// Sub-Consultants API
export interface SubConsultantData {
  company_name: string
  discipline: string
  tier: 'tier_1' | 'tier_2'
  primary_contact_name?: string
  primary_contact_email?: string
  primary_contact_phone?: string
  past_joint_projects?: number
  win_rate_together?: number
  typical_fee_range_low?: number
  typical_fee_range_high?: number
  notes?: string
}

export const subConsultantsApi = {
  list: async (params?: { discipline?: string; tier?: string }) => {
    const response = await api.get('/api/subconsultants/', { params })
    return response.data
  },
  get: async (id: string) => {
    const response = await api.get(`/api/subconsultants/${id}`)
    return response.data
  },
  create: async (data: SubConsultantData) => {
    const response = await api.post('/api/subconsultants/', data)
    return response.data
  },
  update: async (id: string, data: SubConsultantData) => {
    const response = await api.put(`/api/subconsultants/${id}`, data)
    return response.data
  },
  delete: async (id: string) => {
    const response = await api.delete(`/api/subconsultants/${id}`)
    return response.data
  },
  match: async (disciplines: string[]) => {
    const response = await api.get('/api/subconsultants/match', {
      params: { disciplines: disciplines.join(',') },
    })
    return response.data
  },
}
