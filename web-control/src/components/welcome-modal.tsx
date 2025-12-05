

import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Sparkles, BarChart3, Trophy, Twitch, Mic, Brain, Zap, X } from "lucide-react"
import { useState } from "react"

export function WelcomeModal() {
  const [open, setOpen] = useState(true)

  const features = [
    {
      icon: BarChart3,
      title: "Insights Avançados",
      description: "Gráficos, heatmaps e análise profunda de uso",
      color: "text-primary",
    },
    {
      icon: Trophy,
      title: "Gamificação",
      description: "Conquistas, ranking e desafios diários",
      color: "text-secondary",
    },
    {
      icon: Twitch,
      title: "Streaming Integration",
      description: "OBS WebSocket e alertas Twitch/YouTube",
      color: "text-accent",
    },
    {
      icon: Mic,
      title: "Voice Commands",
      description: "Controle por voz com macros avançadas",
      color: "text-success",
    },
    {
      icon: Brain,
      title: "AI Training",
      description: "Fine-tuning personalizado com suas gravações",
      color: "text-primary",
    },
    {
      icon: Zap,
      title: "Performance",
      description: "GPU acceleration e cache inteligente",
      color: "text-secondary",
    },
  ]

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogContent className="max-w-3xl max-h-[80vh] overflow-y-auto">
        <DialogHeader>
          <div className="flex items-center justify-between mb-2">
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 rounded-xl bg-primary/20 flex items-center justify-center glow-primary">
                <Sparkles className="w-7 h-7 text-primary" />
              </div>
              <div>
                <DialogTitle className="text-2xl">Bem-vindo ao AI Mic Analyzer!</DialogTitle>
                <Badge variant="outline" className="mt-1">
                  v2.0 - Edição Completa
                </Badge>
              </div>
            </div>
            <Button variant="ghost" size="icon" onClick={() => setOpen(false)}>
              <X className="w-4 h-4" />
            </Button>
          </div>
          <DialogDescription className="text-base">
            Sua interface de soundboard inteligente agora está completa com todas as funcionalidades avançadas!
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-6 py-4">
          <div className="grid gap-4 md:grid-cols-2">
            {features.map((feature) => {
              const Icon = feature.icon
              return (
                <div
                  key={feature.title}
                  className="p-4 bg-muted/30 rounded-lg border border-border hover:border-primary/50 transition-all"
                >
                  <div className="flex items-start gap-3">
                    <div
                      className={`w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center ${feature.color}`}
                    >
                      <Icon className="w-5 h-5" />
                    </div>
                    <div className="flex-1">
                      <h4 className="font-semibold text-foreground mb-1">{feature.title}</h4>
                      <p className="text-sm text-muted-foreground">{feature.description}</p>
                    </div>
                  </div>
                </div>
              )
            })}
          </div>

          <div className="p-4 bg-primary/10 rounded-lg border border-primary/30">
            <h4 className="font-semibold text-foreground mb-2 flex items-center gap-2">
              <Sparkles className="w-4 h-4 text-primary" />
              Novidades desta versão
            </h4>
            <ul className="space-y-1 text-sm text-muted-foreground">
              <li>• Análise de insights com gráficos interativos e heatmap semanal</li>
              <li>• Sistema de gamificação completo com 45+ conquistas</li>
              <li>• Integração nativa com OBS e Streamer.bot</li>
              <li>• Comandos de voz avançados com macros de teclado/mouse</li>
              <li>• Treinamento de IA personalizado com sua voz</li>
              <li>• Otimizações de performance (GPU, cache, low-latency)</li>
            </ul>
          </div>

          <div className="flex items-center gap-3">
            <Button className="flex-1 bg-primary hover:bg-primary/90 glow-primary" onClick={() => setOpen(false)}>
              Começar a Usar
            </Button>
            <Button variant="outline" className="flex-1 bg-transparent" onClick={() => setOpen(false)}>
              Ver Documentação
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  )
}
