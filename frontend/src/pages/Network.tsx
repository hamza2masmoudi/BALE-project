function Network() {
    const entities = [
        { name: 'TechCorp Inc.', contracts: 12, avgRisk: 34, trend: 'stable', position: 'vendor' },
        { name: 'CloudHost', contracts: 5, avgRisk: 21, trend: 'decreasing', position: 'vendor' },
        { name: 'DataCo', contracts: 3, avgRisk: 58, trend: 'increasing', position: 'partner' },
        { name: 'InnovateCo', contracts: 2, avgRisk: 29, trend: 'stable', position: 'partner' },
    ]

    return (
        <div className="fade-in">
            <div className="page-header">
                <h1 className="page-title">Entity Network</h1>
                <p className="page-description">
                    Frontier IV: Behavioral patterns across counterparties
                </p>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
                <div className="card">
                    <h3 className="text-title mb-6">Network Overview</h3>
                    <div className="h-64 flex items-center justify-center bg-[var(--bale-surface-elevated)] rounded-lg">
                        <div className="text-center text-[var(--bale-text-muted)]">
                            <div className="text-4xl mb-2">🌐</div>
                            <p>Entity relationship graph</p>
                            <p className="text-small">Coming soon</p>
                        </div>
                    </div>
                </div>

                <div className="card">
                    <h3 className="text-title mb-6">Risk Concentration</h3>
                    <div className="space-y-4">
                        {entities.map((entity, idx) => (
                            <div key={idx} className="flex items-center gap-4">
                                <div className="w-10 h-10 rounded-full bg-[var(--bale-accent)] flex items-center justify-center text-white font-bold">
                                    {entity.name[0]}
                                </div>
                                <div className="flex-1">
                                    <div className="font-medium">{entity.name}</div>
                                    <div className="text-small text-[var(--bale-text-muted)]">
                                        {entity.contracts} contracts • {entity.position}
                                    </div>
                                </div>
                                <div className="text-right">
                                    <div className={`font-bold ${entity.avgRisk < 30 ? 'risk-low' : entity.avgRisk < 60 ? 'risk-medium' : 'risk-high'}`}>
                                        {entity.avgRisk}%
                                    </div>
                                    <div className="text-small text-[var(--bale-text-muted)]">
                                        {entity.trend === 'increasing' ? '↑' : entity.trend === 'decreasing' ? '↓' : '→'} {entity.trend}
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            </div>

            <div className="card">
                <h3 className="text-title mb-4">Detected Patterns</h3>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div className="p-4 bg-[var(--bale-surface-elevated)] rounded-lg">
                        <div className="text-2xl mb-2">📊</div>
                        <div className="font-medium">High Concentration</div>
                        <div className="text-small text-[var(--bale-text-muted)]">
                            3 entities represent 80% of contract value
                        </div>
                    </div>
                    <div className="p-4 bg-[var(--bale-surface-elevated)] rounded-lg">
                        <div className="text-2xl mb-2">⚠️</div>
                        <div className="font-medium">Rising Risk</div>
                        <div className="text-small text-[var(--bale-text-muted)]">
                            DataCo risk tolerance increasing
                        </div>
                    </div>
                    <div className="p-4 bg-[var(--bale-surface-elevated)] rounded-lg">
                        <div className="text-2xl mb-2">✓</div>
                        <div className="font-medium">Consistent Terms</div>
                        <div className="text-small text-[var(--bale-text-muted)]">
                            Your templates show 85% consistency
                        </div>
                    </div>
                </div>
            </div>
        </div>
    )
}

export default Network
