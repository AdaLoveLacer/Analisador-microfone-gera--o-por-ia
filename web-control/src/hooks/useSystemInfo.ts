import { useState, useEffect } from "react"

interface AudioDevice {
  id: string | number
  name: string
  index?: number
}

interface WhisperStatus {
  available: boolean
  model: string
  version: string
}

interface LLMConfig {
  ollama_available: boolean
  transformers_available: boolean
  active_backend: string
  models?: string[]
}

interface SystemInfo {
  devices: AudioDevice[]
  whisper_status: WhisperStatus
  llm_config: LLMConfig
  gpu_info?: {
    name: string
    available: boolean
    memory_total_mb?: number
    memory_free_mb?: number
  }
}

const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:5000"

// Verificar se backend está disponível
const checkBackendAvailable = async (): Promise<boolean> => {
  try {
    const response = (await Promise.race([
      fetch(`${API_BASE}/api/status`, { method: "GET" }),
      new Promise<Response>((_, reject) =>
        setTimeout(() => reject(new Error("Timeout")), 10000)
      ),
    ])) as Response
    return response.ok
  } catch {
    return false
  }
}

export function useSystemInfo() {
  const [systemInfo, setSystemInfo] = useState<SystemInfo | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [backendAvailable, setBackendAvailable] = useState(true)

  useEffect(() => {
    const fetchSystemInfo = async (retries = 3) => {
      try {
        setLoading(true)
        setError(null)

        // Verificar se backend está disponível primeiro
        const isAvailable = await checkBackendAvailable()
        setBackendAvailable(isAvailable)

        if (!isAvailable) {
          throw new Error("Backend não está respondendo. Verifique se a aplicação está rodando.")
        }

        // Função helper para fetch com timeout
        const fetchWithTimeout = (url: string, timeout = 15000): Promise<Response> => {
          return Promise.race([
            fetch(url),
            new Promise<Response>((_, reject) =>
              setTimeout(() => reject(new Error("Timeout")), timeout)
            ),
          ]) as unknown as Promise<Response>
        }

        let devicesData = { devices: [] }
        let statusData: any = {}
        let llmData: any = {}

        // Tentar buscar dispositivos de áudio (com retries)
        for (let i = 0; i < retries; i++) {
          try {
            const devicesRes = await fetchWithTimeout(`${API_BASE}/api/devices`)
            devicesData = devicesRes.ok ? await devicesRes.json() : { devices: [] }
            break
          } catch (e) {
            if (i === retries - 1) throw e
            await new Promise(r => setTimeout(r, 500 * (i + 1)))
          }
        }

        // Buscar status do Whisper (com timeout)
        try {
          const statusRes = await fetchWithTimeout(`${API_BASE}/api/status`)
          statusData = statusRes.ok ? await statusRes.json() : {}
        } catch (e) {
          console.warn("Erro ao buscar status do Whisper:", e)
          statusData = {}
        }

        // Buscar status da LLM (com timeout)
        try {
          const llmRes = await fetchWithTimeout(`${API_BASE}/api/llm/status`)
          llmData = llmRes.ok ? await llmRes.json() : { ollama_available: false, transformers_available: false, active_backend: "ollama" }
        } catch (e) {
          console.warn("Erro ao buscar status da LLM:", e)
          llmData = { ollama_available: false, transformers_available: false, active_backend: "ollama" }
        }

        setSystemInfo({
          devices: devicesData.devices || [],
          whisper_status: {
            available: statusData.whisper_available || statusData.whisper_model ? true : false,
            model: statusData.whisper_model || "base",
            version: "v20231117",
          },
          llm_config: {
            ollama_available: Boolean(llmData.ollama_available),
            transformers_available: Boolean(llmData.transformers_available),
            active_backend: String(llmData.active_backend || "ollama"),
          },
          gpu_info: {
            name: statusData.whisper_device === "cuda" ? "NVIDIA CUDA" : "CPU",
            available: statusData.whisper_device === "cuda",
            memory_total_mb: 8192,
            memory_free_mb: 4096,
          },
        })
      } catch (err) {
        const message = err instanceof Error ? err.message : "Erro ao buscar informações do sistema"
        setError(message)
        console.error("Erro ao buscar system info:", err)
      } finally {
        setLoading(false)
      }
    }

    fetchSystemInfo()
  }, [])

  return { systemInfo, loading, error, backendAvailable }
}

// Small helper hook to read/update audio-related config values
export async function getAudioConfig(): Promise<any> {
  const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:5000"
  const resp = await fetch(`${API_BASE}/api/config`, { method: "GET" })
  if (!resp.ok) throw new Error("Failed to fetch config")
  return resp.json()
}

export async function setAudioConfig(values: any): Promise<any> {
  const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:5000"
  const resp = await fetch(`${API_BASE}/api/config`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ audio: values }),
  })
  if (!resp.ok) {
    const body = await resp.json().catch(() => ({}))
    throw new Error(body.error || `HTTP ${resp.status}`)
  }
  return resp.json()
}

