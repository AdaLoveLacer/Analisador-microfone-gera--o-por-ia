

import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import { Mic, MicOff, Activity, Brain, Zap, Volume2, History, Download, Trash2, Copy } from "lucide-react"
import { useState, useEffect, useRef } from "react"
import { toast } from "sonner"
import useSWR from "swr"
import { useSocket, useLLM } from "@/hooks"
import { API } from "@/lib/api"

const fetcher = (url: string) => fetch(url).then((res) => res.json())

// Interface para histórico de transcrições
interface TranscriptionEntry {
  id: string
  text: string
  timestamp: Date
  confidence: number
}

export function Dashboard() {
  const [isCapturing, setIsCapturing] = useState(false)
  const [liveTranscription, setLiveTranscription] = useState("")
  const [llmAnalysis, setLlmAnalysis] = useState<string>("")
  const [analyzingText, setAnalyzingText] = useState(false)
  // Histórico de transcrições da sessão
  const [transcriptionHistory, setTranscriptionHistory] = useState<TranscriptionEntry[]>([])
  const historyRef = useRef<HTMLDivElement>(null)

  const { data: status } = useSWR(API.STATUS(), fetcher, {
    refreshInterval: 2000,
    onError: () => toast.error("Erro ao conectar com o servidor"),
  })

  // Socket.IO para dados em tempo real
  const { connected, audioLevel, recentDetections, transcription, emit: socketEmit } = useSocket()

  // Hooks para LLM
  const { analyzeContext, status: llmStatus } = useLLM()

  // Monitorar transcrições e adicionar ao histórico
  useEffect(() => {
    if (transcription && transcription.text && transcription.text.trim()) {
      setLiveTranscription(transcription.text)
      
      // Adicionar ao histórico (evitar duplicatas)
      setTranscriptionHistory(prev => {
        // Verificar se já existe uma transcrição muito similar recente
        const lastEntry = prev[prev.length - 1]
        if (lastEntry && lastEntry.text === transcription.text) {
          return prev // Não adicionar duplicata
        }
        
        const newEntry: TranscriptionEntry = {
          id: `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
          text: transcription.text,
          timestamp: new Date(),
          confidence: transcription.confidence || 0.8
        }
        return [...prev, newEntry]
      })
      
      // Auto-scroll para o final do histórico
      setTimeout(() => {
        if (historyRef.current) {
          historyRef.current.scrollTop = historyRef.current.scrollHeight
        }
      }, 100)
      
      // Se há keywords configuradas, analisar com LLM
      if (status?.active_keywords && status.active_keywords > 0 && isCapturing) {
        analyzeWithLLM(transcription.text)
      }
    }
  }, [transcription, status, isCapturing])

  // Funções do histórico
  const clearHistory = () => {
    setTranscriptionHistory([])
    toast.success("Histórico limpo")
  }

  const exportHistory = () => {
    if (transcriptionHistory.length === 0) {
      toast.error("Nenhuma transcrição para exportar")
      return
    }
    
    const content = transcriptionHistory
      .map(entry => `[${entry.timestamp.toLocaleTimeString("pt-BR")}] ${entry.text}`)
      .join("\n\n")
    
    const blob = new Blob([content], { type: "text/plain;charset=utf-8" })
    const url = URL.createObjectURL(blob)
    const a = document.createElement("a")
    a.href = url
    a.download = `transcricoes_${new Date().toISOString().split("T")[0]}.txt`
    a.click()
    URL.revokeObjectURL(url)
    toast.success("Histórico exportado!")
  }

  const copyAllHistory = () => {
    if (transcriptionHistory.length === 0) {
      toast.error("Nenhuma transcrição para copiar")
      return
    }
    
    const content = transcriptionHistory.map(entry => entry.text).join("\n\n")
    navigator.clipboard.writeText(content)
    toast.success("Histórico copiado!")
  }

  const analyzeWithLLM = async (text: string) => {
    if (!text || analyzingText) return
    
    try {
      setAnalyzingText(true)
      const result = await analyzeContext(text, ["turbo", "explosão", "vitória"], 0.6)
      
      if (result && result.best_match) {
        setLlmAnalysis(`Contexto: ${result.best_match} (${(result.confidence * 100).toFixed(0)}%)`)
      }
    } catch (error) {
      console.error("Erro ao analisar com LLM:", error)
    } finally {
      setAnalyzingText(false)
    }
  }

  const toggleCapture = async () => {
    try {
      if (isCapturing) {
        // Usar WebSocket se conectado
        if (connected) {
          socketEmit("stop_capture")
        } else {
          await fetch(API.CAPTURE_STOP(), { method: "POST" })
        }
      } else {
        if (connected) {
          socketEmit("start_capture")
        } else {
          await fetch(API.CAPTURE_START(), { method: "POST" })
        }
      }
      
      setIsCapturing(!isCapturing)
      setLlmAnalysis("")
      toast.success(isCapturing ? "Captura parada" : "Captura iniciada")
    } catch (error) {
      toast.error("Erro ao alternar captura")
      console.error(error)
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
                {llmStatus?.active_backend ? llmStatus.active_backend.toUpperCase() : "Ollama"}
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

            <div className="flex items-center justify-between p-3 bg-muted/50 rounded-lg">
              <span className="text-sm text-muted-foreground">WebSocket</span>
              <Badge variant={connected ? "default" : "destructive"} className={connected ? "glow-success" : ""}>
                {connected ? "Conectado" : "Desconectado"}
              </Badge>
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
        <CardContent className="space-y-3">
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

          {llmAnalysis && (
            <div className="p-3 bg-primary/10 rounded-lg border border-primary/30">
              <p className="text-sm text-foreground">
                <span className="text-primary font-bold">IA: </span>
                {llmAnalysis}
              </p>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Histórico de Transcrições da Sessão */}
      <Card className="border-2 border-secondary/50">
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="flex items-center gap-2">
                <History className="w-5 h-5 text-secondary" />
                Histórico da Sessão
              </CardTitle>
              <CardDescription>
                {transcriptionHistory.length} transcrição(ões) salva(s)
              </CardDescription>
            </div>
            <div className="flex gap-2">
              <Button 
                size="sm" 
                variant="outline" 
                onClick={copyAllHistory}
                disabled={transcriptionHistory.length === 0}
                title="Copiar tudo"
              >
                <Copy className="w-4 h-4" />
              </Button>
              <Button 
                size="sm" 
                variant="outline" 
                onClick={exportHistory}
                disabled={transcriptionHistory.length === 0}
                title="Exportar como TXT"
              >
                <Download className="w-4 h-4" />
              </Button>
              <Button 
                size="sm" 
                variant="outline" 
                onClick={clearHistory}
                disabled={transcriptionHistory.length === 0}
                className="text-destructive hover:text-destructive"
                title="Limpar histórico"
              >
                <Trash2 className="w-4 h-4" />
              </Button>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <div 
            ref={historyRef}
            className="max-h-[300px] overflow-y-auto space-y-2 pr-2"
          >
            {transcriptionHistory.length > 0 ? (
              transcriptionHistory.map((entry) => (
                <div
                  key={entry.id}
                  className="p-3 bg-muted/30 rounded-lg border border-border hover:border-secondary/50 transition-colors group"
                >
                  <div className="flex items-start justify-between gap-2">
                    <p className="text-sm text-foreground flex-1">{entry.text}</p>
                    <Button
                      size="sm"
                      variant="ghost"
                      className="opacity-0 group-hover:opacity-100 transition-opacity h-6 w-6 p-0"
                      onClick={() => {
                        navigator.clipboard.writeText(entry.text)
                        toast.success("Copiado!")
                      }}
                    >
                      <Copy className="w-3 h-3" />
                    </Button>
                  </div>
                  <div className="flex items-center gap-2 mt-2">
                    <span className="text-xs text-muted-foreground">
                      {entry.timestamp.toLocaleTimeString("pt-BR")}
                    </span>
                    <Badge variant="outline" className="text-xs">
                      {(entry.confidence * 100).toFixed(0)}%
                    </Badge>
                  </div>
                </div>
              ))
            ) : (
              <div className="text-center p-8 text-muted-foreground">
                <History className="w-8 h-8 mx-auto mb-2 opacity-50" />
                <p className="text-sm">Nenhuma transcrição ainda</p>
                <p className="text-xs mt-1">As transcrições aparecerão aqui durante a sessão</p>
              </div>
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
            {recentDetections && recentDetections.length > 0 ? (
              recentDetections.map((detection, idx) => (
                <div
                  key={idx}
                  className="flex items-center justify-between p-3 bg-muted/30 rounded-lg border border-border hover:border-primary/50 transition-colors"
                >
                  <div className="flex-1">
                    <p className="text-sm font-medium text-foreground">{detection.text}</p>
                    <p className="text-xs text-muted-foreground mt-1">
                      Keyword: <span className="text-primary font-mono">{detection.keyword_id}</span>
                    </p>
                  </div>
                  <div className="flex items-center gap-3">
                    <div className="text-right">
                      <p className="text-xs text-muted-foreground">
                        {new Date(detection.timestamp).toLocaleTimeString("pt-BR")}
                      </p>
                      <p className="text-xs font-mono text-success">
                        {(detection.confidence * 100).toFixed(0)}% conf.
                      </p>
                    </div>
                    <div className="w-2 h-2 rounded-full bg-success glow-success" />
                  </div>
                </div>
              ))
            ) : (
              <div className="text-center p-8 text-muted-foreground">
                <p className="text-sm">Nenhuma detecção ainda</p>
                <p className="text-xs mt-1">Inicie a captura para ver detecções em tempo real</p>
              </div>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

function cn(...classes: (string | boolean | undefined)[]) {
  return classes.filter(Boolean).join(" ")
}
