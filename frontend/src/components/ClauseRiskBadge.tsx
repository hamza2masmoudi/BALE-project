/**
 * ClauseRiskBadge - V7 Risk Analysis UI Component
 * Shows risk level with color coding and optional details
 */
import { useState, useCallback } from 'react'
import { baleApi, V7RiskAnalysisResponse, V7ClassificationResponse } from '../api/client'

// ==================== TYPES ====================

export type RiskLevel = 'HIGH' | 'MEDIUM' | 'LOW' | 'UNKNOWN'

interface ClauseRiskBadgeProps {
    clauseText: string
    showDetails?: boolean
    size?: 'sm' | 'md' | 'lg'
    autoAnalyze?: boolean
}

// ==================== HOOKS ====================

export function useV7RiskAnalysis() {
    const [loading, setLoading] = useState(false)
    const [error, setError] = useState<string | null>(null)
    const [result, setResult] = useState<V7RiskAnalysisResponse | null>(null)

    const analyze = useCallback(async (clauseText: string) => {
        setLoading(true)
        setError(null)

        try {
            const response = await baleApi.analyzeClauseRisk(clauseText)
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

    const reset = useCallback(() => {
        setResult(null)
        setError(null)
    }, [])

    return { analyze, loading, error, result, reset }
}

export function useV7Classification() {
    const [loading, setLoading] = useState(false)
    const [error, setError] = useState<string | null>(null)
    const [result, setResult] = useState<V7ClassificationResponse | null>(null)

    const classify = useCallback(async (clauseText: string) => {
        setLoading(true)
        setError(null)

        try {
            const response = await baleApi.classifyClause(clauseText)
            setResult(response)
            return response
        } catch (e) {
            const message = e instanceof Error ? e.message : 'Classification failed'
            setError(message)
            throw e
        } finally {
            setLoading(false)
        }
    }, [])

    return { classify, loading, error, result }
}

// ==================== COMPONENTS ====================

export function ClauseRiskBadge({
    clauseText,
    showDetails = false,
    size = 'md',
    autoAnalyze = false
}: ClauseRiskBadgeProps) {
    const { analyze, loading, error, result } = useV7RiskAnalysis()
    const [expanded, setExpanded] = useState(false)

    // Auto-analyze on mount if enabled
    const handleAnalyze = () => {
        if (!result && !loading) {
            analyze(clauseText)
        }
    }

    const riskLevel = result?.risk_level || 'UNKNOWN'

    const getColor = (level: RiskLevel) => {
        switch (level) {
            case 'HIGH': return 'var(--risk-high)'
            case 'MEDIUM': return 'var(--risk-medium)'
            case 'LOW': return 'var(--risk-low)'
            default: return 'var(--bale-text-muted)'
        }
    }

    const getBgColor = (level: RiskLevel) => {
        switch (level) {
            case 'HIGH': return 'var(--risk-bg-high)'
            case 'MEDIUM': return 'var(--risk-bg-medium)'
            case 'LOW': return 'var(--risk-bg-low)'
            default: return 'var(--bale-surface-elevated)'
        }
    }

    const sizeClasses = {
        sm: 'text-xs px-2 py-0.5',
        md: 'text-sm px-3 py-1',
        lg: 'text-base px-4 py-2'
    }

    if (!result && !loading) {
        return (
            <button
                onClick={handleAnalyze}
                className={`inline-flex items-center gap-1 rounded-full border border-[var(--bale-border)] bg-[var(--bale-surface)] hover:border-[var(--bale-accent)] transition-colors ${sizeClasses[size]}`}
            >
                <span className="text-[var(--bale-text-muted)]">🔍</span>
                <span className="text-[var(--bale-text-secondary)]">Analyze Risk</span>
            </button>
        )
    }

    if (loading) {
        return (
            <span className={`inline-flex items-center gap-2 rounded-full bg-[var(--bale-surface-elevated)] ${sizeClasses[size]}`}>
                <span className="spinner w-3 h-3"></span>
                <span className="text-[var(--bale-text-muted)]">Analyzing...</span>
            </span>
        )
    }

    if (error) {
        return (
            <span className={`inline-flex items-center gap-1 rounded-full bg-[var(--risk-bg-high)] text-[var(--risk-high)] ${sizeClasses[size]}`}>
                ⚠️ {error}
            </span>
        )
    }

    return (
        <div className="inline-block">
            <button
                onClick={() => showDetails && setExpanded(!expanded)}
                className={`inline-flex items-center gap-2 rounded-full ${sizeClasses[size]} transition-all`}
                style={{
                    backgroundColor: getBgColor(riskLevel),
                    color: getColor(riskLevel),
                    border: `1px solid ${getColor(riskLevel)}22`
                }}
            >
                <span className="font-semibold">{riskLevel}</span>
                {result && (
                    <span className="opacity-75">{result.risk_score.toFixed(0)}%</span>
                )}
                {showDetails && (
                    <svg
                        className={`w-3 h-3 transition-transform ${expanded ? 'rotate-180' : ''}`}
                        fill="none"
                        viewBox="0 0 24 24"
                        stroke="currentColor"
                    >
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                    </svg>
                )}
            </button>

            {expanded && result && (
                <div
                    className="mt-2 p-3 rounded-lg text-sm"
                    style={{ backgroundColor: getBgColor(riskLevel) + '44' }}
                >
                    <div className="text-[var(--bale-text-secondary)] mb-2">
                        {result.reasoning.substring(0, 200)}...
                    </div>

                    {result.problems.length > 0 && (
                        <div className="mb-2">
                            <div className="font-medium text-[var(--risk-high)] mb-1">Problems:</div>
                            <ul className="list-disc list-inside text-xs space-y-1">
                                {result.problems.slice(0, 3).map((p, i) => (
                                    <li key={i} className="text-[var(--bale-text-secondary)]">{p}</li>
                                ))}
                            </ul>
                        </div>
                    )}

                    {result.recommendations.length > 0 && (
                        <div>
                            <div className="font-medium text-[var(--risk-low)] mb-1">Recommendations:</div>
                            <ul className="list-disc list-inside text-xs space-y-1">
                                {result.recommendations.slice(0, 2).map((r, i) => (
                                    <li key={i} className="text-[var(--bale-text-secondary)]">{r}</li>
                                ))}
                            </ul>
                        </div>
                    )}

                    <div className="mt-2 text-xs text-[var(--bale-text-muted)]">
                        Model: {result.model_version}
                    </div>
                </div>
            )}
        </div>
    )
}

/**
 * ClauseCard - Full clause display with classification and risk
 */
interface ClauseCardProps {
    clauseText: string
    index: number
    type?: string
    riskLevel?: RiskLevel
    riskScore?: number
    problems?: string[]
}

export function ClauseCard({
    clauseText,
    index,
    type,
    riskLevel = 'UNKNOWN',
    riskScore = 0,
    problems = []
}: ClauseCardProps) {
    const [expanded, setExpanded] = useState(false)

    const getColor = (level: RiskLevel) => {
        switch (level) {
            case 'HIGH': return 'var(--risk-high)'
            case 'MEDIUM': return 'var(--risk-medium)'
            case 'LOW': return 'var(--risk-low)'
            default: return 'var(--bale-text-muted)'
        }
    }

    return (
        <div
            className="card border-l-4 transition-all hover:shadow-lg cursor-pointer"
            style={{ borderLeftColor: getColor(riskLevel) }}
            onClick={() => setExpanded(!expanded)}
        >
            <div className="flex items-start justify-between gap-4">
                <div className="flex-1">
                    <div className="flex items-center gap-2 mb-2">
                        <span className="badge">{index + 1}</span>
                        {type && (
                            <span className="badge badge-info capitalize">
                                {type.replace(/_/g, ' ')}
                            </span>
                        )}
                    </div>
                    <p className="text-sm text-[var(--bale-text-secondary)] line-clamp-2">
                        {clauseText}
                    </p>
                </div>

                <div className="flex-shrink-0 flex items-center gap-2">
                    <span
                        className="px-3 py-1 rounded-full text-sm font-semibold"
                        style={{
                            color: getColor(riskLevel),
                            backgroundColor: getColor(riskLevel) + '22'
                        }}
                    >
                        {riskLevel} {riskScore > 0 && `(${riskScore}%)`}
                    </span>
                </div>
            </div>

            {expanded && (
                <div className="mt-4 pt-4 border-t border-[var(--bale-border)]">
                    <p className="text-sm text-[var(--bale-text-secondary)] mb-3">
                        {clauseText}
                    </p>

                    {problems.length > 0 && (
                        <div className="p-3 rounded-lg bg-[var(--risk-bg-high)]">
                            <div className="font-medium text-[var(--risk-high)] mb-2">⚠️ Issues Detected</div>
                            <ul className="space-y-1">
                                {problems.map((p, i) => (
                                    <li key={i} className="text-sm text-[var(--bale-text-secondary)] flex items-start gap-2">
                                        <span className="text-[var(--risk-high)]">•</span>
                                        {p}
                                    </li>
                                ))}
                            </ul>
                        </div>
                    )}
                </div>
            )}
        </div>
    )
}

/**
 * V7AnalysisSummary - Dashboard summary widget for V7 contract analysis
 */
interface V7AnalysisSummaryProps {
    highRiskCount: number
    mediumRiskCount: number
    lowRiskCount: number
    overallScore: number
    modelVersion?: string
}

export function V7AnalysisSummary({
    highRiskCount,
    mediumRiskCount,
    lowRiskCount,
    overallScore,
    modelVersion = 'V7'
}: V7AnalysisSummaryProps) {
    const total = highRiskCount + mediumRiskCount + lowRiskCount

    return (
        <div className="card bg-gradient-to-br from-[var(--bale-surface)] to-[var(--bale-surface-elevated)]">
            <div className="flex items-center justify-between mb-4">
                <h3 className="text-title">Clause Risk Analysis</h3>
                <span className="badge badge-info">{modelVersion}</span>
            </div>

            <div className="grid grid-cols-3 gap-4 mb-4">
                <div className="text-center p-3 rounded-lg bg-[var(--risk-bg-high)]">
                    <div className="text-2xl font-bold text-[var(--risk-high)]">{highRiskCount}</div>
                    <div className="text-xs text-[var(--bale-text-muted)]">High Risk</div>
                </div>
                <div className="text-center p-3 rounded-lg bg-[var(--risk-bg-medium)]">
                    <div className="text-2xl font-bold text-[var(--risk-medium)]">{mediumRiskCount}</div>
                    <div className="text-xs text-[var(--bale-text-muted)]">Medium</div>
                </div>
                <div className="text-center p-3 rounded-lg bg-[var(--risk-bg-low)]">
                    <div className="text-2xl font-bold text-[var(--risk-low)]">{lowRiskCount}</div>
                    <div className="text-xs text-[var(--bale-text-muted)]">Low Risk</div>
                </div>
            </div>

            <div className="flex items-center gap-3">
                <div className="flex-1 h-2 bg-[var(--bale-surface-elevated)] rounded-full overflow-hidden">
                    <div
                        className="h-full bg-[var(--risk-high)]"
                        style={{ width: `${total > 0 ? (highRiskCount / total) * 100 : 0}%` }}
                    />
                </div>
                <span className="text-sm font-medium">
                    Score: <span className={overallScore > 50 ? 'text-[var(--risk-high)]' : 'text-[var(--risk-low)]'}>
                        {overallScore.toFixed(0)}%
                    </span>
                </span>
            </div>

            <div className="mt-3 text-xs text-[var(--bale-text-muted)] text-center">
                🌍 Multilingual • 👔 Employment Law • 🤝 M&A
            </div>
        </div>
    )
}

export default ClauseRiskBadge
