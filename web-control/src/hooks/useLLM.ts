import { useState, useCallback } from "react"

interface LLMStatusResponse {
  ollama_available: boolean
  transformers_available: boolean
  active_backend: string
  cached_responses: number
}

interface LLMGenerateResponse {
  prompt: string
  response: string
  backend: string
}

interface LLMAnalysisResponse {
  text: string
  results: Array<{
    keyword: string
    similarity: number
    context_score: number
  }>
  best_match: string | null
  confidence: number
}

const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:5000"

export function useLLM() {
  const [status, setStatus] = useState<LLMStatusResponse | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const getStatus = useCallback(async () => {
    try {
      setLoading(true)
      const response = await fetch(`${API_BASE}/api/llm/status`)
      if (!response.ok) throw new Error("Failed to get LLM status")
      const data = await response.json()
      setStatus(data)
      return data
    } catch (err) {
      const message = err instanceof Error ? err.message : "Unknown error"
      setError(message)
      return null
    } finally {
      setLoading(false)
    }
  }, [])

  const generate = useCallback(
    async (
      prompt: string,
      maxTokens: number = 256,
      temperature: number = 0.7
    ): Promise<LLMGenerateResponse | null> => {
      try {
        setLoading(true)
        setError(null)
        const response = await fetch(`${API_BASE}/api/llm/generate`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ prompt, max_tokens: maxTokens, temperature }),
        })
        if (!response.ok) throw new Error("Failed to generate text")
        const data = await response.json()
        return data
      } catch (err) {
        const message = err instanceof Error ? err.message : "Unknown error"
        setError(message)
        return null
      } finally {
        setLoading(false)
      }
    },
    []
  )

  const analyzeContext = useCallback(
    async (
      text: string,
      contextKeywords: string[],
      threshold: number = 0.6
    ): Promise<LLMAnalysisResponse | null> => {
      try {
        setLoading(true)
        setError(null)
        const response = await fetch(`${API_BASE}/api/llm/analyze-context`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            text,
            context_keywords: contextKeywords,
            threshold,
          }),
        })
        if (!response.ok) throw new Error("Failed to analyze context")
        const data = await response.json()
        return data
      } catch (err) {
        const message = err instanceof Error ? err.message : "Unknown error"
        setError(message)
        return null
      } finally {
        setLoading(false)
      }
    },
    []
  )

  const clearCache = useCallback(async () => {
    try {
      setLoading(true)
      const response = await fetch(`${API_BASE}/api/llm/cache/clear`, {
        method: "POST",
      })
      if (!response.ok) throw new Error("Failed to clear cache")
      return true
    } catch (err) {
      const message = err instanceof Error ? err.message : "Unknown error"
      setError(message)
      return false
    } finally {
      setLoading(false)
    }
  }, [])

  return {
    status,
    loading,
    error,
    getStatus,
    generate,
    analyzeContext,
    clearCache,
  }
}
