import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'

// Mock data for dashboard
const mockStats = {
    contractsAnalyzed: 247,
    avgRiskScore: 32,
    criticalFindings: 18,
    pendingReview: 5,
}

const recentAnalyses = [
    { id: '1', name: 'TechCorp MSA 2024', type: 'MSA', risk: 45, status: 'review', date: '2h ago' },
    { id: '2', name: 'Vendor SLA - CloudHost', type: 'SLA', risk: 23, status: 'complete', date: '4h ago' },
    { id: '3', name: 'NDA - Acme Industries', type: 'NDA', risk: 12, status: 'complete', date: '1d ago' },
    { id: '4', name: 'License Agreement - DataCo', type: 'License', risk: 67, status: 'critical', date: '1d ago' },
    { id: '5', name: 'Employment - Senior Counsel', type: 'Employment', risk: 28, status: 'complete', date: '2d ago' },
]

const frontierInsights = [
    { frontier: 'III', name: 'Temporal Decay', finding: '12 contracts need review due to doctrine shifts', severity: 'warning' },
    { frontier: 'V', name: 'Strain', finding: 'Non-compete clauses at high regulatory risk', severity: 'danger' },
    { frontier: 'VI', name: 'Social', finding: '3 contracts show power imbalance', severity: 'warning' },
    { frontier: 'IX', name: 'Imagination', finding: 'AI liability gaps detected in 7 contracts', severity: 'info' },
]

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

function getStatusBadge(status: string) {
    const styles: Record<string, string> = {
        complete: 'badge-success',
        review: 'badge-warning',
        critical: 'badge-danger',
    }
    return styles[status] || 'badge-info'
}

function Dashboard() {
    const [isLoading, setIsLoading] = useState(true)

    useEffect(() => {
        setTimeout(() => setIsLoading(false), 500)
    }, [])

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
                    value={mockStats.contractsAnalyzed}
                    change="+12 this week"
                    icon="📄"
                    loading={isLoading}
                />
                <StatCard
                    label="Avg Risk Score"
                    value={`${mockStats.avgRiskScore}%`}
                    change="-5% vs last month"
                    icon="📊"
                    positive
                    loading={isLoading}
                />
                <StatCard
                    label="Critical Findings"
                    value={mockStats.criticalFindings}
                    change="Across all contracts"
                    icon="⚠️"
                    loading={isLoading}
                />
                <StatCard
                    label="Pending Review"
                    value={mockStats.pendingReview}
                    change="Due this week"
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

                        <div className="space-y-3">
                            {recentAnalyses.map((analysis) => (
                                <Link
                                    key={analysis.id}
                                    to={`/frontier/${analysis.id}`}
                                    className="flex items-center justify-between p-4 bg-[var(--bale-surface-elevated)] rounded-lg hover:bg-[var(--bale-border)] transition-colors"
                                >
                                    <div className="flex items-center gap-4">
                                        <div className={`w-12 h-12 rounded-lg ${getRiskBg(analysis.risk)} flex items-center justify-center`}>
                                            <span className={`text-lg font-bold ${getRiskColor(analysis.risk)}`}>
                                                {analysis.risk}
                                            </span>
                                        </div>
                                        <div>
                                            <div className="font-medium">{analysis.name}</div>
                                            <div className="text-small text-[var(--bale-text-muted)]">
                                                {analysis.type} • {analysis.date}
                                            </div>
                                        </div>
                                    </div>
                                    <span className={`badge ${getStatusBadge(analysis.status)}`}>
                                        {analysis.status}
                                    </span>
                                </Link>
                            ))}
                        </div>
                    </div>
                </div>

                {/* Frontier Insights */}
                <div className="lg:col-span-1">
                    <div className="card">
                        <div className="flex items-center justify-between mb-6">
                            <h2 className="text-title">Frontier Insights</h2>
                            <span className="badge badge-info">Live</span>
                        </div>

                        <div className="space-y-4">
                            {frontierInsights.map((insight, idx) => (
                                <div
                                    key={idx}
                                    className={`p-4 rounded-lg border-l-4 ${insight.severity === 'danger'
                                            ? 'risk-bg-high border-[var(--risk-high)]'
                                            : insight.severity === 'warning'
                                                ? 'risk-bg-medium border-[var(--risk-medium)]'
                                                : 'bg-[var(--bale-surface-elevated)] border-[var(--bale-accent)]'
                                        }`}
                                >
                                    <div className="flex items-center gap-2 mb-2">
                                        <span className="text-caption px-2 py-0.5 bg-[var(--bale-surface)] rounded">
                                            {insight.frontier}
                                        </span>
                                        <span className="text-small font-medium">{insight.name}</span>
                                    </div>
                                    <p className="text-small text-[var(--bale-text-secondary)]">
                                        {insight.finding}
                                    </p>
                                </div>
                            ))}
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
                    <RiskDistributionChart />
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
function RiskDistributionChart() {
    const data = [
        { range: '0-20%', count: 45, color: 'var(--risk-low)' },
        { range: '21-40%', count: 78, color: 'var(--risk-low)' },
        { range: '41-60%', count: 52, color: 'var(--risk-medium)' },
        { range: '61-80%', count: 28, color: 'var(--risk-high)' },
        { range: '81-100%', count: 8, color: 'var(--risk-critical)' },
    ]

    const max = Math.max(...data.map(d => d.count))

    return (
        <div className="flex items-end justify-between gap-4 h-48">
            {data.map((d, idx) => (
                <div key={idx} className="flex-1 flex flex-col items-center">
                    <div
                        className="w-full rounded-t-md transition-all hover:opacity-80"
                        style={{
                            height: `${(d.count / max) * 100}%`,
                            backgroundColor: d.color,
                            minHeight: '20px'
                        }}
                    ></div>
                    <div className="mt-2 text-center">
                        <div className="font-bold">{d.count}</div>
                        <div className="text-caption text-[var(--bale-text-muted)]">{d.range}</div>
                    </div>
                </div>
            ))}
        </div>
    )
}

export default Dashboard
