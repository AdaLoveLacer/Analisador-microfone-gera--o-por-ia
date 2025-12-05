"use client"

import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Slider } from "@/components/ui/slider"
import { Switch } from "@/components/ui/switch"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Mic, Brain, Palette, Save, Volume2, Zap } from "lucide-react"
import { toast } from "sonner"

export function Settings() {
  const saveSettings = () => {
    toast.success("Configurações salvas com sucesso!")
  }

  return (
    <div className="p-8 space-y-6">
      {/* Header */}
      <div>
        <h2 className="text-3xl font-bold text-foreground mb-2">Configurações</h2>
        <p className="text-muted-foreground">Personalize o comportamento do sistema</p>
      </div>

      <Tabs defaultValue="audio" className="space-y-6">
        <TabsList className="grid w-full grid-cols-5">
          <TabsTrigger value="audio">
            <Mic className="w-4 h-4 mr-2" />
            Áudio
          </TabsTrigger>
          <TabsTrigger value="whisper">
            <Volume2 className="w-4 h-4 mr-2" />
            Whisper
          </TabsTrigger>
          <TabsTrigger value="ai">
            <Brain className="w-4 h-4 mr-2" />
            IA
          </TabsTrigger>
          <TabsTrigger value="performance">
            <Zap className="w-4 h-4 mr-2" />
            Performance
          </TabsTrigger>
          <TabsTrigger value="visual">
            <Palette className="w-4 h-4 mr-2" />
            Visual
          </TabsTrigger>
        </TabsList>

        {/* Audio Settings */}
        <TabsContent value="audio" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Configurações de Áudio</CardTitle>
              <CardDescription>Configure o dispositivo e qualidade de captura</CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="space-y-2">
                <Label htmlFor="device">Dispositivo de Entrada</Label>
                <Select defaultValue="default">
                  <SelectTrigger id="device">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="default">Microfone Padrão</SelectItem>
                    <SelectItem value="mic1">Microfone USB (Realtek)</SelectItem>
                    <SelectItem value="mic2">Headset Bluetooth</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label htmlFor="sampleRate">Taxa de Amostragem</Label>
                <Select defaultValue="16000">
                  <SelectTrigger id="sampleRate">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="8000">8000 Hz</SelectItem>
                    <SelectItem value="16000">16000 Hz (Recomendado)</SelectItem>
                    <SelectItem value="44100">44100 Hz</SelectItem>
                    <SelectItem value="48000">48000 Hz</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <Label htmlFor="sensitivity">Sensibilidade de Detecção</Label>
                  <span className="text-sm text-muted-foreground">70%</span>
                </div>
                <Slider id="sensitivity" defaultValue={[70]} max={100} />
              </div>

              <div className="flex items-center justify-between p-4 bg-muted/30 rounded-lg">
                <div>
                  <Label htmlFor="noiseReduction">Redução de Ruído</Label>
                  <p className="text-xs text-muted-foreground mt-1">Filtra ruídos de fundo automaticamente</p>
                </div>
                <Switch id="noiseReduction" defaultChecked />
              </div>

              <div className="flex items-center justify-between p-4 bg-muted/30 rounded-lg">
                <div>
                  <Label htmlFor="autoGain">Ganho Automático</Label>
                  <p className="text-xs text-muted-foreground mt-1">Ajusta o volume automaticamente</p>
                </div>
                <Switch id="autoGain" defaultChecked />
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Whisper Settings */}
        <TabsContent value="whisper" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Configurações do Whisper</CardTitle>
              <CardDescription>Ajuste o modelo de transcrição de áudio</CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="space-y-2">
                <Label htmlFor="model">Modelo Whisper</Label>
                <Select defaultValue="base">
                  <SelectTrigger id="model">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="tiny">Tiny (rápido, menos preciso)</SelectItem>
                    <SelectItem value="base">Base (recomendado)</SelectItem>
                    <SelectItem value="small">Small (mais lento, mais preciso)</SelectItem>
                    <SelectItem value="medium">Medium (muito preciso)</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label htmlFor="language">Idioma</Label>
                <Select defaultValue="pt">
                  <SelectTrigger id="language">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="pt">Português</SelectItem>
                    <SelectItem value="en">English</SelectItem>
                    <SelectItem value="es">Español</SelectItem>
                    <SelectItem value="auto">Auto-detectar</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <Label htmlFor="confidence">Threshold de Confiança</Label>
                  <span className="text-sm text-muted-foreground">65%</span>
                </div>
                <Slider id="confidence" defaultValue={[65]} max={100} />
                <p className="text-xs text-muted-foreground">
                  Transcrições com confiança abaixo deste valor serão ignoradas
                </p>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* AI Settings */}
        <TabsContent value="ai" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Configurações de IA</CardTitle>
              <CardDescription>Configure o backend de análise inteligente</CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="flex items-center justify-between p-4 bg-muted/30 rounded-lg">
                <div>
                  <Label htmlFor="contextAnalysis">Análise de Contexto</Label>
                  <p className="text-xs text-muted-foreground mt-1">Use IA para entender o contexto das palavras</p>
                </div>
                <Switch id="contextAnalysis" defaultChecked />
              </div>

              <div className="space-y-2">
                <Label htmlFor="backend">Backend Preferido</Label>
                <Select defaultValue="ollama">
                  <SelectTrigger id="backend">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="ollama">Ollama (Local)</SelectItem>
                    <SelectItem value="transformers">Transformers</SelectItem>
                    <SelectItem value="fallback">Fallback (Regex)</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <Label htmlFor="temperature">Temperatura</Label>
                  <span className="text-sm text-muted-foreground">0.7</span>
                </div>
                <Slider id="temperature" defaultValue={[70]} max={100} />
                <p className="text-xs text-muted-foreground">
                  Controla a criatividade da análise (menor = mais determinístico)
                </p>
              </div>

              <div className="space-y-2">
                <Label htmlFor="timeout">Timeout de Processamento (ms)</Label>
                <Input id="timeout" type="number" defaultValue={1000} />
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Performance Settings */}
        <TabsContent value="performance" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Otimização de Performance</CardTitle>
              <CardDescription>Configure cache, latência e aceleração por GPU</CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="space-y-2">
                <Label htmlFor="bufferSize">Buffer Size (ms)</Label>
                <Select defaultValue="512">
                  <SelectTrigger id="bufferSize">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="256">256 ms (Baixa latência)</SelectItem>
                    <SelectItem value="512">512 ms (Recomendado)</SelectItem>
                    <SelectItem value="1024">1024 ms (Alta qualidade)</SelectItem>
                    <SelectItem value="2048">2048 ms (Máxima qualidade)</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="flex items-center justify-between p-4 bg-muted/30 rounded-lg">
                <div>
                  <Label htmlFor="lowLatency">Modo Low-Latency</Label>
                  <p className="text-xs text-muted-foreground mt-1">Reduz latência ao custo de precisão</p>
                </div>
                <Switch id="lowLatency" />
              </div>

              <div className="flex items-center justify-between p-4 bg-muted/30 rounded-lg">
                <div>
                  <Label htmlFor="gpuAcceleration">Aceleração por GPU</Label>
                  <p className="text-xs text-muted-foreground mt-1">Use GPU para processamento mais rápido</p>
                </div>
                <Switch id="gpuAcceleration" defaultChecked />
              </div>

              <div className="flex items-center justify-between p-4 bg-muted/30 rounded-lg">
                <div>
                  <Label htmlFor="smartCache">Cache Inteligente</Label>
                  <p className="text-xs text-muted-foreground mt-1">Armazena transcrições recentes em cache</p>
                </div>
                <Switch id="smartCache" defaultChecked />
              </div>

              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <Label htmlFor="cacheSize">Tamanho do Cache (MB)</Label>
                  <span className="text-sm text-muted-foreground">256 MB</span>
                </div>
                <Slider id="cacheSize" defaultValue={[256]} min={64} max={1024} step={64} />
              </div>

              <div className="space-y-2">
                <Label htmlFor="threads">Threads de Processamento</Label>
                <Select defaultValue="4">
                  <SelectTrigger id="threads">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="1">1 thread</SelectItem>
                    <SelectItem value="2">2 threads</SelectItem>
                    <SelectItem value="4">4 threads (Recomendado)</SelectItem>
                    <SelectItem value="8">8 threads</SelectItem>
                    <SelectItem value="auto">Auto (Detectar)</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Visual Settings */}
        <TabsContent value="visual" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Configurações Visuais</CardTitle>
              <CardDescription>Personalize a aparência da interface</CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="space-y-2">
                <Label htmlFor="theme">Tema</Label>
                <Select defaultValue="dark">
                  <SelectTrigger id="theme">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="dark">Dark Mode (Cyberpunk)</SelectItem>
                    <SelectItem value="light">Light Mode</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label htmlFor="uiLanguage">Idioma da Interface</Label>
                <Select defaultValue="pt">
                  <SelectTrigger id="uiLanguage">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="pt">Português</SelectItem>
                    <SelectItem value="en">English</SelectItem>
                    <SelectItem value="es">Español</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <Label htmlFor="refresh">Taxa de Atualização (ms)</Label>
                  <span className="text-sm text-muted-foreground">100ms</span>
                </div>
                <Slider id="refresh" defaultValue={[100]} min={50} max={500} step={50} />
              </div>

              <div className="flex items-center justify-between p-4 bg-muted/30 rounded-lg">
                <div>
                  <Label htmlFor="animations">Animações</Label>
                  <p className="text-xs text-muted-foreground mt-1">Efeitos visuais e transições suaves</p>
                </div>
                <Switch id="animations" defaultChecked />
              </div>

              <div className="flex items-center justify-between p-4 bg-muted/30 rounded-lg">
                <div>
                  <Label htmlFor="glitch">Efeitos de Glitch</Label>
                  <p className="text-xs text-muted-foreground mt-1">Efeitos cyberpunk ao detectar keywords</p>
                </div>
                <Switch id="glitch" defaultChecked />
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Save Button */}
      <Card className="border-2 border-primary/50">
        <CardContent className="p-6">
          <Button size="lg" className="w-full bg-primary hover:bg-primary/90 glow-primary" onClick={saveSettings}>
            <Save className="w-4 h-4 mr-2" />
            Salvar Configurações
          </Button>
        </CardContent>
      </Card>
    </div>
  )
}
