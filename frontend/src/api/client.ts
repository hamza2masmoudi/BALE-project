/**
 * BALE API Client
 * TypeScript client for interacting with the BALE backend.
 */

const API_BASE = import.meta.env.VITE_API_URL || '/api';

// ==================== TYPES ====================

export interface AnalysisRequest {
    clause_text: string;
    jurisdiction?: string;
    depth?: 'quick' | 'standard' | 'deep';
    include_harmonization?: boolean;
    inference_mode?: 'auto' | 'local' | 'mistral';
}

export interface AnalysisResult {
    id: string;
    verdict: {
        risk_score: number;
        verdict: string;
        confidence: number;
        factors_applied: DecisionFactor[];
        interpretive_gap: number;
        civilist_summary: string;
        commonist_summary: string;
        synthesis: string;
    };
    harmonization?: {
        golden_clause: string;
        rationale: string;
        risk_reduction: number;
    };
    processing_time_ms: number;
    inference_mode_used: string;
}

export interface DecisionFactor {
    rule_name: string;
    rule_description: string;
    triggered: boolean;
    impact_on_risk: number;
    evidence: string;
}

export interface Contract {
    id: string;
    name: string;
    jurisdiction: string;
    status: 'active' | 'archived';
    risk_score?: number;
    clause_count?: number;
    created_at: string;
    updated_at: string;
}

export interface DashboardData {
    summary: {
        total_analyses: number;
        avg_risk_score: number;
        high_risk_count: number;
        low_risk_count: number;
        by_jurisdiction: Record<string, number>;
    };
    risk_trend: Array<{ date: string; risk: number }>;
    jurisdiction_breakdown: Record<string, { count: number; avg_risk: number }>;
    recent_high_risk: Array<{ id: string; risk_score: number; jurisdiction: string }>;
}

export interface JobStatus {
    id: string;
    task_name: string;
    status: 'pending' | 'running' | 'completed' | 'failed' | 'cancelled';
    progress: number;
    created_at: string;
    completed_at?: string;
    result?: unknown;
    error?: string;
}

// ==================== API CLIENT ====================

class BaleAPIClient {
    private baseUrl: string;
    private token: string | null = null;

    constructor(baseUrl: string = API_BASE) {
        this.baseUrl = baseUrl;
    }

    setToken(token: string) {
        this.token = token;
    }

    private async request<T>(
        endpoint: string,
        options: RequestInit = {}
    ): Promise<T> {
        const headers: Record<string, string> = {
            'Content-Type': 'application/json',
            ...(options.headers as Record<string, string> || {})
        };

        if (this.token) {
            headers['Authorization'] = `Bearer ${this.token}`;
        }

        const response = await fetch(`${this.baseUrl}${endpoint}`, {
            ...options,
            headers
        });

        if (!response.ok) {
            const error = await response.json().catch(() => ({}));
            throw new Error(error.error || `HTTP ${response.status}`);
        }

        return response.json();
    }

    // Health
    async health() {
        return this.request<{ status: string; version: string }>('/health');
    }

    // Analysis
    async analyze(request: AnalysisRequest): Promise<AnalysisResult> {
        return this.request<AnalysisResult>('/v1/analyze', {
            method: 'POST',
            body: JSON.stringify(request)
        });
    }

    async simulate(clause_text: string, jurisdiction?: string) {
        return this.request('/v1/simulate', {
            method: 'POST',
            body: JSON.stringify({ clause_text, jurisdiction })
        });
    }

    // Contracts
    async listContracts(params?: { page?: number; limit?: number; status?: string }) {
        const query = new URLSearchParams(params as Record<string, string>).toString();
        return this.request<{ items: Contract[]; total: number }>(`/v1/contracts?${query}`);
    }

    async getContract(id: string): Promise<Contract> {
        return this.request<Contract>(`/v1/contracts/${id}`);
    }

    async createContract(data: { name: string; content: string; jurisdiction: string }) {
        return this.request<Contract>('/v1/contracts', {
            method: 'POST',
            body: JSON.stringify(data)
        });
    }

    async updateContract(id: string, data: Partial<Contract>) {
        return this.request<Contract>(`/v1/contracts/${id}`, {
            method: 'PATCH',
            body: JSON.stringify(data)
        });
    }

    async deleteContract(id: string) {
        return this.request(`/v1/contracts/${id}`, { method: 'DELETE' });
    }

    // Analytics
    async getDashboard(): Promise<DashboardData> {
        return this.request<DashboardData>('/v1/analytics/dashboard');
    }

    async getAnalyticsSummary(timeRange: string = '7d') {
        return this.request(`/v1/analytics/summary?time_range=${timeRange}`);
    }

    async getRiskTrend(days: number = 30) {
        return this.request<Array<{ date: string; risk: number }>>(
            `/v1/analytics/risk-trend?days=${days}`
        );
    }

    // Jobs
    async startBulkAnalysis(contractId: string, clauses: string[], jurisdiction?: string) {
        return this.request<JobStatus>('/v1/jobs/bulk-analysis', {
            method: 'POST',
            body: JSON.stringify({ contract_id: contractId, clauses, jurisdiction })
        });
    }

    async getJobStatus(jobId: string): Promise<JobStatus> {
        return this.request<JobStatus>(`/v1/jobs/${jobId}`);
    }

    async cancelJob(jobId: string) {
        return this.request(`/v1/jobs/${jobId}`, { method: 'DELETE' });
    }

    // Reports
    async generateReport(format: 'html' | 'json' | 'markdown', timeRange: string = '7d') {
        return this.request('/v1/reports/generate', {
            method: 'POST',
            body: JSON.stringify({ format, time_range: timeRange })
        });
    }

    // WebSocket
    createWebSocket(userId: string): WebSocket {
        const wsUrl = this.baseUrl.replace('http', 'ws') + `/ws/${userId}`;
        return new WebSocket(wsUrl);
    }

    // SSE
    createAnalysisStream(analysisId: string): EventSource {
        return new EventSource(`${this.baseUrl}/v1/analyze/${analysisId}/stream`);
    }
}

// Export singleton instance
export const api = new BaleAPIClient();

// Export class for custom instances
export { BaleAPIClient };
