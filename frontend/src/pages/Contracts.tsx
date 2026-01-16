import { useState } from 'react'
import { FileText, Plus, Search, Filter, MoreVertical, TrendingUp, TrendingDown, Minus } from 'lucide-react'
import clsx from 'clsx'

// Mock data
const mockContracts = [
    {
        id: '1',
        name: 'SaaS Master Agreement',
        jurisdiction: 'UK',
        status: 'active',
        risk: 45,
        riskTrend: 'down',
        lastAnalyzed: '2 hours ago',
        clauseCount: 24
    },
    {
        id: '2',
        name: 'NDA - TechCorp',
        jurisdiction: 'US',
        status: 'active',
        risk: 28,
        riskTrend: 'stable',
        lastAnalyzed: '1 day ago',
        clauseCount: 12
    },
    {
        id: '3',
        name: 'IP License Agreement',
        jurisdiction: 'FRANCE',
        status: 'active',
        risk: 72,
        riskTrend: 'up',
        lastAnalyzed: '3 days ago',
        clauseCount: 18
    },
    {
        id: '4',
        name: 'Employment Contract',
        jurisdiction: 'GERMANY',
        status: 'archived',
        risk: 35,
        riskTrend: 'stable',
        lastAnalyzed: '1 week ago',
        clauseCount: 32
    },
]

function RiskIndicator({ risk, trend }: { risk: number; trend: string }) {
    const riskColor = risk > 60 ? 'text-bale-danger' : risk > 40 ? 'text-bale-warning' : 'text-bale-success'
    const bgColor = risk > 60 ? 'bg-red-500/10' : risk > 40 ? 'bg-yellow-500/10' : 'bg-green-500/10'

    const TrendIcon = trend === 'up' ? TrendingUp : trend === 'down' ? TrendingDown : Minus
    const trendColor = trend === 'up' ? 'text-bale-danger' : trend === 'down' ? 'text-bale-success' : 'text-bale-muted'

    return (
        <div className="flex items-center gap-2">
            <span className={`px-3 py-1 rounded-lg text-sm font-medium ${bgColor} ${riskColor}`}>
                {risk}%
            </span>
            <TrendIcon size={16} className={trendColor} />
        </div>
    )
}

function JurisdictionBadge({ jurisdiction }: { jurisdiction: string }) {
    const colors: Record<string, string> = {
        UK: 'bg-blue-500/20 text-blue-400',
        US: 'bg-purple-500/20 text-purple-400',
        FRANCE: 'bg-indigo-500/20 text-indigo-400',
        GERMANY: 'bg-amber-500/20 text-amber-400',
        EU: 'bg-cyan-500/20 text-cyan-400',
    }
    return (
        <span className={`px-2 py-1 rounded text-xs font-medium ${colors[jurisdiction] || 'bg-bale-card text-bale-muted'}`}>
            {jurisdiction}
        </span>
    )
}

export default function Contracts() {
    const [search, setSearch] = useState('')
    const [statusFilter, setStatusFilter] = useState<'all' | 'active' | 'archived'>('all')

    const filteredContracts = mockContracts.filter(c => {
        if (statusFilter !== 'all' && c.status !== statusFilter) return false
        if (search && !c.name.toLowerCase().includes(search.toLowerCase())) return false
        return true
    })

    return (
        <div className="p-8 animate-slide-up">
            {/* Header */}
            <div className="flex items-center justify-between mb-8">
                <div>
                    <h1 className="text-2xl font-bold gradient-text">Contracts</h1>
                    <p className="text-bale-muted mt-1">Manage and monitor your contract portfolio</p>
                </div>
                <button className="px-4 py-2 bg-white text-black rounded-lg font-medium flex items-center gap-2 hover:opacity-90 transition-opacity">
                    <Plus size={20} />
                    Add Contract
                </button>
            </div>

            {/* Filters */}
            <div className="flex items-center gap-4 mb-6">
                <div className="relative flex-1 max-w-md">
                    <Search size={18} className="absolute left-3 top-1/2 -translate-y-1/2 text-bale-muted" />
                    <input
                        type="text"
                        placeholder="Search contracts..."
                        value={search}
                        onChange={(e) => setSearch(e.target.value)}
                        className="w-full pl-10 pr-4 py-2 bg-bale-card border border-bale-border rounded-lg text-sm focus:border-white/20 transition-colors"
                    />
                </div>
                <div className="flex items-center gap-2 bg-bale-card rounded-lg p-1">
                    {(['all', 'active', 'archived'] as const).map((status) => (
                        <button
                            key={status}
                            onClick={() => setStatusFilter(status)}
                            className={clsx(
                                'px-4 py-1.5 rounded-md text-sm font-medium transition-colors capitalize',
                                statusFilter === status ? 'bg-white text-black' : 'text-bale-muted hover:text-white'
                            )}
                        >
                            {status}
                        </button>
                    ))}
                </div>
            </div>

            {/* Table */}
            <div className="glass-card rounded-xl overflow-hidden">
                <table className="w-full">
                    <thead>
                        <tr className="border-b border-bale-border">
                            <th className="text-left p-4 text-sm font-medium text-bale-muted">Contract</th>
                            <th className="text-left p-4 text-sm font-medium text-bale-muted">Jurisdiction</th>
                            <th className="text-left p-4 text-sm font-medium text-bale-muted">Risk Score</th>
                            <th className="text-left p-4 text-sm font-medium text-bale-muted">Clauses</th>
                            <th className="text-left p-4 text-sm font-medium text-bale-muted">Last Analyzed</th>
                            <th className="w-12"></th>
                        </tr>
                    </thead>
                    <tbody>
                        {filteredContracts.map((contract) => (
                            <tr
                                key={contract.id}
                                className="border-b border-bale-border last:border-0 hover:bg-bale-card/50 transition-colors cursor-pointer"
                            >
                                <td className="p-4">
                                    <div className="flex items-center gap-3">
                                        <div className="w-10 h-10 bg-bale-card rounded-lg flex items-center justify-center">
                                            <FileText size={18} className="text-bale-muted" />
                                        </div>
                                        <div>
                                            <p className="font-medium">{contract.name}</p>
                                            <p className="text-xs text-bale-muted capitalize">{contract.status}</p>
                                        </div>
                                    </div>
                                </td>
                                <td className="p-4">
                                    <JurisdictionBadge jurisdiction={contract.jurisdiction} />
                                </td>
                                <td className="p-4">
                                    <RiskIndicator risk={contract.risk} trend={contract.riskTrend} />
                                </td>
                                <td className="p-4 text-sm">{contract.clauseCount}</td>
                                <td className="p-4 text-sm text-bale-muted">{contract.lastAnalyzed}</td>
                                <td className="p-4">
                                    <button className="p-2 hover:bg-bale-card rounded-lg transition-colors">
                                        <MoreVertical size={16} className="text-bale-muted" />
                                    </button>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>

                {filteredContracts.length === 0 && (
                    <div className="p-12 text-center">
                        <FileText size={48} className="mx-auto text-bale-muted mb-4" />
                        <h3 className="font-semibold mb-2">No contracts found</h3>
                        <p className="text-sm text-bale-muted">Try adjusting your filters</p>
                    </div>
                )}
            </div>
        </div>
    )
}
