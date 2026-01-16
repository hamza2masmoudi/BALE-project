import { useState } from 'react'
import { Link } from 'react-router-dom'

const mockContracts = [
    { id: '1', name: 'TechCorp MSA 2024', type: 'MSA', jurisdiction: 'US', risk: 45, status: 'review', date: '2024-01-15', parties: ['TechCorp Inc.', 'AcmeCo LLC'] },
    { id: '2', name: 'Vendor SLA - CloudHost', type: 'SLA', jurisdiction: 'US', risk: 23, status: 'complete', date: '2024-01-14', parties: ['CloudHost', 'Your Company'] },
    { id: '3', name: 'NDA - Acme Industries', type: 'NDA', jurisdiction: 'UK', risk: 12, status: 'complete', date: '2024-01-12', parties: ['Acme Industries', 'Your Company'] },
    { id: '4', name: 'License Agreement - DataCo', type: 'License', jurisdiction: 'EU', risk: 67, status: 'critical', date: '2024-01-10', parties: ['DataCo', 'Your Company'] },
    { id: '5', name: 'Employment - Senior Counsel', type: 'Employment', jurisdiction: 'US', risk: 28, status: 'complete', date: '2024-01-08', parties: ['Your Company', 'John Doe'] },
    { id: '6', name: 'Partnership - InnovateCo', type: 'Partnership', jurisdiction: 'SINGAPORE', risk: 34, status: 'review', date: '2024-01-05', parties: ['InnovateCo', 'Your Company'] },
]

function getRiskColor(risk: number): string {
    if (risk < 30) return 'risk-low'
    if (risk < 60) return 'risk-medium'
    return 'risk-high'
}

function getStatusBadge(status: string) {
    const styles: Record<string, string> = {
        complete: 'badge-success',
        review: 'badge-warning',
        critical: 'badge-danger',
    }
    return styles[status] || 'badge-info'
}

function Contracts() {
    const [search, setSearch] = useState('')
    const [filter, setFilter] = useState('all')

    const filtered = mockContracts.filter(c => {
        const matchesSearch = c.name.toLowerCase().includes(search.toLowerCase()) ||
            c.type.toLowerCase().includes(search.toLowerCase())
        const matchesFilter = filter === 'all' || c.status === filter
        return matchesSearch && matchesFilter
    })

    return (
        <div className="fade-in">
            <div className="page-header flex items-center justify-between">
                <div>
                    <h1 className="page-title">Contract Library</h1>
                    <p className="page-description">{mockContracts.length} contracts analyzed</p>
                </div>
                <Link to="/analyze" className="btn btn-primary">
                    + New Analysis
                </Link>
            </div>

            {/* Filters */}
            <div className="flex gap-4 mb-6">
                <input
                    type="text"
                    className="input max-w-xs"
                    placeholder="Search contracts..."
                    value={search}
                    onChange={(e) => setSearch(e.target.value)}
                />
                <select
                    className="input select max-w-[200px]"
                    value={filter}
                    onChange={(e) => setFilter(e.target.value)}
                >
                    <option value="all">All Status</option>
                    <option value="complete">Complete</option>
                    <option value="review">Needs Review</option>
                    <option value="critical">Critical</option>
                </select>
            </div>

            {/* Table */}
            <div className="card overflow-hidden p-0">
                <table className="w-full">
                    <thead>
                        <tr className="border-b border-[var(--bale-border)]">
                            <th className="text-left p-4 text-small font-medium text-[var(--bale-text-muted)]">Name</th>
                            <th className="text-left p-4 text-small font-medium text-[var(--bale-text-muted)]">Type</th>
                            <th className="text-left p-4 text-small font-medium text-[var(--bale-text-muted)]">Jurisdiction</th>
                            <th className="text-left p-4 text-small font-medium text-[var(--bale-text-muted)]">Risk</th>
                            <th className="text-left p-4 text-small font-medium text-[var(--bale-text-muted)]">Status</th>
                            <th className="text-left p-4 text-small font-medium text-[var(--bale-text-muted)]">Date</th>
                            <th className="p-4"></th>
                        </tr>
                    </thead>
                    <tbody>
                        {filtered.map((contract) => (
                            <tr
                                key={contract.id}
                                className="border-b border-[var(--bale-border)] hover:bg-[var(--bale-surface-elevated)] transition-colors"
                            >
                                <td className="p-4">
                                    <Link
                                        to={`/frontier/${contract.id}`}
                                        className="font-medium hover:text-[var(--bale-accent)]"
                                    >
                                        {contract.name}
                                    </Link>
                                </td>
                                <td className="p-4 text-small text-[var(--bale-text-secondary)]">{contract.type}</td>
                                <td className="p-4 text-small text-[var(--bale-text-secondary)]">{contract.jurisdiction}</td>
                                <td className="p-4">
                                    <span className={`font-bold ${getRiskColor(contract.risk)}`}>{contract.risk}%</span>
                                </td>
                                <td className="p-4">
                                    <span className={`badge ${getStatusBadge(contract.status)}`}>{contract.status}</span>
                                </td>
                                <td className="p-4 text-small text-[var(--bale-text-muted)]">{contract.date}</td>
                                <td className="p-4">
                                    <button className="btn btn-ghost btn-sm">⋮</button>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </div>
    )
}

export default Contracts
