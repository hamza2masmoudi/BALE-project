import { useState, useEffect } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useCorpusStats, useAnalysisList } from '../api/client'

function Dashboard() {
    const navigate = useNavigate()
    const { stats, loading: _statsLoading, refresh: refreshStats } = useCorpusStats()
    const { analyses, loading: _analysesLoading, load: loadAnalyses } = useAnalysisList()
    const [isLoading, setIsLoading] = useState(true)

    useEffect(() => {
        const loadData = async () => {
            try {
                await Promise.all([refreshStats(), loadAnalyses({ limit: 5 })])
            } catch (e) {
                console.error('Failed to load:', e)
            } finally {
                setIsLoading(false)
            }
        }
        loadData()
    }, [])

    const hasData = stats && stats.total_analyses > 0

    return (
        <div className="fade-in max-w-5xl mx-auto">
            {/* Hero Section - Clean Entry Point */}
            <div className="text-center py-12">
                <h1 className="text-4xl font-bold text-[var(--bale-text)] mb-3">
                    Welcome to BALE
                </h1>
                <p className="text-lg text-[var(--bale-text-muted)] mb-8 max-w-xl mx-auto">
                    Your AI-powered legal intelligence assistant. Analyze contracts,
                    get insights, and make informed decisions.
                </p>

                {/* Primary CTA */}
                <div className="flex items-center justify-center gap-4">
                    <button
                        onClick={() => navigate('/chat')}
                        className="px-8 py-4 bg-[var(--bale-accent)] text-white rounded-2xl font-medium text-lg hover:opacity-90 transition-all flex items-center gap-3 shadow-lg shadow-[var(--bale-accent)]/20"
                    >
                        <span className="text-2xl">💬</span>
                        Ask BALE Anything
                    </button>
                    <button
                        onClick={() => navigate('/analyze')}
                        className="px-6 py-4 bg-[var(--bale-surface-elevated)] text-[var(--bale-text-secondary)] rounded-2xl font-medium hover:bg-[var(--bale-border)] transition-all border border-[var(--bale-border)]"
                    >
                        Upload Contract
                    </button>
                </div>
            </div>

            {/* Quick Actions - Natural Next Steps */}
            <div className="grid grid-cols-3 gap-4 mb-12">
                <QuickAction
                    icon="📝"
                    label="Generate Contract"
                    description="Create from scratch"
                    onClick={() => navigate('/generate')}
                />
                <QuickAction
                    icon="📊"
                    label="View Reports"
                    description="Analysis summaries"
                    onClick={() => navigate('/reports')}
                />
                <QuickAction
                    icon="📁"
                    label="Browse Contracts"
                    description="Your library"
                    onClick={() => navigate('/contracts')}
                />
            </div>

            {/* Content Based on State */}
            {isLoading ? (
                <LoadingState />
            ) : hasData ? (
                <DataView stats={stats!} analyses={analyses} />
            ) : (
                <EmptyState onUpload={() => navigate('/analyze')} />
            )}
        </div>
    )
}

// Quick Action Card
function QuickAction({ icon, label, description, onClick }: {
    icon: string
    label: string
    description: string
    onClick: () => void
}) {
    return (
        <button
            onClick={onClick}
            className="p-5 bg-[var(--bale-surface)] border border-[var(--bale-border)] rounded-2xl text-left hover:border-[var(--bale-accent)] hover:bg-[var(--bale-surface-elevated)] transition-all group"
        >
            <span className="text-2xl">{icon}</span>
            <div className="mt-3 font-medium text-[var(--bale-text)] group-hover:text-[var(--bale-accent)]">
                {label}
            </div>
            <div className="text-sm text-[var(--bale-text-muted)]">{description}</div>
        </button>
    )
}

// Empty State - Guides new users
function EmptyState({ onUpload }: { onUpload: () => void }) {
    return (
        <div className="bg-[var(--bale-surface)] border border-[var(--bale-border)] rounded-3xl p-12 text-center">
            <div className="w-16 h-16 bg-[var(--bale-surface-elevated)] rounded-2xl flex items-center justify-center mx-auto mb-6">
                <span className="text-3xl">📄</span>
            </div>
            <h3 className="text-xl font-semibold text-[var(--bale-text)] mb-2">
                No contracts yet
            </h3>
            <p className="text-[var(--bale-text-muted)] mb-6 max-w-sm mx-auto">
                Upload your first contract to start discovering insights and managing risk.
            </p>
            <button
                onClick={onUpload}
                className="px-6 py-3 bg-[var(--bale-accent)] text-white rounded-xl font-medium hover:opacity-90 transition-all"
            >
                Upload Your First Contract
            </button>
        </div>
    )
}

