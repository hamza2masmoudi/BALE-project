import { useState } from 'react'
import { Settings as SettingsIcon, Key, Globe, Cpu, Database, Bell, Shield } from 'lucide-react'
import clsx from 'clsx'

type TabId = 'inference' | 'api' | 'notifications' | 'security'

const tabs = [
    { id: 'inference' as const, label: 'Inference', icon: Cpu },
    { id: 'api' as const, label: 'API Keys', icon: Key },
    { id: 'notifications' as const, label: 'Notifications', icon: Bell },
    { id: 'security' as const, label: 'Security', icon: Shield },
]

function ToggleSwitch({ enabled, onChange }: { enabled: boolean; onChange: (v: boolean) => void }) {
    return (
        <button
            onClick={() => onChange(!enabled)}
            className={clsx(
                'relative w-11 h-6 rounded-full transition-colors',
                enabled ? 'bg-white' : 'bg-bale-border'
            )}
        >
            <div className={clsx(
                'absolute top-1 w-4 h-4 rounded-full transition-all',
                enabled ? 'left-6 bg-black' : 'left-1 bg-bale-muted'
            )} />
        </button>
    )
}

function SettingRow({
    title,
    description,
    children
}: {
    title: string
    description: string
    children: React.ReactNode
}) {
    return (
        <div className="flex items-center justify-between py-4 border-b border-bale-border last:border-0">
            <div>
                <h4 className="font-medium">{title}</h4>
                <p className="text-sm text-bale-muted mt-1">{description}</p>
            </div>
            <div>{children}</div>
        </div>
    )
}

