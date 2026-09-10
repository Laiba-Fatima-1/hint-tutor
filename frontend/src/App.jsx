import { useEffect, useRef, useState } from 'react'
import './App.css'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const TAXONOMY = [
  { policy: 'hint', label: 'Hint', color: 'var(--hint)', when: 'you have a bug' },
  { policy: 'socratic_question', label: 'Socratic Question', color: 'var(--socratic)', when: "you're confused about a concept" },
  { policy: 'concept_explanation', label: 'Concept Explanation', color: 'var(--concept)', when: 'you ask "what is X"' },
  { policy: 'partial_code_feedback', label: 'Partial-Code Feedback', color: 'var(--partial)', when: "you've written something so far" },
  { policy: 'refuse_and_redirect', label: 'Refuse & Redirect', color: 'var(--refuse)', when: 'you ask for the whole answer' },
]

function ChalkTag({ label, color }) {
  return (
    <span className="chalk-tag" style={{ '--tag-color': color }}>
      {label}
    </span>
  )
}

function Message({ msg }) {
  if (msg.role === 'student') {
    return (
      <div className="msg msg-student">
        <div className="msg-student-bubble">
          <p>{msg.text}</p>
          {msg.code && <pre className="msg-code">{msg.code}</pre>}
        </div>
      </div>
    )
  }
  if (msg.role === 'error') {
    return (
      <div className="msg msg-error">
        <p><strong>The tutor couldn't respond.</strong> {msg.text}</p>
      </div>
    )
  }
  return (
    <div className="msg msg-tutor">
      <ChalkTag label={msg.policyLabel} color={msg.policyColor} />
      <p className="msg-tutor-text">{msg.text}</p>
    </div>
  )
}

export default function App() {
  const [messages, setMessages] = useState([])
  const [message, setMessage] = useState('')
  const [code, setCode] = useState('')
  const [showCode, setShowCode] = useState(false)
  const [loading, setLoading] = useState(false)
  const threadRef = useRef(null)

  useEffect(() => {
    if (threadRef.current) {
      threadRef.current.scrollTop = threadRef.current.scrollHeight
    }
  }, [messages, loading])

  async function handleSend(e) {
    e.preventDefault()
    const trimmed = message.trim()
    if (!trimmed || loading) return

    const studentMsg = { role: 'student', text: trimmed, code: showCode ? code.trim() : '' }
    setMessages((m) => [...m, studentMsg])
    setMessage('')
    setLoading(true)

    try {
      const resp = await fetch(`${API_URL}/api/tutor`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: trimmed,
          code: showCode && code.trim() ? code.trim() : null,
        }),
      })
      if (!resp.ok) {
        const body = await resp.json().catch(() => ({}))
        throw new Error(body.detail || `Request failed (${resp.status})`)
      }
      const data = await resp.json()
      setMessages((m) => [
        ...m,
        {
          role: 'tutor',
          text: data.response,
          policyLabel: data.policy_label,
          policyColor: data.policy_color,
        },
      ])
    } catch (err) {
      setMessages((m) => [...m, { role: 'error', text: err.message }])
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="app">
      <header className="topbar">
        <h1>
          <em>Hint,</em> Don't Solve
        </h1>
        <p>A tutor that answers your question — not your assignment.</p>
      </header>

      <main className="layout">
        <section className="ask-panel">
          <form onSubmit={handleSend}>
            <label className="field-label" htmlFor="message">
              What are you stuck on?
            </label>
            <textarea
              id="message"
              placeholder="e.g. Why does this throw an IndexError on the last row?"
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              rows={4}
              required
            />

            <button
              type="button"
              className="code-toggle"
              onClick={() => setShowCode((s) => !s)}
            >
              {showCode ? 'Remove code' : 'Add code'}
            </button>

            {showCode && (
              <textarea
                className="code-input"
                placeholder="Paste the relevant code here"
                value={code}
                onChange={(e) => setCode(e.target.value)}
                rows={8}
              />
            )}

            <button type="submit" className="send-btn" disabled={loading}>
              {loading ? 'Thinking it through…' : 'Ask the tutor'}
            </button>
          </form>

          <div className="legend">
            <p className="legend-title">How it decides what to say</p>
            <ul>
              {TAXONOMY.map((t) => (
                <li key={t.policy}>
                  <span className="swatch" style={{ background: t.color }} />
                  <span className="legend-label">{t.label}</span>
                  <span className="legend-when">— when {t.when}</span>
                </li>
              ))}
            </ul>
          </div>
        </section>

        <section className="thread-panel" ref={threadRef}>
          {messages.length === 0 && (
            <div className="empty-state">
              <p>
                Ask about a bug, a confusing concept, or code you're partway
                through. This tutor won't hand you a finished answer — it'll
                pick a teaching move from the taxonomy on the left and stick
                to it.
              </p>
            </div>
          )}
          {messages.map((m, i) => (
            <Message key={i} msg={m} />
          ))}
          {loading && (
            <div className="msg msg-tutor msg-loading">
              <span className="dot" />
              <span className="dot" />
              <span className="dot" />
            </div>
          )}
        </section>
      </main>
    </div>
  )
}