// Loading State
function LoadingState() {
    return (
        <div className="grid grid-cols-2 gap-6">
            <div className="bg-[var(--bale-surface)] border border-[var(--bale-border)] rounded-2xl p-6 h-64 animate-pulse" />
            <div className="bg-[var(--bale-surface)] border border-[var(--bale-border)] rounded-2xl p-6 h-64 animate-pulse" />
        </div>
    )
}

// Data View - Shows when user has contracts
function DataView({ stats, analyses }: { stats: any; analyses: any[] }) {
    return (
        <div className="grid grid-cols-2 gap-6">
            {/* Risk Overview Chart */}
            <div className="bg-[var(--bale-surface)] border border-[var(--bale-border)] rounded-2xl p-6">
                <h3 className="text-lg font-semibold text-[var(--bale-text)] mb-6">
                    Risk Overview
                </h3>
                <RiskDonutChart distribution={stats.risk_distribution || {}} />
                <div className="grid grid-cols-3 gap-4 mt-6">
                    <RiskLegend color="var(--risk-low)" label="Low" count={stats.risk_distribution?.low || 0} />
                    <RiskLegend color="var(--risk-medium)" label="Medium" count={stats.risk_distribution?.medium || 0} />
                    <RiskLegend color="var(--risk-high)" label="High" count={stats.risk_distribution?.high || 0} />
                </div>
            </div>

            {/* Portfolio Stats */}
            <div className="bg-[var(--bale-surface)] border border-[var(--bale-border)] rounded-2xl p-6">
                <h3 className="text-lg font-semibold text-[var(--bale-text)] mb-6">
                    Portfolio Summary
                </h3>
                <div className="space-y-4">
                    <StatRow label="Total Contracts" value={stats.total_analyses} />
                    <StatRow label="Entities Tracked" value={stats.total_entities} />
                    <StatRow
                        label="Average Risk"
                        value={`${stats.avg_risk_score?.toFixed(0) || 0}%`}
                        color={stats.avg_risk_score < 40 ? 'var(--risk-low)' : stats.avg_risk_score < 60 ? 'var(--risk-medium)' : 'var(--risk-high)'}
                    />
                </div>

                {/* Mini Bar Chart */}
                <div className="mt-6">
                    <div className="text-sm text-[var(--bale-text-muted)] mb-2">By Type</div>
                    <div className="space-y-2">
                        {Object.entries(stats.type_distribution || {}).slice(0, 4).map(([type, count]: [string, any]) => (
                            <div key={type} className="flex items-center gap-3">
                                <div className="w-16 text-xs text-[var(--bale-text-muted)] uppercase">{type}</div>
                                <div className="flex-1 bg-[var(--bale-surface-elevated)] rounded-full h-2">
                                    <div
                                        className="bg-[var(--bale-accent)] h-2 rounded-full transition-all"
                                        style={{ width: `${Math.min((count / stats.total_analyses) * 100, 100)}%` }}
                                    />
                                </div>
                                <div className="w-8 text-sm text-[var(--bale-text-secondary)] text-right">{count}</div>
                            </div>
                        ))}
                    </div>
                </div>
            </div>

            {/* Recent Activity */}
            <div className="col-span-2 bg-[var(--bale-surface)] border border-[var(--bale-border)] rounded-2xl p-6">
                <div className="flex items-center justify-between mb-6">
                    <h3 className="text-lg font-semibold text-[var(--bale-text)]">
                        Recent Activity
                    </h3>
                    <Link to="/contracts" className="text-sm text-[var(--bale-accent)] hover:underline">
                        View all →
                    </Link>
                </div>

                {analyses.length === 0 ? (
                    <p className="text-[var(--bale-text-muted)] text-center py-8">No recent activity</p>
                ) : (
                    <div className="space-y-3">
                        {analyses.map((a: any) => (
                            <Link
                                key={a.analysis_id}
                                to={`/frontier/${a.analysis_id}`}
                                className="flex items-center gap-4 p-4 rounded-xl hover:bg-[var(--bale-surface-elevated)] transition-all"
                            >
                                <div className={`w-10 h-10 rounded-xl flex items-center justify-center ${a.risk_score < 30 ? 'bg-green-500/10' : a.risk_score < 60 ? 'bg-yellow-500/10' : 'bg-red-500/10'
                                    }`}>
                                    <span className={`text-sm font-bold ${a.risk_score < 30 ? 'text-green-400' : a.risk_score < 60 ? 'text-yellow-400' : 'text-red-400'
                                        }`}>
                                        {a.risk_score}
                                    </span>
                                </div>
                                <div className="flex-1 min-w-0">
                                    <div className="font-medium text-[var(--bale-text)] truncate">{a.contract_name}</div>
                                    <div className="text-sm text-[var(--bale-text-muted)]">{a.contract_type?.toUpperCase()}</div>
                                </div>
                                <div className="text-sm text-[var(--bale-text-muted)]">
                                    {new Date(a.analyzed_at).toLocaleDateString()}
                                </div>
                            </Link>
                        ))}
                    </div>
                )}
            </div>
        </div>
    )
}

