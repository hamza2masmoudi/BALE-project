import { Outlet, Link, useLocation } from 'react-router-dom'
import { Scale, FileText, Settings, BarChart3, Zap } from 'lucide-react'
import clsx from 'clsx'

const navItems = [
    { path: '/', label: 'Dashboard', icon: BarChart3 },
    { path: '/analyze', label: 'Analyze', icon: Scale },
    { path: '/contracts', label: 'Contracts', icon: FileText },
    { path: '/settings', label: 'Settings', icon: Settings },
]

export default function Layout() {
    const location = useLocation()

    return (
        <div className="min-h-screen bg-bale-dark flex">
            {/* Sidebar */}
            <aside className="w-64 bg-bale-darker border-r border-bale-border flex flex-col">
                {/* Logo */}
                <div className="p-6 border-b border-bale-border">
                    <div className="flex items-center gap-3">
                        <div className="w-10 h-10 bg-white rounded-lg flex items-center justify-center">
                            <span className="text-black font-bold text-lg">///</span>
                        </div>
                        <div>
                            <h1 className="font-semibold text-lg">BALE</h1>
                            <p className="text-xs text-bale-muted">Legal Intelligence</p>
                        </div>
                    </div>
                </div>

                {/* Navigation */}
                <nav className="flex-1 p-4 space-y-1">
                    {navItems.map((item) => {
                        const Icon = item.icon
                        const isActive = location.pathname === item.path
                        return (
                            <Link
                                key={item.path}
                                to={item.path}
                                className={clsx(
                                    'flex items-center gap-3 px-4 py-3 rounded-lg transition-all duration-200',
                                    isActive
                                        ? 'bg-white text-black'
                                        : 'text-bale-muted hover:text-white hover:bg-bale-card'
                                )}
                            >
                                <Icon size={20} />
                                <span className="font-medium">{item.label}</span>
                            </Link>
                        )
                    })}
                </nav>

                {/* Status */}
                <div className="p-4 border-t border-bale-border">
                    <div className="glass-card rounded-lg p-4">
                        <div className="flex items-center gap-2 mb-2">
                            <Zap size={16} className="text-bale-success" />
                            <span className="text-sm font-medium">System Status</span>
                        </div>
                        <div className="space-y-2 text-xs">
                            <div className="flex justify-between">
                                <span className="text-bale-muted">Local LLM</span>
                                <span className="text-bale-success">● Online</span>
                            </div>
                            <div className="flex justify-between">
                                <span className="text-bale-muted">Database</span>
                                <span className="text-bale-success">● Connected</span>
                            </div>
                        </div>
                    </div>
                </div>
            </aside>

            {/* Main Content */}
            <main className="flex-1 overflow-auto">
                <Outlet />
            </main>
        </div>
    )
}
