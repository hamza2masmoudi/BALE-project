import { useState, useRef, useEffect, useCallback } from 'react'

interface ChatMessage {
    role: 'user' | 'assistant'
    content: string
    timestamp: string
    data?: any
}

const QUICK_QUERIES = [
    { label: '📊 Risk Summary', query: 'What is my total risk exposure?' },
    { label: '🔴 High Risk', query: 'Show me high-risk contracts' },
    { label: '📅 Expiring Soon', query: 'What contracts expire in next 90 days?' },
    { label: '📈 Portfolio Stats', query: 'Give me a portfolio summary' },
    { label: '🏢 Counterparties', query: 'Who are my biggest counterparties?' },
    { label: '⚖️ Market Compare', query: 'How do my terms compare to market?' },
]

function Chat() {
    const [messages, setMessages] = useState<ChatMessage[]>([
        {
            role: 'assistant',
            content: `👋 Hi! I'm BALE, your legal intelligence assistant.

I can help you with:
- **Risk Analysis** - "What is my total risk exposure?"
- **Contract Search** - "Find all NDAs with UK jurisdiction"
- **Portfolio Stats** - "Give me a portfolio summary"
- **Clause Explanations** - "Explain the indemnification clause"
- **Contract Generation** - "Generate an NDA for a software company"

Ask me anything about your contracts!`,
            timestamp: new Date().toISOString(),
        }
    ])
    const [input, setInput] = useState('')
    const [isLoading, setIsLoading] = useState(false)
    const [suggestions, setSuggestions] = useState<string[]>([])
    const messagesEndRef = useRef<HTMLDivElement>(null)
    const inputRef = useRef<HTMLInputElement>(null)

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
    }

    useEffect(() => {
        scrollToBottom()
    }, [messages])

    const sendMessage = useCallback(async (query: string) => {
        if (!query.trim() || isLoading) return

        const userMessage: ChatMessage = {
            role: 'user',
            content: query,
            timestamp: new Date().toISOString(),
        }

        setMessages(prev => [...prev, userMessage])
        setInput('')
        setIsLoading(true)
        setSuggestions([])

        try {
            const response = await fetch('/api/intelligence/query', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ query }),
            })

            if (!response.ok) throw new Error('Query failed')

            const result = await response.json()

            const assistantMessage: ChatMessage = {
                role: 'assistant',
                content: result.answer,
                timestamp: new Date().toISOString(),
                data: result.data,
            }

            setMessages(prev => [...prev, assistantMessage])
            setSuggestions(result.follow_up_suggestions || [])
        } catch (error) {
            console.error('Chat error:', error)
            setMessages(prev => [...prev, {
                role: 'assistant',
                content: 'Sorry, I encountered an error processing your request. Please try again.',
                timestamp: new Date().toISOString(),
            }])
        } finally {
            setIsLoading(false)
        }
    }, [isLoading])

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault()
        sendMessage(input)
    }

    const handleQuickQuery = (query: string) => {
        setInput(query)
        sendMessage(query)
    }

    return (
        <div className="fade-in h-full flex flex-col" style={{ height: 'calc(100vh - 120px)' }}>
            {/* Header */}
            <div className="page-header pb-4">
                <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-[var(--bale-accent)] to-[var(--frontier-reflexive)] flex items-center justify-center">
                        <span className="text-xl">🧠</span>
                    </div>
                    <div>
                        <h1 className="page-title">BALE Intelligence</h1>
                        <p className="text-small text-[var(--bale-text-muted)]">
                            Ask anything about your contracts
                        </p>
                    </div>
                </div>
            </div>

            {/* Quick Queries */}
            <div className="flex flex-wrap gap-2 mb-4">
                {QUICK_QUERIES.map((qq, idx) => (
                    <button
                        key={idx}
                        onClick={() => handleQuickQuery(qq.query)}
                        className="px-3 py-1.5 rounded-full text-small bg-[var(--bale-surface-elevated)] hover:bg-[var(--bale-border)] transition-colors border border-[var(--bale-border)]"
                    >
                        {qq.label}
                    </button>
                ))}
            </div>

            {/* Chat Messages */}
            <div className="flex-1 overflow-y-auto rounded-lg bg-[var(--bale-surface)] border border-[var(--bale-border)] p-4 mb-4">
                <div className="space-y-4">
                    {messages.map((msg, idx) => (
                        <div
                            key={idx}
                            className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
                        >
                            <div
                                className={`max-w-[80%] rounded-2xl px-4 py-3 ${msg.role === 'user'
                                    ? 'bg-[var(--bale-accent)] text-white rounded-br-sm'
                                    : 'bg-[var(--bale-surface-elevated)] border border-[var(--bale-border)] rounded-bl-sm'
                                    }`}
                            >
                                {msg.role === 'assistant' && (
                                    <div className="flex items-center gap-2 mb-2">
                                        <span className="text-sm">🧠</span>
                                        <span className="text-caption font-medium text-[var(--bale-accent)]">BALE</span>
                                    </div>
                                )}
                                <div
                                    className="whitespace-pre-wrap text-sm"
                                    style={{ lineHeight: '1.6' }}
                                    dangerouslySetInnerHTML={{
                                        __html: msg.content
                                            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
                                            .replace(/\n/g, '<br>')
                                    }}
                                />
                                {msg.data && Object.keys(msg.data).length > 0 && (
                                    <div className="mt-3 pt-3 border-t border-[var(--bale-border)]">
                                        <details className="text-caption">
                                            <summary className="cursor-pointer text-[var(--bale-text-muted)]">
                                                📊 View data
                                            </summary>
                                            <pre className="mt-2 p-2 bg-[var(--bale-surface)] rounded text-xs overflow-auto">
                                                {JSON.stringify(msg.data, null, 2)}
                                            </pre>
                                        </details>
                                    </div>
                                )}
                            </div>
                        </div>
                    ))}

                    {isLoading && (
                        <div className="flex justify-start">
                            <div className="bg-[var(--bale-surface-elevated)] border border-[var(--bale-border)] rounded-2xl rounded-bl-sm px-4 py-3">
                                <div className="flex items-center gap-2">
                                    <div className="spinner"></div>
                                    <span className="text-small text-[var(--bale-text-muted)]">Thinking...</span>
                                </div>
                            </div>
                        </div>
                    )}

                    <div ref={messagesEndRef} />
                </div>
            </div>

            {/* Suggestions */}
            {suggestions.length > 0 && (
                <div className="flex flex-wrap gap-2 mb-3">
                    <span className="text-caption text-[var(--bale-text-muted)]">Suggestions:</span>
                    {suggestions.map((s, idx) => (
                        <button
                            key={idx}
                            onClick={() => handleQuickQuery(s)}
                            className="px-2 py-1 rounded text-caption bg-[var(--bale-surface-elevated)] hover:bg-[var(--bale-border)] transition-colors"
                        >
                            {s}
                        </button>
                    ))}
                </div>
            )}

            {/* Input */}
            <form onSubmit={handleSubmit} className="flex gap-3">
                <input
                    ref={inputRef}
                    type="text"
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    placeholder="Ask about your contracts..."
                    className="input flex-1"
                    disabled={isLoading}
                />
                <button
                    type="submit"
                    disabled={isLoading || !input.trim()}
                    className="btn btn-primary"
                >
                    <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
                    </svg>
                    Send
                </button>
            </form>

            {/* Keyboard hint */}
            <div className="text-center mt-2">
                <span className="text-caption text-[var(--bale-text-muted)]">
                    Press Enter to send • Type "generate" to create contracts
                </span>
            </div>
        </div>
    )
}

export default Chat