// Donut Chart Component
function RiskDonutChart({ distribution }: { distribution: Record<string, number> }) {
    const low = distribution.low || 0
    const medium = distribution.medium || 0
    const high = distribution.high || 0
    const total = low + medium + high || 1

    const lowPct = (low / total) * 100
    const mediumPct = (medium / total) * 100
    const highPct = (high / total) * 100

    // SVG donut chart
    const size = 160
    const strokeWidth = 24
    const radius = (size - strokeWidth) / 2
    const circumference = 2 * Math.PI * radius

    const lowDash = (lowPct / 100) * circumference
    const mediumDash = (mediumPct / 100) * circumference
    const highDash = (highPct / 100) * circumference

    let offset = 0

    return (
        <div className="flex justify-center">
            <div className="relative">
                <svg width={size} height={size} className="transform -rotate-90">
                    {/* Low */}
                    <circle
                        cx={size / 2}
                        cy={size / 2}
                        r={radius}
                        fill="none"
                        stroke="var(--risk-low)"
                        strokeWidth={strokeWidth}
                        strokeDasharray={`${lowDash} ${circumference}`}
                        strokeDashoffset={-offset}
                        className="transition-all duration-500"
                    />
                    {/* Medium */}
                    <circle
                        cx={size / 2}
                        cy={size / 2}
                        r={radius}
                        fill="none"
                        stroke="var(--risk-medium)"
                        strokeWidth={strokeWidth}
                        strokeDasharray={`${mediumDash} ${circumference}`}
                        strokeDashoffset={-(offset + lowDash)}
                        className="transition-all duration-500"
                    />
                    {/* High */}
                    <circle
                        cx={size / 2}
                        cy={size / 2}
                        r={radius}
                        fill="none"
                        stroke="var(--risk-high)"
                        strokeWidth={strokeWidth}
                        strokeDasharray={`${highDash} ${circumference}`}
                        strokeDashoffset={-(offset + lowDash + mediumDash)}
                        className="transition-all duration-500"
                    />
                </svg>
                <div className="absolute inset-0 flex items-center justify-center">
                    <div className="text-center">
                        <div className="text-3xl font-bold text-[var(--bale-text)]">{total}</div>
                        <div className="text-sm text-[var(--bale-text-muted)]">Contracts</div>
                    </div>
                </div>
            </div>
        </div>
    )
}

// Risk Legend
function RiskLegend({ color, label, count }: { color: string; label: string; count: number }) {
    return (
        <div className="text-center">
            <div className="flex items-center justify-center gap-2 mb-1">
                <div className="w-3 h-3 rounded-full" style={{ backgroundColor: color }} />
                <span className="text-sm text-[var(--bale-text-muted)]">{label}</span>
            </div>
            <div className="text-xl font-bold text-[var(--bale-text)]">{count}</div>
        </div>
    )
}

// Stat Row
function StatRow({ label, value, color }: { label: string; value: string | number; color?: string }) {
    return (
        <div className="flex items-center justify-between py-2 border-b border-[var(--bale-border)] last:border-0">
            <span className="text-[var(--bale-text-muted)]">{label}</span>
            <span
                className="font-semibold text-lg"
                style={{ color: color || 'var(--bale-text)' }}
            >
                {value}
            </span>
        </div>
    )
}

export default Dashboard
