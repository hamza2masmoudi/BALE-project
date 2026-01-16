import { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'

// Mock frontier analysis result
const mockResult = {
    contractId: 'f2c8bf4b',
    contractName: 'TechCorp MSA 2024',
    contractType: 'MSA',
    jurisdiction: 'US',
    analysisTimestamp: '2026-01-16T15:34:32',
    overallRisk: 29.67,

    criticalFindings: [
        'Template not fully customized: 7 placeholders found',
        'Non-compete clauses at high regulatory risk',
        'Severe power imbalance: Provider dominates',
        'AI liability gaps detected - doctrine unclear',
    ],

    recommendedActions: [
        'Replace generic placeholders with specific terms',
        'Consider rebalancing terms',
        'Seek specialized counsel for novel legal areas',
    ],

    frontiers: {
        silence: {
            score: 0,
            total: 6,
            present: 6,
            missing: [],
            strategic: [],
            oversights: [],
        },
        archaeology: {
            intensity: 0.75,
            draftLayers: 16,
            templateRatio: 1.0,
            defensiveInsertions: 1,
            placeholders: 7,
        },
        temporal: {
            daysElapsed: 1476,
            stability: 0.676,
            riskDelta: 12,
            shifts: ['Non-Compete Enforceability'],
            urgency: 'medium',
        },
        network: {
            partyA: { trend: 'stable', power: 0.8 },
            partyB: { trend: 'stable', power: 0.2 },
        },
        strain: {
            score: 0.8,
            points: 1,
            unstable: 7,
            landmines: ['Non-compete Agreements: clause may not be enforced'],
            predictions: ['Expect changes in Non-compete within 2 years'],
        },
        social: {
            type: 'arms_length',
            asymmetry: 1.0,
            dominant: 'Provider',
            monitoring: 0,
            narrative: 'Structure nominally equal but Provider has all discretionary rights',
            concerns: ['Severe power imbalance may lead to exploitation'],
        },
        ambiguity: {
            score: 6,
            risk: 18,
            terms: 4,
            intentional: 1,
            accidental: 3,
        },
        dispute: {
            probability: 0.123,
            highRisk: 1,
            attractors: ['warranty', 'limitation_liability', 'force_majeure'],
            predictions: [
                { clause: 'warranty', prob: 0.305, timeframe: 'medium' },
                { clause: 'limitation_liability', prob: 0.223, timeframe: 'distant' },
                { clause: 'force_majeure', prob: 0.222, timeframe: 'medium' },
            ],
        },
        imagination: {
            exposure: 0.8,
            gaps: 1,
            novel: 1,
            topics: ['AI Agents - no doctrine exists'],
            pioneering: true,
        },
        reflexive: {
            homogeneity: 0,
            convergence: 0,
            trend: 0,
            alerts: [],
        },
    },
}

const FRONTIERS = [
    { num: 'I', name: 'Silence', key: 'silence', color: 'var(--frontier-silence)', question: "What's NOT in the contract?" },
    { num: 'II', name: 'Archaeology', key: 'archaeology', color: 'var(--frontier-archaeology)', question: 'What drafting traces remain?' },
    { num: 'III', name: 'Temporal', key: 'temporal', color: 'var(--frontier-temporal)', question: 'How has meaning drifted?' },
    { num: 'IV', name: 'Network', key: 'network', color: 'var(--frontier-network)', question: 'What does behavior reveal?' },
    { num: 'V', name: 'Strain', key: 'strain', color: 'var(--frontier-strain)', question: 'Where is law under stress?' },
    { num: 'VI', name: 'Social', key: 'social', color: 'var(--frontier-social)', question: 'What power dynamics exist?' },
    { num: 'VII', name: 'Ambiguity', key: 'ambiguity', color: 'var(--frontier-ambiguity)', question: 'Is vagueness strategic?' },
    { num: 'VIII', name: 'Dispute', key: 'dispute', color: 'var(--frontier-dispute)', question: 'Which clauses will be contested?' },
    { num: 'IX', name: 'Imagination', key: 'imagination', color: 'var(--frontier-imagination)', question: 'Where does doctrine not exist?' },
    { num: 'X', name: 'Reflexive', key: 'reflexive', color: 'var(--frontier-reflexive)', question: 'How does analysis change law?' },
]

function FrontierAnalysis() {
    const { id } = useParams()
    const [loading, setLoading] = useState(true)
    const [activeFrontier, setActiveFrontier] = useState<string | null>(null)

    useEffect(() => {
        setTimeout(() => setLoading(false), 800)
    }, [])

    if (loading) {
        return <LoadingState />
    }

    return (
        <div className="fade-in">
            {/* Header */}
            <div className="page-header flex items-center justify-between">
                <div>
                    <div className="flex items-center gap-3 mb-2">
                        <Link to="/contracts" className="text-[var(--bale-text-muted)] hover:text-white">
                            ← Back
                        </Link>
                        <span className="badge badge-info">{mockResult.contractType}</span>
                        <span className="badge">{mockResult.jurisdiction}</span>
                    </div>
                    <h1 className="page-title">{mockResult.contractName}</h1>
                    <p className="page-description">
                        Frontier Analysis • {new Date(mockResult.analysisTimestamp).toLocaleString()}
                    </p>
                </div>
                <div className="flex gap-3">
                    <button className="btn btn-secondary">
                        <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                        </svg>
                        Export
                    </button>
                    <button className="btn btn-primary">
                        <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.368 2.684 3 3 0 00-5.368-2.684z" />
                        </svg>
                        Share
                    </button>
                </div>
            </div>

            {/* Summary Section */}
            <div className="grid grid-cols-1 lg:grid-cols-4 gap-6 mb-8">
                {/* Risk Gauge */}
                <div className="card flex flex-col items-center justify-center">
                    <RiskGauge value={mockResult.overallRisk} />
                    <div className="text-small text-[var(--bale-text-muted)] mt-2">Overall Frontier Risk</div>
                </div>

                {/* Critical Findings */}
                <div className="lg:col-span-2 card">
                    <h3 className="text-title mb-4 flex items-center gap-2">
                        <span className="text-[var(--risk-high)]">⚠️</span> Critical Findings
                    </h3>
                    <ul className="space-y-2">
                        {mockResult.criticalFindings.map((finding, idx) => (
                            <li key={idx} className="flex items-start gap-3 text-small">
                                <span className="text-[var(--risk-high)] mt-0.5">•</span>
                                <span className="text-[var(--bale-text-secondary)]">{finding}</span>
                            </li>
                        ))}
                    </ul>
                </div>

                {/* Quick Actions */}
                <div className="card">
                    <h3 className="text-title mb-4">Recommended Actions</h3>
                    <ul className="space-y-2">
                        {mockResult.recommendedActions.map((action, idx) => (
                            <li key={idx} className="flex items-start gap-3 text-small">
                                <span className="text-[var(--risk-low)]">✓</span>
                                <span className="text-[var(--bale-text-secondary)]">{action}</span>
                            </li>
                        ))}
                    </ul>
                </div>
            </div>

            {/* Frontier Navigator */}
            <div className="mb-6">
                <div className="flex gap-2 overflow-x-auto pb-2">
                    {FRONTIERS.map(f => (
                        <button
                            key={f.key}
                            onClick={() => setActiveFrontier(activeFrontier === f.key ? null : f.key)}
                            className={`flex-shrink-0 px-4 py-2 rounded-lg border transition-all ${activeFrontier === f.key
                                    ? 'border-[var(--bale-accent)] bg-[var(--bale-surface-elevated)]'
                                    : 'border-[var(--bale-border)] bg-[var(--bale-surface)] hover:border-[var(--bale-border-strong)]'
                                }`}
                            style={{ borderLeftColor: f.color, borderLeftWidth: '3px' }}
                        >
                            <span className="text-caption" style={{ color: f.color }}>{f.num}</span>
                            <span className="text-small ml-2">{f.name}</span>
                        </button>
                    ))}
                </div>
            </div>

            {/* Frontier Cards Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {/* Silence */}
                <FrontierCard
                    frontier={FRONTIERS[0]}
                    expanded={activeFrontier === 'silence'}
                >
                    <div className="flex items-center gap-4 mb-4">
                        <div className="text-4xl font-bold text-[var(--risk-low)]">
                            {mockResult.frontiers.silence.present}/{mockResult.frontiers.silence.total}
                        </div>
                        <div className="text-small text-[var(--bale-text-muted)]">
                            Expected clauses present
                        </div>
                    </div>
                    <div className="text-small text-[var(--bale-text-secondary)]">
                        All standard MSA clauses are present. No strategic omissions detected.
                    </div>
                </FrontierCard>

                {/* Archaeology */}
                <FrontierCard
                    frontier={FRONTIERS[1]}
                    expanded={activeFrontier === 'archaeology'}
                >
                    <div className="space-y-3">
                        <MetricRow label="Negotiation Intensity" value={`${(mockResult.frontiers.archaeology.intensity * 100).toFixed(0)}%`} />
                        <MetricRow label="Draft Layers" value={mockResult.frontiers.archaeology.draftLayers} />
                        <MetricRow label="Placeholder Scars" value={mockResult.frontiers.archaeology.placeholders} warning />
                    </div>
                </FrontierCard>

                {/* Temporal */}
                <FrontierCard
                    frontier={FRONTIERS[2]}
                    expanded={activeFrontier === 'temporal'}
                >
                    <div className="space-y-3">
                        <div className="flex items-center justify-between">
                            <span className="text-small text-[var(--bale-text-muted)]">Stability Index</span>
                            <span className={`font-bold ${mockResult.frontiers.temporal.stability < 0.7 ? 'text-[var(--risk-medium)]' : 'text-[var(--risk-low)]'}`}>
                                {(mockResult.frontiers.temporal.stability * 100).toFixed(0)}%
                            </span>
                        </div>
                        <div className="h-2 bg-[var(--bale-surface-elevated)] rounded-full overflow-hidden">
                            <div
                                className="h-full bg-[var(--frontier-temporal)] transition-all"
                                style={{ width: `${mockResult.frontiers.temporal.stability * 100}%` }}
                            />
                        </div>
                        <div className="text-small text-[var(--bale-text-secondary)]">
                            {mockResult.frontiers.temporal.daysElapsed} days since execution
                        </div>
                        {mockResult.frontiers.temporal.shifts.map((shift, idx) => (
                            <div key={idx} className="p-2 bg-[var(--bale-surface-elevated)] rounded text-small">
                                ⚡ {shift}
                            </div>
                        ))}
                    </div>
                </FrontierCard>

                {/* Network */}
                <FrontierCard
                    frontier={FRONTIERS[3]}
                    expanded={activeFrontier === 'network'}
                >
                    <PowerDiagram
                        partyA={{ name: 'Provider', power: mockResult.frontiers.network.partyA.power }}
                        partyB={{ name: 'Customer', power: mockResult.frontiers.network.partyB.power }}
                    />
                </FrontierCard>

                {/* Strain */}
                <FrontierCard
                    frontier={FRONTIERS[4]}
                    expanded={activeFrontier === 'strain'}
                >
                    <div className="space-y-3">
                        <div className="flex items-center gap-2">
                            <span className="text-2xl font-bold text-[var(--risk-high)]">{mockResult.frontiers.strain.unstable}</span>
                            <span className="text-small text-[var(--bale-text-muted)]">unstable clauses</span>
                        </div>
                        {mockResult.frontiers.strain.landmines.map((lm, idx) => (
                            <div key={idx} className="p-3 bg-[var(--risk-bg-high)] rounded-lg border-l-4 border-[var(--risk-high)]">
                                <div className="text-small font-medium text-[var(--risk-high)]">💣 Landmine</div>
                                <div className="text-small text-[var(--bale-text-secondary)]">{lm}</div>
                            </div>
                        ))}
                    </div>
                </FrontierCard>

                {/* Social */}
                <FrontierCard
                    frontier={FRONTIERS[5]}
                    expanded={activeFrontier === 'social'}
                >
                    <div className="space-y-4">
                        <div className="text-center">
                            <div className="text-2xl font-bold text-[var(--risk-high)]">
                                +{mockResult.frontiers.social.asymmetry.toFixed(1)}
                            </div>
                            <div className="text-small text-[var(--bale-text-muted)]">Power Score → {mockResult.frontiers.social.dominant}</div>
                        </div>
                        <div className="p-3 bg-[var(--bale-surface-elevated)] rounded-lg text-small text-[var(--bale-text-secondary)]">
                            {mockResult.frontiers.social.narrative}
                        </div>
                    </div>
                </FrontierCard>

                {/* Ambiguity */}
                <FrontierCard
                    frontier={FRONTIERS[6]}
                    expanded={activeFrontier === 'ambiguity'}
                >
                    <div className="space-y-3">
                        <MetricRow label="Ambiguity Score" value={mockResult.frontiers.ambiguity.score} />
                        <MetricRow label="Interpretation Risk" value={`${mockResult.frontiers.ambiguity.risk}%`} />
                        <MetricRow label="Intentional Terms" value={mockResult.frontiers.ambiguity.intentional} />
                        <MetricRow label="Accidental Terms" value={mockResult.frontiers.ambiguity.accidental} />
                    </div>
                </FrontierCard>

                {/* Dispute */}
                <FrontierCard
                    frontier={FRONTIERS[7]}
                    expanded={activeFrontier === 'dispute'}
                >
                    <div className="space-y-3">
                        {mockResult.frontiers.dispute.predictions.map((pred, idx) => (
                            <DisputeBar
                                key={idx}
                                clause={pred.clause}
                                probability={pred.prob}
                                timeframe={pred.timeframe}
                            />
                        ))}
                    </div>
                </FrontierCard>

                {/* Imagination */}
                <FrontierCard
                    frontier={FRONTIERS[8]}
                    expanded={activeFrontier === 'imagination'}
                >
                    <div className="space-y-3">
                        <div className="flex items-center gap-2">
                            <span className="text-2xl">🔮</span>
                            <span className="text-small text-[var(--bale-text-muted)]">{mockResult.frontiers.imagination.gaps} doctrine gaps</span>
                        </div>
                        {mockResult.frontiers.imagination.topics.map((topic, idx) => (
                            <div key={idx} className="p-3 bg-[var(--frontier-bg-imagination)] rounded-lg border-l-4 border-[var(--frontier-imagination)]">
                                <div className="text-small font-medium text-[var(--frontier-imagination)]">Uncharted Territory</div>
                                <div className="text-small text-[var(--bale-text-secondary)]">{topic}</div>
                            </div>
                        ))}
                        {mockResult.frontiers.imagination.pioneering && (
                            <div className="text-small text-[var(--risk-medium)]">
                                ⚠️ First-mover litigation will set precedent
                            </div>
                        )}
                    </div>
                </FrontierCard>

                {/* Reflexive */}
                <FrontierCard
                    frontier={FRONTIERS[9]}
                    expanded={activeFrontier === 'reflexive'}
                >
                    <div className="space-y-3">
                        <MetricRow label="Homogeneity Index" value={`${mockResult.frontiers.reflexive.homogeneity}%`} />
                        <MetricRow label="Convergence Rate" value={`${mockResult.frontiers.reflexive.convergence}%`} />
                        <div className="text-small text-[var(--bale-text-muted)] text-center mt-4">
                            System influence metrics will accumulate over time
                        </div>
                    </div>
                </FrontierCard>
            </div>
        </div>
    )
}

// Components

function RiskGauge({ value }: { value: number }) {
    const radius = 80
    const stroke = 16
    const circumference = Math.PI * radius
    const progress = (value / 100) * circumference

    const getColor = () => {
        if (value < 30) return 'var(--risk-low)'
        if (value < 60) return 'var(--risk-medium)'
        return 'var(--risk-high)'
    }

    return (
        <div className="relative" style={{ width: 200, height: 120 }}>
            <svg viewBox="0 0 200 120" className="w-full h-full">
                <path
                    d={`M ${20} ${100} A ${radius} ${radius} 0 0 1 ${180} ${100}`}
                    fill="none"
                    stroke="var(--bale-surface-elevated)"
                    strokeWidth={stroke}
                    strokeLinecap="round"
                />
                <path
                    d={`M ${20} ${100} A ${radius} ${radius} 0 0 1 ${180} ${100}`}
                    fill="none"
                    stroke={getColor()}
                    strokeWidth={stroke}
                    strokeLinecap="round"
                    strokeDasharray={circumference}
                    strokeDashoffset={circumference - progress}
                    style={{ transition: 'stroke-dashoffset 1s ease-out' }}
                />
            </svg>
            <div className="absolute inset-0 flex flex-col items-center justify-end pb-2">
                <span className="text-4xl font-bold" style={{ color: getColor() }}>
                    {value.toFixed(1)}%
                </span>
            </div>
        </div>
    )
}

function FrontierCard({
    frontier,
    expanded,
    children
}: {
    frontier: typeof FRONTIERS[0]
    expanded: boolean
    children: React.ReactNode
}) {
    return (
        <div
            className="frontier-card"
            style={{ '--frontier-color': frontier.color } as React.CSSProperties}
        >
            <div className="frontier-card-header">
                <span className="frontier-card-number" style={{ background: frontier.color }}>
                    {frontier.num}
                </span>
                <span className="frontier-card-title">{frontier.name}</span>
            </div>
            <div className="text-caption text-[var(--bale-text-muted)] mb-4">
                {frontier.question}
            </div>
            {children}
        </div>
    )
}

function MetricRow({
    label,
    value,
    warning = false
}: {
    label: string
    value: string | number
    warning?: boolean
}) {
    return (
        <div className="flex items-center justify-between">
            <span className="text-small text-[var(--bale-text-muted)]">{label}</span>
            <span className={`font-bold ${warning ? 'text-[var(--risk-medium)]' : ''}`}>{value}</span>
        </div>
    )
}

function PowerDiagram({
    partyA,
    partyB
}: {
    partyA: { name: string; power: number }
    partyB: { name: string; power: number }
}) {
    const position = partyA.power * 100

    return (
        <div className="space-y-4">
            <div className="flex justify-between text-small">
                <span className="font-medium">{partyA.name}</span>
                <span className="font-medium">{partyB.name}</span>
            </div>
            <div className="relative h-2 bg-[var(--bale-surface-elevated)] rounded-full">
                <div
                    className="absolute top-1/2 -translate-y-1/2 w-4 h-4 rounded-full bg-[var(--bale-accent)] border-2 border-white shadow-lg transition-all"
                    style={{ left: `calc(${position}% - 8px)` }}
                />
            </div>
            <div className="text-center text-small text-[var(--bale-text-muted)]">
                Power imbalance: {partyA.name} dominates
            </div>
        </div>
    )
}

function DisputeBar({
    clause,
    probability,
    timeframe
}: {
    clause: string
    probability: number
    timeframe: string
}) {
    const getColor = () => {
        if (probability < 0.2) return 'var(--risk-low)'
        if (probability < 0.4) return 'var(--risk-medium)'
        return 'var(--risk-high)'
    }

    return (
        <div className="dispute-bar">
            <span className="dispute-bar-label capitalize">{clause.replace('_', ' ')}</span>
            <div className="dispute-bar-track">
                <div
                    className="dispute-bar-fill"
                    style={{
                        width: `${probability * 100}%`,
                        backgroundColor: getColor()
                    }}
                />
            </div>
            <span className="dispute-bar-value">{(probability * 100).toFixed(0)}%</span>
        </div>
    )
}

function LoadingState() {
    return (
        <div className="space-y-6">
            <div className="skeleton h-12 w-64"></div>
            <div className="grid grid-cols-4 gap-6">
                <div className="skeleton h-40"></div>
                <div className="skeleton h-40 col-span-2"></div>
                <div className="skeleton h-40"></div>
            </div>
            <div className="grid grid-cols-3 gap-6">
                {[...Array(9)].map((_, i) => (
                    <div key={i} className="skeleton h-48"></div>
                ))}
            </div>
        </div>
    )
}

export default FrontierAnalysis
