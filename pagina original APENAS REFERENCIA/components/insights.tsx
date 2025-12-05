"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Badge } from "@/components/ui/badge"
import { BarChart3, TrendingUp, Zap, Calendar } from "lucide-react"
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  LineChart,
  Line,
  PieChart,
  Pie,
  Cell,
} from "recharts"

export function Insights() {
  const topKeywords = [
    { keyword: "explosão", count: 245, trend: "+12%" },
    { keyword: "vitória", count: 189, trend: "+8%" },
    { keyword: "turbo", count: 156, trend: "-3%" },
    { keyword: "épico", count: 134, trend: "+15%" },
    { keyword: "ataque", count: 98, trend: "+5%" },
  ]

  const hourlyData = [
    { hour: "00h", detections: 12 },
    { hour: "04h", detections: 5 },
    { hour: "08h", detections: 45 },
    { hour: "12h", detections: 89 },
    { hour: "16h", detections: 134 },
    { hour: "20h", detections: 156 },
  ]

  const weeklyData = [
    { day: "Seg", detections: 340 },
    { day: "Ter", detections: 420 },
    { day: "Qua", detections: 380 },
    { day: "Qui", detections: 520 },
    { day: "Sex", detections: 680 },
    { day: "Sáb", detections: 890 },
    { day: "Dom", detections: 560 },
  ]

  const categoryData = [
    { name: "Gaming", value: 450, color: "oklch(0.7 0.25 330)" },
    { name: "Celebração", value: 280, color: "oklch(0.75 0.25 150)" },
    { name: "Ação", value: 190, color: "oklch(0.7 0.3 260)" },
    { name: "Outros", value: 80, color: "oklch(0.65 0.2 200)" },
  ]

  const heatmapData = [
    { day: "Seg", "00-06": 5, "06-12": 45, "12-18": 89, "18-24": 67 },
    { day: "Ter", "00-06": 8, "06-12": 52, "12-18": 95, "18-24": 72 },
    { day: "Qua", "00-06": 6, "06-12": 48, "12-18": 87, "18-24": 69 },
    { day: "Qui", "00-06": 12, "06-12": 68, "12-18": 112, "18-24": 89 },
    { day: "Sex", "00-06": 15, "06-12": 78, "12-18": 145, "18-24": 124 },
    { day: "Sáb", "00-06": 28, "06-12": 95, "12-18": 178, "18-24": 156 },
    { day: "Dom", "00-06": 18, "06-12": 72, "12-18": 134, "18-24": 98 },
  ]

  return (
    <div className="p-8 space-y-6">
      <div>
        <h2 className="text-3xl font-bold text-foreground mb-2">Análise e Insights</h2>
        <p className="text-muted-foreground">Estatísticas detalhadas sobre o uso e detecções</p>
      </div>

      {/* Stats Overview */}
      <div className="grid gap-4 md:grid-cols-4">
        <Card className="border-primary/50">
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium text-muted-foreground">Total de Detecções</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-primary">1,247</div>
            <p className="text-xs text-success mt-1 flex items-center gap-1">
              <TrendingUp className="w-3 h-3" />
              +18% esta semana
            </p>
          </CardContent>
        </Card>

        <Card className="border-secondary/50">
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium text-muted-foreground">Média por Hora</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-secondary">23.4</div>
            <p className="text-xs text-success mt-1 flex items-center gap-1">
              <TrendingUp className="w-3 h-3" />
              +5% vs. ontem
            </p>
          </CardContent>
        </Card>

        <Card className="border-accent/50">
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium text-muted-foreground">Keywords Ativas</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-accent">42</div>
            <p className="text-xs text-muted-foreground mt-1">8 mais usadas</p>
          </CardContent>
        </Card>

        <Card className="border-success/50">
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium text-muted-foreground">Taxa de Acerto</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-success">94.2%</div>
            <p className="text-xs text-success mt-1">Confiança média</p>
          </CardContent>
        </Card>
      </div>

      <Tabs defaultValue="trends" className="space-y-4">
        <TabsList>
          <TabsTrigger value="trends">
            <TrendingUp className="w-4 h-4 mr-2" />
            Tendências
          </TabsTrigger>
          <TabsTrigger value="top">
            <BarChart3 className="w-4 h-4 mr-2" />
            Top Keywords
          </TabsTrigger>
          <TabsTrigger value="heatmap">
            <Calendar className="w-4 h-4 mr-2" />
            Heatmap
          </TabsTrigger>
          <TabsTrigger value="categories">
            <Zap className="w-4 h-4 mr-2" />
            Categorias
          </TabsTrigger>
        </TabsList>

        {/* Trends Tab */}
        <TabsContent value="trends" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Detecções ao Longo da Semana</CardTitle>
              <CardDescription>Volume de keywords detectadas por dia</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="h-[300px]">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={weeklyData}>
                    <CartesianGrid strokeDasharray="3 3" stroke="oklch(0.3 0.05 260)" />
                    <XAxis dataKey="day" stroke="oklch(0.6 0.15 260)" />
                    <YAxis stroke="oklch(0.6 0.15 260)" />
                    <Tooltip
                      contentStyle={{
                        backgroundColor: "oklch(0.2 0.05 260)",
                        border: "1px solid oklch(0.4 0.15 260)",
                        borderRadius: "8px",
                      }}
                    />
                    <Line
                      type="monotone"
                      dataKey="detections"
                      stroke="oklch(0.7 0.25 330)"
                      strokeWidth={3}
                      dot={{ fill: "oklch(0.7 0.25 330)", r: 5 }}
                    />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Padrão de Uso por Hora</CardTitle>
              <CardDescription>Horários de pico de atividade</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="h-[300px]">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={hourlyData}>
                    <CartesianGrid strokeDasharray="3 3" stroke="oklch(0.3 0.05 260)" />
                    <XAxis dataKey="hour" stroke="oklch(0.6 0.15 260)" />
                    <YAxis stroke="oklch(0.6 0.15 260)" />
                    <Tooltip
                      contentStyle={{
                        backgroundColor: "oklch(0.2 0.05 260)",
                        border: "1px solid oklch(0.4 0.15 260)",
                        borderRadius: "8px",
                      }}
                    />
                    <Bar dataKey="detections" fill="oklch(0.75 0.25 150)" radius={[8, 8, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Top Keywords Tab */}
        <TabsContent value="top" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Palavras Mais Detectadas</CardTitle>
              <CardDescription>Ranking das keywords mais acionadas</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {topKeywords.map((item, index) => (
                  <div
                    key={item.keyword}
                    className="flex items-center gap-4 p-3 bg-muted/30 rounded-lg border border-border"
                  >
                    <div
                      className={`w-10 h-10 rounded-lg flex items-center justify-center font-bold text-lg ${
                        index === 0
                          ? "bg-primary/20 text-primary"
                          : index === 1
                            ? "bg-secondary/20 text-secondary"
                            : "bg-accent/20 text-accent"
                      }`}
                    >
                      #{index + 1}
                    </div>
                    <div className="flex-1">
                      <p className="font-semibold text-foreground">{item.keyword}</p>
                      <p className="text-sm text-muted-foreground">{item.count} detecções</p>
                    </div>
                    <Badge variant={item.trend.startsWith("+") ? "default" : "secondary"} className="font-mono">
                      {item.trend}
                    </Badge>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Heatmap Tab */}
        <TabsContent value="heatmap" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Mapa de Calor Semanal</CardTitle>
              <CardDescription>Atividade por dia e período do dia</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="overflow-x-auto">
                <div className="inline-block min-w-full">
                  <div className="grid grid-cols-5 gap-2">
                    <div className="font-semibold text-sm text-muted-foreground"></div>
                    <div className="font-semibold text-sm text-center text-muted-foreground">00-06h</div>
                    <div className="font-semibold text-sm text-center text-muted-foreground">06-12h</div>
                    <div className="font-semibold text-sm text-center text-muted-foreground">12-18h</div>
                    <div className="font-semibold text-sm text-center text-muted-foreground">18-24h</div>

                    {heatmapData.map((row) => (
                      <>
                        <div key={`${row.day}-label`} className="font-semibold text-sm text-muted-foreground">
                          {row.day}
                        </div>
                        {["00-06", "06-12", "12-18", "18-24"].map((period) => {
                          const value = row[period as keyof typeof row] as number
                          const intensity = Math.min(value / 200, 1)
                          return (
                            <div
                              key={`${row.day}-${period}`}
                              className="h-16 rounded-lg flex items-center justify-center font-bold text-lg transition-all hover:scale-105 cursor-pointer"
                              style={{
                                backgroundColor: `oklch(${0.4 + intensity * 0.3} ${0.2 + intensity * 0.1} 330 / ${0.3 + intensity * 0.7})`,
                                color: intensity > 0.5 ? "oklch(0.95 0.05 260)" : "oklch(0.7 0.15 260)",
                              }}
                            >
                              {value}
                            </div>
                          )
                        })}
                      </>
                    ))}
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Categories Tab */}
        <TabsContent value="categories" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Distribuição por Categoria</CardTitle>
              <CardDescription>Keywords organizadas por tipo</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="flex flex-col md:flex-row items-center gap-8">
                <div className="h-[300px] w-[300px]">
                  <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                      <Pie
                        data={categoryData}
                        cx="50%"
                        cy="50%"
                        labelLine={false}
                        outerRadius={120}
                        fill="#8884d8"
                        dataKey="value"
                      >
                        {categoryData.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={entry.color} />
                        ))}
                      </Pie>
                      <Tooltip
                        contentStyle={{
                          backgroundColor: "oklch(0.2 0.05 260)",
                          border: "1px solid oklch(0.4 0.15 260)",
                          borderRadius: "8px",
                        }}
                      />
                    </PieChart>
                  </ResponsiveContainer>
                </div>

                <div className="flex-1 space-y-3">
                  {categoryData.map((category) => (
                    <div key={category.name} className="flex items-center gap-4">
                      <div className="w-4 h-4 rounded-full" style={{ backgroundColor: category.color }} />
                      <div className="flex-1">
                        <div className="flex items-center justify-between mb-1">
                          <span className="font-semibold text-foreground">{category.name}</span>
                          <span className="text-sm text-muted-foreground">{category.value} detecções</span>
                        </div>
                        <div className="h-2 bg-muted rounded-full overflow-hidden">
                          <div
                            className="h-full transition-all"
                            style={{
                              width: `${(category.value / 1000) * 100}%`,
                              backgroundColor: category.color,
                            }}
                          />
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}
