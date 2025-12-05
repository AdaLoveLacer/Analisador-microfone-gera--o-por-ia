

import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Mic, MicOff, Volume2 } from "lucide-react"
import { useState, useEffect } from "react"
import { useMicrophone } from "@/hooks/useMicrophone"
import { useSocket } from "@/hooks"

export function MicrophoneCapture() {
  const socket = useSocket()
  const {
    isRecording,
    error,
    audioLevel,
    devices,
    selectedDeviceId,
    setSelectedDeviceId,
    startRecording,
    stopRecording,
  } = useMicrophone()

  const [recordingTime, setRecordingTime] = useState(0)

  useEffect(() => {
    let interval: NodeJS.Timeout

    if (isRecording) {
      interval = setInterval(() => {
        setRecordingTime((prev) => prev + 1)
      }, 1000)
    } else {
      setRecordingTime(0)
    }

    return () => clearInterval(interval)
  }, [isRecording])

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60)
    const secs = seconds % 60
    return `${mins.toString().padStart(2, "0")}:${secs.toString().padStart(2, "0")}`
  }

  const handleStartRecording = async () => {
    await startRecording(selectedDeviceId || undefined)
  }

  return (
    <Card className="border-2 border-primary/50">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Mic className="w-5 h-5" />
          Captura de Áudio (Navegador)
        </CardTitle>
        <CardDescription>Usa Web Audio API para capturar do seu microfone</CardDescription>
      </CardHeader>

      <CardContent className="space-y-6">
        {/* Seletor de Dispositivo */}
        <div className="space-y-2">
          <label className="text-sm font-medium">Dispositivo de Áudio</label>
          {selectedDeviceId ? (
            <Select value={selectedDeviceId} onValueChange={setSelectedDeviceId}>
              <SelectTrigger>
                <SelectValue placeholder="Selecione um microfone..." />
              </SelectTrigger>
              <SelectContent>
                {devices.map((device) => (
                  <SelectItem key={device.deviceId} value={device.deviceId}>
                    {device.label || `Dispositivo ${device.deviceId.slice(0, 8)}`}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          ) : (
            <div className="flex items-center justify-center h-10 border rounded-md bg-muted text-sm text-muted-foreground">
              Carregando dispositivos...
            </div>
          )}
        </div>

        {/* Visualizador de Nível de Áudio */}
        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <label className="text-sm font-medium flex items-center gap-2">
              <Volume2 className="w-4 h-4" />
              Nível de Áudio
            </label>
            <span className="text-xs text-muted-foreground">
              {Math.round(audioLevel * 100)}%
            </span>
          </div>

          {/* Barra de progresso animada */}
          <div className="h-2 bg-muted rounded-full overflow-hidden">
            <div
              className="h-full bg-gradient-to-r from-green-500 via-yellow-500 to-red-500 transition-all duration-100"
              style={{ width: `${audioLevel * 100}%` }}
            />
          </div>
        </div>

        {/* Status */}
        {isRecording && (
          <div className="p-3 bg-primary/10 rounded-lg border border-primary/30">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <div className="w-2 h-2 bg-primary rounded-full animate-pulse" />
                <span className="text-sm font-medium">Gravando...</span>
              </div>
              <span className="text-sm font-mono text-muted-foreground">
                {formatTime(recordingTime)}
              </span>
            </div>
          </div>
        )}

        {/* Erro */}
        {error && (
          <div className="p-3 bg-destructive/10 rounded-lg border border-destructive/30 text-destructive text-sm">
            ❌ {error}
          </div>
        )}

        {/* Status da Conexão WebSocket */}
        {socket.connected && (
          <div className="p-2 bg-success/10 rounded-lg border border-success/30 text-success text-xs">
            ✓ WebSocket conectado - Transcrição em tempo real ativa
          </div>
        )}

        {/* Botões */}
        <div className="flex gap-3">
          {!isRecording ? (
            <Button
              onClick={handleStartRecording}
              className="flex-1 bg-primary hover:bg-primary/90 glow-primary"
              disabled={devices.length === 0}
            >
              <Mic className="w-4 h-4 mr-2" />
              Iniciar Gravação
            </Button>
          ) : (
            <Button
              onClick={stopRecording}
              variant="destructive"
              className="flex-1"
            >
              <MicOff className="w-4 h-4 mr-2" />
              Parar Gravação
            </Button>
          )}
        </div>

        {/* Info */}
        <p className="text-xs text-muted-foreground">
          💡 {devices.length > 0
            ? `${devices.length} dispositivo(s) de áudio detectado(s)`
            : "Nenhum dispositivo de áudio encontrado. Verifique as permissões."}
        </p>
      </CardContent>
    </Card>
  )
}
