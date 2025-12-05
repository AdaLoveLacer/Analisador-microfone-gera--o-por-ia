import { useState, useEffect, useRef } from "react"

interface AudioLevel {
  level: number
  frequency: string
}

const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:5000"

export function useMicrophone() {
  const [isRecording, setIsRecording] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [audioLevel, setAudioLevel] = useState(0)
  const [devices, setDevices] = useState<MediaDeviceInfo[]>([])
  const [selectedDeviceId, setSelectedDeviceId] = useState<string | null>(null)

  const audioContextRef = useRef<AudioContext | null>(null)
  const analyserRef = useRef<AnalyserNode | null>(null)
  const streamRef = useRef<MediaStream | null>(null)
  const dataArrayRef = useRef<Uint8Array | null>(null)
  const animationFrameRef = useRef<number | null>(null)

  // Listar dispositivos de áudio disponíveis
  useEffect(() => {
    const listDevices = async () => {
      try {
        const mediaDevices = await navigator.mediaDevices.enumerateDevices()
        const audioInputs = mediaDevices.filter((device) => device.kind === "audioinput")
        setDevices(audioInputs)

        // Selecionar primeiro dispositivo como padrão
        if (audioInputs.length > 0) {
          setSelectedDeviceId(audioInputs[0].deviceId)
        }
      } catch (err) {
        console.error("Erro ao listar dispositivos:", err)
        setError("Erro ao acessar dispositivos de áudio")
      }
    }

    listDevices()

    // Ouvir mudanças de dispositivos
    const handleDeviceChange = () => {
      listDevices()
    }

    navigator.mediaDevices.addEventListener("devicechange", handleDeviceChange)
    return () => {
      navigator.mediaDevices.removeEventListener("devicechange", handleDeviceChange)
    }
  }, [])

  // Começar a capturar áudio
  const startRecording = async (deviceId?: string) => {
    try {
      setError(null)

      const deviceIdToUse = deviceId || selectedDeviceId
      const constraints: MediaStreamConstraints = {
        audio: {
          deviceId: deviceIdToUse ? { exact: deviceIdToUse } : undefined,
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: false, // Deixar ganho manual para capturar variações
        },
      }

      const stream = await navigator.mediaDevices.getUserMedia(constraints)
      streamRef.current = stream

      // Criar contexto de áudio
      const audioContext = new (window.AudioContext || (window as any).webkitAudioContext)()
      audioContextRef.current = audioContext

      // Criar analisador
      const analyser = audioContext.createAnalyser()
      analyser.fftSize = 2048
      analyserRef.current = analyser

      // Conectar stream ao analisador
      const source = audioContext.createMediaStreamSource(stream)
      source.connect(analyser)

      // Preparar array para frequências
      const bufferLength = analyser.frequencyBinCount
      const dataArray = new Uint8Array(bufferLength)
      dataArrayRef.current = dataArray

      // Loop de captura de nível de áudio
      const updateAudioLevel = () => {
        if (analyserRef.current && dataArrayRef.current) {
          analyserRef.current.getByteFrequencyData(dataArrayRef.current as Uint8Array<ArrayBuffer>)

          // Calcular nível RMS (root mean square)
          let sum = 0
          for (let i = 0; i < dataArrayRef.current.length; i++) {
            sum += dataArrayRef.current[i] * dataArrayRef.current[i]
          }
          const rms = Math.sqrt(sum / dataArrayRef.current.length)
          const normalizedLevel = Math.min(1, rms / 255) // Normalizar para 0-1

          setAudioLevel(normalizedLevel)

          // Enviar para backend se estiver em captura ativa
          if (isRecording) {
            // Converter para PCM e enviar para backend
            analyserRef.current.getByteTimeDomainData(dataArrayRef.current as Uint8Array<ArrayBuffer>)
          }
        }

        animationFrameRef.current = requestAnimationFrame(updateAudioLevel)
      }

      updateAudioLevel()
      setIsRecording(true)
    } catch (err) {
      const message = err instanceof Error ? err.message : "Erro ao acessar microfone"
      setError(message)
      console.error("Erro ao iniciar captura:", err)
    }
  }

  // Parar captura
  const stopRecording = () => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach((track) => track.stop())
      streamRef.current = null
    }

    if (animationFrameRef.current) {
      cancelAnimationFrame(animationFrameRef.current)
    }

    if (audioContextRef.current) {
      audioContextRef.current.close()
      audioContextRef.current = null
    }

    setIsRecording(false)
    setAudioLevel(0)
  }

  // Enviar áudio para transcrição
  const sendAudioToTranscription = async (audioData: Float32Array) => {
    try {
      const response = await fetch(`${API_BASE}/api/transcribe/audio`, {
        method: "POST",
        headers: { "Content-Type": "application/octet-stream" },
        body: audioData.buffer as ArrayBuffer,
      })

      if (!response.ok) {
        throw new Error("Erro ao enviar áudio")
      }

      return await response.json()
    } catch (error) {
      console.error("Erro ao enviar áudio:", error)
      throw error
    }
  }

  return {
    isRecording,
    error,
    audioLevel,
    devices,
    selectedDeviceId,
    setSelectedDeviceId,
    startRecording,
    stopRecording,
    sendAudioToTranscription,
  }
}
