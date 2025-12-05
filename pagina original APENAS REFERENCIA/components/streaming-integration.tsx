"use client"

import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Badge } from "@/components/ui/badge"
import { Switch } from "@/components/ui/switch"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Twitch, Youtube, Radio, Wifi, WifiOff, Settings, Send } from "lucide-react"
import { useState } from "react"
import { toast } from "sonner"

export function StreamingIntegration() {
  const [obsConnected, setObsConnected] = useState(false)
  const [streamerBotConnected, setStreamerBotConnected] = useState(false)

  const connectOBS = () => {
    setObsConnected(!obsConnected)
    toast.success(obsConnected ? "OBS desconectado" : "Conectado ao OBS WebSocket")
  }

  const connectStreamerBot = () => {
    setStreamerBotConnected(!streamerBotConnected)
    toast.success(streamerBotConnected ? "Streamer.bot desconectado" : "Conectado ao Streamer.bot")
  }

  const testSceneChange = () => {
    toast.info("Mudando para cena 'Gaming'")
  }

  const testChatMessage = () => {
    toast.info("Enviando mensagem para o chat")
  }

  const obsScenes = [
    { id: 1, name: "Starting Soon", active: false },
    { id: 2, name: "Gaming", active: true },
    { id: 3, name: "Just Chatting", active: false },
    { id: 4, name: "BRB", active: false },
    { id: 5, name: "Ending", active: false },
  ]

  const keywordActions = [
    { id: 1, keyword: "explosão", action: "Mudar para cena 'Action'", platform: "OBS" },
    { id: 2, keyword: "vitória", action: "Enviar '🎉 VITÓRIA!' no chat", platform: "Twitch" },
    { id: 3, keyword: "turbo", action: "Ativar filtro 'Speed Effect'", platform: "OBS" },
    { id: 4, keyword: "épico", action: "Tocar som + Slow-mo 2s", platform: "OBS" },
  ]

  return (
    <div className="p-8 space-y-6">
      <div>
        <h2 className="text-3xl font-bold text-foreground mb-2">Integração com Streaming</h2>
        <p className="text-muted-foreground">Conecte com OBS, Twitch e YouTube para automações ao vivo</p>
      </div>

      {/* Connection Status */}
      <div className="grid gap-4 md:grid-cols-2">
        <Card className={`border-2 ${obsConnected ? "border-primary/50 glow-primary" : "border-border"}`}>
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle className="flex items-center gap-2">
                <Radio className="w-5 h-5 text-primary" />
                OBS WebSocket
              </CardTitle>
              {obsConnected ? (
                <Badge className="bg-success text-white">
                  <Wifi className="w-3 h-3 mr-1" />
                  Conectado
                </Badge>
              ) : (
                <Badge variant="secondary">
                  <WifiOff className="w-3 h-3 mr-1" />
                  Desconectado
                </Badge>
              )}
            </div>
            <CardDescription>Controle cenas e fontes do OBS Studio</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="obsHost">Host</Label>
              <Input id="obsHost" defaultValue="localhost:4455" disabled={obsConnected} />
            </div>
            <div className="space-y-2">
              <Label htmlFor="obsPassword">Senha</Label>
              <Input id="obsPassword" type="password" placeholder="••••••••" disabled={obsConnected} />
            </div>
            <Button className="w-full" variant={obsConnected ? "destructive" : "default"} onClick={connectOBS}>
              {obsConnected ? "Desconectar" : "Conectar ao OBS"}
            </Button>
          </CardContent>
        </Card>

        <Card className={`border-2 ${streamerBotConnected ? "border-secondary/50 glow-secondary" : "border-border"}`}>
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle className="flex items-center gap-2">
                <Twitch className="w-5 h-5 text-secondary" />
                Streamer.bot
              </CardTitle>
              {streamerBotConnected ? (
                <Badge className="bg-success text-white">
                  <Wifi className="w-3 h-3 mr-1" />
                  Conectado
                </Badge>
              ) : (
                <Badge variant="secondary">
                  <WifiOff className="w-3 h-3 mr-1" />
                  Desconectado
                </Badge>
              )}
            </div>
            <CardDescription>Envie alertas para Twitch/YouTube chat</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="botHost">Host</Label>
              <Input id="botHost" defaultValue="localhost:8080" disabled={streamerBotConnected} />
            </div>
            <div className="space-y-2">
              <Label htmlFor="botToken">Token de API</Label>
              <Input id="botToken" type="password" placeholder="••••••••" disabled={streamerBotConnected} />
            </div>
            <Button
              className="w-full"
              variant={streamerBotConnected ? "destructive" : "default"}
              onClick={connectStreamerBot}
            >
              {streamerBotConnected ? "Desconectar" : "Conectar ao Streamer.bot"}
            </Button>
          </CardContent>
        </Card>
      </div>

      <Tabs defaultValue="obs" className="space-y-4">
        <TabsList>
          <TabsTrigger value="obs">
            <Radio className="w-4 h-4 mr-2" />
            OBS Control
          </TabsTrigger>
          <TabsTrigger value="chat">
            <Send className="w-4 h-4 mr-2" />
            Chat Alerts
          </TabsTrigger>
          <TabsTrigger value="actions">
            <Settings className="w-4 h-4 mr-2" />
            Ações Automáticas
          </TabsTrigger>
        </TabsList>

        {/* OBS Control Tab */}
        <TabsContent value="obs" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Controle de Cenas</CardTitle>
              <CardDescription>Mude cenas do OBS automaticamente com keywords</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid gap-3 md:grid-cols-2">
                {obsScenes.map((scene) => (
                  <Button
                    key={scene.id}
                    variant={scene.active ? "default" : "outline"}
                    className={`justify-start h-auto py-4 ${scene.active && "border-2 border-primary glow-primary"}`}
                    disabled={!obsConnected}
                    onClick={testSceneChange}
                  >
                    <div className="text-left">
                      <p className="font-semibold">{scene.name}</p>
                      {scene.active && <p className="text-xs text-primary">Cena Ativa</p>}
                    </div>
                  </Button>
                ))}
              </div>

              <div className="mt-6 space-y-4">
                <div className="flex items-center justify-between p-4 bg-muted/30 rounded-lg">
                  <div>
                    <Label>Auto Scene Switching</Label>
                    <p className="text-xs text-muted-foreground mt-1">Mude cenas baseado em keywords</p>
                  </div>
                  <Switch disabled={!obsConnected} />
                </div>

                <div className="flex items-center justify-between p-4 bg-muted/30 rounded-lg">
                  <div>
                    <Label>Source Control</Label>
                    <p className="text-xs text-muted-foreground mt-1">Controle visibilidade de fontes</p>
                  </div>
                  <Switch disabled={!obsConnected} />
                </div>

                <div className="flex items-center justify-between p-4 bg-muted/30 rounded-lg">
                  <div>
                    <Label>Filter Effects</Label>
                    <p className="text-xs text-muted-foreground mt-1">Ative filtros temporários</p>
                  </div>
                  <Switch disabled={!obsConnected} defaultChecked />
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Chat Alerts Tab */}
        <TabsContent value="chat" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Configurações de Chat</CardTitle>
              <CardDescription>Envie mensagens automáticas para Twitch/YouTube</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label>Plataforma</Label>
                <div className="grid grid-cols-2 gap-4">
                  <Button variant="outline" className="justify-start h-auto py-4 bg-transparent">
                    <Twitch className="w-5 h-5 mr-2 text-purple-400" />
                    <div className="text-left">
                      <p className="font-semibold">Twitch</p>
                      <p className="text-xs text-muted-foreground">@seucanal</p>
                    </div>
                  </Button>
                  <Button variant="outline" className="justify-start h-auto py-4 bg-transparent">
                    <Youtube className="w-5 h-5 mr-2 text-red-500" />
                    <div className="text-left">
                      <p className="font-semibold">YouTube</p>
                      <p className="text-xs text-muted-foreground">Live Chat</p>
                    </div>
                  </Button>
                </div>
              </div>

              <div className="space-y-2">
                <Label htmlFor="testMessage">Mensagem de Teste</Label>
                <Input id="testMessage" placeholder="Digite uma mensagem..." />
              </div>

              <Button className="w-full" disabled={!streamerBotConnected} onClick={testChatMessage}>
                <Send className="w-4 h-4 mr-2" />
                Enviar Mensagem de Teste
              </Button>

              <div className="space-y-4 mt-6">
                <div className="flex items-center justify-between p-4 bg-muted/30 rounded-lg">
                  <div>
                    <Label>Enviar Detecções no Chat</Label>
                    <p className="text-xs text-muted-foreground mt-1">Mensagens automáticas ao detectar keywords</p>
                  </div>
                  <Switch disabled={!streamerBotConnected} />
                </div>

                <div className="flex items-center justify-between p-4 bg-muted/30 rounded-lg">
                  <div>
                    <Label>Cooldown de Mensagens</Label>
                    <p className="text-xs text-muted-foreground mt-1">Evitar spam (30 segundos)</p>
                  </div>
                  <Switch disabled={!streamerBotConnected} defaultChecked />
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Actions Tab */}
        <TabsContent value="actions" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Ações Automáticas</CardTitle>
              <CardDescription>Keywords vinculadas a ações de streaming</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {keywordActions.map((item) => (
                  <div
                    key={item.id}
                    className="flex items-center gap-4 p-4 bg-muted/30 rounded-lg border border-border"
                  >
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-1">
                        <Badge variant="outline" className="font-mono text-primary border-primary">
                          {item.keyword}
                        </Badge>
                        <Badge variant="secondary">{item.platform}</Badge>
                      </div>
                      <p className="text-sm text-muted-foreground">{item.action}</p>
                    </div>
                    <Switch defaultChecked />
                  </div>
                ))}
              </div>

              <Button variant="outline" className="w-full mt-4 bg-transparent">
                + Adicionar Nova Ação
              </Button>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}
