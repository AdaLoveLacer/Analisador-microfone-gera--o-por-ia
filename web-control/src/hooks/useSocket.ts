import { useEffect, useState, useRef, useCallback } from "react"
import { io, Socket } from "socket.io-client"

interface SocketData {
  transcription: string
  confidence: number
  timestamp: string
}

interface DetectionData {
  keyword_id: string
  text: string
  confidence: number
  context_score: number
  timestamp: string
}

interface AudioLevelData {
  level: number
  energy: number
  timestamp: string
}

export function useSocket() {
  const socketRef = useRef<Socket | null>(null)
  const [connected, setConnected] = useState(false)
  const [transcription, setTranscription] = useState<SocketData | null>(null)
  const [lastDetection, setLastDetection] = useState<DetectionData | null>(null)
  const [audioLevel, setAudioLevel] = useState(0)
  const [recentDetections, setRecentDetections] = useState<DetectionData[]>([])

  const handleTranscription = useCallback((data: SocketData) => {
    setTranscription(data)
  }, [])

  const handleDetection = useCallback((data: DetectionData) => {
    setLastDetection(data)
    setRecentDetections((prev) => [data, ...prev].slice(0, 5))
  }, [])

  const handleAudioLevel = useCallback((data: AudioLevelData) => {
    setAudioLevel(data.level)
  }, [])

  useEffect(() => {
    const socketUrl = import.meta.env.VITE_API_URL || "http://localhost:5000"
    socketRef.current = io(socketUrl, {
      transports: ["websocket", "polling"],
      reconnection: true,
      reconnectionDelay: 1000,
      reconnectionAttempts: 5,
    })

    socketRef.current.on("connect", () => {
      setConnected(true)
      console.log("✓ Socket connected")
    })

    socketRef.current.on("disconnect", () => {
      setConnected(false)
      console.log("✗ Socket disconnected")
    })

    socketRef.current.on("transcription_update", handleTranscription)
    socketRef.current.on("keyword_detected", handleDetection)
    socketRef.current.on("audio_level", handleAudioLevel)

    return () => {
      if (socketRef.current) {
        socketRef.current.disconnect()
      }
    }
  }, [handleTranscription, handleDetection, handleAudioLevel])

  const emit = useCallback((event: string, data?: any) => {
    if (socketRef.current?.connected) {
      socketRef.current.emit(event, data)
    } else {
      console.warn(`Socket não conectado, não foi possível emitir evento: ${event}`)
    }
  }, [])

  return {
    connected,
    transcription,
    lastDetection,
    audioLevel,
    recentDetections,
    emit,
    socket: socketRef.current,
  }
}
