/**
 * BALE Frontend API Client
 * Connects to the real backend API for frontier analysis, negotiation, and export.
 */

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000/api'

// ==================== TYPES ====================

export interface FrontierAnalyzeRequest {
    contract_text: string
    contract_type: string
    jurisdiction: string
    industry: string
    effective_date?: string
    party_a: string
    party_b: string
    parties?: string[]
    contract_name: string
    include_negotiation: boolean
    your_position: string
    save_to_corpus: boolean
}

export interface FrontierAnalyzeResponse {
    analysis_id: string
    contract_id: string
    analyzed_at: string
    overall_frontier_risk: number
    risk_level: string
    critical_findings: string[]
    recommended_actions: string[]
    frontiers: FrontierResults
    negotiation_playbook?: NegotiationPlaybook
}

export interface FrontierResults {
    silence?: {
        silence_score: number
        total_expected: number
        total_present: number
        missing_clauses: string[]
    }
    archaeology?: {
        negotiation_intensity_score: number
        estimated_draft_layers: number
        template_vs_custom_ratio: number
        placeholder_scars: any[]
    }
    temporal?: {
        time_elapsed_days: number
        meaning_stability_index: number
        risk_delta: number
        applicable_doctrine_shifts: any[]
        review_urgency: string
    }
    strain?: {
        total_strain_score: number
        strain_points: any[]
        unstable_clauses: any[]
        litigation_landmines: string[]
    }
    social?: {
        relationship_type: string
        power_asymmetry_score: number
        dominant_party: string
        monitoring_intensity: number
        relationship_narrative: string
        structural_concerns: string[]
    }
    ambiguity?: {
        total_ambiguity_score: number
        interpretation_risk_score: number
        ambiguous_terms: any[]
        likely_intentional: string[]
    }
    dispute?: {
        total_dispute_probability: number
        high_risk_clause_count: number
        clause_predictions: DisputePrediction[]
        dispute_attractors: string[]
    }
    imagination?: {
        total_gap_exposure: number
        imagination_gaps: any[]
        novel_concepts: any[]
        needs_pioneering_attention: boolean
    }
    reflexive?: {
        contract_homogeneity_index: number
        term_convergence_rate: number
        alerts: string[]
    }
}

export interface DisputePrediction {
    clause_type: string
    dispute_probability: number
    expected_timeframe: string
}

export interface NegotiationPlaybook {
    contract_id: string
    your_position: string
    counterparty_power: number
    recommended_stance: string
    must_have: NegotiationSuggestion[]
    should_have: NegotiationSuggestion[]
    nice_to_have: NegotiationSuggestion[]
    walk_away_triggers: string[]
    concession_order: string[]
    total_risk_reduction: number
    estimated_difficulty: string
}

export interface NegotiationSuggestion {
    clause_type: string
    current_text: string
    suggested_text: string
    mitigation_type: string
    rationale: string
    market_comparison: string
    risk_reduction: number
    negotiation_difficulty: string
    priority: string
}

export interface CorpusStats {
    total_analyses: number
    total_entities: number
    avg_risk_score: number
    risk_distribution: Record<string, number>
    jurisdiction_distribution: Record<string, number>
    type_distribution: Record<string, number>
}

export interface StoredAnalysis {
    analysis_id: string
    contract_id: string
    contract_name: string
    contract_type: string
    jurisdiction: string
    industry: string
    risk_score: number
    frontier_risk: number
    analyzed_at: string
    parties: string[]
}

export interface EntityProfile {
    entity_id: string
    entity_name: string
    total_contracts: number
    avg_risk_score: number
    risk_trend: string
    last_updated: string
}

// ==================== API CLIENT ====================

class BaleApiClient {
    private baseUrl: string

    constructor(baseUrl: string = API_BASE) {
        this.baseUrl = baseUrl
    }

    private async request<T>(
        endpoint: string,
        options: RequestInit = {}
    ): Promise<T> {
        const url = `${this.baseUrl}${endpoint}`

        const response = await fetch(url, {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers,
            },
            ...options,
        })

        if (!response.ok) {
            const error = await response.json().catch(() => ({ detail: 'Unknown error' }))
            throw new Error(error.detail || `API error: ${response.status}`)
        }