export function useTestWhisper() {
  const [testing, setTesting] = useState(false)
  const [result, setResult] = useState<{ success: boolean; message: string } | null>(null)

  const testWhisper = async () => {
    try {
      setTesting(true)
      setResult(null)

      // Verificar se backend está disponível
      const isAvailable = await checkBackendAvailable()
      if (!isAvailable) {
        setResult({
          success: false,
          message: "Backend não está respondendo",
        })
        return
      }

      const response = (await Promise.race([
        fetch(`${API_BASE}/api/whisper/test`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
        }),
        new Promise<Response>((_, reject) =>
          setTimeout(() => reject(new Error("Timeout - O teste pode demorar alguns segundos")), 30000)
        ),
      ])) as Response

      const data = await response.json()

      if (response.ok && data.success) {
        setResult({
          success: true,
          message: `✓ Whisper operacional! Modelo: ${data.model}, Device: ${data.device}`,
        })
      } else {
        setResult({
          success: false,
          message: data.error || data.message || "Erro ao testar Whisper",
        })
      }
    } catch (error) {
      const message = error instanceof Error ? error.message : "Erro na conexão"
      setResult({
        success: false,
        message: `Erro: ${message}`,
      })
    } finally {
      setTesting(false)
    }
  }

  return { testWhisper, testing, result }
}

export function useGPUControl() {
  const [gpuUsage, setGpuUsage] = useState(50)
  const [saving, setSaving] = useState(false)

  const setGPUUsage = async (percentage: number) => {
    try {
      setSaving(true)

      // Verificar se backend está disponível
      const isAvailable = await checkBackendAvailable()
      if (!isAvailable) {
        console.error("Backend não está respondendo")
        return false
      }

      const response = (await Promise.race([
        fetch(`${API_BASE}/api/config/gpu`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ gpu_usage_percent: percentage }),
        }),
        new Promise<Response>((_, reject) =>
          setTimeout(() => reject(new Error("Timeout")), 15000)
        ),
      ])) as Response

      if (response.ok) {
        setGpuUsage(percentage)
        return true
      }
      return false
    } catch (error) {
      console.error("Erro ao configurar GPU:", error)
      return false
    } finally {
      setSaving(false)
    }
  }

  return { gpuUsage, setGPUUsage, saving }
}

export function useAudioDeviceConfig() {
  const [selectedDevice, setSelectedDevice] = useState<string | number | null>(null)
  const [saving, setSaving] = useState(false)

  // Carregar dispositivo salvo ao inicializar
  useEffect(() => {
    const loadSavedDevice = async () => {
      try {
        const response = await fetch(`${API_BASE}/api/config`, {
          method: "GET"
        })
        if (response.ok) {
          const config = await response.json()
          const savedDevice = config?.audio?.input_device
          if (savedDevice !== undefined && savedDevice !== null) {
            setSelectedDevice(savedDevice)
          }
        }
      } catch (error) {
        console.warn("Erro ao carregar dispositivo salvo:", error)
      }
    }
    
    loadSavedDevice()
  }, [])

  const setAudioDevice = async (deviceId: string | number) => {
    try {
      setSaving(true)

      // Verificar se backend está disponível
      const isAvailable = await checkBackendAvailable()
      if (!isAvailable) {
        return { success: false, message: "Backend não está respondendo" }
      }

      const response = (await Promise.race([
        fetch(`${API_BASE}/api/config/device`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ device_id: deviceId }),
        }),
        new Promise<Response>((_, reject) =>
          setTimeout(() => reject(new Error("Timeout")), 15000)
        ),
      ])) as Response

      if (response.ok) {
        setSelectedDevice(deviceId)
        const data = await response.json()
        return { success: true, message: data.message || "Dispositivo salvo com sucesso" }
      } else {
        const data = await response.json()
        return { success: false, message: data.error || "Erro ao salvar dispositivo" }
      }
    } catch (error) {
      const message = error instanceof Error ? error.message : "Erro na conexão"
      console.error("Erro ao configurar dispositivo:", error)

      // Se for timeout, tentar confirmar se a configuração foi persistida
      if (message && message.toLowerCase().includes("timeout")) {
        try {
          const cfgRes = await fetch(`${API_BASE}/api/config`, { method: "GET" })
          if (cfgRes.ok) {
            const cfg = await cfgRes.json()
            const persisted = cfg?.audio?.input_device
            if (persisted !== undefined && String(persisted) === String(deviceId)) {
              // Persistido no servidor mesmo com timeout na resposta; tratar como sucesso
              setSelectedDevice(deviceId)
              return { success: true, message: "Configuração salva (confirmado após timeout)" }
            }
          }
        } catch (e) {
          console.warn("Falha ao verificar persistência após timeout:", e)
        }
      }

      return { success: false, message }
    } finally {
      setSaving(false)
    }
  }

  return { selectedDevice, setAudioDevice, saving }
}

