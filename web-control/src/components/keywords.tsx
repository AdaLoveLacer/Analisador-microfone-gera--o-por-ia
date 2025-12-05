

import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import { Switch } from "@/components/ui/switch"
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
import { Plus, Edit, Trash2, Search, Play, KeySquare } from "lucide-react"
import { useState } from "react"
import { toast } from "sonner"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"

interface Keyword {
  id: number
  name: string
  pattern: string
  variations: string[]
  context: string[]
  sound: string
  weight: number
  active: boolean
}

export function Keywords() {
  const [searchQuery, setSearchQuery] = useState("")
  const [isDialogOpen, setIsDialogOpen] = useState(false)

  const [keywords, setKeywords] = useState<Keyword[]>([
    {
      id: 1,
      name: "Turbo",
      pattern: "turbo",
      variations: ["ativar turbo", "modo turbo", "turbo on"],
      context: ["velocidade", "rápido"],
      sound: "turbo-sound.mp3",
      weight: 0.8,
      active: true,
    },
    {
      id: 2,
      name: "Explosão",
      pattern: "explosão",
      variations: ["boom", "explode", "detonar"],
      context: ["destruição", "impacto"],
      sound: "explosion.mp3",
      weight: 0.9,
      active: true,
    },
    {
      id: 3,
      name: "Vitória",
      pattern: "vitória",
      variations: ["vencedor", "win", "ganhou"],
      context: ["sucesso", "conquista"],
      sound: "victory.mp3",
      weight: 0.7,
      active: false,
    },
  ])

  const filteredKeywords = keywords.filter(
    (kw) =>
      kw.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      kw.pattern.toLowerCase().includes(searchQuery.toLowerCase()),
  )

  const toggleKeyword = (id: number) => {
    setKeywords(keywords.map((kw) => (kw.id === id ? { ...kw, active: !kw.active } : kw)))
    toast.success("Keyword atualizada")
  }

  const deleteKeyword = (id: number) => {
    setKeywords(keywords.filter((kw) => kw.id !== id))
    toast.success("Keyword deletada")
  }

  return (
    <div className="p-8 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold text-foreground mb-2">Palavras-Chave</h2>
          <p className="text-muted-foreground">Gerencie as keywords que acionam efeitos sonoros</p>
        </div>

        <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
          <DialogTrigger asChild>
            <Button size="lg" className="bg-primary hover:bg-primary/90 glow-primary">
              <Plus className="w-4 h-4 mr-2" />
              Nova Palavra-Chave
            </Button>
          </DialogTrigger>
          <DialogContent className="sm:max-w-[500px]">
            <DialogHeader>
              <DialogTitle>Adicionar Palavra-Chave</DialogTitle>
              <DialogDescription>Configure uma nova keyword para detecção</DialogDescription>
            </DialogHeader>
            <div className="space-y-4 py-4">
              <div className="space-y-2">
                <Label htmlFor="name">Nome</Label>
                <Input id="name" placeholder="Ex: Turbo" />
              </div>
              <div className="space-y-2">
                <Label htmlFor="pattern">Padrão</Label>
                <Input id="pattern" placeholder="Ex: turbo" />
              </div>
              <div className="space-y-2">
                <Label htmlFor="variations">Variações (separadas por vírgula)</Label>
                <Input id="variations" placeholder="ativar turbo, modo turbo, turbo on" />
              </div>
              <div className="space-y-2">
                <Label htmlFor="context">Contexto (separadas por vírgula)</Label>
                <Input id="context" placeholder="velocidade, rápido" />
              </div>
              <div className="space-y-2">
                <Label htmlFor="sound">Som Associado</Label>
                <Select>
                  <SelectTrigger>
                    <SelectValue placeholder="Selecione um som" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="turbo">turbo-sound.mp3</SelectItem>
                    <SelectItem value="explosion">explosion.mp3</SelectItem>
                    <SelectItem value="victory">victory.mp3</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-2">
                <Label htmlFor="weight">Peso de Confiança: 0.8</Label>
                <Slider id="weight" defaultValue={[80]} max={100} step={1} />
              </div>
            </div>
            <DialogFooter>
              <Button variant="outline" onClick={() => setIsDialogOpen(false)}>
                Cancelar
              </Button>
              <Button
                onClick={() => {
                  setIsDialogOpen(false)
                  toast.success("Palavra-chave adicionada!")
                }}
              >
                Adicionar
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </div>

      {/* Search */}
      <div className="relative">
        <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-muted-foreground" />
        <Input
          placeholder="Buscar palavras-chave..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="pl-10"
        />
      </div>

      {/* Keywords Table */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <KeySquare className="w-5 h-5 text-primary" />
            Lista de Keywords ({filteredKeywords.length})
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {filteredKeywords.map((keyword) => (
              <div
                key={keyword.id}
                className="p-4 bg-muted/30 rounded-lg border border-border hover:border-primary/50 transition-all"
              >
                <div className="flex items-start justify-between gap-4">
                  <div className="flex-1 space-y-2">
                    <div className="flex items-center gap-3">
                      <h3 className="text-lg font-bold text-foreground">{keyword.name}</h3>
                      <Badge variant={keyword.active ? "default" : "secondary"}>
                        {keyword.active ? "Ativo" : "Inativo"}
                      </Badge>
                    </div>

                    <div className="grid gap-2 text-sm">
                      <div>
                        <span className="text-muted-foreground">Padrão: </span>
                        <code className="text-primary bg-primary/10 px-2 py-0.5 rounded">{keyword.pattern}</code>
                      </div>

                      <div>
                        <span className="text-muted-foreground">Variações: </span>
                        <div className="flex flex-wrap gap-1 mt-1">
                          {keyword.variations.map((variation, i) => (
                            <Badge key={i} variant="outline" className="text-xs">
                              {variation}
                            </Badge>
                          ))}
                        </div>
                      </div>

                      <div>
                        <span className="text-muted-foreground">Contexto: </span>
                        <div className="flex flex-wrap gap-1 mt-1">
                          {keyword.context.map((ctx, i) => (
                            <Badge key={i} variant="outline" className="text-xs border-secondary text-secondary">
                              {ctx}
                            </Badge>
                          ))}
                        </div>
                      </div>

                      <div>
                        <span className="text-muted-foreground">Som: </span>
                        <span className="text-foreground font-mono text-xs">{keyword.sound}</span>
                      </div>

                      <div>
                        <span className="text-muted-foreground">Peso: </span>
                        <span className="text-foreground font-bold">{keyword.weight}</span>
                      </div>
                    </div>
                  </div>

                  <div className="flex flex-col items-end gap-2">
                    <Switch checked={keyword.active} onCheckedChange={() => toggleKeyword(keyword.id)} />

                    <div className="flex gap-1">
                      <Button size="sm" variant="outline" className="h-8 w-8 p-0 bg-transparent">
                        <Play className="w-3 h-3" />
                      </Button>
                      <Button size="sm" variant="outline" className="h-8 w-8 p-0 bg-transparent">
                        <Edit className="w-3 h-3" />
                      </Button>
                      <Button
                        size="sm"
                        variant="outline"
                        className="h-8 w-8 p-0 hover:bg-destructive hover:text-destructive-foreground bg-transparent"
                        onClick={() => deleteKeyword(keyword.id)}
                      >
                        <Trash2 className="w-3 h-3" />
                      </Button>
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
