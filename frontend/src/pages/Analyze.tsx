import { useState } from 'react'
import { useMutation } from '@tanstack/react-query'
import { Scale, Play, Loader2, AlertCircle, CheckCircle2, ChevronDown } from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'
import clsx from 'clsx'

// Types
interface AnalysisResult {
    id: string
    verdict: {
        risk_score: number
        verdict: string
        confidence: number
        factors_applied: Array<{
            rule: string
            triggered: boolean
            impact: number
            evidence: string
        }>
        interpretive_gap: number
        civilist_summary: string
        commonist_summary: string
        synthesis: string
    }
    harmonization?: {
        golden_clause: string
        rationale: string
        risk_reduction: number
    }
    processing_time_ms: number
}

const JURISDICTIONS = ['INTERNATIONAL', 'UK', 'FRANCE', 'US', 'GERMANY', 'EU']

const SAMPLE_CLAUSES = [
    {
        name: 'Liability Exclusion',
        text: 'The Supplier shall not be liable for any indirect, consequential, or incidental damages arising from this Agreement, including but not limited to lost profits, data loss, or business interruption.'
    },
    {
        name: 'Force Majeure',
        text: 'Neither party shall be liable for failure to perform due to acts of God, war, terrorism, or government action beyond the reasonable control of the affected party.'
    },
    {
        name: 'IP Assignment',
        text: 'All intellectual property created by Contractor under this Agreement shall belong exclusively to Client, including all moral rights which are hereby waived to the maximum extent permitted by law.'
    }
]

function RiskGauge({ risk }: { risk: number }) {
    const rotation = (risk / 100) * 180 - 90 // -90 to 90 degrees
    return (
        <div className="relative w-48 h-24 mx-auto">
            {/* Background arc */}
            <svg className="w-full h-full" viewBox="0 0 200 100">
                <defs>
                    <linearGradient id="gaugeGradient" x1="0%" y1="0%" x2="100%" y2="0%">
                        <stop offset="0%" stopColor="#10b981" />
                        <stop offset="50%" stopColor="#f59e0b" />
                        <stop offset="100%" stopColor="#ef4444" />
                    </linearGradient>
                </defs>
                <path
                    d="M 20 90 A 80 80 0 0 1 180 90"
                    fill="none"
                    stroke="url(#gaugeGradient)"
                    strokeWidth="12"
                    strokeLinecap="round"
                />
            </svg>
            {/* Needle */}
            <div
                className="absolute bottom-0 left-1/2 w-1 h-16 bg-white origin-bottom rounded-full transition-transform duration-700"
                style={{ transform: `translateX(-50%) rotate(${rotation}deg)` }}
            />
            {/* Value */}
            <div className="absolute bottom-2 left-1/2 -translate-x-1/2">
                <span className="text-3xl font-bold">{risk}%</span>
            </div>
        </div>
    )
}

function FactorCard({ factor }: { factor: AnalysisResult['verdict']['factors_applied'][0] }) {
    return (
        <div className={clsx(
            'p-4 rounded-lg border transition-colors',
            factor.triggered
                ? factor.impact > 0
                    ? 'bg-red-500/10 border-red-500/30'
                    : 'bg-green-500/10 border-green-500/30'
                : 'bg-bale-card border-bale-border'
        )}>
            <div className="flex items-start justify-between mb-2">
                <span className="font-medium">{factor.rule}</span>
                <span className={clsx(
                    'text-sm font-mono',
                    factor.impact > 0 ? 'text-bale-danger' : factor.impact < 0 ? 'text-bale-success' : 'text-bale-muted'
                )}>
                    {factor.impact > 0 ? '+' : ''}{factor.impact}%
                </span>
            </div>
            <p className="text-sm text-bale-muted">{factor.evidence}</p>
        </div>
    )
}

