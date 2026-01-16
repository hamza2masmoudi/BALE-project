import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { baleApi, useCorpusStats, useAnalysisList, StoredAnalysis, CorpusStats } from '../api/client'

function getRiskColor(risk: number): string {
    if (risk < 30) return 'risk-low'
    if (risk < 60) return 'risk-medium'
    return 'risk-high'
}

function getRiskBg(risk: number): string {
    if (risk < 30) return 'risk-bg-low'
    if (risk < 60) return 'risk-bg-medium'
    return 'risk-bg-high'
}

function getStatusBadge(risk: number) {
    if (risk < 30) return 'badge-success'
    if (risk < 60) return 'badge-warning'
    return 'badge-danger'
}

function getStatus(risk: number): string {
    if (risk < 30) return 'complete'
    if (risk < 60) return 'review'
    return 'critical'
}

function timeAgo(dateString: string): string {
    const date = new Date(dateString)
    const now = new Date()
    const seconds = Math.floor((now.getTime() - date.getTime()) / 1000)

    if (seconds < 60) return 'Just now'
    if (seconds < 3600) return `${Math.floor(seconds / 60)}m ago`
    if (seconds < 86400) return `${Math.floor(seconds / 3600)}h ago`
    return `${Math.floor(seconds / 86400)}d ago`
}

function Dashboard() {
    const { stats, loading: statsLoading, refresh: refreshStats } = useCorpusStats()
    const { analyses, loading: analysesLoading, load: loadAnalyses } = useAnalysisList()
    const [isLoading, setIsLoading] = useState(true)

    useEffect(() => {
        const loadData = async () => {
            try {
                await Promise.all([
                    refreshStats(),
                    loadAnalyses({ limit: 5 })
                ])
            } catch (e) {
                console.error('Failed to load dashboard data:', e)
            } finally {
                setIsLoading(false)
            }
        }
        loadData()
    }, [])

    const displayStats = stats || {
        total_analyses: 0,
        avg_risk_score: 0,
        risk_distribution: { low: 0, medium: 0, high: 0 },
        total_entities: 0,
        jurisdiction_distribution: {},
        type_distribution: {},
    }

    const criticalCount = displayStats.risk_distribution.high || 0
    const pendingReview = displayStats.risk_distribution.medium || 0

    return (
        <div className="fade-in">
            {/* Header */}
            <div className="page-header flex items-center justify-between">
                <div>
                    <h1 className="page-title">Dashboard</h1>
                    <p className="page-description">Overview of your legal intelligence</p>
                </div>
                <Link to="/analyze" className="btn btn-primary btn-lg">
                    <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                    </svg>
                    New Analysis
                </Link>
            </div>

            {/* Stats Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
                <StatCard
                    label="Contracts Analyzed"
                    value={displayStats.total_analyses}
                    change="Total in corpus"
                    icon="📄"
                    loading={isLoading}
                />
                <StatCard
                    label="Avg Risk Score"
                    value={`${displayStats.avg_risk_score.toFixed(0)}%`}
                    change={displayStats.avg_risk_score < 40 ? "Good standing" : "Needs attention"}
                    icon="📊"
                    positive={displayStats.avg_risk_score < 40}
                    loading={isLoading}
                />
                <StatCard
                    label="Critical Findings"
                    value={criticalCount}
                    change="High-risk contracts"
                    icon="⚠️"
                    loading={isLoading}
                />
                <StatCard
                    label="Pending Review"
                    value={pendingReview}
                    change="Medium-risk contracts"
                    icon="⏰"
                    loading={isLoading}
                />
            </div>

            {/* Main Content Grid */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Recent Analyses */}
                <div className="lg:col-span-2">
                    <div className="card">
                        <div className="flex items-center justify-between mb-6">
                            <h2 className="text-title">Recent Analyses</h2>
                            <Link to="/contracts" className="btn btn-ghost text-small">
                                View All →
                            </Link>
                        </div>

                        {analysesLoading ? (
                            <div className="space-y-3">
                                {[...Array(3)].map((_, i) => (
                                    <div key={i} className="skeleton h-20"></div>
                                ))}
                            </div>
                        ) : analyses.length === 0 ? (
                            <div className="text-center py-12 text-[var(--bale-text-muted)]">
                                <div className="text-4xl mb-4">📄</div>
                                <p>No analyses yet</p>
                                <Link to="/analyze" className="btn btn-primary mt-4">
                                    Analyze Your First Contract
                                </Link>
                            </div>
                        ) : (
                            <div className="space-y-3">
                                {analyses.map((analysis) => (
                                    <Link
                                        key={analysis.analysis_id}
                                        to={`/frontier/${analysis.analysis_id}`}
                                        className="flex items-center justify-between p-4 bg-[var(--bale-surface-elevated)] rounded-lg hover:bg-[var(--bale-border)] transition-colors"
                                    >
                                        <div className="flex items-center gap-4">
                                            <div className={`w-12 h-12 rounded-lg ${getRiskBg(analysis.risk_score)} flex items-center justify-center`}>
                                                <span className={`text-lg font-bold ${getRiskColor(analysis.risk_score)}`}>
                                                    {analysis.risk_score}
                                                </span>
                                            </div>
                                            <div>
                                                <div className="font-medium">{analysis.contract_name}</div>
                                                <div className="text-small text-[var(--bale-text-muted)]">
                                                    {analysis.contract_type.toUpperCase()} • {timeAgo(analysis.analyzed_at)}
                                                </div>
                                            </div>
                                        </div>
                                        <span className={`badge ${getStatusBadge(analysis.risk_score)}`}>
                                            {getStatus(analysis.risk_score)}
                                        </span>
                                    </Link>
                                ))}
                            </div>
                        )}
                    </div>
                </div>

                {/* Quick Stats */}
                <div className="lg:col-span-1">
                    <div className="card">
                        <h2 className="text-title mb-6">Corpus Overview</h2>

                        <div className="space-y-4">
                            <div className="p-4 bg-[var(--bale-surface-elevated)] rounded-lg">
                                <div className="text-2xl font-bold">{displayStats.total_entities}</div>
                                <div className="text-small text-[var(--bale-text-muted)]">
                                    Tracked Entities
                                </div>
                            </div>

                            {Object.keys(displayStats.jurisdiction_distribution).length > 0 && (
                                <div className="p-4 bg-[var(--bale-surface-elevated)] rounded-lg">
                                    <div className="text-small font-medium mb-2">By Jurisdiction</div>
                                    {Object.entries(displayStats.jurisdiction_distribution).slice(0, 3).map(([jur, count]) => (
                                        <div key={jur} className="flex justify-between text-small text-[var(--bale-text-muted)]">
                                            <span>{jur}</span>
                                            <span>{count}</span>
                                        </div>
                                    ))}
                                </div>
                            )}

                            {Object.keys(displayStats.type_distribution).length > 0 && (
                                <div className="p-4 bg-[var(--bale-surface-elevated)] rounded-lg">
                                    <div className="text-small font-medium mb-2">By Type</div>
                                    {Object.entries(displayStats.type_distribution).slice(0, 3).map(([type, count]) => (
                                        <div key={type} className="flex justify-between text-small text-[var(--bale-text-muted)]">
                                            <span>{type.toUpperCase()}</span>
                                            <span>{count}</span>
                                        </div>
                                    ))}
                                </div>
                            )}
                        </div>

                        <Link
                            to="/frontier"
                            className="btn btn-secondary w-full mt-6"
                        >
                            View All Frontiers
                        </Link>
                    </div>
                </div>
            </div>

            {/* Risk Distribution */}
            <div className="mt-8">
                <div className="card">
                    <h2 className="text-title mb-6">Risk Distribution</h2>
                    <RiskDistributionChart distribution={displayStats.risk_distribution} />
                </div>
            </div>
        </div>
    )
}

