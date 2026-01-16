function Temporal() {
    const decayItems = [
        { contract: 'TechCorp MSA 2024', age: '4 years', stability: 67, urgency: 'medium', shifts: 1 },
        { contract: 'NDA - Acme Industries', age: '5 years', stability: 45, urgency: 'high', shifts: 2 },
        { contract: 'License Agreement - DataCo', age: '3 years', stability: 78, urgency: 'low', shifts: 0 },
        { contract: 'Partnership - InnovateCo', age: '2 years', stability: 89, urgency: 'low', shifts: 0 },
    ]

    const doctrineShifts = [
        { name: 'Non-Compete Enforceability', jurisdiction: 'US', date: '2024-01', severity: 'high', contracts: 3 },
        { name: 'Force Majeure - Pandemic', jurisdiction: 'UK', date: '2020-03', severity: 'medium', contracts: 8 },
        { name: 'Data Transfer (Schrems II)', jurisdiction: 'EU', date: '2020-07', severity: 'high', contracts: 5 },
    ]

    return (
        <div className="fade-in">
            <div className="page-header">
                <h1 className="page-title">Temporal Decay</h1>
                <p className="page-description">
                    Frontier III: How contract meanings drift over time
                </p>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
                <div className="card text-center">
                    <div className="text-4xl font-bold text-[var(--risk-medium)]">4</div>
                    <div className="text-small text-[var(--bale-text-muted)]">Contracts need review</div>
                </div>
                <div className="card text-center">
                    <div className="text-4xl font-bold text-[var(--frontier-temporal)]">3</div>
                    <div className="text-small text-[var(--bale-text-muted)]">Doctrine shifts detected</div>
                </div>
                <div className="card text-center">
                    <div className="text-4xl font-bold">72%</div>
                    <div className="text-small text-[var(--bale-text-muted)]">Avg stability index</div>
                </div>
            </div>

            <div className="card mb-8">
                <h3 className="text-title mb-6">Stability Timeline</h3>
                <div className="space-y-4">
                    {decayItems.map((item, idx) => (
                        <div key={idx} className="flex items-center gap-4 p-4 bg-[var(--bale-surface-elevated)] rounded-lg">
                            <div className="flex-1">
                                <div className="font-medium">{item.contract}</div>
                                <div className="text-small text-[var(--bale-text-muted)]">
                                    Age: {item.age} • {item.shifts} doctrine shifts
                                </div>
                            </div>
                            <div className="w-32">
                                <div className="flex justify-between text-small mb-1">
                                    <span>Stability</span>
                                    <span className={item.stability < 60 ? 'text-[var(--risk-medium)]' : ''}>{item.stability}%</span>
                                </div>
                                <div className="h-2 bg-[var(--bale-surface)] rounded-full overflow-hidden">
                                    <div
                                        className="h-full transition-all"
                                        style={{
                                            width: `${item.stability}%`,
                                            backgroundColor: item.stability < 60 ? 'var(--risk-medium)' : 'var(--frontier-temporal)'
                                        }}
                                    />
                                </div>
                            </div>
                            <span className={`badge ${item.urgency === 'high' ? 'badge-danger' :
                                    item.urgency === 'medium' ? 'badge-warning' : 'badge-success'
                                }`}>
                                {item.urgency}
                            </span>
                        </div>
                    ))}
                </div>
            </div>

            <div className="card">
                <h3 className="text-title mb-6">Recent Doctrine Shifts</h3>
                <div className="timeline">
                    {doctrineShifts.map((shift, idx) => (
                        <div key={idx} className={`timeline-item ${shift.severity === 'high' ? 'danger' : 'warning'}`}>
                            <div className="flex items-center gap-2 mb-1">
                                <span className="font-medium">{shift.name}</span>
                                <span className="badge badge-info">{shift.jurisdiction}</span>
                            </div>
                            <div className="text-small text-[var(--bale-text-muted)]">
                                {shift.date} • Affects {shift.contracts} contracts
                            </div>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    )
}

export default Temporal
