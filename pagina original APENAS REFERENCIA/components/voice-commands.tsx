"use client"

import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Badge } from "@/components/ui/badge"
import { Switch } from "@/components/ui/switch"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Mic, Play, Square, Keyboard, Mouse, Settings } from "lucide-react"
import { useState } from "react"
import { toast } from "sonner"

export function VoiceCommands() {
  const [isListening, setIsListening] = useState(false)

  const toggleListening = () => {
    setIsListening(!isListening)
    toast.success(isListening ? "Comandos de voz desativados" : "Comandos de voz ativados")
  }

  const systemCommands = [
    { id: 1, command: "volume up", action: "Aumentar volume do sistema", category: "Sistema", active: true },
    { id: 2, command: "volume down", action: "Diminuir volume do sistema", category: "Sistema", active: true },
    { id: 3, command: "mute", action: "Mutar áudio", category: "Sistema", active: true },
    { id: 4, command: "unmute", action: "Desmutar áudio", category: "Sistema", active: true },
  ]

  const appCommands = [
    { id: 5, command: "start capture", action: "Iniciar captura de áudio", category: "App", active: true },
    { id: 6, command: "stop capture", action: "Parar captura", category: "App", active: true },
    { id: 7, command: "show stats", action: "Abrir aba de insights", category: "App", active: true },
    { id: 8, command: "clear history", action: "Limpar histórico", category: "App", active: false },
  ]

  const macroCommands = [
    {
      id: 9,
      command: "gaming mode",
      actions: ["Iniciar captura", "Mudar para preset Gaming", "Ativar keywords de jogo"],
      category: "Macro",
      active: true,
    },
    {
      id: 10,
      command: "stream mode",
      actions: ["Conectar OBS", "Ativar alertas de chat", "Maximizar performance"],
      category: "Macro",
      active: true,
    },
  ]

  const keyboardMacros = [
    { id: 1, command: "press enter", key: "Enter", active: true },
    { id: 2, command: "press space", key: "Space", active: true },
    { id: 3, command: "press escape", key: "Escape", active: true },
    { id: 4, command: "screenshot", key: "F12", active: true },
  ]

  return (
    <div className="p-8 space-y-6">
      <div>
        <h2 className="text-3xl font-bold text-foreground mb-2">Comandos de Voz Avançados</h2>
        <p className="text-muted-foreground">Controle o sistema e app por voz com macros inteligentes</p>
      </div>

      {/* Control Panel */}
      <Card className="border-2 border-primary/50">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Mic className="w-5 h-5 text-primary" />
            Controle de Comandos de Voz
          </CardTitle>
          <CardDescription>Ative ou desative o reconhecimento de comandos</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <Button
            size="lg"
            className={`w-full h-16 text-lg font-bold ${isListening ? "bg-destructive hover:bg-destructive/90" : "bg-primary hover:bg-primary/90 glow-primary"}`}
            onClick={toggleListening}
          >
            {isListening ? (
              <>
                <Square className="w-5 h-5 mr-2" />
                Parar Reconhecimento
              </>
            ) : (
              <>
                <Play className="w-5 h-5 mr-2" />
                Iniciar Reconhecimento
              </>
            )}
          </Button>

          {isListening && (
            <div className="p-4 bg-primary/10 rounded-lg border border-primary/30 animate-pulse">
              <p className="text-sm text-center text-foreground">
                🎤 Ouvindo comandos...
                <span className="inline-block w-2 h-4 ml-1 bg-primary animate-pulse" />
              </p>
            </div>
          )}

          <div className="grid grid-cols-2 gap-4">
            <div className="p-3 bg-muted/30 rounded-lg text-center">
              <p className="text-xs text-muted-foreground">Comandos Ativos</p>
              <p className="text-2xl font-bold text-primary mt-1">18</p>
            </div>
            <div className="p-3 bg-muted/30 rounded-lg text-center">
              <p className="text-xs text-muted-foreground">Executados Hoje</p>
              <p className="text-2xl font-bold text-secondary mt-1">47</p>
            </div>
          </div>
        </CardContent>
      </Card>

      <Tabs defaultValue="system" className="space-y-4">
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="system">
            <Settings className="w-4 h-4 mr-2" />
            Sistema
          </TabsTrigger>
          <TabsTrigger value="macros">
            <Keyboard className="w-4 h-4 mr-2" />
            Macros
          </TabsTrigger>
          <TabsTrigger value="keyboard">
            <Mouse className="w-4 h-4 mr-2" />
            Teclado/Mouse
          </TabsTrigger>
        </TabsList>

        {/* System Commands Tab */}
        <TabsContent value="system" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Comandos de Sistema</CardTitle>
              <CardDescription>Controle o volume, áudio e funcionalidades do sistema</CardDescription>
            </CardHeader>
            <CardContent className="space-y-2">
              {[...systemCommands, ...appCommands].map((cmd) => (
                <div
                  key={cmd.id}
                  className="flex items-center justify-between p-3 bg-muted/30 rounded-lg border border-border"
                >
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      <Badge variant="outline" className="font-mono text-primary border-primary">
                        "{cmd.command}"
                      </Badge>
                      <Badge variant="secondary">{cmd.category}</Badge>
                    </div>
                    <p className="text-sm text-muted-foreground">{cmd.action}</p>
                  </div>
                  <Switch defaultChecked={cmd.active} />
                </div>
              ))}

              <Button variant="outline" className="w-full mt-4 bg-transparent">
                + Adicionar Novo Comando
              </Button>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Macros Tab */}
        <TabsContent value="macros" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Macros de Comandos</CardTitle>
              <CardDescription>Execute múltiplas ações com um único comando</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {macroCommands.map((macro) => (
                <Card key={macro.id} className="border-primary/30">
                  <CardHeader>
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <Badge variant="outline" className="font-mono text-lg text-primary border-primary">
                          "{macro.command}"
                        </Badge>
                        <Badge>{macro.category}</Badge>
                      </div>
                      <Switch defaultChecked={macro.active} />
                    </div>
                  </CardHeader>
                  <CardContent>
                    <p className="text-sm text-muted-foreground mb-3">Sequência de ações:</p>
                    <div className="space-y-2">
                      {macro.actions.map((action, idx) => (
                        <div key={idx} className="flex items-center gap-2 p-2 bg-muted/50 rounded">
                          <div className="w-6 h-6 rounded-full bg-primary/20 flex items-center justify-center text-xs font-bold text-primary">
                            {idx + 1}
                          </div>
                          <p className="text-sm text-foreground">{action}</p>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              ))}

              <Button variant="outline" className="w-full bg-transparent">
                + Criar Nova Macro
              </Button>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Keyboard/Mouse Tab */}
        <TabsContent value="keyboard" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Comandos de Teclado e Mouse</CardTitle>
              <CardDescription>Simule teclas e cliques do mouse por voz</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {keyboardMacros.map((macro) => (
                <div
                  key={macro.id}
                  className="flex items-center justify-between p-3 bg-muted/30 rounded-lg border border-border"
                >
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      <Badge variant="outline" className="font-mono text-primary border-primary">
                        "{macro.command}"
                      </Badge>
                      <span className="text-sm text-muted-foreground">→</span>
                      <Badge variant="secondary" className="font-mono">
                        {macro.key}
                      </Badge>
                    </div>
                  </div>
                  <Switch defaultChecked={macro.active} />
                </div>
              ))}

              <div className="pt-4 border-t border-border space-y-4">
                <div className="space-y-2">
                  <Label>Criar Novo Atalho</Label>
                  <div className="flex gap-2">
                    <Input placeholder='Comando de voz (ex: "next slide")' className="flex-1" />
                    <Select>
                      <SelectTrigger className="w-32">
                        <SelectValue placeholder="Tecla" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="enter">Enter</SelectItem>
                        <SelectItem value="space">Space</SelectItem>
                        <SelectItem value="esc">Escape</SelectItem>
                        <SelectItem value="tab">Tab</SelectItem>
                        <SelectItem value="f1">F1-F12</SelectItem>
                      </SelectContent>
                    </Select>
                    <Button>Adicionar</Button>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Configurações Avançadas</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center justify-between p-4 bg-muted/30 rounded-lg">
                <div>
                  <Label>Confirmação de Comando</Label>
                  <p className="text-xs text-muted-foreground mt-1">Pedir confirmação antes de executar</p>
                </div>
                <Switch />
              </div>

              <div className="flex items-center justify-between p-4 bg-muted/30 rounded-lg">
                <div>
                  <Label>Feedback Sonoro</Label>
                  <p className="text-xs text-muted-foreground mt-1">Tocar som ao reconhecer comando</p>
                </div>
                <Switch defaultChecked />
              </div>

              <div className="flex items-center justify-between p-4 bg-muted/30 rounded-lg">
                <div>
                  <Label>Hotword Detection</Label>
                  <p className="text-xs text-muted-foreground mt-1">Ativar apenas após palavra-chave</p>
                </div>
                <Switch defaultChecked />
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}
