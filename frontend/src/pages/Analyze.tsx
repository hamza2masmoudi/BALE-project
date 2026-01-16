import { useState } from 'react'
import { useNavigate } from 'react-router-dom'

const contractTypes = [
    { value: 'msa', label: 'Master Services Agreement' },
    { value: 'nda', label: 'Non-Disclosure Agreement' },
    { value: 'sla', label: 'Service Level Agreement' },
    { value: 'license', label: 'License Agreement' },
    { value: 'employment', label: 'Employment Agreement' },
    { value: 'vendor', label: 'Vendor Agreement' },
    { value: 'partnership', label: 'Partnership Agreement' },
    { value: 'consulting', label: 'Consulting Agreement' },
]

const jurisdictions = [
    { value: 'US', label: 'United States' },
    { value: 'UK', label: 'United Kingdom' },
    { value: 'EU', label: 'European Union' },
    { value: 'GERMANY', label: 'Germany' },
    { value: 'FRANCE', label: 'France' },
    { value: 'SINGAPORE', label: 'Singapore' },
    { value: 'INTERNATIONAL', label: 'International' },
]

const industries = [
    { value: 'technology', label: 'Technology' },
    { value: 'finance', label: 'Financial Services' },
    { value: 'healthcare', label: 'Healthcare' },
    { value: 'manufacturing', label: 'Manufacturing' },
    { value: 'retail', label: 'Retail' },
    { value: 'legal', label: 'Legal Services' },
    { value: 'general', label: 'General' },
]

