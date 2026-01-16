import { useState } from 'react'

const CONTRACT_TYPES = [
    { id: 'msa', name: 'Master Services Agreement', icon: '📋', description: 'Comprehensive services framework' },
    { id: 'nda', name: 'Non-Disclosure Agreement', icon: '🔒', description: 'Protect confidential information' },
    { id: 'sla', name: 'Service Level Agreement', icon: '📊', description: 'Uptime and support commitments' },
    { id: 'license', name: 'Software License', icon: '💻', description: 'Software usage rights' },
    { id: 'employment', name: 'Employment Agreement', icon: '👤', description: 'Employment terms' },
    { id: 'consulting', name: 'Consulting Agreement', icon: '🎯', description: 'Consulting engagement' },
    { id: 'vendor', name: 'Vendor Agreement', icon: '🏪', description: 'Supplier relationship' },
    { id: 'partnership', name: 'Partnership Agreement', icon: '🤝', description: 'Business partnership' },
]

const JURISDICTIONS = [
    { id: 'US', name: 'United States', flag: '🇺🇸' },
    { id: 'UK', name: 'United Kingdom', flag: '🇬🇧' },
    { id: 'EU', name: 'European Union', flag: '🇪🇺' },
    { id: 'GERMANY', name: 'Germany', flag: '🇩🇪' },
    { id: 'SINGAPORE', name: 'Singapore', flag: '🇸🇬' },
]

const STYLES = [
    { id: 'balanced', name: 'Balanced', description: 'Fair to both parties', color: 'var(--risk-low)' },
    { id: 'protective', name: 'Protective', description: 'Favors your position', color: 'var(--risk-medium)' },
    { id: 'aggressive', name: 'Aggressive', description: 'Strongly favors you', color: 'var(--risk-high)' },
]

interface GeneratedContract {
    contract_id: string
    title: string
    full_text: string
    sections: Array<{ name: string; content: string }>
    risk_score: number
    warnings: string[]
}

