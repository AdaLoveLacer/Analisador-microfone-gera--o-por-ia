import { useState } from "react"

const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:5000"

export function useAudioDiagnostics() {
  const [diagnosing, setDiagnosing] = useState(false)
  const [result, setResult] = useState<any | null>(null)
  const [error, setError] = useState<string | null>(null)

  const runDiagnostics = async (timeout = 10000) => {
    setDiagnosing(true)
    setError(null)
    setResult(null)
    try {
      // Primeiro, garantir que a captura está iniciada
      await fetch(`${API_BASE}/api/capture/start`, { method: "POST" })
      
      // Aguardar um pouco para o microfone inicializar
      await new Promise(resolve => setTimeout(resolve, 1500))
      
      const resp = await Promise.race([
        fetch(`${API_BASE}/api/audio/level`),
        new Promise<Response>((_, reject) => setTimeout(() => reject(new Error("Timeout")), timeout)),
      ]) as Response

      if (!resp.ok) {
        const data = await resp.json().catch(() => ({}))
        setError(data.error || `HTTP ${resp.status}`)
        return null
      }

      const data = await resp.json()
      setResult(data)
      return data
    } catch (err: any) {
      setError(err?.message || String(err))
      return null
    } finally {
      setDiagnosing(false)
    }
  }

  return { diagnosing, result, error, runDiagnostics }
}

export default useAudioDiagnostics
