import { useState } from 'react'
import { useNavigate } from 'react-router-dom'

const CONTRACT_TYPES = [
    { id: 'nda', name: 'NDA', icon: '🔒', desc: 'Non-Disclosure' },
    { id: 'msa', name: 'MSA', icon: '📋', desc: 'Master Services' },
    { id: 'sla', name: 'SLA', icon: '📊', desc: 'Service Level' },
    { id: 'employment', name: 'Employment', icon: '👤', desc: 'Hiring' },
    { id: 'consulting', name: 'Consulting', icon: '🎯', desc: 'Advisory' },
    { id: 'license', name: 'License', icon: '💻', desc: 'Software' },
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
    const navigate = useNavigate()
    const [step, setStep] = useState<'type' | 'details' | 'result'>('type')
    const [selectedType, setSelectedType] = useState('')
    const [prompt, setPrompt] = useState('')
    const [isGenerating, setIsGenerating] = useState(false)
    const [generated, setGenerated] = useState<GeneratedContract | null>(null)

    const handleSelectType = (type: string) => {
        setSelectedType(type)
        setStep('details')
    }

    const handleGenerate = async () => {
        if (!prompt.trim()) return

        setIsGenerating(true)
        try {
            const response = await fetch('/api/intelligence/generate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    prompt: `Generate a ${selectedType.toUpperCase()}: ${prompt}`,
                    contract_type: selectedType
                }),
            })

            if (!response.ok) throw new Error('Generation failed')
            const result = await response.json()
            setGenerated(result)
            setStep('result')
        } catch (error) {
            console.error('Generation error:', error)
        } finally {
            setIsGenerating(false)
        }
    }

    const handleDownload = () => {
        if (!generated) return
        const blob = new Blob([generated.full_text], { type: 'text/plain' })
        const url = URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = `${generated.title.toLowerCase().replace(/\s+/g, '_')}.txt`
        a.click()
        URL.revokeObjectURL(url)
    }

    const handleCopy = () => {
        if (generated) navigator.clipboard.writeText(generated.full_text)
    }

    return (
        <div className="fade-in max-w-3xl mx-auto py-8">
            {/* Progress Indicator */}
            <div className="flex items-center justify-center gap-2 mb-12">
                {['type', 'details', 'result'].map((s, i) => (
                    <div key={s} className="flex items-center">
                        <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium transition-all ${step === s
                                ? 'bg-[var(--bale-accent)] text-white'
                                : i < ['type', 'details', 'result'].indexOf(step)
                                    ? 'bg-green-500 text-white'
                                    : 'bg-[var(--bale-surface-elevated)] text-[var(--bale-text-muted)]'
                            }`}>
                            {i + 1}
                        </div>
                        {i < 2 && <div className={`w-12 h-0.5 mx-2 ${i < ['type', 'details', 'result'].indexOf(step)
                                ? 'bg-green-500'
                                : 'bg-[var(--bale-border)]'
                            }`} />}
                    </div>
                ))}
            </div>

            {/* Step 1: Select Type */}
            {step === 'type' && (
                <div className="text-center">
                    <h1 className="text-3xl font-bold text-[var(--bale-text)] mb-2">
                        What would you like to create?
                    </h1>
                    <p className="text-[var(--bale-text-muted)] mb-8">
                        Select a contract type to get started
                    </p>

                    <div className="grid grid-cols-3 gap-4 max-w-xl mx-auto">
                        {CONTRACT_TYPES.map((ct) => (
                            <button
                                key={ct.id}
                                onClick={() => handleSelectType(ct.id)}
                                className="p-6 bg-[var(--bale-surface)] border border-[var(--bale-border)] rounded-2xl hover:border-[var(--bale-accent)] hover:bg-[var(--bale-surface-elevated)] transition-all group"
                            >
                                <span className="text-3xl">{ct.icon}</span>
                                <div className="mt-3 font-medium text-[var(--bale-text)] group-hover:text-[var(--bale-accent)]">
                                    {ct.name}
                                </div>
                                <div className="text-sm text-[var(--bale-text-muted)]">{ct.desc}</div>
                            </button>
                        ))}
                    </div>
                </div>
            )}

            {/* Step 2: Add Details */}
            {step === 'details' && (
                <div>
                    <button
                        onClick={() => setStep('type')}
                        className="flex items-center gap-2 text-[var(--bale-text-muted)] hover:text-[var(--bale-text)] mb-6 transition-colors"
                    >
                        ← Back
                    </button>

                    <h1 className="text-3xl font-bold text-[var(--bale-text)] mb-2">
                        Describe your {CONTRACT_TYPES.find(t => t.id === selectedType)?.name}
                    </h1>
                    <p className="text-[var(--bale-text-muted)] mb-8">
                        Tell us about the parties, requirements, and any special terms
                    </p>

                    <textarea
                        value={prompt}
                        onChange={(e) => setPrompt(e.target.value)}
                        placeholder={`Example: A ${selectedType.toUpperCase()} between TechCorp (provider) and ClientCo (customer) for software development services. US jurisdiction, 12-month term, mutual confidentiality...`}
                        className="w-full px-5 py-4 bg-[var(--bale-surface)] border border-[var(--bale-border)] rounded-2xl text-[var(--bale-text)] placeholder-[var(--bale-text-muted)] focus:outline-none focus:border-[var(--bale-accent)] transition-colors resize-none"
                        rows={6}
                    />

                    <button
                        onClick={handleGenerate}
                        disabled={isGenerating || !prompt.trim()}
                        className="w-full mt-6 py-4 bg-[var(--bale-accent)] text-white rounded-2xl font-medium text-lg disabled:opacity-50 hover:opacity-90 transition-all flex items-center justify-center gap-2"
                    >
                        {isGenerating ? (
                            <>
                                <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                                Generating...
                            </>
                        ) : (
                            <>
                                <span>✨</span>
                                Generate Contract
                            </>
                        )}
                    </button>
                </div>
            )}

            {/* Step 3: Result */}
            {step === 'result' && generated && (
                <div>
                    <button
                        onClick={() => { setStep('details'); setGenerated(null) }}
                        className="flex items-center gap-2 text-[var(--bale-text-muted)] hover:text-[var(--bale-text)] mb-6 transition-colors"
                    >
                        ← Edit prompt
                    </button>

                    <div className="flex items-center justify-between mb-6">
                        <div>
                            <h1 className="text-2xl font-bold text-[var(--bale-text)]">
                                {generated.title}
                            </h1>
                            <p className="text-[var(--bale-text-muted)]">
                                {generated.sections.length} sections • Risk score: {generated.risk_score}%
                            </p>
                        </div>
                        <div className="flex gap-2">
                            <button onClick={handleCopy} className="px-4 py-2 bg-[var(--bale-surface)] border border-[var(--bale-border)] rounded-xl text-sm hover:bg-[var(--bale-surface-elevated)] transition-colors">
                                📋 Copy
                            </button>
                            <button onClick={handleDownload} className="px-4 py-2 bg-[var(--bale-accent)] text-white rounded-xl text-sm hover:opacity-90 transition-colors">
                                ⬇️ Download
                            </button>
                        </div>
                    </div>

                    {/* Warnings */}
                    {generated.warnings.length > 0 && (
                        <div className="mb-6 p-4 bg-yellow-500/10 border border-yellow-500/30 rounded-xl">
                            <div className="font-medium text-yellow-400 mb-1">⚠️ Review Notes</div>
                            <ul className="text-sm text-[var(--bale-text-secondary)] space-y-1">
                                {generated.warnings.map((w, i) => <li key={i}>• {w}</li>)}
                            </ul>
                        </div>
                    )}

                    {/* Contract Preview */}
                    <div className="bg-[var(--bale-surface)] border border-[var(--bale-border)] rounded-2xl p-6 max-h-[500px] overflow-y-auto">
                        <pre className="whitespace-pre-wrap font-mono text-sm leading-relaxed text-[var(--bale-text-secondary)]">
                            {generated.full_text}
                        </pre>
                    </div>

                    {/* Next Steps */}
                    <div className="mt-8 flex items-center justify-center gap-4">
                        <button
                            onClick={() => { setStep('type'); setGenerated(null); setPrompt(''); setSelectedType('') }}
                            className="px-6 py-3 border border-[var(--bale-border)] rounded-xl hover:bg-[var(--bale-surface)] transition-colors"
                        >
                            Create Another
                        </button>
                        <button
                            onClick={() => navigate('/analyze')}
                            className="px-6 py-3 bg-[var(--bale-surface-elevated)] rounded-xl hover:bg-[var(--bale-border)] transition-colors"
                        >
                            Analyze This Contract →
                        </button>
                    </div>
                </div>
            )}
        </div>
    )
}

export default Generate