export default function Settings() {
    const [activeTab, setActiveTab] = useState<TabId>('inference')
    const [localEnabled, setLocalEnabled] = useState(true)
    const [mistralEnabled, setMistralEnabled] = useState(false)

    return (
        <div className="p-8 animate-slide-up">
            {/* Header */}
            <div className="mb-8">
                <h1 className="text-2xl font-bold gradient-text">Settings</h1>
                <p className="text-bale-muted mt-1">Configure your BALE instance</p>
            </div>

            <div className="flex gap-8">
                {/* Sidebar */}
                <div className="w-56 shrink-0">
                    <nav className="space-y-1">
                        {tabs.map((tab) => {
                            const Icon = tab.icon
                            return (
                                <button
                                    key={tab.id}
                                    onClick={() => setActiveTab(tab.id)}
                                    className={clsx(
                                        'w-full flex items-center gap-3 px-4 py-3 rounded-lg text-left transition-all',
                                        activeTab === tab.id
                                            ? 'bg-white text-black'
                                            : 'text-bale-muted hover:text-white hover:bg-bale-card'
                                    )}
                                >
                                    <Icon size={18} />
                                    <span className="font-medium">{tab.label}</span>
                                </button>
                            )
                        })}
                    </nav>
                </div>

                {/* Content */}
                <div className="flex-1 glass-card rounded-xl p-6">
                    {activeTab === 'inference' && (
                        <div>
                            <h2 className="text-lg font-semibold mb-6">Inference Configuration</h2>

                            <div className="space-y-0">
                                <SettingRow
                                    title="Local LLM (Ollama)"
                                    description="Use locally running Qwen/Llama models"
                                >
                                    <ToggleSwitch enabled={localEnabled} onChange={setLocalEnabled} />
                                </SettingRow>

                                {localEnabled && (
                                    <div className="py-4 pl-4 border-b border-bale-border">
                                        <label className="text-sm text-bale-muted block mb-2">Endpoint URL</label>
                                        <input
                                            type="text"
                                            defaultValue="http://localhost:11434/v1/chat/completions"
                                            className="w-full px-4 py-2 bg-bale-card border border-bale-border rounded-lg text-sm"
                                        />
                                        <label className="text-sm text-bale-muted block mb-2 mt-4">Model Name</label>
                                        <input
                                            type="text"
                                            defaultValue="qwen2.5:32b"
                                            className="w-full px-4 py-2 bg-bale-card border border-bale-border rounded-lg text-sm"
                                        />
                                    </div>
                                )}

                                <SettingRow
                                    title="Mistral API"
                                    description="Use Mistral cloud API as fallback"
                                >
                                    <ToggleSwitch enabled={mistralEnabled} onChange={setMistralEnabled} />
                                </SettingRow>

                                {mistralEnabled && (
                                    <div className="py-4 pl-4 border-b border-bale-border">
                                        <label className="text-sm text-bale-muted block mb-2">API Key</label>
                                        <input
                                            type="password"
                                            placeholder="sk-..."
                                            className="w-full px-4 py-2 bg-bale-card border border-bale-border rounded-lg text-sm"
                                        />
                                    </div>
                                )}

                                <SettingRow
                                    title="Default Mode"
                                    description="Which inference backend to prefer"
                                >
                                    <select className="px-4 py-2 bg-bale-card border border-bale-border rounded-lg text-sm">
                                        <option value="auto">Auto (Local → Cloud)</option>
                                        <option value="local">Local Only</option>
                                        <option value="cloud">Cloud Only</option>
                                    </select>
                                </SettingRow>
                            </div>

                            <div className="mt-6 pt-6 border-t border-bale-border flex justify-end">
                                <button className="px-6 py-2 bg-white text-black rounded-lg font-medium hover:opacity-90 transition-opacity">
                                    Save Changes
                                </button>
                            </div>
                        </div>
                    )}

                    {activeTab === 'api' && (
                        <div>
                            <h2 className="text-lg font-semibold mb-6">API Keys</h2>
                            <div className="bg-bale-card rounded-lg p-4 mb-4">
                                <div className="flex items-center justify-between">
                                    <div>
                                        <p className="font-medium">Production Key</p>
                                        <p className="text-sm text-bale-muted font-mono mt-1">bale_pk_****...****7f3a</p>
                                    </div>
                                    <button className="px-3 py-1.5 bg-bale-border rounded text-sm hover:bg-white/10 transition-colors">
                                        Regenerate
                                    </button>
                                </div>
                            </div>
                            <button className="text-sm text-bale-muted hover:text-white transition-colors">
                                + Create new API key
                            </button>
                        </div>
                    )}

                    {activeTab === 'notifications' && (
                        <div>
                            <h2 className="text-lg font-semibold mb-6">Notifications</h2>
                            <SettingRow
                                title="Email Alerts"
                                description="Receive email for high-risk analyses"
                            >
                                <ToggleSwitch enabled={true} onChange={() => { }} />
                            </SettingRow>
                            <SettingRow
                                title="Risk Threshold"
                                description="Alert when risk exceeds this value"
                            >
                                <select className="px-4 py-2 bg-bale-card border border-bale-border rounded-lg text-sm">
                                    <option value="50">50%</option>
                                    <option value="60">60%</option>
                                    <option value="70">70%</option>
                                    <option value="80">80%</option>
                                </select>
                            </SettingRow>
                        </div>
                    )}

                    {activeTab === 'security' && (
                        <div>
                            <h2 className="text-lg font-semibold mb-6">Security</h2>
                            <SettingRow
                                title="Two-Factor Authentication"
                                description="Require 2FA for all users"
                            >
                                <ToggleSwitch enabled={false} onChange={() => { }} />
                            </SettingRow>
                            <SettingRow
                                title="Session Timeout"
                                description="Auto-logout after inactivity"
                            >
                                <select className="px-4 py-2 bg-bale-card border border-bale-border rounded-lg text-sm">
                                    <option value="30">30 minutes</option>
                                    <option value="60">1 hour</option>
                                    <option value="240">4 hours</option>
                                    <option value="0">Never</option>
                                </select>
                            </SettingRow>
                        </div>
                    )}
                </div>
            </div>
        </div>
    )
}
