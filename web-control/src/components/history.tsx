

import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Input } from "@/components/ui/input"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Clock, Download, Filter, TrendingUp, Calendar } from "lucide-react"
import { toast } from "sonner"

interface HistoryEntry {
  id: number
  timestamp: string
  transcription: string
  keyword: string
  confidence: number
  sound: string
  date: string
}

export function History() {
  const historyEntries: HistoryEntry[] = [
    {
      id: 1,
      timestamp: "14:23:45",
      transcription: "ativar modo turbo agora",
      keyword: "turbo",
      confidence: 0.95,
      sound: "turbo-sound.mp3",
      date: "2025-12-04",
    },
    {
      id: 2,
      timestamp: "14:22:10",
      transcription: "explosão massiva boom",
      keyword: "explosão",
      confidence: 0.88,
      sound: "explosion.mp3",
      date: "2025-12-04",
    },
    {
      id: 3,
      timestamp: "14:20:33",
      transcription: "vitória épica conquistada",
      keyword: "vitória",
      confidence: 0.92,
      sound: "victory.mp3",
      date: "2025-12-04",
    },
    {
      id: 4,
      timestamp: "14:18:22",
      transcription: "ativar turbo boost",
      keyword: "turbo",
      confidence: 0.87,
      sound: "turbo-sound.mp3",
      date: "2025-12-04",
    },
    {
      id: 5,
      timestamp: "14:15:09",
      transcription: "disparo laser carregado",
      keyword: "laser",
      confidence: 0.91,
      sound: "laser.mp3",
      date: "2025-12-04",
    },
  ]

  const exportHistory = (format: string) => {
    toast.success(`Histórico exportado em ${format.toUpperCase()}`)
  }

  // Stats for most detected keywords
  const topKeywords = [
    { name: "turbo", count: 45, color: "bg-primary" },
    { name: "explosão", count: 32, color: "bg-accent" },
    { name: "vitória", count: 28, color: "bg-secondary" },
    { name: "laser", count: 21, color: "bg-success" },
  ]

  return (
    <div className="p-8 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold text-foreground mb-2">Histórico</h2>
          <p className="text-muted-foreground">Timeline completa de detecções</p>
        </div>

        <div className="flex gap-2">
          <Button variant="outline" onClick={() => exportHistory("csv")}>
            <Download className="w-4 h-4 mr-2" />
            Exportar CSV
          </Button>
          <Button variant="outline" onClick={() => exportHistory("json")}>
            <Download className="w-4 h-4 mr-2" />
            Exportar JSON
          </Button>
        </div>
      </div>

      {/* Filters */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-base">
            <Filter className="w-4 h-4" />
            Filtros
          </CardTitle>
        </CardHeader>
        <CardContent className="flex flex-wrap gap-4">
          <div className="flex-1 min-w-[200px]">
            <Input placeholder="Buscar na transcrição..." />
          </div>
          <Select defaultValue="all">
            <SelectTrigger className="w-[180px]">
              <SelectValue placeholder="Keyword" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">Todas Keywords</SelectItem>
              <SelectItem value="turbo">Turbo</SelectItem>
              <SelectItem value="explosao">Explosão</SelectItem>
              <SelectItem value="vitoria">Vitória</SelectItem>
            </SelectContent>
          </Select>
          <Select defaultValue="today">
            <SelectTrigger className="w-[180px]">
              <SelectValue placeholder="Data" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="today">Hoje</SelectItem>
              <SelectItem value="week">Última Semana</SelectItem>
              <SelectItem value="month">Último Mês</SelectItem>
              <SelectItem value="all">Todo Período</SelectItem>
            </SelectContent>
          </Select>
          <Select defaultValue="all">
            <SelectTrigger className="w-[180px]">
              <SelectValue placeholder="Confiança" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">Todas</SelectItem>
              <SelectItem value="high">Alta (≥ 90%)</SelectItem>
              <SelectItem value="medium">Média (70-89%)</SelectItem>
              <SelectItem value="low">Baixa (&lt; 70%)</SelectItem>
            </SelectContent>
          </Select>
        </CardContent>
      </Card>

      {/* Statistics */}
      <div className="grid gap-4 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <TrendingUp className="w-5 h-5 text-primary" />
              Top Keywords Detectadas
            </CardTitle>
            <CardDescription>Palavras mais frequentes nas últimas 24h</CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            {topKeywords.map((keyword, index) => (
              <div key={keyword.name} className="space-y-1">
                <div className="flex items-center justify-between text-sm">
                  <div className="flex items-center gap-2">
                    <span className="text-muted-foreground">#{index + 1}</span>
                    <span className="font-mono text-foreground">{keyword.name}</span>
                  </div>
                  <span className="font-bold text-foreground">{keyword.count}x</span>
                </div>
                <div className="h-2 bg-muted rounded-full overflow-hidden">
                  <div
                    className={`h-full ${keyword.color}`}
                    style={{ width: `${(keyword.count / topKeywords[0].count) * 100}%` }}
                  />
                </div>
              </div>
            ))}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Calendar className="w-5 h-5 text-secondary" />
              Estatísticas Rápidas
            </CardTitle>
            <CardDescription>Resumo do período selecionado</CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="flex items-center justify-between p-3 bg-muted/30 rounded-lg">
              <span className="text-sm text-muted-foreground">Total de Detecções</span>
              <span className="text-2xl font-bold text-primary">126</span>
            </div>
            <div className="flex items-center justify-between p-3 bg-muted/30 rounded-lg">
              <span className="text-sm text-muted-foreground">Confiança Média</span>
              <span className="text-2xl font-bold text-success">89%</span>
            </div>
            <div className="flex items-center justify-between p-3 bg-muted/30 rounded-lg">
              <span className="text-sm text-muted-foreground">Keywords Únicas</span>
              <span className="text-2xl font-bold text-accent">12</span>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Timeline */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Clock className="w-5 h-5 text-foreground" />
            Timeline de Detecções ({historyEntries.length})
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {historyEntries.map((entry) => (
              <div key={entry.id} className="relative pl-8 pb-6 border-l-2 border-border last:pb-0">
                {/* Timeline dot */}
                <div className="absolute left-0 top-1 transform -translate-x-1/2 w-4 h-4 rounded-full bg-primary glow-primary" />

                <div className="p-4 bg-muted/30 rounded-lg border border-border hover:border-primary/50 transition-colors">
                  <div className="flex items-start justify-between gap-4">
                    <div className="flex-1 space-y-2">
                      <div className="flex items-center gap-2">
                        <span className="text-xs text-muted-foreground font-mono">{entry.date}</span>
                        <span className="text-xs text-muted-foreground font-mono">{entry.timestamp}</span>
                      </div>

                      <p className="text-foreground font-medium">"{entry.transcription}"</p>

                      <div className="flex flex-wrap gap-2 text-sm">
                        <div className="flex items-center gap-1">
                          <span className="text-muted-foreground">Keyword:</span>
                          <Badge variant="outline" className="text-primary border-primary">
                            {entry.keyword}
                          </Badge>
                        </div>

                        <div className="flex items-center gap-1">
                          <span className="text-muted-foreground">Som:</span>
                          <span className="font-mono text-xs text-foreground">{entry.sound}</span>
                        </div>
                      </div>
                    </div>

                    <div className="text-right">
                      <Badge
                        variant="default"
                        className={
                          entry.confidence >= 0.9
                            ? "bg-success text-success-foreground"
                            : entry.confidence >= 0.7
                              ? "bg-primary"
                              : "bg-warning text-warning-foreground"
                        }
                      >
                        {(entry.confidence * 100).toFixed(0)}%
                      </Badge>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
