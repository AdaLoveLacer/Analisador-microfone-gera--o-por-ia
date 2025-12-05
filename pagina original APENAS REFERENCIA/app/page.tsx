"use client"

import { Dashboard } from "@/components/dashboard"
import { Keywords } from "@/components/keywords"
import { SoundLibrary } from "@/components/sound-library"
import { Settings } from "@/components/settings"
import { History } from "@/components/history"
import { Insights } from "@/components/insights"
import { Gamification } from "@/components/gamification"
import { StreamingIntegration } from "@/components/streaming-integration"
import { VoiceCommands } from "@/components/voice-commands"
import { AITraining } from "@/components/ai-training"
import { Sidebar } from "@/components/sidebar"
import { WelcomeModal } from "@/components/welcome-modal"
import { Toaster } from "sonner"
import { useState } from "react"

export default function Page() {
  const [activeTab, setActiveTab] = useState("dashboard")

  return (
    <>
      <div className="flex h-screen overflow-hidden bg-background">
        <Sidebar activeTab={activeTab} onTabChange={setActiveTab} />

        <main className="flex-1 overflow-auto">
          {activeTab === "dashboard" && <Dashboard />}
          {activeTab === "keywords" && <Keywords />}
          {activeTab === "sounds" && <SoundLibrary />}
          {activeTab === "settings" && <Settings />}
          {activeTab === "history" && <History />}
          {activeTab === "insights" && <Insights />}
          {activeTab === "gamification" && <Gamification />}
          {activeTab === "streaming" && <StreamingIntegration />}
          {activeTab === "voice-commands" && <VoiceCommands />}
          {activeTab === "ai-training" && <AITraining />}
        </main>

        <Toaster theme="dark" richColors />
      </div>

      <WelcomeModal />
    </>
  )
}
