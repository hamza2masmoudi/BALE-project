import { NavLink, Outlet } from 'react-router-dom'

function Layout() {
    return (
        <div className="flex min-h-screen">
            {/* Simplified Sidebar */}
            <aside className="w-64 bg-[var(--bale-surface)] border-r border-[var(--bale-border)] flex flex-col">
                {/* Logo */}
                <div className="p-5 border-b border-[var(--bale-border)]">
                    <div className="flex items-center gap-2">
                        <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-[var(--bale-accent)] to-purple-600 flex items-center justify-center">
                            <span className="text-white font-bold text-lg">B</span>
                        </div>
                        <div>
                            <span className="text-lg font-semibold text-[var(--bale-text)]">BALE</span>
                            <span className="text-xs text-[var(--bale-text-muted)] block -mt-1">Legal Intelligence</span>
                        </div>
                    </div>
                </div>

                {/* Primary Actions - Clear Entry Points */}
                <nav className="flex-1 p-4">
                    <div className="space-y-1">
                        <NavLink
                            to="/"
                            className={({ isActive }) =>
                                `flex items-center gap-3 px-4 py-3 rounded-xl transition-all ${isActive
                                    ? 'bg-[var(--bale-accent)] text-white'
                                    : 'text-[var(--bale-text-secondary)] hover:bg-[var(--bale-surface-elevated)]'
                                }`
                            }
                            end
                        >
                            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
                            </svg>
                            <span className="font-medium">Home</span>
                        </NavLink>

                        <NavLink
                            to="/chat"
                            className={({ isActive }) =>
                                `flex items-center gap-3 px-4 py-3 rounded-xl transition-all ${isActive
                                    ? 'bg-[var(--bale-accent)] text-white'
                                    : 'text-[var(--bale-text-secondary)] hover:bg-[var(--bale-surface-elevated)]'
                                }`
                            }
                        >
                            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                            </svg>
                            <span className="font-medium">Ask BALE</span>
                        </NavLink>

                        <NavLink
                            to="/contracts"
                            className={({ isActive }) =>
                                `flex items-center gap-3 px-4 py-3 rounded-xl transition-all ${isActive
                                    ? 'bg-[var(--bale-accent)] text-white'
                                    : 'text-[var(--bale-text-secondary)] hover:bg-[var(--bale-surface-elevated)]'
                                }`
                            }
                        >
                            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                            </svg>
                            <span className="font-medium">Contracts</span>
                        </NavLink>
                    </div>

                    {/* Secondary Actions */}
                    <div className="mt-8 pt-6 border-t border-[var(--bale-border)]">
                        <p className="px-4 text-xs font-medium text-[var(--bale-text-muted)] uppercase tracking-wider mb-3">
                            Tools
                        </p>
                        <div className="space-y-1">
                            <NavLink
                                to="/analyze"
                                className={({ isActive }) =>
                                    `flex items-center gap-3 px-4 py-2.5 rounded-lg transition-all text-sm ${isActive
                                        ? 'bg-[var(--bale-surface-elevated)] text-[var(--bale-accent)]'
                                        : 'text-[var(--bale-text-muted)] hover:text-[var(--bale-text-secondary)]'
                                    }`
                                }
                            >
                                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
                                </svg>
                                <span>Analyze</span>
                            </NavLink>

                            <NavLink
                                to="/generate"
                                className={({ isActive }) =>
                                    `flex items-center gap-3 px-4 py-2.5 rounded-lg transition-all text-sm ${isActive
                                        ? 'bg-[var(--bale-surface-elevated)] text-[var(--bale-accent)]'
                                        : 'text-[var(--bale-text-muted)] hover:text-[var(--bale-text-secondary)]'
                                    }`
                                }
                            >
                                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
                                </svg>
                                <span>Generate</span>
                            </NavLink>

                            <NavLink
                                to="/reports"
                                className={({ isActive }) =>
                                    `flex items-center gap-3 px-4 py-2.5 rounded-lg transition-all text-sm ${isActive
                                        ? 'bg-[var(--bale-surface-elevated)] text-[var(--bale-accent)]'
                                        : 'text-[var(--bale-text-muted)] hover:text-[var(--bale-text-secondary)]'
                                    }`
                                }
                            >
                                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                                </svg>
                                <span>Reports</span>
                            </NavLink>
                        </div>
                    </div>
                </nav>

                {/* Footer */}
                <div className="p-4 border-t border-[var(--bale-border)]">
                    <NavLink
                        to="/settings"
                        className={({ isActive }) =>
                            `flex items-center gap-3 px-4 py-2.5 rounded-lg transition-all text-sm ${isActive
                                ? 'bg-[var(--bale-surface-elevated)] text-[var(--bale-accent)]'
                                : 'text-[var(--bale-text-muted)] hover:text-[var(--bale-text-secondary)]'
                            }`
                        }
                    >
                        <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                        </svg>
                        <span>Settings</span>
                    </NavLink>
                    <div className="mt-4 px-4 text-xs text-[var(--bale-text-muted)]">
                        v2.2 Enterprise
                    </div>
                </div>
            </aside>

            {/* Main Content */}
            <main className="flex-1 p-8 overflow-auto bg-[var(--bale-bg)]">
                <Outlet />
            </main>
        </div>
    )
}

export default Layout