export default function Analyze() {
    const [clauseText, setClauseText] = useState('')
    const [jurisdiction, setJurisdiction] = useState('INTERNATIONAL')
    const [showSamples, setShowSamples] = useState(false)

    const analyzeMutation = useMutation({
        mutationFn: async () => {
            const response = await fetch('/api/v1/analyze', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    clause_text: clauseText,
                    jurisdiction,
                    depth: 'standard',
                    include_harmonization: true
                })
            })
            if (!response.ok) throw new Error('Analysis failed')
            return response.json() as Promise<AnalysisResult>
        }
    })

    const result = analyzeMutation.data

    return (
        <div className="p-8 animate-slide-up">
            {/* Header */}
            <div className="mb-8">
                <h1 className="text-2xl font-bold gradient-text">Analyze Clause</h1>
                <p className="text-bale-muted mt-1">Run AI-powered legal analysis on contract clauses</p>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                {/* Input Panel */}
                <div className="space-y-6">
                    {/* Clause Input */}
                    <div className="glass-card rounded-xl p-6">
                        <div className="flex items-center justify-between mb-4">
                            <label className="font-semibold">Contract Clause</label>
                            <button
                                onClick={() => setShowSamples(!showSamples)}
                                className="text-sm text-bale-muted hover:text-white flex items-center gap-1"
                            >
                                Sample Clauses
                                <ChevronDown size={14} className={clsx('transition-transform', showSamples && 'rotate-180')} />
                            </button>
                        </div>

                        <AnimatePresence>
                            {showSamples && (
                                <motion.div
                                    initial={{ height: 0, opacity: 0 }}
                                    animate={{ height: 'auto', opacity: 1 }}
                                    exit={{ height: 0, opacity: 0 }}
                                    className="overflow-hidden mb-4"
                                >
                                    <div className="space-y-2 pb-4 border-b border-bale-border">
                                        {SAMPLE_CLAUSES.map((sample) => (
                                            <button
                                                key={sample.name}
                                                onClick={() => setClauseText(sample.text)}
                                                className="w-full text-left p-3 rounded-lg bg-bale-card hover:bg-bale-border transition-colors text-sm"
                                            >
                                                <span className="font-medium">{sample.name}</span>
                                            </button>
                                        ))}
                                    </div>
                                </motion.div>
                            )}
                        </AnimatePresence>

                        <textarea
                            value={clauseText}
                            onChange={(e) => setClauseText(e.target.value)}
                            placeholder="Paste your contract clause here..."
                            className="w-full h-48 bg-bale-card border border-bale-border rounded-lg p-4 text-sm resize-none focus:border-white/20 transition-colors"
                        />
                        <p className="text-xs text-bale-muted mt-2">{clauseText.length} characters</p>
                    </div>

                    {/* Options */}
                    <div className="glass-card rounded-xl p-6">
                        <label className="font-semibold block mb-4">Jurisdiction</label>
                        <div className="grid grid-cols-3 gap-2">
                            {JURISDICTIONS.map((j) => (
                                <button
                                    key={j}
                                    onClick={() => setJurisdiction(j)}
                                    className={clsx(
                                        'px-4 py-2 rounded-lg text-sm font-medium transition-colors',
                                        jurisdiction === j
                                            ? 'bg-white text-black'
                                            : 'bg-bale-card hover:bg-bale-border'
                                    )}
                                >
                                    {j}
                                </button>
                            ))}
                        </div>
                    </div>

                    {/* Analyze Button */}
                    <button
                        onClick={() => analyzeMutation.mutate()}
                        disabled={!clauseText || clauseText.length < 20 || analyzeMutation.isPending}
                        className={clsx(
                            'w-full py-4 rounded-xl font-semibold flex items-center justify-center gap-2 transition-all',
                            !clauseText || clauseText.length < 20
                                ? 'bg-bale-card text-bale-muted cursor-not-allowed'
                                : 'bg-white text-black hover:opacity-90'
                        )}
                    >
                        {analyzeMutation.isPending ? (
                            <>
                                <Loader2 size={20} className="animate-spin" />
                                Analyzing...
                            </>
                        ) : (
                            <>
                                <Play size={20} />
                                Run Analysis
                            </>
                        )}
                    </button>

                    {analyzeMutation.isError && (
                        <div className="flex items-center gap-2 p-4 bg-red-500/10 border border-red-500/30 rounded-lg text-bale-danger">
                            <AlertCircle size={20} />
                            <span>Analysis failed. Check API connection.</span>
                        </div>
                    )}
                </div>

                {/* Results Panel */}
                <div className="space-y-6">
                    {result ? (
                        <>
                            {/* Risk Score */}
                            <div className="glass-card rounded-xl p-6">
                                <h3 className="font-semibold text-center mb-4">Litigation Risk</h3>
                                <RiskGauge risk={result.verdict.risk_score} />
                                <div className="text-center mt-4">
                                    <span className={clsx(
                                        'px-4 py-2 rounded-full text-sm font-semibold',
                                        result.verdict.verdict === 'PLAINTIFF_FAVOR'
                                            ? 'bg-red-500/20 text-bale-danger'
                                            : 'bg-green-500/20 text-bale-success'
                                    )}>
                                        {result.verdict.verdict.replace('_', ' ')}
                                    </span>
                                </div>
                                <p className="text-center text-sm text-bale-muted mt-2">
                                    Confidence: {Math.round(result.verdict.confidence * 100)}% •
                                    Gap: {result.verdict.interpretive_gap}%
                                </p>
                            </div>

                            {/* Decision Factors */}
                            <div className="glass-card rounded-xl p-6">
                                <h3 className="font-semibold mb-4">Decision Factors</h3>
                                <div className="space-y-3">
                                    {result.verdict.factors_applied.map((factor, i) => (
                                        <FactorCard key={i} factor={factor} />
                                    ))}
                                </div>
                            </div>

                            {/* Harmonization */}
                            {result.harmonization && (
                                <div className="glass-card rounded-xl p-6">
                                    <div className="flex items-center gap-2 mb-4">
                                        <CheckCircle2 size={20} className="text-bale-success" />
                                        <h3 className="font-semibold">Suggested Improvement</h3>
                                    </div>
                                    <div className="bg-bale-card p-4 rounded-lg mb-4">
                                        <p className="text-sm font-mono">{result.harmonization.golden_clause}</p>
                                    </div>
                                    <p className="text-sm text-bale-muted">{result.harmonization.rationale}</p>
                                    <p className="text-sm text-bale-success mt-2">
                                        Estimated risk reduction: {result.harmonization.risk_reduction}%
                                    </p>
                                </div>
                            )}
                        </>
                    ) : (
                        <div className="glass-card rounded-xl p-12 text-center">
                            <Scale size={48} className="mx-auto text-bale-muted mb-4" />
                            <h3 className="font-semibold mb-2">Ready to Analyze</h3>
                            <p className="text-sm text-bale-muted">
                                Paste a contract clause and click "Run Analysis" to get started
                            </p>
                        </div>
                    )}
                </div>
            </div>
        </div>
    )
}
