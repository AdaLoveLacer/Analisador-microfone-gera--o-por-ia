

import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Textarea } from "@/components/ui/textarea"
import { Brain, Upload, Mic, Laugh, Clock, FileAudio, TrendingUp, Download, Play, Trash2 } from "lucide-react"
import { toast } from "sonner"

export function AITraining() {
  const trainModel = () => {
    toast.success("Treinamento iniciado! Isso pode levar alguns minutos...")
  }

  const uploadRecording = () => {
    toast.success("Gravação adicionada ao dataset de treino")
  }

  const trainingDatasets = [
    {
      id: 1,
      name: "Minha Voz - Variações",
      recordings: 45,
      duration: "2h 34m",
      quality: 94,
      status: "ready",
    },
    {
      id: 2,
      name: "Sotaque Regional",
      recordings: 28,
      duration: "1h 15m",
      quality: 87,
      status: "ready",
    },
    {
      id: 3,
      name: "Sons Não-Verbais",
      recordings: 12,
      duration: "18m",
      quality: 76,
      status: "training",
    },
  ]

  const nonVerbalSounds = [
    { id: 1, type: "Risada", samples: 24, confidence: 92, active: true },
    { id: 2, type: "Tosse", samples: 18, confidence: 88, active: true },
    { id: 3, type: "Suspiro", samples: 15, confidence: 85, active: false },
    { id: 4, type: "Grito", samples: 9, confidence: 78, active: false },
  ]

  const accentVariations = [
    { id: 1, accent: "Português Brasileiro", variations: 156, accuracy: 96 },
    { id: 2, accent: "Português Portugal", variations: 42, accuracy: 89 },
    { id: 3, accent: "Sotaque Nordestino", variations: 28, accuracy: 84 },
    { id: 4, accent: "Sotaque Gaúcho", variations: 19, accuracy: 81 },
  ]

  return (
    <div className="p-8 space-y-6">
      <div>
        <h2 className="text-3xl font-bold text-foreground mb-2">Treinamento de IA Personalizado</h2>
        <p className="text-muted-foreground">Fine-tuning do modelo com suas gravações e variações</p>
      </div>

      {/* Training Overview */}
      <div className="grid gap-4 md:grid-cols-4">
        <Card className="border-primary/50">
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium text-muted-foreground">Gravações Totais</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-primary">85</div>
            <p className="text-xs text-muted-foreground mt-1">4h 7m de áudio</p>
          </CardContent>
        </Card>

        <Card className="border-secondary/50">
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium text-muted-foreground">Acurácia do Modelo</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-secondary">94.2%</div>
            <p className="text-xs text-success mt-1 flex items-center gap-1">
              <TrendingUp className="w-3 h-3" />
              +3.5% após treino
            </p>
          </CardContent>
        </Card>

        <Card className="border-accent/50">
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium text-muted-foreground">Palavras Treinadas</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-accent">42</div>
            <p className="text-xs text-muted-foreground mt-1">18 variações médias</p>
          </CardContent>
        </Card>

        <Card className="border-success/50">
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium text-muted-foreground">Última Sessão</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-success">2d</div>
            <p className="text-xs text-muted-foreground mt-1">há 2 dias</p>
          </CardContent>
        </Card>
      </div>

      <Tabs defaultValue="datasets" className="space-y-4">
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="datasets">
            <FileAudio className="w-4 h-4 mr-2" />
            Datasets
          </TabsTrigger>
          <TabsTrigger value="non-verbal">
            <Laugh className="w-4 h-4 mr-2" />
            Não-Verbais
          </TabsTrigger>
          <TabsTrigger value="accents">
            <Mic className="w-4 h-4 mr-2" />
            Sotaques
          </TabsTrigger>
        </TabsList>

        {/* Datasets Tab */}
        <TabsContent value="datasets" className="space-y-4">
          <Card className="border-2 border-primary/50">
            <CardHeader>
              <CardTitle>Iniciar Novo Treinamento</CardTitle>
              <CardDescription>Fine-tune o modelo com suas gravações personalizadas</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="datasetName">Nome do Dataset</Label>
                <Input id="datasetName" placeholder="Ex: Minha Voz - Comandos de Jogo" />
              </div>

              <div className="space-y-2">
                <Label htmlFor="keywords">Keywords para Treinar</Label>
                <Textarea
                  id="keywords"
                  placeholder="explosão, vitória, turbo, ataque..."
                  rows={3}
                  className="resize-none"
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="epochs">Épocas de Treino</Label>
                  <Input id="epochs" type="number" defaultValue={10} />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="batchSize">Batch Size</Label>
                  <Input id="batchSize" type="number" defaultValue={16} />
                </div>
              </div>

              <Button className="w-full bg-primary hover:bg-primary/90 glow-primary" onClick={trainModel}>
                <Brain className="w-4 h-4 mr-2" />
                Iniciar Treinamento
              </Button>
            </CardContent>
          </Card>

          <div className="space-y-3">
            {trainingDatasets.map((dataset) => (
              <Card key={dataset.id} className="border-border">
                <CardHeader>
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <CardTitle className="text-lg">{dataset.name}</CardTitle>
                      <div className="flex items-center gap-4 mt-2">
                        <Badge variant="outline" className="font-mono">
                          <FileAudio className="w-3 h-3 mr-1" />
                          {dataset.recordings} gravações
                        </Badge>
                        <Badge variant="outline" className="font-mono">
                          <Clock className="w-3 h-3 mr-1" />
                          {dataset.duration}
                        </Badge>
                      </div>
                    </div>
                    <Badge variant={dataset.status === "ready" ? "default" : "secondary"}>
                      {dataset.status === "ready" ? "Pronto" : "Treinando..."}
                    </Badge>
                  </div>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div>
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-sm text-muted-foreground">Qualidade dos Dados</span>
                      <span className="text-sm font-mono text-foreground">{dataset.quality}%</span>
                    </div>
                    <Progress value={dataset.quality} className="h-2" />
                  </div>

                  <div className="flex gap-2">
                    <Button variant="outline" size="sm" className="flex-1 bg-transparent">
                      <Play className="w-4 h-4 mr-2" />
                      Testar Modelo
                    </Button>
                    <Button variant="outline" size="sm" className="flex-1 bg-transparent">
                      <Download className="w-4 h-4 mr-2" />
                      Exportar
                    </Button>
                    <Button variant="outline" size="sm">
                      <Trash2 className="w-4 h-4" />
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        {/* Non-Verbal Tab */}
        <TabsContent value="non-verbal" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Detecção de Sons Não-Verbais</CardTitle>
              <CardDescription>Treine o modelo para identificar risadas, tosse, suspiros e outros sons</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="p-4 bg-primary/10 rounded-lg border border-primary/30">
                <div className="flex items-start gap-3">
                  <Laugh className="w-5 h-5 text-primary mt-1" />
                  <div>
                    <p className="font-semibold text-foreground">Como Funciona</p>
                    <p className="text-sm text-muted-foreground mt-1">
                      Grave exemplos de sons não-verbais e o modelo aprenderá a detectá-los automaticamente. Você pode
                      vincular efeitos sonoros a essas detecções.
                    </p>
                  </div>
                </div>
              </div>

              {nonVerbalSounds.map((sound) => (
                <Card key={sound.id} className="border-border">
                  <CardContent className="p-4">
                    <div className="flex items-center justify-between mb-3">
                      <div className="flex items-center gap-3">
                        <div className="w-10 h-10 rounded-lg bg-accent/20 flex items-center justify-center">
                          <Laugh className="w-5 h-5 text-accent" />
                        </div>
                        <div>
                          <p className="font-semibold text-foreground">{sound.type}</p>
                          <p className="text-xs text-muted-foreground">{sound.samples} amostras</p>
                        </div>
                      </div>
                      <Badge variant={sound.active ? "default" : "secondary"}>
                        {sound.active ? "Ativo" : "Inativo"}
                      </Badge>
                    </div>

                    <div className="space-y-2">
                      <div className="flex items-center justify-between text-sm">
                        <span className="text-muted-foreground">Confiança Média</span>
                        <span className="font-mono text-foreground">{sound.confidence}%</span>
                      </div>
                      <Progress value={sound.confidence} className="h-2" />
                    </div>

                    <div className="flex gap-2 mt-3">
                      <Button variant="outline" size="sm" className="flex-1 bg-transparent" onClick={uploadRecording}>
                        <Upload className="w-4 h-4 mr-2" />
                        Adicionar Amostra
                      </Button>
                      <Button variant="outline" size="sm" className="flex-1 bg-transparent">
                        <Play className="w-4 h-4 mr-2" />
                        Testar
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              ))}

              <Button variant="outline" className="w-full bg-transparent">
                + Adicionar Novo Tipo de Som
              </Button>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Accents Tab */}
        <TabsContent value="accents" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Variações de Sotaque e Pronúncia</CardTitle>
              <CardDescription>Melhore a detecção para diferentes sotaques e formas de pronúncia</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="p-4 bg-secondary/10 rounded-lg border border-secondary/30">
                <div className="flex items-start gap-3">
                  <Mic className="w-5 h-5 text-secondary mt-1" />
                  <div>
                    <p className="font-semibold text-foreground">Treinamento Multi-Sotaque</p>
                    <p className="text-sm text-muted-foreground mt-1">
                      Adicione variações de como você ou outras pessoas pronunciam as keywords. O modelo se tornará mais
                      robusto e preciso.
                    </p>
                  </div>
                </div>
              </div>

              {accentVariations.map((accent, idx) => (
                <div key={accent.id} className="p-4 bg-muted/30 rounded-lg border border-border">
                  <div className="flex items-center justify-between mb-3">
                    <div className="flex items-center gap-3">
                      <div
                        className={`w-10 h-10 rounded-lg flex items-center justify-center font-bold ${
                          idx === 0
                            ? "bg-primary/20 text-primary"
                            : idx === 1
                              ? "bg-secondary/20 text-secondary"
                              : "bg-accent/20 text-accent"
                        }`}
                      >
                        #{idx + 1}
                      </div>
                      <div>
                        <p className="font-semibold text-foreground">{accent.accent}</p>
                        <p className="text-xs text-muted-foreground">{accent.variations} variações</p>
                      </div>
                    </div>
                    <Badge variant="outline" className="font-mono">
                      {accent.accuracy}% acc.
                    </Badge>
                  </div>

                  <Progress value={accent.accuracy} className="h-2 mb-3" />

                  <div className="flex gap-2">
                    <Button variant="outline" size="sm" className="flex-1 bg-transparent">
                      <Upload className="w-4 h-4 mr-2" />
                      Adicionar Variação
                    </Button>
                    <Button variant="outline" size="sm" className="flex-1 bg-transparent">
                      <Play className="w-4 h-4 mr-2" />
                      Testar
                    </Button>
                  </div>
                </div>
              ))}

              <Button variant="outline" className="w-full bg-transparent">
                + Adicionar Novo Sotaque
              </Button>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}
