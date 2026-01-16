import { NavLink, Outlet } from 'react-router-dom'

// Icons as simple SVG components
const Icons = {
    Dashboard: () => (
        <svg className="sidebar-link-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zM14 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2zM14 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z" />
        </svg>
    ),
    Analyze: () => (
        <svg className="sidebar-link-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
        </svg>
    ),
    Frontier: () => (
        <svg className="sidebar-link-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
        </svg>
    ),
    Contracts: () => (
        <svg className="sidebar-link-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
        </svg>
    ),
    Network: () => (
        <svg className="sidebar-link-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 01-9 9m9-9a9 9 0 00-9-9m9 9H3m9 9a9 9 0 01-9-9m9 9c1.657 0 3-4.03 3-9s-1.343-9-3-9m0 18c-1.657 0-3-4.03-3-9s1.343-9 3-9m-9 9a9 9 0 019-9" />
        </svg>
    ),
    Temporal: () => (
        <svg className="sidebar-link-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
    ),
    Reports: () => (
        <svg className="sidebar-link-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
        </svg>
    ),
    Settings: () => (
        <svg className="sidebar-link-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
        </svg>
    ),
    Help: () => (
        <svg className="sidebar-link-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
    ),
}

function Layout() {
    return (
        <div className="flex min-h-screen">
            {/* Sidebar */}
            <aside className="sidebar">
                {/* Logo */}
                <div className="sidebar-header">
                    <div className="sidebar-logo">
                        <div className="w-8 h-8 rounded-lg gradient-accent flex items-center justify-center">
                            <span className="text-white font-bold text-sm">B</span>
                        </div>
                        <span className="gradient-text">BALE</span>
                    </div>
                    <div className="text-caption text-bale-text-muted mt-1">
                        <span>Legal Intelligence</span>
                    </div>
                </div>

                {/* Navigation */}
                <nav className="sidebar-nav">
                    {/* Main */}
                    <div className="sidebar-section">
                        <div className="sidebar-section-title">Main</div>
                        <NavLink
                            to="/"
                            className={({ isActive }) => `sidebar-link ${isActive ? 'active' : ''}`}
                            end
                        >
                            <Icons.Dashboard />
                            <span>Dashboard</span>
                        </NavLink>
                        <NavLink
                            to="/analyze"
                            className={({ isActive }) => `sidebar-link ${isActive ? 'active' : ''}`}
                        >
                            <Icons.Analyze />
                            <span>Analyze</span>
                        </NavLink>
                        <NavLink
                            to="/frontier"
                            className={({ isActive }) => `sidebar-link ${isActive ? 'active' : ''}`}
                        >
                            <Icons.Frontier />
                            <span>Frontier Analysis</span>
                        </NavLink>
                    </div>

                    {/* Library */}
                    <div className="sidebar-section">
                        <div className="sidebar-section-title">Library</div>
                        <NavLink
                            to="/contracts"
                            className={({ isActive }) => `sidebar-link ${isActive ? 'active' : ''}`}
                        >
                            <Icons.Contracts />
                            <span>Contracts</span>
                        </NavLink>
                        <NavLink
                            to="/network"
                            className={({ isActive }) => `sidebar-link ${isActive ? 'active' : ''}`}
                        >
                            <Icons.Network />
                            <span>Entity Network</span>
                        </NavLink>
                        <NavLink
                            to="/temporal"
                            className={({ isActive }) => `sidebar-link ${isActive ? 'active' : ''}`}
                        >
                            <Icons.Temporal />
                            <span>Temporal View</span>
                        </NavLink>
                    </div>

                    {/* Insights */}
                    <div className="sidebar-section">
                        <div className="sidebar-section-title">Insights</div>
                        <NavLink
                            to="/reports"
                            className={({ isActive }) => `sidebar-link ${isActive ? 'active' : ''}`}
                        >
                            <Icons.Reports />
                            <span>Reports</span>
                        </NavLink>
                    </div>
                </nav>

                {/* Footer */}
                <div className="mt-auto p-4 border-t border-[var(--bale-border)]">
                    <NavLink
                        to="/settings"
                        className={({ isActive }) => `sidebar-link ${isActive ? 'active' : ''}`}
                    >
                        <Icons.Settings />
                        <span>Settings</span>
                    </NavLink>
                    <a
                        href="https://docs.bale.dev"
                        target="_blank"
                        rel="noopener noreferrer"
                        className="sidebar-link"
                    >
                        <Icons.Help />
                        <span>Help & Docs</span>
                    </a>

                    {/* Version */}
                    <div className="mt-4 px-3 py-2 bg-[var(--bale-surface)] rounded-lg">
                        <div className="text-caption text-[var(--bale-text-muted)]">Version</div>
                        <div className="text-small font-medium text-[var(--bale-text-secondary)]">
                            BALE 2.2 Enterprise
                        </div>
                    </div>
                </div>
            </aside>

            {/* Main Content */}
            <main className="main-content">
                <Outlet />
            </main>
        </div>
    )
}

export default Layout
