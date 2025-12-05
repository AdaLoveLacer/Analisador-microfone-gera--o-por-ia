"use client"

import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog"
import { Label } from "@/components/ui/label"
import { Slider } from "@/components/ui/slider"
import { Upload, Play, Edit, Trash2, Volume2, Music } from "lucide-react"
import { useState } from "react"
import { toast } from "sonner"

interface Sound {
  id: number
  name: string
  filename: string
  duration: string
  volume: number
  category: string
}

export function SoundLibrary() {
  const [sounds, setSounds] = useState<Sound[]>([
    {
      id: 1,
      name: "Turbo Sound",
      filename: "turbo-sound.mp3",
      duration: "2.3s",
      volume: 80,
      category: "Efeitos",
    },
    {
      id: 2,
      name: "Explosão",
      filename: "explosion.mp3",
      duration: "1.8s",
      volume: 90,
      category: "Impacto",
    },
    {
      id: 3,
      name: "Victory",
      filename: "victory.mp3",
      duration: "3.2s",
      volume: 75,
      category: "Celebração",
    },
    {
      id: 4,
      name: "Laser Blast",
      filename: "laser.mp3",
      duration: "0.8s",
      volume: 85,
      category: "Efeitos",
    },
  ])

  const deleteSound = (id: number) => {
    setSounds(sounds.filter((sound) => sound.id !== id))
    toast.success("Som deletado")
  }

  const playSound = (name: string) => {
    toast.success(`Reproduzindo: ${name}`)
  }

  return (
    <div className="p-8 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold text-foreground mb-2">Biblioteca de Sons</h2>
          <p className="text-muted-foreground">Gerencie seus efeitos sonoros</p>
        </div>

        <Dialog>
          <DialogTrigger asChild>
            <Button size="lg" className="bg-primary hover:bg-primary/90 glow-primary">
              <Upload className="w-4 h-4 mr-2" />
              Upload de Som
            </Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Upload de Som</DialogTitle>
              <DialogDescription>Adicione um novo efeito sonoro à sua biblioteca</DialogDescription>
            </DialogHeader>
            <div className="space-y-4 py-4">
              <div className="space-y-2">
                <Label htmlFor="file">Arquivo de Áudio</Label>
                <Input id="file" type="file" accept="audio/*" />
              </div>
              <div className="space-y-2">
                <Label htmlFor="soundName">Nome</Label>
                <Input id="soundName" placeholder="Ex: Laser Sound" />
              </div>
              <div className="space-y-2">
                <Label htmlFor="category">Categoria</Label>
                <Input id="category" placeholder="Ex: Efeitos" />
              </div>
              <div className="space-y-2">
                <Label htmlFor="volume">Volume: 80%</Label>
                <Slider id="volume" defaultValue={[80]} max={100} step={1} />
              </div>
            </div>
            <DialogFooter>
              <Button variant="outline">Cancelar</Button>
              <Button onClick={() => toast.success("Som adicionado!")}>Upload</Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </div>

      {/* Upload Zone */}
      <Card className="border-2 border-dashed border-border hover:border-primary/50 transition-colors">
        <CardContent className="p-12">
          <div className="flex flex-col items-center justify-center text-center space-y-4">
            <div className="w-16 h-16 rounded-full bg-primary/20 flex items-center justify-center">
              <Upload className="w-8 h-8 text-primary" />
            </div>
            <div>
              <h3 className="text-lg font-semibold text-foreground mb-1">Arraste arquivos aqui</h3>
              <p className="text-sm text-muted-foreground">ou clique para selecionar (MP3, WAV, OGG)</p>
            </div>
            <Button variant="outline">Selecionar Arquivos</Button>
          </div>
        </CardContent>
      </Card>

      {/* Sounds Grid */}
      <div>
        <h3 className="text-xl font-bold text-foreground mb-4 flex items-center gap-2">
          <Music className="w-5 h-5 text-accent" />
          Seus Sons ({sounds.length})
        </h3>

        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {sounds.map((sound) => (
            <Card key={sound.id} className="border-2 border-border hover:border-primary/50 transition-all">
              <CardHeader className="pb-3">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <CardTitle className="text-base">{sound.name}</CardTitle>
                    <CardDescription className="text-xs mt-1">{sound.filename}</CardDescription>
                  </div>
                  <Badge variant="outline" className="text-xs">
                    {sound.category}
                  </Badge>
                </div>
              </CardHeader>
              <CardContent className="space-y-3">
                {/* Waveform Placeholder */}
                <div className="h-16 bg-muted/30 rounded-lg border border-border flex items-center justify-center">
                  <div className="flex items-end gap-0.5 h-12">
                    {Array.from({ length: 40 }).map((_, i) => (
                      <div
                        key={i}
                        className="w-1 bg-primary rounded-full"
                        style={{
                          height: `${Math.random() * 100}%`,
                          opacity: 0.3 + Math.random() * 0.7,
                        }}
                      />
                    ))}
                  </div>
                </div>

                <div className="flex items-center justify-between text-xs">
                  <span className="text-muted-foreground">Duração</span>
                  <span className="text-foreground font-mono">{sound.duration}</span>
                </div>

                <div className="space-y-1">
                  <div className="flex items-center justify-between text-xs">
                    <span className="text-muted-foreground flex items-center gap-1">
                      <Volume2 className="w-3 h-3" />
                      Volume
                    </span>
                    <span className="text-foreground font-mono">{sound.volume}%</span>
                  </div>
                  <Slider value={[sound.volume]} max={100} className="h-1" />
                </div>

                <div className="flex gap-2 pt-2">
                  <Button
                    size="sm"
                    className="flex-1 bg-primary hover:bg-primary/90"
                    onClick={() => playSound(sound.name)}
                  >
                    <Play className="w-3 h-3 mr-1" />
                    Play
                  </Button>
                  <Button size="sm" variant="outline" className="w-9 p-0 bg-transparent">
                    <Edit className="w-3 h-3" />
                  </Button>
                  <Button
                    size="sm"
                    variant="outline"
                    className="w-9 p-0 hover:bg-destructive hover:text-destructive-foreground bg-transparent"
                    onClick={() => deleteSound(sound.id)}
                  >
                    <Trash2 className="w-3 h-3" />
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    </div>
  )
}