function Generate() {
    const [mode, setMode] = useState<'simple' | 'advanced'>('simple')
    const [prompt, setPrompt] = useState('')
    const [isGenerating, setIsGenerating] = useState(false)
    const [generated, setGenerated] = useState<GeneratedContract | null>(null)

    // Advanced mode state
    const [contractType, setContractType] = useState('msa')
    const [jurisdiction, setJurisdiction] = useState('US')
    const [style, setStyle] = useState('balanced')
    const [partyA, setPartyA] = useState('')
    const [partyB, setPartyB] = useState('')
    const [position, setPosition] = useState('buyer')
    const [termMonths, setTermMonths] = useState(12)
    const [autoRenew, setAutoRenew] = useState(true)
    const [description, setDescription] = useState('')

    const handleGenerate = async () => {
        setIsGenerating(true)
        setGenerated(null)

        try {
            const body = mode === 'simple'
                ? { prompt }
                : {
                    contract_type: contractType,
                    description,
                    jurisdiction,
                    industry: 'technology',
                    party_a_name: partyA || 'Party A',
                    party_a_type: 'corporation',
                    party_b_name: partyB || 'Party B',
                    party_b_type: 'corporation',
                    your_position: position,
                    style,
                    term_months: termMonths,
                    auto_renew: autoRenew,
                }

            const response = await fetch('/api/intelligence/generate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(body),
            })

            if (!response.ok) throw new Error('Generation failed')

            const result = await response.json()
            setGenerated(result)
        } catch (error) {
            console.error('Generation error:', error)
        } finally {
            setIsGenerating(false)
        }
    }

    const handleCopy = () => {
        if (generated) {
            navigator.clipboard.writeText(generated.full_text)
        }
    }

    const handleDownload = () => {
        if (generated) {
            const blob = new Blob([generated.full_text], { type: 'text/plain' })
            const url = URL.createObjectURL(blob)
            const a = document.createElement('a')
            a.href = url
            a.download = `${generated.title.toLowerCase().replace(/\s+/g, '_')}.txt`
            a.click()
            URL.revokeObjectURL(url)
        }
    }

    return (
        <div className="fade-in">
            {/* Header */}
            <div className="page-header">
                <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-[var(--frontier-imagination)] to-[var(--bale-accent)] flex items-center justify-center">
                        <span className="text-xl">✨</span>
                    </div>
                    <div>
                        <h1 className="page-title">Generate Contract</h1>
                        <p className="text-small text-[var(--bale-text-muted)]">
                            AI-powered contract generation from natural language
                        </p>
                    </div>
                </div>
            </div>

            {/* Mode Toggle */}
            <div className="flex gap-2 mb-6">
                <button
                    onClick={() => setMode('simple')}
                    className={`btn ${mode === 'simple' ? 'btn-primary' : 'btn-secondary'}`}
                >
                    ✨ Simple Mode
                </button>
                <button
                    onClick={() => setMode('advanced')}
                    className={`btn ${mode === 'advanced' ? 'btn-primary' : 'btn-secondary'}`}
                >
                    ⚙️ Advanced Mode
                </button>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Input Panel */}
                <div>
                    {mode === 'simple' ? (
                        <div className="card">
                            <h3 className="text-title mb-4">Describe Your Contract</h3>
                            <p className="text-small text-[var(--bale-text-muted)] mb-4">
                                Just describe what you need in plain English. BALE will figure out the rest.
                            </p>
                            <textarea
                                value={prompt}
                                onChange={(e) => setPrompt(e.target.value)}
                                placeholder="Example: Generate an NDA for a software company based in the US. We're the disclosing party sharing our trade secrets with a potential partner. Make it protective of our interests."
                                className="input textarea font-normal"
                                rows={8}
                            />
                            <div className="mt-4 space-y-2 text-small text-[var(--bale-text-muted)]">
                                <p>💡 <strong>Tips:</strong></p>
                                <ul className="list-disc list-inside space-y-1 pl-4">
                                    <li>Mention the contract type (MSA, NDA, SLA, etc.)</li>
                                    <li>Specify your role (buyer, seller, discloser)</li>
                                    <li>Include jurisdiction if important</li>
                                    <li>Mention any special requirements</li>
                                </ul>
                            </div>
                        </div>
                    ) : (
                        <div className="space-y-4">
                            {/* Contract Type Selection */}
                            <div className="card">
                                <h3 className="text-title mb-4">Contract Type</h3>
                                <div className="grid grid-cols-2 gap-2">
                                    {CONTRACT_TYPES.map((ct) => (
                                        <button
                                            key={ct.id}
                                            onClick={() => setContractType(ct.id)}
                                            className={`p-3 rounded-lg border text-left transition-all ${contractType === ct.id
                                                    ? 'border-[var(--bale-accent)] bg-[var(--bale-accent-muted)]'
                                                    : 'border-[var(--bale-border)] hover:border-[var(--bale-border-strong)]'
                                                }`}
                                        >
                                            <span className="text-lg">{ct.icon}</span>
                                            <div className="text-small font-medium mt-1">{ct.name}</div>
                                        </button>
                                    ))}
                                </div>
                            </div>

                            {/* Parties */}
                            <div className="card">
                                <h3 className="text-title mb-4">Parties</h3>
                                <div className="space-y-4">
                                    <div>
                                        <label className="label">Your Company</label>
                                        <input
                                            type="text"
                                            value={partyA}
                                            onChange={(e) => setPartyA(e.target.value)}
                                            placeholder="e.g., Acme Corporation"
                                            className="input"
                                        />
                                    </div>
                                    <div>
                                        <label className="label">Counterparty</label>
                                        <input
                                            type="text"
                                            value={partyB}
                                            onChange={(e) => setPartyB(e.target.value)}
                                            placeholder="e.g., TechVendor Inc."
                                            className="input"
                                        />
                                    </div>
                                    <div>
                                        <label className="label">Your Position</label>
                                        <select
                                            value={position}
                                            onChange={(e) => setPosition(e.target.value)}
                                            className="input select"
                                        >
                                            <option value="buyer">Buyer / Customer</option>
                                            <option value="seller">Seller / Provider</option>
                                            <option value="neutral">Neutral</option>
                                        </select>
                                    </div>
                                </div>
                            </div>

                            {/* Jurisdiction & Style */}
                            <div className="card">
                                <h3 className="text-title mb-4">Configuration</h3>
                                <div className="grid grid-cols-2 gap-4">
                                    <div>
                                        <label className="label">Jurisdiction</label>
                                        <select
                                            value={jurisdiction}
                                            onChange={(e) => setJurisdiction(e.target.value)}
                                            className="input select"
                                        >
                                            {JURISDICTIONS.map((j) => (
                                                <option key={j.id} value={j.id}>{j.flag} {j.name}</option>
                                            ))}
                                        </select>
                                    </div>
                                    <div>
                                        <label className="label">Term (months)</label>
                                        <input
                                            type="number"
                                            value={termMonths}
                                            onChange={(e) => setTermMonths(parseInt(e.target.value))}
                                            className="input"
                                            min={1}
                                            max={120}
                                        />
                                    </div>
                                </div>

                                <div className="mt-4">
                                    <label className="label">Style</label>
                                    <div className="flex gap-2">
                                        {STYLES.map((s) => (
                                            <button
                                                key={s.id}
                                                onClick={() => setStyle(s.id)}
                                                className={`flex-1 p-2 rounded-lg border text-center text-small ${style === s.id
                                                        ? 'border-[var(--bale-accent)]'
                                                        : 'border-[var(--bale-border)]'
                                                    }`}
                                                style={style === s.id ? { borderColor: s.color } : {}}
                                            >
                                                {s.name}
                                            </button>
                                        ))}
                                    </div>
                                </div>

                                <div className="mt-4">
                                    <label className="flex items-center gap-2 cursor-pointer">
                                        <input
                                            type="checkbox"
                                            checked={autoRenew}
                                            onChange={(e) => setAutoRenew(e.target.checked)}
                                            className="w-4 h-4 accent-[var(--bale-accent)]"
                                        />
                                        <span className="text-small">Auto-renewal clause</span>
                                    </label>
                                </div>
                            </div>

                            {/* Description */}
                            <div className="card">
                                <label className="label">Additional Requirements</label>
                                <textarea
                                    value={description}
                                    onChange={(e) => setDescription(e.target.value)}
                                    placeholder="Any specific requirements or context..."
                                    className="input textarea"
                                    rows={3}
                                />
                            </div>
                        </div>
                    )}

                    {/* Generate Button */}
                    <button
                        onClick={handleGenerate}
                        disabled={isGenerating || (mode === 'simple' && !prompt.trim())}
                        className="btn btn-primary btn-lg w-full mt-4"
                    >
                        {isGenerating ? (
                            <>
                                <div className="spinner"></div>
                                Generating...
                            </>
                        ) : (
                            <>
                                <span className="text-lg">✨</span>
                                Generate Contract
                            </>
                        )}
                    </button>
                </div>

                {/* Output Panel */}
                <div>
                    {generated ? (
                        <div className="card">
                            <div className="flex items-center justify-between mb-4">
                                <h3 className="text-title">{generated.title}</h3>
                                <div className="flex gap-2">
                                    <button onClick={handleCopy} className="btn btn-secondary btn-sm">
                                        📋 Copy
                                    </button>
                                    <button onClick={handleDownload} className="btn btn-secondary btn-sm">
                                        ⬇️ Download
                                    </button>
                                </div>
                            </div>

                            {/* Warnings */}
                            {generated.warnings.length > 0 && (
                                <div className="mb-4 p-3 bg-[var(--risk-bg-medium)] rounded-lg border border-[var(--risk-medium)]">
                                    <div className="font-medium text-small text-[var(--risk-medium)] mb-1">⚠️ Review Notes</div>
                                    <ul className="text-small text-[var(--bale-text-secondary)] space-y-1">
                                        {generated.warnings.map((w, i) => (
                                            <li key={i}>• {w}</li>
                                        ))}
                                    </ul>
                                </div>
                            )}

                            {/* Risk Score */}
                            <div className="mb-4 flex items-center gap-2">
                                <span className="text-small text-[var(--bale-text-muted)]">Draft Risk:</span>
                                <span className={`badge ${generated.risk_score < 30 ? 'badge-success' :
                                        generated.risk_score < 60 ? 'badge-warning' : 'badge-danger'
                                    }`}>
                                    {generated.risk_score}%
                                </span>
                            </div>

                            {/* Contract Preview */}
                            <div className="bg-[var(--bale-surface-elevated)] rounded-lg p-4 max-h-[600px] overflow-y-auto">
                                <pre className="whitespace-pre-wrap font-mono text-sm" style={{ lineHeight: '1.6' }}>
                                    {generated.full_text}
                                </pre>
                            </div>

                            {/* Sections Navigator */}
                            <div className="mt-4">
                                <div className="text-small font-medium mb-2">Sections:</div>
                                <div className="flex flex-wrap gap-1">
                                    {generated.sections.map((s, i) => (
                                        <span key={i} className="px-2 py-1 bg-[var(--bale-surface-elevated)] rounded text-caption">
                                            {s.name}
                                        </span>
                                    ))}
                                </div>
                            </div>
                        </div>
                    ) : (
                        <div className="card h-full flex items-center justify-center min-h-[400px]">
                            <div className="text-center text-[var(--bale-text-muted)]">
                                <div className="text-6xl mb-4">📝</div>
                                <p className="text-lg mb-2">Your contract will appear here</p>
                                <p className="text-small">
                                    Describe what you need and click Generate
                                </p>
                            </div>
                        </div>
                    )}
                </div>
            </div>
        </div>
    )
}

export default Generate
