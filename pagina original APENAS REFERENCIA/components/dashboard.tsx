"use client"

import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import { Mic, MicOff, Activity, Brain, Zap, Volume2 } from "lucide-react"
import { useState, useEffect } from "react"
import { toast } from "sonner"
import useSWR from "swr"

const fetcher = (url: string) => fetch(url).then((res) => res.json())

export function Dashboard() {
  const [isCapturing, setIsCapturing] = useState(false)
  const [audioLevel, setAudioLevel] = useState(0)
  const [liveTranscription, setLiveTranscription] = useState("")

  const { data: status } = useSWR("http://localhost:5000/api/status", fetcher, {
    refreshInterval: 2000,
    onError: () => toast.error("Erro ao conectar com o servidor"),
  })

  const recentDetections = [
    { id: 1, text: "ativar modo turbo", keyword: "turbo", time: "14:23:45", confidence: 0.95 },
    { id: 2, text: "explosão agora", keyword: "explosão", time: "14:22:10", confidence: 0.88 },
    { id: 3, text: "vitória épica", keyword: "vitória", time: "14:20:33", confidence: 0.92 },
  ]

  useEffect(() => {
    // Simula variação do nível de áudio quando capturing
    if (isCapturing) {
      const interval = setInterval(() => {
        setAudioLevel(Math.random() * 100)
      }, 100)
      return () => clearInterval(interval)
    } else {
      setAudioLevel(0)
    }
  }, [isCapturing])

  const toggleCapture = async () => {
    try {
      const endpoint = isCapturing ? "/capture/stop" : "/capture/start"
      await fetch(`http://localhost:5000/api${endpoint}`, { method: "POST" })
      setIsCapturing(!isCapturing)
      toast.success(isCapturing ? "Captura parada" : "Captura iniciada")
    } catch (error) {
      toast.error("Erro ao alternar captura")
    }
  }

  return (
    <div className="p-8 space-y-6">
      {/* Header */}
      <div>
        <h2 className="text-3xl font-bold text-foreground mb-2">Dashboard</h2>
        <p className="text-muted-foreground">Monitore a captura de áudio e detecções em tempo real</p>
      </div>

      {/* Main Control */}
      <div className="grid gap-6 md:grid-cols-2">
        <Card className="border-2 border-border">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Activity className="w-5 h-5 text-primary" />
              Controle de Captura
            </CardTitle>
            <CardDescription>Inicie ou pare a captura de áudio do microfone</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <Button
              size="lg"
              className={cn(
                "w-full h-20 text-lg font-bold transition-all",
                isCapturing
                  ? "bg-destructive hover:bg-destructive/90 glow-accent"
                  : "bg-primary hover:bg-primary/90 glow-primary pulse-glow",
              )}
              onClick={toggleCapture}
            >
              {isCapturing ? (
                <>
                  <MicOff className="w-6 h-6 mr-2" />
                  Parar Captura
                </>
              ) : (
                <>
                  <Mic className="w-6 h-6 mr-2" />
                  Iniciar Captura
                </>
              )}
            </Button>

            <div className="space-y-2">
              <div className="flex items-center justify-between text-sm">
                <span className="text-muted-foreground">Nível de Áudio</span>
                <span className="text-foreground font-mono">{Math.round(audioLevel)}%</span>
              </div>
              <Progress value={audioLevel} className={cn("h-3", audioLevel > 80 && "glow-success")} />
            </div>
          </CardContent>
        </Card>

        {/* Status */}
        <Card className="border-2 border-border">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Brain className="w-5 h-5 text-secondary" />
              Status do Sistema
            </CardTitle>
            <CardDescription>Informações sobre o backend de IA</CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="flex items-center justify-between p-3 bg-muted/50 rounded-lg">
              <span className="text-sm text-muted-foreground">Estado</span>
              <Badge variant={isCapturing ? "default" : "secondary"} className={isCapturing ? "glow-primary" : ""}>
                {isCapturing ? "Capturando" : "Idle"}
              </Badge>
            </div>

            <div className="flex items-center justify-between p-3 bg-muted/50 rounded-lg">
              <span className="text-sm text-muted-foreground">Backend IA</span>
              <Badge variant="outline" className="text-primary border-primary">
                {status?.backend || "Ollama"}
              </Badge>
            </div>

            <div className="flex items-center justify-between p-3 bg-muted/50 rounded-lg">
              <span className="text-sm text-muted-foreground">Modelo Whisper</span>
              <span className="text-sm font-mono text-foreground">{status?.whisper_model || "base"}</span>
            </div>

            <div className="flex items-center justify-between p-3 bg-muted/50 rounded-lg">
              <span className="text-sm text-muted-foreground">Keywords Ativas</span>
              <span className="text-sm font-bold text-primary">{status?.active_keywords || 0}</span>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Live Transcription */}
      <Card className="border-2 border-primary/50 glow-primary">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Zap className="w-5 h-5 text-primary animate-pulse" />
            Transcrição ao Vivo
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="min-h-[100px] p-4 bg-muted/30 rounded-lg border border-border font-mono text-sm">
            {isCapturing ? (
              <p className="text-foreground">
                {liveTranscription || "Aguardando áudio..."}
                <span className="inline-block w-2 h-4 ml-1 bg-primary animate-pulse" />
              </p>
            ) : (
              <p className="text-muted-foreground italic">Inicie a captura para ver a transcrição</p>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Recent Detections */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Volume2 className="w-5 h-5 text-accent" />
            Detecções Recentes
          </CardTitle>
          <CardDescription>Últimas 5 palavras-chave detectadas</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-2">
            {recentDetections.map((detection) => (
              <div
                key={detection.id}
                className="flex items-center justify-between p-3 bg-muted/30 rounded-lg border border-border hover:border-primary/50 transition-colors"
              >
                <div className="flex-1">
                  <p className="text-sm font-medium text-foreground">{detection.text}</p>
                  <p className="text-xs text-muted-foreground mt-1">
                    Keyword: <span className="text-primary font-mono">{detection.keyword}</span>
                  </p>
                </div>
                <div className="flex items-center gap-3">
                  <div className="text-right">
                    <p className="text-xs text-muted-foreground">{detection.time}</p>
                    <p className="text-xs font-mono text-success">{(detection.confidence * 100).toFixed(0)}% conf.</p>
                  </div>
                  <div className="w-2 h-2 rounded-full bg-success glow-success" />
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

function cn(...classes: (string | boolean | undefined)[]) {
  return classes.filter(Boolean).join(" ")
}
