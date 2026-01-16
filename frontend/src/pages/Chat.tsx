import { useState, useRef, useEffect, useCallback } from 'react'

interface ChatMessage {
    role: 'user' | 'assistant'
    content: string
    timestamp: string
    data?: any
}

const SUGGESTIONS = [
    'What is my total risk exposure?',
    'Show me high-risk contracts',
    'Explain the indemnification clause',
    'Give me a portfolio summary',
]

function Chat() {
    const [messages, setMessages] = useState<ChatMessage[]>([])
    const [input, setInput] = useState('')
    const [isLoading, setIsLoading] = useState(false)
    const messagesEndRef = useRef<HTMLDivElement>(null)
    const inputRef = useRef<HTMLInputElement>(null)

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
    }

    useEffect(() => {
        scrollToBottom()
        inputRef.current?.focus()
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
        } catch (error) {
            console.error('Chat error:', error)
            setMessages(prev => [...prev, {
                role: 'assistant',
                content: 'Sorry, something went wrong. Please try again.',
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

    const hasMessages = messages.length > 0

    return (
        <div className="fade-in h-full flex flex-col max-w-3xl mx-auto" style={{ height: 'calc(100vh - 80px)' }}>

            {/* Empty State - Clean Welcome */}
            {!hasMessages && (
                <div className="flex-1 flex flex-col items-center justify-center text-center px-8">
                    <div className="w-20 h-20 bg-gradient-to-br from-[var(--bale-accent)] to-purple-600 rounded-3xl flex items-center justify-center mb-6 shadow-lg shadow-[var(--bale-accent)]/20">
                        <span className="text-4xl">💬</span>
                    </div>
                    <h1 className="text-3xl font-bold text-[var(--bale-text)] mb-2">
                        Ask BALE Anything
                    </h1>
                    <p className="text-lg text-[var(--bale-text-muted)] mb-8 max-w-md">
                        Get insights about your contracts, understand risks, or ask about legal clauses.
                    </p>

                    {/* Suggestion Chips */}
                    <div className="flex flex-wrap justify-center gap-2 max-w-lg">
                        {SUGGESTIONS.map((s, idx) => (
                            <button
                                key={idx}
                                onClick={() => sendMessage(s)}
                                className="px-4 py-2 bg-[var(--bale-surface)] border border-[var(--bale-border)] rounded-full text-sm text-[var(--bale-text-secondary)] hover:border-[var(--bale-accent)] hover:text-[var(--bale-accent)] transition-all"
                            >
                                {s}
                            </button>
                        ))}
                    </div>
                </div>
            )}

            {/* Messages */}
            {hasMessages && (
                <div className="flex-1 overflow-y-auto py-4 space-y-4">
                    {messages.map((msg, idx) => (
                        <div
                            key={idx}
                            className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
                        >
                            <div
                                className={`max-w-[85%] rounded-2xl px-5 py-3 ${msg.role === 'user'
                                        ? 'bg-[var(--bale-accent)] text-white'
                                        : 'bg-[var(--bale-surface)] border border-[var(--bale-border)]'
                                    }`}
                            >
                                <div
                                    className="whitespace-pre-wrap text-[15px] leading-relaxed"
                                    dangerouslySetInnerHTML={{
                                        __html: msg.content
                                            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
                                            .replace(/\n/g, '<br>')
                                    }}
                                />
                                {msg.data && Object.keys(msg.data).length > 0 && (
                                    <details className="mt-3 text-sm opacity-70">
                                        <summary className="cursor-pointer">View data</summary>
                                        <pre className="mt-2 p-2 bg-black/10 rounded text-xs overflow-auto max-h-32">
                                            {JSON.stringify(msg.data, null, 2)}
                                        </pre>
                                    </details>
                                )}
                            </div>
                        </div>
                    ))}

                    {isLoading && (
                        <div className="flex justify-start">
                            <div className="bg-[var(--bale-surface)] border border-[var(--bale-border)] rounded-2xl px-5 py-3">
                                <div className="flex items-center gap-2">
                                    <div className="w-2 h-2 bg-[var(--bale-accent)] rounded-full animate-pulse" />
                                    <div className="w-2 h-2 bg-[var(--bale-accent)] rounded-full animate-pulse" style={{ animationDelay: '0.2s' }} />
                                    <div className="w-2 h-2 bg-[var(--bale-accent)] rounded-full animate-pulse" style={{ animationDelay: '0.4s' }} />
                                </div>
                            </div>
                        </div>
                    )}

                    <div ref={messagesEndRef} />
                </div>
            )}

            {/* Input Bar - Always at Bottom */}
            <div className="pt-4 border-t border-[var(--bale-border)]">
                <form onSubmit={handleSubmit} className="flex gap-3">
                    <input
                        ref={inputRef}
                        type="text"
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        placeholder="Ask about your contracts..."
                        className="flex-1 px-5 py-4 bg-[var(--bale-surface)] border border-[var(--bale-border)] rounded-2xl text-[var(--bale-text)] placeholder-[var(--bale-text-muted)] focus:outline-none focus:border-[var(--bale-accent)] transition-colors"
                        disabled={isLoading}
                    />
                    <button
                        type="submit"
                        disabled={isLoading || !input.trim()}
                        className="px-6 py-4 bg-[var(--bale-accent)] text-white rounded-2xl font-medium disabled:opacity-50 hover:opacity-90 transition-all"
                    >
                        <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
                        </svg>
                    </button>
                </form>
            </div>
        </div>
    )
}

export default Chat
