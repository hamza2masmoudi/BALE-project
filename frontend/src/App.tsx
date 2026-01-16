import { BrowserRouter, Routes, Route } from 'react-router-dom'
import Layout from './components/Layout'
import Dashboard from './pages/Dashboard'
import Analyze from './pages/Analyze'
import FrontierAnalysis from './pages/FrontierAnalysis'
import Contracts from './pages/Contracts'
import Network from './pages/Network'
import Temporal from './pages/Temporal'
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
                    <Route path="analyze" element={<Analyze />} />
                    <Route path="frontier" element={<FrontierAnalysis />} />
                    <Route path="frontier/:id" element={<FrontierAnalysis />} />
                    <Route path="contracts" element={<Contracts />} />
                    <Route path="network" element={<Network />} />
                    <Route path="temporal" element={<Temporal />} />
                    <Route path="reports" element={<Reports />} />
                    <Route path="settings" element={<Settings />} />
                    <Route path="chat" element={<Chat />} />
                    <Route path="generate" element={<Generate />} />
                </Route>
            </Routes>
        </BrowserRouter>
    )
}

export default App
