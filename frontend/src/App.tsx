import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import Layout from './components/Layout'
import Dashboard from './pages/Dashboard'
import Analyze from './pages/Analyze'
import FrontierAnalysis from './pages/FrontierAnalysis'
import Contracts from './pages/Contracts'
import Reports from './pages/Reports'
import Settings from './pages/Settings'
import Chat from './pages/Chat'
import Generate from './pages/Generate'

function App() {
    return (
        <BrowserRouter>
            <Routes>
                <Route path="/" element={<Layout />}>
                    <Route index element={<Dashboard />} />
                    <Route path="chat" element={<Chat />} />
                    <Route path="analyze" element={<Analyze />} />
                    <Route path="frontier" element={<FrontierAnalysis />} />
                    <Route path="frontier/:id" element={<FrontierAnalysis />} />
                    <Route path="contracts" element={<Contracts />} />
                    <Route path="generate" element={<Generate />} />
                    <Route path="reports" element={<Reports />} />
                    <Route path="settings" element={<Settings />} />
                    {/* Redirect old routes */}
                    <Route path="network" element={<Navigate to="/contracts" replace />} />
                    <Route path="temporal" element={<Navigate to="/contracts" replace />} />
                </Route>
            </Routes>
        </BrowserRouter>
    )
}

export default App
