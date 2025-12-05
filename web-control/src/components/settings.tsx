

import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Slider } from "@/components/ui/slider"
import { Switch } from "@/components/ui/switch"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Mic, Brain, Palette, Save, Volume2, Zap, CheckCircle, AlertCircle, Loader, RefreshCw } from "lucide-react"
import { toast } from "sonner"
import { useTheme } from "@/contexts/theme-context"
import { useEffect, useState } from "react"
import { useSystemInfo, useTestWhisper, useGPUControl, useAudioDeviceConfig, useWhisperDeviceConfig, useWhisperConfig, getAudioConfig, setAudioConfig } from "@/hooks"
import useAudioDiagnostics from "@/hooks/useAudioDiagnostics"

export function Settings() {
  const { theme, setTheme } = useTheme()
  const [mounted, setMounted] = useState(false)
  const [selectedDevice, setSelectedDevice] = useState("default")
  const [selectedBackend, setSelectedBackend] = useState("ollama")
  const [sensitivity, setSensitivity] = useState(70)
  const [temperature, setTemperature] = useState(70)
  const [gpuUsagePercent, setGpuUsagePercent] = useState(50)
  const [whisperDevice, setWhisperDeviceState] = useState("auto")
  const [autoGainEnabled, setAutoGainEnabled] = useState(true)
  const [targetDb, setTargetDb] = useState(-20)
  const [maxGainDb, setMaxGainDb] = useState(20)
  // Novos estados para configuração de tempo de transcrição
  const [minDuration, setMinDuration] = useState(2.0)
  const [maxDuration, setMaxDuration] = useState(15.0)
  const [silenceDuration, setSilenceDuration] = useState(1.0)

  const { systemInfo, loading: sysLoading } = useSystemInfo()
  const { testWhisper, testing, result } = useTestWhisper()
  const { gpuUsage, setGPUUsage } = useGPUControl()
  const { setAudioDevice, saving: deviceSaving } = useAudioDeviceConfig()
  const { setWhisperDevice, saving: whisperDeviceSaving } = useWhisperDeviceConfig()
  const { diagnosing, result: audioResult, error: audioError, runDiagnostics } = useAudioDiagnostics()

  useEffect(() => {
    // carregar config de auto-gain e tempos de transcrição
    const loadAudioConfig = async () => {
      try {
        const cfg = await getAudioConfig()
        const audioCfg = cfg?.audio || {}
        if (audioCfg && typeof audioCfg.auto_gain_enabled !== 'undefined') {
          setAutoGainEnabled(Boolean(audioCfg.auto_gain_enabled))
        }
        if (audioCfg && typeof audioCfg.target_db !== 'undefined') {
          setTargetDb(Number(audioCfg.target_db))
        }
        if (audioCfg && typeof audioCfg.max_gain_db !== 'undefined') {
          setMaxGainDb(Number(audioCfg.max_gain_db))
        }
        // Carregar tempos de transcrição
        if (audioCfg && typeof audioCfg.min_duration_seconds !== 'undefined') {
          setMinDuration(Number(audioCfg.min_duration_seconds))
        }
        if (audioCfg && typeof audioCfg.max_duration_seconds !== 'undefined') {
          setMaxDuration(Number(audioCfg.max_duration_seconds))
        }
        if (audioCfg && typeof audioCfg.silence_duration_to_stop !== 'undefined') {
          setSilenceDuration(Number(audioCfg.silence_duration_to_stop))
        }
      } catch (e) {
        // ignore
      }
    }
    loadAudioConfig()

    setMounted(true)
  }, [])

  const saveSettings = async () => {
    try {
      // Salvar dispositivo de áudio
      if (selectedDevice && selectedDevice !== "default") {
        const deviceResult = await setAudioDevice(selectedDevice)
        if (!deviceResult.success) {
          toast.error(deviceResult.message)
          return
        }
      }

      // Salvar device do Whisper (CPU/GPU)
      const whisperResult = await setWhisperDevice(whisperDevice as "auto" | "cuda" | "cpu")
      if (!whisperResult.success) {
        toast.error(whisperResult.message)
        return
      }

      // Salvar configurações de GPU
      if (gpuUsagePercent !== gpuUsage) {
        await setGPUUsage(gpuUsagePercent)
      }

      // Save auto-gain options e tempos de transcrição
      try {
        await setAudioConfig({ 
          auto_gain_enabled: autoGainEnabled, 
          target_db: Number(targetDb), 
          max_gain_db: Number(maxGainDb),
          min_duration_seconds: minDuration,
          max_duration_seconds: maxDuration,
          silence_duration_to_stop: silenceDuration
        })
      } catch (e) {
        toast.error("Erro ao salvar opções de Ganho Automático")
        return
      }

      toast.success("Configurações salvas com sucesso!")
    } catch (error) {
      toast.error("Erro ao salvar configurações")
    }
  }

  if (!mounted) {
    return null
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
                <Select value={selectedDevice} onValueChange={setSelectedDevice}>
                  <SelectTrigger id="device">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {sysLoading ? (
                      <SelectItem key="loading" value="loading">
                        Carregando dispositivos...
                      </SelectItem>
                    ) : systemInfo?.devices && systemInfo.devices.length > 0 ? (
                      systemInfo.devices.map((device, idx) => (
                        <SelectItem key={`device-${device.id || idx}`} value={String(device.id || idx)}>
                          {device.name}
                        </SelectItem>
                      ))
                    ) : (
                      <>
                        <SelectItem key="default" value="default">
                          Microfone Padrão
                        </SelectItem>
                        <SelectItem key="mic1" value="mic1">
                          Microfone USB
                        </SelectItem>
                        <SelectItem key="mic2" value="mic2">
                          Headset
                        </SelectItem>
                      </>
                    )}
                  </SelectContent>
                </Select>
                {!sysLoading && systemInfo?.devices && systemInfo.devices.length > 0 && (
                  <p className="text-xs text-success mt-1">✓ {systemInfo.devices.length} dispositivo(s) detectado(s)</p>
                )}
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
                  <span className="text-sm text-muted-foreground">{sensitivity}%</span>
                </div>
                <Slider id="sensitivity" value={[sensitivity]} onValueChange={(v) => setSensitivity(v[0])} max={100} />
              </div>

              {/* Configurações de Tempo de Transcrição */}
              <div className="p-4 border rounded-lg bg-secondary/5 space-y-4">
                <div>
                  <Label className="text-base font-semibold">⏱️ Tempo de Transcrição</Label>
                  <p className="text-xs text-muted-foreground mt-1">Configure quanto tempo de áudio capturar antes de transcrever</p>
                </div>
                
                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <Label htmlFor="minDuration">Duração Mínima</Label>
                    <span className="text-sm font-mono text-primary">{minDuration.toFixed(1)}s</span>
                  </div>
                  <Slider 
                    id="minDuration" 
                    value={[minDuration * 10]} 
                    onValueChange={(v) => setMinDuration(v[0] / 10)} 
                    min={5} 
                    max={50} 
                    step={1}
                  />
                  <p className="text-xs text-muted-foreground">Tempo mínimo antes de transcrever (0.5s - 5s)</p>
                </div>
                
                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <Label htmlFor="maxDuration">Duração Máxima</Label>
                    <span className="text-sm font-mono text-primary">{maxDuration.toFixed(0)}s</span>
                  </div>
                  <Slider 
                    id="maxDuration" 
                    value={[maxDuration]} 
                    onValueChange={(v) => setMaxDuration(v[0])} 
                    min={5} 
                    max={60} 
                    step={1}
                  />
                  <p className="text-xs text-muted-foreground">Tempo máximo de captura (5s - 60s)</p>
                </div>
                
                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <Label htmlFor="silenceDuration">Pausa para Finalizar</Label>
                    <span className="text-sm font-mono text-primary">{silenceDuration.toFixed(1)}s</span>
                  </div>
                  <Slider 
                    id="silenceDuration" 
                    value={[silenceDuration * 10]} 
                    onValueChange={(v) => setSilenceDuration(v[0] / 10)} 
                    min={3} 
                    max={30} 
                    step={1}
                  />
                  <p className="text-xs text-muted-foreground">Tempo de silêncio para detectar fim da frase (0.3s - 3s)</p>
                </div>
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
                  <p className="text-xs text-muted-foreground mt-1">Ajusta o volume automaticamente antes da transcrição</p>
                </div>
                <div className="flex items-center gap-3">
                  <Switch id="autoGain" checked={autoGainEnabled} onCheckedChange={(v) => setAutoGainEnabled(Boolean(v))} />
                  <div className="flex flex-col text-xs text-muted-foreground">
                    <div>Target dB: <input className="w-20 bg-transparent text-xs" value={String(targetDb)} onChange={(e) => setTargetDb(Number(e.target.value))} /></div>
                    <div>Max gain (dB): <input className="w-20 bg-transparent text-xs" value={String(maxGainDb)} onChange={(e) => setMaxGainDb(Number(e.target.value))} /></div>
                  </div>
                </div>
              </div>

              {/* Diagnostic button */}
              <div className="p-4 border rounded-lg bg-muted/20">
                <div className="flex items-center justify-between">
                  <div>
                    <Label>Diagnóstico do Microfone</Label>
                    <p className="text-xs text-muted-foreground">Execute uma medição rápida de energia e dB</p>
                  </div>
                  <div className="flex items-center gap-2">
                    <Button size="sm" onClick={() => runDiagnostics()} variant="outline" disabled={diagnosing}>
                      {diagnosing ? "Executando..." : "Diagnosticar"}
                    </Button>
                  </div>
                </div>

                {audioResult && (
                  <div className="mt-3 text-sm">
                    <div>Energy: {audioResult.energy}</div>
                    <div>dB: {audioResult.db} dB</div>
                    <div>Normalized: {audioResult.normalized_level}</div>
                    <div>Is silent: {String(audioResult.is_silent)}</div>
                    {audioResult.suggestion && <div className="mt-1 text-xs text-warning">⚠️ {audioResult.suggestion}</div>}
                  </div>
                )}

                {audioError && (
                  <div className="mt-2 text-xs text-destructive">Erro: {audioError}</div>
                )}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Whisper Settings */}
        <TabsContent value="whisper" className="space-y-4">
          <WhisperSettingsCard 
            systemInfo={systemInfo} 
            testWhisper={testWhisper} 
            testing={testing} 
            result={result}
          />
        </TabsContent>

        {/* AI Settings */}
        <TabsContent value="ai" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Configurações de IA</CardTitle>
              <CardDescription>Configure o backend de análise inteligente</CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              {/* AI Status */}
              <div className="grid grid-cols-2 gap-4">
                <div className="p-3 bg-muted/30 rounded-lg border border-border">
                  <p className="text-xs text-muted-foreground">Ollama</p>
                  <p className="text-sm font-bold mt-1">
                    {systemInfo?.llm_config.ollama_available ? (
                      <span className="text-success">✓ Disponível</span>
                    ) : (
                      <span className="text-muted-foreground">✗ Indisponível</span>
                    )}
                  </p>
                </div>
                <div className="p-3 bg-muted/30 rounded-lg border border-border">
                  <p className="text-xs text-muted-foreground">Transformers</p>
                  <p className="text-sm font-bold mt-1">
                    {systemInfo?.llm_config.transformers_available ? (
                      <span className="text-success">✓ Disponível</span>
                    ) : (
                      <span className="text-muted-foreground">✗ Indisponível</span>
                    )}
                  </p>
                </div>
              </div>

              <div className="flex items-center justify-between p-4 bg-muted/30 rounded-lg">
                <div>
                  <Label htmlFor="contextAnalysis">Análise de Contexto</Label>
                  <p className="text-xs text-muted-foreground mt-1">Use IA para entender o contexto das palavras</p>
                </div>
                <Switch id="contextAnalysis" defaultChecked />
              </div>

              <div className="space-y-2">
                <Label htmlFor="backend">Backend Preferido</Label>
                <Select value={selectedBackend} onValueChange={setSelectedBackend}>
                  <SelectTrigger id="backend">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="ollama">
                      Ollama (Local){systemInfo?.llm_config.ollama_available ? " ✓" : " ✗"}
                    </SelectItem>
                    <SelectItem value="transformers">
                      Transformers{systemInfo?.llm_config.transformers_available ? " ✓" : " ✗"}
                    </SelectItem>
                    <SelectItem value="fallback">Fallback (Regex)</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label htmlFor="aiModel">Modelo de IA</Label>
                <Select defaultValue="phi">
                  <SelectTrigger id="aiModel">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="phi">Phi 2 (Pequeno, Rápido)</SelectItem>
                    <SelectItem value="mistral">Mistral 7B (Equilibrado)</SelectItem>
                    <SelectItem value="neural-chat">Neural Chat (Conversação)</SelectItem>
                    <SelectItem value="orca">Orca (Precisão)</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <Label htmlFor="temperature">Temperatura (Criatividade)</Label>
                  <span className="text-sm text-muted-foreground">{temperature / 100}</span>
                </div>
                <Slider
                  id="temperature"
                  value={[temperature]}
                  onValueChange={(v) => setTemperature(v[0])}
                  max={200}
                  step={10}
                />
                <p className="text-xs text-muted-foreground">
                  Controla a criatividade da análise (0.1 = determinístico, 2.0 = criativo)
                </p>
              </div>

              <div className="space-y-2">
                <Label htmlFor="timeout">Timeout de Processamento (ms)</Label>
                <Input id="timeout" type="number" defaultValue={1000} />
              </div>

              <div className="space-y-2">
                <Label htmlFor="maxTokens">Máximo de Tokens</Label>
                <Select defaultValue="256">
                  <SelectTrigger id="maxTokens">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="128">128 (Rápido)</SelectItem>
                    <SelectItem value="256">256 (Recomendado)</SelectItem>
                    <SelectItem value="512">512 (Detalhado)</SelectItem>
                    <SelectItem value="1024">1024 (Muito detalhado)</SelectItem>
                  </SelectContent>
                </Select>
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
              {/* GPU Info */}
              {systemInfo?.gpu_info && (
                <div className="p-4 bg-secondary/10 rounded-lg border border-secondary/30">
                  <div className="flex items-start justify-between">
                    <div>
                      <p className="text-sm font-bold">{systemInfo.gpu_info.name}</p>
                      <p className="text-xs text-muted-foreground mt-1">
                        {systemInfo.gpu_info.available ? "✓ Disponível" : "✗ Indisponível"}
                      </p>
                      {systemInfo.gpu_info.available && (
                        <p className="text-xs text-muted-foreground mt-1">
                          Memória: {systemInfo.gpu_info.memory_free_mb} / {systemInfo.gpu_info.memory_total_mb} MB
                        </p>
                      )}
                    </div>
                  </div>
                </div>
              )}

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

              {/* GPU Usage Control */}
              <div className="space-y-3 p-4 bg-secondary/5 rounded-lg border border-secondary/20">
                <div className="flex items-center justify-between">
                  <div>
                    <Label htmlFor="gpuUsage">Utilização de GPU</Label>
                    <p className="text-xs text-muted-foreground mt-1">
                      Controle quanto da GPU usar para processamento
                    </p>
                  </div>
                  <span className="text-sm font-bold text-secondary">{gpuUsagePercent}%</span>
                </div>
                <Slider
                  id="gpuUsage"
                  value={[gpuUsagePercent]}
                  onValueChange={(v) => setGpuUsagePercent(v[0])}
                  max={100}
                  step={10}
                />
                <p className="text-xs text-muted-foreground">
                  Aumente para melhor performance em troca de mais consumo de energia
                </p>
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
                <Select value={theme || "dark"} onValueChange={setTheme}>
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
          <Button 
            size="lg" 
            className="w-full bg-primary hover:bg-primary/90 glow-primary" 
            onClick={saveSettings}
            disabled={deviceSaving}
          >
            {deviceSaving ? (
              <>
                <Loader className="w-4 h-4 mr-2 animate-spin" />
                Salvando...
              </>
            ) : (
              <>
                <Save className="w-4 h-4 mr-2" />
                Salvar Configurações
              </>
            )}
          </Button>
        </CardContent>
      </Card>
    </div>
  )
}