        return response.json()
    }

    // ==================== FRONTIER ANALYSIS ====================

    async analyzeFrontier(request: FrontierAnalyzeRequest): Promise<FrontierAnalyzeResponse> {
        return this.request<FrontierAnalyzeResponse>('/frontier/analyze', {
            method: 'POST',
            body: JSON.stringify(request),
        })
    }

    async getAnalysis(analysisId: string): Promise<StoredAnalysis> {
        return this.request<StoredAnalysis>(`/frontier/analysis/${analysisId}`)
    }

    async listAnalyses(params?: {
        limit?: number
        contract_type?: string
        jurisdiction?: string
        min_risk?: number
    }): Promise<StoredAnalysis[]> {
        const searchParams = new URLSearchParams()
        if (params?.limit) searchParams.set('limit', params.limit.toString())
        if (params?.contract_type) searchParams.set('contract_type', params.contract_type)
        if (params?.jurisdiction) searchParams.set('jurisdiction', params.jurisdiction)
        if (params?.min_risk) searchParams.set('min_risk', params.min_risk.toString())

        const query = searchParams.toString()
        return this.request<StoredAnalysis[]>(`/frontier/analyses${query ? `?${query}` : ''}`)
    }

    // ==================== NEGOTIATION ====================

    async generateNegotiationPlaybook(
        contractText: string,
        jurisdiction: string = 'US',
        industry: string = 'technology',
        yourPosition: string = 'buyer'
    ): Promise<NegotiationPlaybook> {
        return this.request<NegotiationPlaybook>('/frontier/negotiate', {
            method: 'POST',
            body: JSON.stringify({
                contract_text: contractText,
                jurisdiction,
                industry,
                your_position: yourPosition,
            }),
        })
    }

    // ==================== EXPORT ====================

    async exportAnalysis(
        analysisId: string,
        format: 'markdown' | 'html' | 'json' = 'markdown',
        options?: {
            include_executive_summary?: boolean
            include_risk_analysis?: boolean
            include_frontier_insights?: boolean
            include_negotiation_playbook?: boolean
        }
    ): Promise<{ format: string; content: string; analysis_id: string }> {
        return this.request('/frontier/export', {
            method: 'POST',
            body: JSON.stringify({
                analysis_id: analysisId,
                format,
                ...options,
            }),
        })
    }

    // ==================== CORPUS ====================

    async getCorpusStats(): Promise<CorpusStats> {
        return this.request<CorpusStats>('/frontier/stats')
    }

    async listEntities(limit: number = 50): Promise<EntityProfile[]> {
        return this.request<EntityProfile[]>(`/frontier/entities?limit=${limit}`)
    }

    async getEntity(entityId: string): Promise<EntityProfile> {
        return this.request<EntityProfile>(`/frontier/entity/${entityId}`)
    }

    // ==================== BENCHMARKS ====================

    async getMarketBenchmarks(): Promise<Record<string, any>> {
        return this.request<Record<string, any>>('/frontier/benchmarks')
    }

    // ==================== HEALTH ====================

    async health(): Promise<{ status: string }> {
        return this.request<{ status: string }>('/health')
    }

    // ==================== V7 LOCAL RISK ANALYSIS ====================

    async analyzeClauseRisk(clauseText: string): Promise<V7RiskAnalysisResponse> {
        return this.request<V7RiskAnalysisResponse>('/v5/risk', {
            method: 'POST',
            body: JSON.stringify({ clause_text: clauseText }),
        })
    }

    async classifyClause(clauseText: string): Promise<V7ClassificationResponse> {
        return this.request<V7ClassificationResponse>('/v5/classify', {
            method: 'POST',
            body: JSON.stringify({ clause_text: clauseText }),
        })
    }

    async analyzeContractV7(contractText: string): Promise<V7ContractAnalysisResponse> {
        return this.request<V7ContractAnalysisResponse>('/v5/analyze-contract', {
            method: 'POST',
            body: JSON.stringify({ contract_text: contractText }),
        })
    }

    async getV7Status(): Promise<V7StatusResponse> {
        return this.request<V7StatusResponse>('/v5/status')
    }
}

// V7 Response Types
export interface V7RiskAnalysisResponse {
    risk_level: 'HIGH' | 'MEDIUM' | 'LOW' | 'UNKNOWN'
    risk_score: number
    reasoning: string
    problems: string[]
    recommendations: string[]
    model_version: string
}

export interface V7ClassificationResponse {
    clause_type: string
    confidence: number
    reasoning: string
    key_indicators: string[]
    model_version: string
}

export interface V7ContractAnalysisResponse {
    overall_risk_score: number
    total_sections: number
    high_risk_count: number
    medium_risk_count: number
    low_risk_count: number
    high_risk_clauses: V7ClauseAnalysis[]
    classifications: V7ClauseClassification[]
    model_version: string
}

export interface V7ClauseAnalysis {
    index: number
    text: string
    type: string
    risk_level: string
    risk_score: number
    problems: string[]
}

export interface V7ClauseClassification {
    index: number
    type: string
    confidence: number
}

export interface V7StatusResponse {
    v5_available: boolean
    model: string
    adapter_path: string
    loaded: boolean
}

// Singleton instance
export const baleApi = new BaleApiClient()

// ==================== REACT HOOKS ====================

import { useState, useCallback } from 'react'

export function useFrontierAnalysis() {
    const [loading, setLoading] = useState(false)
    const [error, setError] = useState<string | null>(null)
    const [result, setResult] = useState<FrontierAnalyzeResponse | null>(null)

    const analyze = useCallback(async (request: FrontierAnalyzeRequest) => {
        setLoading(true)
        setError(null)

        try {
            const response = await baleApi.analyzeFrontier(request)
            setResult(response)
            return response
        } catch (e) {
            const message = e instanceof Error ? e.message : 'Analysis failed'
            setError(message)
            throw e
        } finally {
            setLoading(false)
        }
    }, [])

    return { analyze, loading, error, result }
}

export function useCorpusStats() {
    const [loading, setLoading] = useState(false)
    const [stats, setStats] = useState<CorpusStats | null>(null)

    const refresh = useCallback(async () => {
        setLoading(true)
        try {
            const data = await baleApi.getCorpusStats()
            setStats(data)
        } catch (e) {
            console.error('Failed to load corpus stats:', e)
        } finally {
            setLoading(false)
        }
    }, [])

    return { stats, loading, refresh }
}

export function useAnalysisList() {
    const [loading, setLoading] = useState(false)
    const [analyses, setAnalyses] = useState<StoredAnalysis[]>([])

    const load = useCallback(async (params?: Parameters<typeof baleApi.listAnalyses>[0]) => {
        setLoading(true)
        try {
            const data = await baleApi.listAnalyses(params)
            setAnalyses(data)
        } catch (e) {
            console.error('Failed to load analyses:', e)
        } finally {
            setLoading(false)
        }
    }, [])

    return { analyses, loading, load }
}