function Analyze() {
    const navigate = useNavigate()
    const [isAnalyzing, setIsAnalyzing] = useState(false)
    const [activeTab, setActiveTab] = useState<'paste' | 'upload'>('paste')

    const [formData, setFormData] = useState({
        contractText: '',
        contractType: 'msa',
        jurisdiction: 'US',
        industry: 'technology',
        partyA: '',
        partyB: '',
        effectiveDate: '',
        runFrontier: true,
    })

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault()
        setIsAnalyzing(true)

        // Simulate analysis
        await new Promise(resolve => setTimeout(resolve, 2000))

        // Navigate to results
        navigate('/frontier/new-analysis')
    }

    return (
        <div className="fade-in max-w-4xl mx-auto">
            {/* Header */}
            <div className="page-header">
                <h1 className="page-title">Analyze Contract</h1>
                <p className="page-description">
                    Run comprehensive analysis including all 10 frontier capabilities
                </p>
            </div>

            {/* Input Method Tabs */}
            <div className="flex gap-2 mb-6">
                <button
                    onClick={() => setActiveTab('paste')}
                    className={`btn ${activeTab === 'paste' ? 'btn-primary' : 'btn-secondary'}`}
                >
                    <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                    </svg>
                    Paste Text
                </button>
                <button
                    onClick={() => setActiveTab('upload')}
                    className={`btn ${activeTab === 'upload' ? 'btn-primary' : 'btn-secondary'}`}
                >
                    <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" />
                    </svg>
                    Upload File
                </button>
            </div>

            <form onSubmit={handleSubmit}>
                <div className="card mb-6">
                    {activeTab === 'paste' ? (
                        <div>
                            <label className="label">Contract Text</label>
                            <textarea
                                className="input textarea font-mono text-sm"
                                placeholder="Paste your contract text here..."
                                value={formData.contractText}
                                onChange={(e) => setFormData({ ...formData, contractText: e.target.value })}
                                rows={16}
                                required
                            />
                            <p className="text-small text-[var(--bale-text-muted)] mt-2">
                                {formData.contractText.length} characters • {formData.contractText.split(/\s+/).filter(Boolean).length} words
                            </p>
                        </div>
                    ) : (
                        <div className="border-2 border-dashed border-[var(--bale-border)] rounded-lg p-12 text-center">
                            <svg className="w-12 h-12 mx-auto mb-4 text-[var(--bale-text-muted)]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                            </svg>
                            <p className="text-[var(--bale-text-secondary)] mb-2">
                                Drag and drop your contract file here
                            </p>
                            <p className="text-small text-[var(--bale-text-muted)] mb-4">
                                Supports PDF, DOCX, TXT (Max 10MB)
                            </p>
                            <button type="button" className="btn btn-secondary">
                                Browse Files
                            </button>
                        </div>
                    )}
                </div>

                {/* Metadata */}
                <div className="card mb-6">
                    <h3 className="text-title mb-6">Contract Details</h3>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        <div>
                            <label className="label">Contract Type</label>
                            <select
                                className="input select"
                                value={formData.contractType}
                                onChange={(e) => setFormData({ ...formData, contractType: e.target.value })}
                            >
                                {contractTypes.map(t => (
                                    <option key={t.value} value={t.value}>{t.label}</option>
                                ))}
                            </select>
                        </div>

                        <div>
                            <label className="label">Jurisdiction</label>
                            <select
                                className="input select"
                                value={formData.jurisdiction}
                                onChange={(e) => setFormData({ ...formData, jurisdiction: e.target.value })}
                            >
                                {jurisdictions.map(j => (
                                    <option key={j.value} value={j.value}>{j.label}</option>
                                ))}
                            </select>
                        </div>

                        <div>
                            <label className="label">Industry</label>
                            <select
                                className="input select"
                                value={formData.industry}
                                onChange={(e) => setFormData({ ...formData, industry: e.target.value })}
                            >
                                {industries.map(i => (
                                    <option key={i.value} value={i.value}>{i.label}</option>
                                ))}
                            </select>
                        </div>

                        <div>
                            <label className="label">Effective Date</label>
                            <input
                                type="date"
                                className="input"
                                value={formData.effectiveDate}
                                onChange={(e) => setFormData({ ...formData, effectiveDate: e.target.value })}
                            />
                        </div>

                        <div>
                            <label className="label">Party A (Your Side)</label>
                            <input
                                type="text"
                                className="input"
                                placeholder="e.g., Your Company Inc."
                                value={formData.partyA}
                                onChange={(e) => setFormData({ ...formData, partyA: e.target.value })}
                            />
                        </div>

                        <div>
                            <label className="label">Party B (Counterparty)</label>
                            <input
                                type="text"
                                className="input"
                                placeholder="e.g., Vendor Corp."
                                value={formData.partyB}
                                onChange={(e) => setFormData({ ...formData, partyB: e.target.value })}
                            />
                        </div>
                    </div>
                </div>

                {/* Analysis Options */}
                <div className="card mb-6">
                    <h3 className="text-title mb-6">Analysis Options</h3>

                    <label className="flex items-center gap-3 cursor-pointer">
                        <input
                            type="checkbox"
                            checked={formData.runFrontier}
                            onChange={(e) => setFormData({ ...formData, runFrontier: e.target.checked })}
                            className="w-5 h-5 rounded border-[var(--bale-border)] bg-[var(--bale-surface)] accent-[var(--bale-accent)]"
                        />
                        <div>
                            <div className="font-medium">Include Frontier Analysis</div>
                            <div className="text-small text-[var(--bale-text-muted)]">
                                Run all 10 second-order legal intelligence capabilities
                            </div>
                        </div>
                    </label>

                    {formData.runFrontier && (
                        <div className="mt-4 p-4 bg-[var(--bale-surface-elevated)] rounded-lg">
                            <div className="grid grid-cols-2 md:grid-cols-5 gap-2 text-center">
                                {[
                                    { num: 'I', name: 'Silence' },
                                    { num: 'II', name: 'Archaeology' },
                                    { num: 'III', name: 'Temporal' },
                                    { num: 'IV', name: 'Network' },
                                    { num: 'V', name: 'Strain' },
                                    { num: 'VI', name: 'Social' },
                                    { num: 'VII', name: 'Ambiguity' },
                                    { num: 'VIII', name: 'Dispute' },
                                    { num: 'IX', name: 'Imagination' },
                                    { num: 'X', name: 'Reflexive' },
                                ].map(f => (
                                    <div key={f.num} className="p-2 rounded bg-[var(--bale-surface)] text-small">
                                        <span className="text-caption text-[var(--bale-accent)]">{f.num}</span>
                                        <span className="text-[var(--bale-text-muted)]"> {f.name}</span>
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}
                </div>

                {/* Submit */}
                <div className="flex justify-end gap-4">
                    <button type="button" className="btn btn-secondary">
                        Save as Draft
                    </button>
                    <button
                        type="submit"
                        className="btn btn-primary btn-lg"
                        disabled={isAnalyzing || !formData.contractText}
                    >
                        {isAnalyzing ? (
                            <>
                                <div className="spinner"></div>
                                Analyzing...
                            </>
                        ) : (
                            <>
                                <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                                </svg>
                                Run Analysis
                            </>
                        )}
                    </button>
                </div>
            </form>
        </div>
    )
}

export default Analyze
