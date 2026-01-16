import { useState } from 'react'

function Reports() {
    const [reportType, setReportType] = useState('summary')

    const recentReports = [
        { name: 'Monthly Risk Summary', type: 'summary', date: '2024-01-15', format: 'PDF' },
        { name: 'Q4 2023 Analysis', type: 'quarterly', date: '2024-01-01', format: 'PDF' },
        { name: 'Frontier Insights Export', type: 'frontier', date: '2023-12-28', format: 'JSON' },
    ]

    return (
        <div className="fade-in">
            <div className="page-header">
                <h1 className="page-title">Reports</h1>
                <p className="page-description">Generate and export analysis reports</p>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
                <div className="lg:col-span-2 card">
                    <h3 className="text-title mb-6">Generate Report</h3>

                    <div className="space-y-6">
                        <div>
                            <label className="label">Report Type</label>
                            <div className="grid grid-cols-3 gap-3">
                                {[
                                    { value: 'summary', label: 'Risk Summary', icon: '📊' },
                                    { value: 'frontier', label: 'Frontier Analysis', icon: '⚡' },
                                    { value: 'compliance', label: 'Compliance', icon: '✓' },
                                ].map(opt => (
                                    <button
                                        key={opt.value}
                                        onClick={() => setReportType(opt.value)}
                                        className={`p-4 rounded-lg border text-left transition-all ${reportType === opt.value
                                                ? 'border-[var(--bale-accent)] bg-[var(--bale-surface-elevated)]'
                                                : 'border-[var(--bale-border)] hover:border-[var(--bale-border-strong)]'
                                            }`}
                                    >
                                        <div className="text-2xl mb-2">{opt.icon}</div>
                                        <div className="font-medium">{opt.label}</div>
                                    </button>
                                ))}
                            </div>
                        </div>

                        <div className="grid grid-cols-2 gap-4">
                            <div>
                                <label className="label">Date Range</label>
                                <select className="input select">
                                    <option>Last 30 days</option>
                                    <option>Last quarter</option>
                                    <option>Last year</option>
                                    <option>Custom</option>
                                </select>
                            </div>
                            <div>
                                <label className="label">Format</label>
                                <select className="input select">
                                    <option>PDF</option>
                                    <option>HTML</option>
                                    <option>JSON</option>
                                    <option>Markdown</option>
                                </select>
                            </div>
                        </div>

                        <div>
                            <label className="label">Include</label>
                            <div className="space-y-2">
                                {['Risk Scores', 'Critical Findings', 'Frontier Insights', 'Recommendations'].map(item => (
                                    <label key={item} className="flex items-center gap-2 cursor-pointer">
                                        <input type="checkbox" className="w-4 h-4 accent-[var(--bale-accent)]" defaultChecked />
                                        <span className="text-small">{item}</span>
                                    </label>
                                ))}
                            </div>
                        </div>

                        <button className="btn btn-primary btn-lg w-full">
                            Generate Report
                        </button>
                    </div>
                </div>

                <div className="card">
                    <h3 className="text-title mb-6">Recent Reports</h3>
                    <div className="space-y-3">
                        {recentReports.map((report, idx) => (
                            <div key={idx} className="p-3 bg-[var(--bale-surface-elevated)] rounded-lg">
                                <div className="font-medium text-small">{report.name}</div>
                                <div className="flex items-center gap-2 mt-1">
                                    <span className="text-caption text-[var(--bale-text-muted)]">{report.date}</span>
                                    <span className="badge badge-info">{report.format}</span>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            </div>
        </div>
    )
}

export default Reports