// Stat Card Component
function StatCard({
    label,
    value,
    change,
    icon,
    positive = false,
    loading = false
}: {
    label: string
    value: string | number
    change: string
    icon: string
    positive?: boolean
    loading?: boolean
}) {
    if (loading) {
        return (
            <div className="card">
                <div className="skeleton h-4 w-20 mb-3"></div>
                <div className="skeleton h-8 w-16 mb-2"></div>
                <div className="skeleton h-3 w-24"></div>
            </div>
        )
    }

    return (
        <div className="card hover:border-[var(--bale-border-strong)] transition-colors">
            <div className="flex items-center justify-between mb-2">
                <span className="text-small text-[var(--bale-text-muted)]">{label}</span>
                <span className="text-xl">{icon}</span>
            </div>
            <div className="text-display mb-1">{value}</div>
            <div className={`text-small ${positive ? 'text-[var(--risk-low)]' : 'text-[var(--bale-text-muted)]'}`}>
                {change}
            </div>
        </div>
    )
}

// Risk Distribution Chart
function RiskDistributionChart({ distribution }: { distribution: Record<string, number> }) {
    const data = [
        { range: 'Low (0-30%)', count: distribution.low || 0, color: 'var(--risk-low)' },
        { range: 'Medium (30-60%)', count: distribution.medium || 0, color: 'var(--risk-medium)' },
        { range: 'High (60%+)', count: distribution.high || 0, color: 'var(--risk-high)' },
    ]

    const max = Math.max(...data.map(d => d.count), 1)

    return (
        <div className="flex items-end justify-around gap-8 h-48">
            {data.map((d, idx) => (
                <div key={idx} className="flex-1 flex flex-col items-center max-w-32">
                    <div
                        className="w-full rounded-t-md transition-all hover:opacity-80"
                        style={{
                            height: `${Math.max((d.count / max) * 100, 5)}%`,
                            backgroundColor: d.color,
                            minHeight: '20px'
                        }}
                    ></div>
                    <div className="mt-2 text-center">
                        <div className="font-bold text-xl">{d.count}</div>
                        <div className="text-caption text-[var(--bale-text-muted)]">{d.range}</div>
                    </div>
                </div>
            ))}
        </div>
    )
}

export default Dashboard
