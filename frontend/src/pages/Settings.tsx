import { useState } from 'react'

function Settings() {
    const [llmMode, setLlmMode] = useState('auto')

    return (
        <div className="fade-in max-w-3xl">
            <div className="page-header">
                <h1 className="page-title">Settings</h1>
                <p className="page-description">Configure BALE to your preferences</p>
            </div>

            <div className="space-y-6">
                {/* LLM Configuration */}
                <div className="card">
                    <h3 className="text-title mb-6">LLM Configuration</h3>
                    <div className="space-y-4">
                        <div>
                            <label className="label">Inference Mode</label>
                            <div className="grid grid-cols-3 gap-3">
                                {[
                                    { value: 'auto', label: 'Auto', desc: 'Smart fallback' },
                                    { value: 'local', label: 'Local', desc: 'Ollama/vLLM' },
                                    { value: 'mistral', label: 'Cloud', desc: 'Mistral API' },
                                ].map(opt => (
                                    <button
                                        key={opt.value}
                                        onClick={() => setLlmMode(opt.value)}
                                        className={`p-4 rounded-lg border text-left ${llmMode === opt.value
                                                ? 'border-[var(--bale-accent)] bg-[var(--bale-surface-elevated)]'
                                                : 'border-[var(--bale-border)]'
                                            }`}
                                    >
                                        <div className="font-medium">{opt.label}</div>
                                        <div className="text-small text-[var(--bale-text-muted)]">{opt.desc}</div>
                                    </button>
                                ))}
                            </div>
                        </div>

                        <div>
                            <label className="label">Local LLM Endpoint</label>
                            <input
                                type="text"
                                className="input"
                                placeholder="http://localhost:11434"
                                disabled={llmMode === 'mistral'}
                            />
                        </div>

                        <div>
                            <label className="label">Mistral API Key</label>
                            <input
                                type="password"
                                className="input"
                                placeholder="••••••••••••••••"
                                disabled={llmMode === 'local'}
                            />
                        </div>
                    </div>
                </div>

                {/* Analysis Defaults */}
                <div className="card">
                    <h3 className="text-title mb-6">Analysis Defaults</h3>
                    <div className="space-y-4">
                        <div className="grid grid-cols-2 gap-4">
                            <div>
                                <label className="label">Default Jurisdiction</label>
                                <select className="input select">
                                    <option value="US">United States</option>
                                    <option value="UK">United Kingdom</option>
                                    <option value="EU">European Union</option>
                                    <option value="INTERNATIONAL">International</option>
                                </select>
                            </div>
                            <div>
                                <label className="label">Default Industry</label>
                                <select className="input select">
                                    <option value="technology">Technology</option>
                                    <option value="finance">Financial Services</option>
                                    <option value="healthcare">Healthcare</option>
                                    <option value="general">General</option>
                                </select>
                            </div>
                        </div>

                        <label className="flex items-center gap-3 cursor-pointer">
                            <input type="checkbox" className="w-5 h-5 accent-[var(--bale-accent)]" defaultChecked />
                            <div>
                                <div className="font-medium">Always run Frontier Analysis</div>
                                <div className="text-small text-[var(--bale-text-muted)]">
                                    Include all 10 capabilities by default
                                </div>
                            </div>
                        </label>

                        <label className="flex items-center gap-3 cursor-pointer">
                            <input type="checkbox" className="w-5 h-5 accent-[var(--bale-accent)]" defaultChecked />
                            <div>
                                <div className="font-medium">Auto-save to library</div>
                                <div className="text-small text-[var(--bale-text-muted)]">
                                    Save analyzed contracts automatically
                                </div>
                            </div>
                        </label>
                    </div>
                </div>

                {/* Risk Thresholds */}
                <div className="card">
                    <h3 className="text-title mb-6">Risk Thresholds</h3>
                    <div className="space-y-4">
                        <div>
                            <label className="label">Low Risk Threshold</label>
                            <input type="range" min="0" max="100" defaultValue="30" className="w-full" />
                            <div className="flex justify-between text-small text-[var(--bale-text-muted)]">
                                <span>0%</span>
                                <span className="risk-low">30%</span>
                                <span>100%</span>
                            </div>
                        </div>
                        <div>
                            <label className="label">High Risk Threshold</label>
                            <input type="range" min="0" max="100" defaultValue="60" className="w-full" />
                            <div className="flex justify-between text-small text-[var(--bale-text-muted)]">
                                <span>0%</span>
                                <span className="risk-high">60%</span>
                                <span>100%</span>
                            </div>
                        </div>
                    </div>
                </div>

                {/* Account */}
                <div className="card">
                    <h3 className="text-title mb-6">Account</h3>
                    <div className="space-y-4">
                        <div className="flex items-center gap-4">
                            <div className="w-16 h-16 rounded-full bg-[var(--bale-accent)] flex items-center justify-center text-2xl font-bold text-white">
                                U
                            </div>
                            <div>
                                <div className="font-medium">User</div>
                                <div className="text-small text-[var(--bale-text-muted)]">user@company.com</div>
                            </div>
                        </div>
                        <div className="flex gap-3">
                            <button className="btn btn-secondary">Change Password</button>
                            <button className="btn btn-ghost">Sign Out</button>
                        </div>
                    </div>
                </div>

                <div className="flex justify-end">
                    <button className="btn btn-primary btn-lg">Save Settings</button>
                </div>
            </div>
        </div>
    )
}

export default Settings
