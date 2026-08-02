import { useEffect, useState } from 'react'
import './App.css'

const POLL_INTERVAL_MS = 2 * 60 * 1000

function prettyStatus(status) {
  if (!status) return 'Waiting to check status'
  return String(status).replaceAll('_', ' ').toLowerCase()
}

function App() {
  const [restaurantUrl, setRestaurantUrl] = useState('')
  const [task, setTask] = useState(null)
  const [error, setError] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [lastChecked, setLastChecked] = useState(null)

  useEffect(() => {
    if (!task?.taskId || task.complete) return undefined

    let cancelled = false

    const checkTask = async () => {
      try {
        const response = await fetch(`http://localhost:8000/api/task/${encodeURIComponent(task.taskId)}`)
        const data = await response.json().catch(() => ({}))

        if (!response.ok) {
          throw new Error(data.detail || 'Unable to retrieve the task status.')
        }

        if (cancelled) return

        const status = data.status ?? data.state ?? 'PENDING'
        const complete = ['SUCCESS', 'FAILURE', 'REVOKED'].includes(String(status).toUpperCase())
        setTask((current) => ({
          ...current,
          status,
          result: data.result,
          complete,
        }))
        setLastChecked(new Date())
        setError('')
      } catch (requestError) {
        if (!cancelled) setError(requestError.message)
      }
    }

    const pollTimer = window.setInterval(checkTask, POLL_INTERVAL_MS)
    return () => {
      cancelled = true
      window.clearInterval(pollTimer)
    }
  }, [task?.taskId, task?.complete])

  async function handleSubmit(event) {
    event.preventDefault()
    setError('')
    setIsSubmitting(true)

    try {
      const response = await fetch('http://localhost:8000/api/scrape', {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8' },
        body: new URLSearchParams({ url: restaurantUrl }),
      })
      const data = await response.json().catch(() => ({}))

      if (response.status !== 202) {
        throw new Error(data.detail || 'The scrape request could not be started.')
      }
      if (!data.task_id) {
        throw new Error('The server accepted the request but did not return a task ID.')
      }

      setTask({ taskId: data.task_id, status: 'PENDING', result: null, complete: false })
    } catch (requestError) {
      setError(requestError.message)
    } finally {
      setIsSubmitting(false)
    }
  }

  const isSuccess = String(task?.status).toUpperCase() === 'SUCCESS'

  return (
    <main className="page-shell">
      <section className="card" aria-labelledby="page-title">
        <div className="eyebrow"><span aria-hidden="true">✦</span> EatToGo</div>
        <h1 id="page-title">Find your next table.</h1>
        <p className="intro">Share a restaurant’s booking page and we’ll watch its availability for you.</p>

        {!task ? (
          <form className="scrape-form" onSubmit={handleSubmit}>
            <label htmlFor="restaurant-url">Restaurant booking URL</label>
            <div className="input-row">
              <input
                id="restaurant-url"
                type="url"
                value={restaurantUrl}
                onChange={(event) => setRestaurantUrl(event.target.value)}
                placeholder="https://restaurant.com/reservations"
                required
                disabled={isSubmitting}
              />
              <button type="submit" disabled={isSubmitting}>
                {isSubmitting ? 'Starting…' : 'Check availability'}
              </button>
            </div>
          </form>
        ) : (
          <section className="task-panel" aria-live="polite">
            <div className="status-line">
              <span className={`status-dot ${task.complete ? 'complete' : ''}`} aria-hidden="true" />
              <div>
                <p className="status-label">Task status</p>
                <h2>{prettyStatus(task.status)}</h2>
              </div>
            </div>

            <p className="poll-copy">
              {task.complete
                ? 'This task is finished.'
                : 'We’ll check again every 2 minutes. You can safely leave this page open.'}
            </p>
            <p className="task-id">Task ID: <code>{task.taskId}</code></p>
            {lastChecked && <p className="checked-at">Last checked at {lastChecked.toLocaleTimeString()}.</p>}

            {isSuccess && task.result != null && (
              <div className="result-box">
                <p className="result-label">Availability result</p>
                <pre>{JSON.stringify(task.result, null, 2)}</pre>
              </div>
            )}
            {String(task.status).toUpperCase() === 'FAILURE' && (
              <p className="failure-message">The availability check could not be completed. Please try again later.</p>
            )}
          </section>
        )}

        {error && <p className="error-message" role="alert">{error}</p>}
      </section>
    </main>
  )
}

export default App
