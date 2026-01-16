import { BarChart3, TrendingUp, AlertTriangle, CheckCircle, ArrowUp, ArrowDown } from 'lucide-react'
import { AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts'

// Mock data
const riskTrendData = [
    { date: 'Jan 10', risk: 45 },
    { date: 'Jan 11', risk: 52 },
    { date: 'Jan 12', risk: 48 },
    { date: 'Jan 13', risk: 55 },
    { date: 'Jan 14', risk: 42 },
    { date: 'Jan 15', risk: 38 },
    { date: 'Jan 16', risk: 35 },
]

const jurisdictionData = [
    { name: 'UK', value: 35, color: '#3b82f6' },
    { name: 'France', value: 25, color: '#8b5cf6' },
    { name: 'US', value: 22, color: '#10b981' },
    { name: 'Germany', value: 12, color: '#f59e0b' },
    { name: 'Other', value: 6, color: '#6b7280' },
]

const recentAnalyses = [
    { id: 1, name: 'Force Majeure Clause', risk: 72, verdict: 'PLAINTIFF', time: '2m ago' },
    { id: 2, name: 'Liability Limitation', risk: 35, verdict: 'DEFENSE', time: '15m ago' },
    { id: 3, name: 'IP Assignment', risk: 58, verdict: 'PLAINTIFF', time: '1h ago' },
    { id: 4, name: 'Termination Terms', risk: 28, verdict: 'DEFENSE', time: '2h ago' },
]

function StatCard({
    title,
    value,
    change,
    changeType,
    icon: Icon
}: {
    title: string
    value: string
    change: string
    changeType: 'up' | 'down' | 'neutral'
    icon: any
}) {
    return (
        <div className="glass-card rounded-xl p-6">
            <div className="flex items-start justify-between">
                <div>
                    <p className="text-bale-muted text-sm">{title}</p>
                    <p className="text-3xl font-bold mt-2">{value}</p>
                    <div className={`flex items-center gap-1 mt-2 text-sm ${changeType === 'up' ? 'text-bale-success' :
                            changeType === 'down' ? 'text-bale-danger' : 'text-bale-muted'
                        }`}>
                        {changeType === 'up' ? <ArrowUp size={14} /> :
                            changeType === 'down' ? <ArrowDown size={14} /> : null}
                        <span>{change}</span>
                    </div>
                </div>
                <div className="w-12 h-12 bg-bale-card rounded-lg flex items-center justify-center">
                    <Icon size={24} className="text-bale-muted" />
                </div>
            </div>
        </div>
    )
}

function RiskBadge({ risk }: { risk: number }) {
    const color = risk > 60 ? 'text-bale-danger bg-red-500/10' :
        risk > 40 ? 'text-bale-warning bg-yellow-500/10' :
            'text-bale-success bg-green-500/10'
    return (
        <span className={`px-2 py-1 rounded text-xs font-medium ${color}`}>
            {risk}%
        </span>
    )
}

export default function Dashboard() {
    return (
        <div className="p-8 animate-slide-up">
            {/* Header */}
            <div className="mb-8">
                <h1 className="text-2xl font-bold gradient-text">Dashboard</h1>
                <p className="text-bale-muted mt-1">Overview of your legal intelligence operations</p>
            </div>

            {/* Stats Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
                <StatCard
                    title="Analyses Today"
                    value="24"
                    change="+12% from yesterday"
                    changeType="up"
                    icon={BarChart3}
                />
                <StatCard
                    title="Avg Risk Score"
                    value="42%"
                    change="-8% from last week"
                    changeType="down"
                    icon={TrendingUp}
                />
                <StatCard
                    title="High Risk Clauses"
                    value="7"
                    change="3 require attention"
                    changeType="neutral"
                    icon={AlertTriangle}
                />
                <StatCard
                    title="Contracts Reviewed"
                    value="156"
                    change="+23 this month"
                    changeType="up"
                    icon={CheckCircle}
                />
            </div>

            {/* Charts Row */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
                {/* Risk Trend */}
                <div className="lg:col-span-2 glass-card rounded-xl p-6">
                    <h3 className="font-semibold mb-4">Risk Trend (7 Days)</h3>
                    <ResponsiveContainer width="100%" height={250}>
                        <AreaChart data={riskTrendData}>
                            <defs>
                                <linearGradient id="riskGradient" x1="0" y1="0" x2="0" y2="1">
                                    <stop offset="5%" stopColor="#ffffff" stopOpacity={0.3} />
                                    <stop offset="95%" stopColor="#ffffff" stopOpacity={0} />
                                </linearGradient>
                            </defs>
                            <XAxis dataKey="date" stroke="#6b7280" fontSize={12} />
                            <YAxis stroke="#6b7280" fontSize={12} domain={[0, 100]} />
                            <Tooltip
                                contentStyle={{
                                    backgroundColor: '#111',
                                    border: '1px solid #374151',
                                    borderRadius: '8px'
                                }}
                            />
                            <Area
                                type="monotone"
                                dataKey="risk"
                                stroke="#ffffff"
                                strokeWidth={2}
                                fill="url(#riskGradient)"
                            />
                        </AreaChart>
                    </ResponsiveContainer>
                </div>

                {/* Jurisdiction Distribution */}
                <div className="glass-card rounded-xl p-6">
                    <h3 className="font-semibold mb-4">By Jurisdiction</h3>
                    <ResponsiveContainer width="100%" height={180}>
                        <PieChart>
                            <Pie
                                data={jurisdictionData}
                                cx="50%"
                                cy="50%"
                                innerRadius={50}
                                outerRadius={70}
                                paddingAngle={2}
                                dataKey="value"
                            >
                                {jurisdictionData.map((entry, index) => (
                                    <Cell key={`cell-${index}`} fill={entry.color} />
                                ))}
                            </Pie>
                        </PieChart>
                    </ResponsiveContainer>
                    <div className="grid grid-cols-2 gap-2 mt-4">
                        {jurisdictionData.map((item) => (
                            <div key={item.name} className="flex items-center gap-2 text-sm">
                                <div className="w-2 h-2 rounded-full" style={{ backgroundColor: item.color }} />
                                <span className="text-bale-muted">{item.name}</span>
                                <span className="ml-auto">{item.value}%</span>
                            </div>
                        ))}
                    </div>
                </div>
            </div>

            {/* Recent Analyses */}
            <div className="glass-card rounded-xl p-6">
                <div className="flex items-center justify-between mb-4">
                    <h3 className="font-semibold">Recent Analyses</h3>
                    <button className="text-sm text-bale-muted hover:text-white transition-colors">
                        View All →
                    </button>
                </div>
                <div className="space-y-3">
                    {recentAnalyses.map((analysis) => (
                        <div
                            key={analysis.id}
                            className="flex items-center justify-between p-4 bg-bale-card rounded-lg hover:bg-bale-border transition-colors cursor-pointer"
                        >
                            <div className="flex items-center gap-4">
                                <div className="w-10 h-10 bg-bale-dark rounded-lg flex items-center justify-center">
                                    <BarChart3 size={18} className="text-bale-muted" />
                                </div>
                                <div>
                                    <p className="font-medium">{analysis.name}</p>
                                    <p className="text-sm text-bale-muted">{analysis.time}</p>
                                </div>
                            </div>
                            <div className="flex items-center gap-4">
                                <span className={`text-sm ${analysis.verdict === 'PLAINTIFF' ? 'text-bale-danger' : 'text-bale-success'
                                    }`}>
                                    {analysis.verdict}
                                </span>
                                <RiskBadge risk={analysis.risk} />
                            </div>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    )
}