export function useWhisperDeviceConfig() {
  const [selectedDevice, setSelectedDevice] = useState<string | null>("auto")
  const [saving, setSaving] = useState(false)

  // Carregar dispositivo Whisper salvo ao inicializar
  useEffect(() => {
    const loadSavedDevice = async () => {
      try {
        const response = await fetch(`${API_BASE}/api/config`, {
          method: "GET"
        })
        if (response.ok) {
          const config = await response.json()
          const savedDevice = config?.whisper?.device
          if (savedDevice && (savedDevice === "auto" || savedDevice === "cuda" || savedDevice === "cpu")) {
            setSelectedDevice(savedDevice)
          }
        }
      } catch (error) {
        console.warn("Erro ao carregar dispositivo Whisper salvo:", error)
      }
    }
    
    loadSavedDevice()
  }, [])

  const setWhisperDevice = async (device: "auto" | "cuda" | "cpu") => {
    try {
      setSaving(true)

      // Verificar se backend está disponível
      const isAvailable = await checkBackendAvailable()
      if (!isAvailable) {
        return { success: false, message: "Backend não está respondendo" }
      }

      const response = (await Promise.race([
        fetch(`${API_BASE}/api/config/whisper-device`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ device }),
        }),
        new Promise<Response>((_, reject) =>
          setTimeout(() => reject(new Error("Timeout")), 15000)
        ),
      ])) as Response

      if (response.ok) {
        setSelectedDevice(device)
        const data = await response.json()
        return { success: true, message: data.message || "Dispositivo Whisper configurado" }
      } else {
        const data = await response.json()
        return { success: false, message: data.error || "Erro ao configurar Whisper" }
      }
    } catch (error) {
      const message = error instanceof Error ? error.message : "Erro na conexão"
      console.error("Erro ao configurar Whisper device:", error)

      // Em caso de timeout, verificar se o backend já persistiu a opção
      if (message && message.toLowerCase().includes("timeout")) {
        try {
          const cfgRes = await fetch(`${API_BASE}/api/config`, { method: "GET" })
          if (cfgRes.ok) {
            const cfg = await cfgRes.json()
            const persisted = cfg?.whisper?.device
            if (persisted && String(persisted) === String(device)) {
              setSelectedDevice(device)
              return { success: true, message: "Configuração do Whisper salva (confirmado após timeout)" }
            }
          }
        } catch (e) {
          console.warn("Falha ao verificar Whisper config após timeout:", e)
        }
      }

      return { success: false, message }
    } finally {
      setSaving(false)
    }
  }

  return { selectedDevice, setWhisperDevice, saving }
}

// Interface para configurações do Whisper
export interface WhisperConfig {
  model: string
  language: string
  task: string
  fp16: boolean
  device: string
  beam_size: number
  best_of: number
  temperature: number
  patience: number
  length_penalty: number
  suppress_blank: boolean
  condition_on_previous_text: boolean
  no_speech_threshold: number
  compression_ratio_threshold: number
  logprob_threshold: number
  initial_prompt: string
  word_timestamps: boolean
  hallucination_silence_threshold: number | null
}

export function useWhisperConfig() {
  const [config, setConfig] = useState<WhisperConfig | null>(null)
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState<string | null>(null)

  // Carregar configurações ao inicializar
  useEffect(() => {
    loadConfig()
  }, [])

  const loadConfig = async () => {
    try {
      setLoading(true)
      setError(null)
      
      const response = await fetch(`${API_BASE}/api/config/whisper`, {
        method: "GET"
      })
      
      if (response.ok) {
        const data = await response.json()
        setConfig(data)
      } else {
        const data = await response.json()
        setError(data.error || "Erro ao carregar configurações")
      }
    } catch (err) {
      const message = err instanceof Error ? err.message : "Erro na conexão"
      setError(message)
    } finally {
      setLoading(false)
    }
  }

  const saveConfig = async (newConfig: Partial<WhisperConfig>) => {
    try {
      setSaving(true)
      setError(null)

      const response = await fetch(`${API_BASE}/api/config/whisper`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(newConfig),
      })

      const data = await response.json()

      if (response.ok) {
        // Atualizar estado local
        setConfig(prev => prev ? { ...prev, ...newConfig } : null)
        return { success: true, message: data.message || "Configurações salvas" }
      } else {
        return { success: false, message: data.error || "Erro ao salvar" }
      }
    } catch (err) {
      const message = err instanceof Error ? err.message : "Erro na conexão"
      return { success: false, message }
    } finally {
      setSaving(false)
    }
  }

  const reloadModel = async (newModel?: string) => {
    try {
      setSaving(true)
      setError(null)

      const response = await fetch(`${API_BASE}/api/whisper/reload`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ model: newModel }),
      })

      const data = await response.json()

      if (response.ok) {
        // Atualizar config local se modelo foi alterado
        if (newModel) {
          setConfig(prev => prev ? { ...prev, model: newModel } : null)
        }
        return { success: true, message: data.message || "Modelo recarregado" }
      } else {
        return { success: false, message: data.error || "Erro ao recarregar modelo" }
      }
    } catch (err) {
      const message = err instanceof Error ? err.message : "Erro na conexão"
      return { success: false, message }
    } finally {
      setSaving(false)
    }
  }

  return { config, loading, saving, error, loadConfig, saveConfig, reloadModel }
}