// ============ Componente de Configurações do Whisper ============

interface WhisperSettingsCardProps {
  systemInfo: any
  testWhisper: () => void
  testing: boolean
  result: { success: boolean; message: string } | null
}

function WhisperSettingsCard({ systemInfo, testWhisper, testing, result }: WhisperSettingsCardProps) {
  const { config, loading, saving, error, saveConfig, reloadModel } = useWhisperConfig()
  const [reloading, setReloading] = useState(false)
  
  // Estados locais para os campos
  const [model, setModel] = useState("base")
  const [language, setLanguage] = useState("pt")
  const [device, setDevice] = useState("auto")
  const [beamSize, setBeamSize] = useState(5)
  const [bestOf, setBestOf] = useState(5)
  const [temperature, setTemperature] = useState(0.0)
  const [patience, setPatience] = useState(1.0)
  const [lengthPenalty, setLengthPenalty] = useState(1.0)
  const [suppressBlank, setSuppressBlank] = useState(true)
  const [conditionOnPrevious, setConditionOnPrevious] = useState(true)
  const [noSpeechThreshold, setNoSpeechThreshold] = useState(0.6)
  const [compressionThreshold, setCompressionThreshold] = useState(2.4)
  const [logprobThreshold, setLogprobThreshold] = useState(-1.0)
  const [initialPrompt, setInitialPrompt] = useState("Esta é uma transcrição em português brasileiro.")
  const [wordTimestamps, setWordTimestamps] = useState(false)
  
  // Função para aplicar modelo em tempo real
  const handleReloadModel = async () => {
    setReloading(true)
    try {
      const result = await reloadModel(model)
      if (result.success) {
        toast.success(result.message)
      } else {
        toast.error(result.message)
      }
    } catch (e) {
      toast.error("Erro ao aplicar modelo")
    } finally {
      setReloading(false)
    }
  }
  
  // Carregar config quando disponível
  useEffect(() => {
    if (config) {
      setModel(config.model || "base")
      setLanguage(config.language || "pt")
      setDevice(config.device || "auto")
      setBeamSize(config.beam_size || 5)
      setBestOf(config.best_of || 5)
      setTemperature(config.temperature || 0.0)
      setPatience(config.patience || 1.0)
      setLengthPenalty(config.length_penalty || 1.0)
      setSuppressBlank(config.suppress_blank !== false)
      setConditionOnPrevious(config.condition_on_previous_text !== false)
      setNoSpeechThreshold(config.no_speech_threshold || 0.6)
      setCompressionThreshold(config.compression_ratio_threshold || 2.4)
      setLogprobThreshold(config.logprob_threshold || -1.0)
      setInitialPrompt(config.initial_prompt || "")
      setWordTimestamps(config.word_timestamps || false)
    }
  }, [config])
  
  const handleSave = async () => {
    const result = await saveConfig({
      model,
      language,
      device,
      beam_size: beamSize,
      best_of: bestOf,
      temperature,
      patience,
      length_penalty: lengthPenalty,
      suppress_blank: suppressBlank,
      condition_on_previous_text: conditionOnPrevious,
      no_speech_threshold: noSpeechThreshold,
      compression_ratio_threshold: compressionThreshold,
      logprob_threshold: logprobThreshold,
      initial_prompt: initialPrompt,
      word_timestamps: wordTimestamps,
    })
    
    if (result.success) {
      toast.success(result.message)
    } else {
      toast.error(result.message)
    }
  }
  
  if (loading) {
    return (
      <Card>
        <CardContent className="p-6 flex items-center justify-center">
          <Loader className="w-6 h-6 animate-spin mr-2" />
          Carregando configurações...
        </CardContent>
      </Card>
    )
  }
  
  return (
    <div className="space-y-4">
      {/* Status Card */}
      <Card>
        <CardHeader>
          <CardTitle>Status do Whisper</CardTitle>
          <CardDescription>Verifique o funcionamento do modelo de transcrição</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="p-4 bg-primary/10 rounded-lg border border-primary/30 flex items-start gap-3">
            <div className="flex-1">
              <p className="text-sm font-medium">Status</p>
              <p className="text-xs text-muted-foreground mt-1">
                {systemInfo?.whisper_status?.available
                  ? `✓ Operacional (${systemInfo.whisper_status.model})`
                  : "✗ Não disponível"}
              </p>
            </div>
            <Button
              size="sm"
              onClick={testWhisper}
              disabled={testing}
              variant="outline"
              className="border-primary text-primary hover:bg-primary/10"
            >
              {testing ? (
                <>
                  <Loader className="w-4 h-4 mr-2 animate-spin" />
                  Testando...
                </>
              ) : (
                <>
                  <CheckCircle className="w-4 h-4 mr-2" />
                  Testar
                </>
              )}
            </Button>
          </div>

          {result && (
            <div
              className={`p-3 rounded-lg border flex items-start gap-2 ${
                result.success
                  ? "bg-success/10 border-success/30 text-success"
                  : "bg-destructive/10 border-destructive/30 text-destructive"
              }`}
            >
              {result.success ? (
                <CheckCircle className="w-4 h-4 mt-0.5 flex-shrink-0" />
              ) : (
                <AlertCircle className="w-4 h-4 mt-0.5 flex-shrink-0" />
              )}
              <p className="text-sm">{result.message}</p>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Configurações Básicas */}
      <Card>
        <CardHeader>
          <CardTitle>Configurações Básicas</CardTitle>
          <CardDescription>Modelo, idioma e dispositivo de processamento</CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="model">Modelo Whisper</Label>
              <div className="flex gap-2">
                <Select value={model} onValueChange={setModel}>
                  <SelectTrigger id="model" className="flex-1">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="tiny">Tiny (39M params - muito rápido)</SelectItem>
                    <SelectItem value="base">Base (74M params - recomendado)</SelectItem>
                    <SelectItem value="small">Small (244M params - mais preciso)</SelectItem>
                    <SelectItem value="medium">Medium (769M params - alta precisão)</SelectItem>
                    <SelectItem value="large">Large (1550M params - máxima precisão)</SelectItem>
                    <SelectItem value="large-v2">Large-v2 (melhor para PT-BR)</SelectItem>
                    <SelectItem value="large-v3">Large-v3 (mais recente)</SelectItem>
                  </SelectContent>
                </Select>
                <Button 
                  size="sm" 
                  variant="outline" 
                  onClick={handleReloadModel}
                  disabled={reloading || model === config?.model}
                  className="shrink-0"
                  title="Aplicar modelo em tempo real"
                >
                  {reloading ? (
                    <Loader className="w-4 h-4 animate-spin" />
                  ) : (
                    <RefreshCw className="w-4 h-4" />
                  )}
                </Button>
              </div>
              {model !== config?.model && (
                <p className="text-xs text-warning">
                  ⚠️ Modelo diferente do atual ({config?.model}). Clique em ↻ para aplicar agora.
                </p>
              )}
            </div>

            <div className="space-y-2">
              <Label htmlFor="language">Idioma</Label>
              <Select value={language} onValueChange={setLanguage}>
                <SelectTrigger id="language">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="pt">🇧🇷 Português (PT-BR)</SelectItem>
                  <SelectItem value="en">🇺🇸 English</SelectItem>
                  <SelectItem value="es">🇪🇸 Español</SelectItem>
                  <SelectItem value="fr">🇫🇷 Français</SelectItem>
                  <SelectItem value="de">🇩🇪 Deutsch</SelectItem>
                  <SelectItem value="it">🇮🇹 Italiano</SelectItem>
                  <SelectItem value="ja">🇯🇵 日本語</SelectItem>
                  <SelectItem value="ko">🇰🇷 한국어</SelectItem>
                  <SelectItem value="zh">🇨🇳 中文</SelectItem>
                  <SelectItem value="auto">🔄 Auto-detectar</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>

          <div className="space-y-2">
            <Label htmlFor="device">Processador (CPU/GPU)</Label>
            <Select value={device} onValueChange={setDevice}>
              <SelectTrigger id="device">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="auto">🔄 Auto-detectar (recomendado)</SelectItem>
                <SelectItem value="cuda" disabled={!systemInfo?.gpu_info?.available}>
                  🚀 GPU CUDA (muito mais rápido)
                </SelectItem>
                <SelectItem value="cpu">💻 CPU (mais compatível)</SelectItem>
              </SelectContent>
            </Select>
            <p className="text-xs text-muted-foreground">
              {systemInfo?.gpu_info?.available
                ? `✓ GPU disponível: ${systemInfo.gpu_info.name}`
                : "⚠️ GPU não detectada"}
            </p>
          </div>

          <div className="space-y-2">
            <Label htmlFor="initialPrompt">Prompt Inicial</Label>
            <Input
              id="initialPrompt"
              value={initialPrompt}
              onChange={(e) => setInitialPrompt(e.target.value)}
              placeholder="Ex: Esta é uma transcrição em português brasileiro."
            />
            <p className="text-xs text-muted-foreground">
              Ajuda o Whisper a entender o contexto e idioma do áudio
            </p>
          </div>
        </CardContent>
      </Card>

      {/* Configurações Avançadas */}
      <Card>
        <CardHeader>
          <CardTitle>Configurações Avançadas</CardTitle>
          <CardDescription>Parâmetros de decodificação e qualidade da transcrição</CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="grid grid-cols-2 gap-6">
            {/* Beam Search */}
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <Label htmlFor="beamSize">Beam Size</Label>
                <span className="text-sm text-muted-foreground">{beamSize}</span>
              </div>
              <Slider
                id="beamSize"
                value={[beamSize]}
                onValueChange={(v) => setBeamSize(v[0])}
                min={1}
                max={10}
                step={1}
              />
              <p className="text-xs text-muted-foreground">
                Maior = mais preciso, mais lento (recomendado: 5)
              </p>
            </div>

            {/* Best Of */}
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <Label htmlFor="bestOf">Best Of (Candidatos)</Label>
                <span className="text-sm text-muted-foreground">{bestOf}</span>
              </div>
              <Slider
                id="bestOf"
                value={[bestOf]}
                onValueChange={(v) => setBestOf(v[0])}
                min={1}
                max={10}
                step={1}
              />
              <p className="text-xs text-muted-foreground">
                Número de candidatos a considerar (recomendado: 5)
              </p>
            </div>

            {/* Temperature */}
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <Label htmlFor="temperature">Temperatura</Label>
                <span className="text-sm text-muted-foreground">{temperature.toFixed(1)}</span>
              </div>
              <Slider
                id="temperature"
                value={[temperature * 10]}
                onValueChange={(v) => setTemperature(v[0] / 10)}
                min={0}
                max={10}
                step={1}
              />
              <p className="text-xs text-muted-foreground">
                0.0 = determinístico, 1.0 = mais criativo (recomendado: 0.0)
              </p>
            </div>

            {/* No Speech Threshold */}
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <Label htmlFor="noSpeech">Threshold de Silêncio</Label>
                <span className="text-sm text-muted-foreground">{noSpeechThreshold.toFixed(1)}</span>
              </div>
              <Slider
                id="noSpeech"
                value={[noSpeechThreshold * 10]}
                onValueChange={(v) => setNoSpeechThreshold(v[0] / 10)}
                min={0}
                max={10}
                step={1}
              />
              <p className="text-xs text-muted-foreground">
                Detecta quando não há fala (recomendado: 0.6)
              </p>
            </div>

            {/* Compression Ratio */}
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <Label htmlFor="compression">Threshold de Compressão</Label>
                <span className="text-sm text-muted-foreground">{compressionThreshold.toFixed(1)}</span>
              </div>
              <Slider
                id="compression"
                value={[compressionThreshold * 10]}
                onValueChange={(v) => setCompressionThreshold(v[0] / 10)}
                min={10}
                max={50}
                step={1}
              />
              <p className="text-xs text-muted-foreground">
                Filtra alucinações - menor = mais estrito (recomendado: 2.4)
              </p>
            </div>

            {/* Log Probability Threshold */}
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <Label htmlFor="logprob">Threshold de Log Prob</Label>
                <span className="text-sm text-muted-foreground">{logprobThreshold.toFixed(1)}</span>
              </div>
              <Slider
                id="logprob"
                value={[logprobThreshold + 2]}
                onValueChange={(v) => setLogprobThreshold(v[0] - 2)}
                min={0}
                max={2}
                step={0.1}
              />
              <p className="text-xs text-muted-foreground">
                Threshold de probabilidade (recomendado: -1.0)
              </p>
            </div>
          </div>

          {/* Switches */}
          <div className="grid grid-cols-2 gap-4 pt-4">
            <div className="flex items-center justify-between p-4 bg-muted/30 rounded-lg">
              <div>
                <Label htmlFor="suppressBlank">Suprimir Vazios</Label>
                <p className="text-xs text-muted-foreground mt-1">Remove outputs em branco</p>
              </div>
              <Switch
                id="suppressBlank"
                checked={suppressBlank}
                onCheckedChange={setSuppressBlank}
              />
            </div>

            <div className="flex items-center justify-between p-4 bg-muted/30 rounded-lg">
              <div>
                <Label htmlFor="conditionPrev">Contexto Anterior</Label>
                <p className="text-xs text-muted-foreground mt-1">Usa texto anterior como contexto</p>
              </div>
              <Switch
                id="conditionPrev"
                checked={conditionOnPrevious}
                onCheckedChange={setConditionOnPrevious}
              />
            </div>

            <div className="flex items-center justify-between p-4 bg-muted/30 rounded-lg">
              <div>
                <Label htmlFor="wordTimestamps">Timestamps por Palavra</Label>
                <p className="text-xs text-muted-foreground mt-1">Extrai tempo de cada palavra</p>
              </div>
              <Switch
                id="wordTimestamps"
                checked={wordTimestamps}
                onCheckedChange={setWordTimestamps}
              />
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Botão Salvar */}
      <Card>
        <CardContent className="p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-muted-foreground">
                ⚠️ Alterações requerem reinício da captura para aplicar mudanças no modelo
              </p>
            </div>
            <Button onClick={handleSave} disabled={saving}>
              {saving ? (
                <>
                  <Loader className="w-4 h-4 mr-2 animate-spin" />
                  Salvando...
                </>
              ) : (
                <>
                  <Save className="w-4 h-4 mr-2" />
                  Salvar Configurações do Whisper
                </>
              )}
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
