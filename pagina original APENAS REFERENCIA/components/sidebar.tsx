"use client"

import { Button } from "@/components/ui/button"
import {
  Mic2,
  KeySquare,
  Music,
  SettingsIcon,
  Clock,
  Sparkles,
  BarChart3,
  Trophy,
  Twitch,
  Mic,
  Brain,
} from "lucide-react"
import { cn } from "@/lib/utils"

interface SidebarProps {
  activeTab: string
  onTabChange: (tab: string) => void
}

export function Sidebar({ activeTab, onTabChange }: SidebarProps) {
  const tabs = [
    { id: "dashboard", label: "Dashboard", icon: Mic2 },
    { id: "keywords", label: "Keywords", icon: KeySquare },
    { id: "sounds", label: "Sounds", icon: Music },
    { id: "insights", label: "Insights", icon: BarChart3 },
    { id: "gamification", label: "Gamification", icon: Trophy },
    { id: "streaming", label: "Streaming", icon: Twitch },
    { id: "voice-commands", label: "Voice Commands", icon: Mic },
    { id: "ai-training", label: "AI Training", icon: Brain },
    { id: "settings", label: "Settings", icon: SettingsIcon },
    { id: "history", label: "History", icon: Clock },
  ]

  return (
    <aside className="w-64 border-r border-border bg-card p-4 flex flex-col gap-4 overflow-y-auto">
      <div className="flex items-center gap-2 px-2 py-4">
        <div className="w-10 h-10 rounded-lg bg-primary/20 flex items-center justify-center glow-primary">
          <Sparkles className="w-6 h-6 text-primary" />
        </div>
        <div>
          <h1 className="text-lg font-bold text-foreground">AI Mic Analyzer</h1>
          <p className="text-xs text-muted-foreground">Soundboard Inteligente</p>
        </div>
      </div>

      <nav className="flex flex-col gap-1">
        {tabs.map((tab) => {
          const Icon = tab.icon
          const isActive = activeTab === tab.id

          return (
            <Button
              key={tab.id}
              variant={isActive ? "default" : "ghost"}
              className={cn("justify-start gap-3 h-11", isActive && "bg-primary text-primary-foreground glow-primary")}
              onClick={() => onTabChange(tab.id)}
            >
              <Icon className="w-4 h-4" />
              {tab.label}
            </Button>
          )
        })}
      </nav>

      <div className="mt-auto p-4 rounded-lg bg-muted/50 border border-border">
        <p className="text-xs text-muted-foreground">Conectado ao servidor local</p>
        <p className="text-xs font-mono text-primary mt-1">localhost:5000</p>
      </div>
    </aside>
  )
}
