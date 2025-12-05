"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import { Trophy, Star, Zap, Target, Award, TrendingUp, Crown, Flame } from "lucide-react"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"

export function Gamification() {
  const achievements = [
    {
      id: 1,
      name: "Primeira Detecção",
      description: "Detectou sua primeira keyword",
      icon: Star,
      unlocked: true,
      rarity: "common",
      date: "2024-01-15",
    },
    {
      id: 2,
      name: "Centenário",
      description: "100 detecções totais",
      icon: Trophy,
      unlocked: true,
      rarity: "rare",
      date: "2024-01-20",
    },
    {
      id: 3,
      name: "Streamer Pro",
      description: "Usou por 10 horas seguidas",
      icon: Flame,
      unlocked: true,
      rarity: "epic",
      date: "2024-01-25",
    },
    {
      id: 4,
      name: "Mestre das Palavras",
      description: "1000 detecções totais",
      icon: Crown,
      unlocked: false,
      rarity: "legendary",
      progress: 742,
      total: 1000,
    },
    {
      id: 5,
      name: "Speedrun",
      description: "10 detecções em 1 minuto",
      icon: Zap,
      unlocked: false,
      rarity: "epic",
      progress: 7,
      total: 10,
    },
    {
      id: 6,
      name: "Precisão Cirúrgica",
      description: "95% de confiança média em 50 detecções",
      icon: Target,
      unlocked: false,
      rarity: "rare",
      progress: 32,
      total: 50,
    },
  ]

  const leaderboard = [
    { rank: 1, keyword: "explosão", count: 245, percentage: 19.6 },
    { rank: 2, keyword: "vitória", count: 189, percentage: 15.2 },
    { rank: 3, keyword: "turbo", count: 156, percentage: 12.5 },
    { rank: 4, keyword: "épico", count: 134, percentage: 10.7 },
    { rank: 5, keyword: "ataque", count: 98, percentage: 7.9 },
    { rank: 6, keyword: "defesa", count: 87, percentage: 7.0 },
    { rank: 7, keyword: "poder", count: 76, percentage: 6.1 },
    { rank: 8, keyword: "combo", count: 65, percentage: 5.2 },
  ]

  const challenges = [
    {
      id: 1,
      name: "Desafio Diário: Detector Rápido",
      description: "Detecte 50 keywords hoje",
      progress: 34,
      total: 50,
      reward: "100 XP + Badge Especial",
      timeLeft: "6h 23m",
    },
    {
      id: 2,
      name: "Desafio Semanal: Variado",
      description: "Use 20 keywords diferentes esta semana",
      progress: 14,
      total: 20,
      reward: "500 XP + Conquista Rara",
      timeLeft: "3d 12h",
    },
    {
      id: 3,
      name: "Desafio Mensal: Mestre",
      description: "1000 detecções este mês",
      progress: 742,
      total: 1000,
      reward: "2000 XP + Título Exclusivo",
      timeLeft: "12d 8h",
    },
  ]

  const rarityColors = {
    common: "text-muted-foreground border-muted-foreground",
    rare: "text-blue-400 border-blue-400",
    epic: "text-purple-400 border-purple-400",
    legendary: "text-yellow-400 border-yellow-400",
  }

  return (
    <div className="p-8 space-y-6">
      <div>
        <h2 className="text-3xl font-bold text-foreground mb-2">Gamificação</h2>
        <p className="text-muted-foreground">Conquistas, desafios e rankings</p>
      </div>

      {/* Player Stats */}
      <div className="grid gap-4 md:grid-cols-4">
        <Card className="border-primary/50">
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium text-muted-foreground">Nível</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-end gap-2">
              <div className="text-4xl font-bold text-primary">24</div>
              <div className="text-lg text-muted-foreground mb-1">Pro</div>
            </div>
            <Progress value={65} className="mt-2 h-2" />
            <p className="text-xs text-muted-foreground mt-1">650/1000 XP até nível 25</p>
          </CardContent>
        </Card>

        <Card className="border-secondary/50">
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium text-muted-foreground">Total de XP</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-4xl font-bold text-secondary">24,650</div>
            <p className="text-xs text-success mt-1 flex items-center gap-1">
              <TrendingUp className="w-3 h-3" />
              +850 esta semana
            </p>
          </CardContent>
        </Card>

        <Card className="border-accent/50">
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium text-muted-foreground">Conquistas</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-4xl font-bold text-accent">23/45</div>
            <p className="text-xs text-muted-foreground mt-1">51% completado</p>
          </CardContent>
        </Card>

        <Card className="border-success/50">
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium text-muted-foreground">Streak</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <Flame className="w-8 h-8 text-success" />
              <div className="text-4xl font-bold text-success">7</div>
            </div>
            <p className="text-xs text-muted-foreground mt-1">dias consecutivos</p>
          </CardContent>
        </Card>
      </div>

      <Tabs defaultValue="achievements" className="space-y-4">
        <TabsList>
          <TabsTrigger value="achievements">
            <Trophy className="w-4 h-4 mr-2" />
            Conquistas
          </TabsTrigger>
          <TabsTrigger value="leaderboard">
            <Award className="w-4 h-4 mr-2" />
            Ranking
          </TabsTrigger>
          <TabsTrigger value="challenges">
            <Target className="w-4 h-4 mr-2" />
            Desafios
          </TabsTrigger>
        </TabsList>

        {/* Achievements Tab */}
        <TabsContent value="achievements" className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2">
            {achievements.map((achievement) => {
              const Icon = achievement.icon
              const colorClass = rarityColors[achievement.rarity as keyof typeof rarityColors]

              return (
                <Card
                  key={achievement.id}
                  className={`border-2 ${achievement.unlocked ? colorClass : "border-muted opacity-60"} transition-all hover:scale-105`}
                >
                  <CardHeader>
                    <div className="flex items-start justify-between">
                      <div
                        className={`w-12 h-12 rounded-lg flex items-center justify-center ${achievement.unlocked ? "bg-primary/20" : "bg-muted/50"}`}
                      >
                        <Icon
                          className={`w-6 h-6 ${achievement.unlocked ? "text-primary" : "text-muted-foreground"}`}
                        />
                      </div>
                      <Badge variant={achievement.unlocked ? "default" : "outline"} className={colorClass}>
                        {achievement.rarity}
                      </Badge>
                    </div>
                    <CardTitle className={achievement.unlocked ? "text-foreground" : "text-muted-foreground"}>
                      {achievement.name}
                    </CardTitle>
                    <CardDescription>{achievement.description}</CardDescription>
                  </CardHeader>
                  <CardContent>
                    {achievement.unlocked ? (
                      <div className="flex items-center gap-2 text-sm text-success">
                        <Star className="w-4 h-4" />
                        Desbloqueado em {achievement.date}
                      </div>
                    ) : (
                      <div className="space-y-2">
                        <div className="flex items-center justify-between text-sm">
                          <span className="text-muted-foreground">Progresso</span>
                          <span className="font-mono text-foreground">
                            {achievement.progress}/{achievement.total}
                          </span>
                        </div>
                        <Progress value={(achievement.progress! / achievement.total!) * 100} className="h-2" />
                      </div>
                    )}
                  </CardContent>
                </Card>
              )
            })}
          </div>
        </TabsContent>

        {/* Leaderboard Tab */}
        <TabsContent value="leaderboard" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Ranking de Keywords</CardTitle>
              <CardDescription>As palavras mais detectadas</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {leaderboard.map((item) => (
                  <div
                    key={item.rank}
                    className={`flex items-center gap-4 p-4 rounded-lg border transition-all hover:border-primary/50 ${
                      item.rank <= 3 ? "bg-primary/5 border-primary/30" : "bg-muted/30 border-border"
                    }`}
                  >
                    <div
                      className={`w-12 h-12 rounded-full flex items-center justify-center font-bold text-xl ${
                        item.rank === 1
                          ? "bg-yellow-500/20 text-yellow-400 border-2 border-yellow-400"
                          : item.rank === 2
                            ? "bg-gray-400/20 text-gray-300 border-2 border-gray-400"
                            : item.rank === 3
                              ? "bg-orange-500/20 text-orange-400 border-2 border-orange-400"
                              : "bg-muted text-muted-foreground"
                      }`}
                    >
                      {item.rank === 1 ? "🥇" : item.rank === 2 ? "🥈" : item.rank === 3 ? "🥉" : item.rank}
                    </div>
                    <div className="flex-1">
                      <p className="font-bold text-lg text-foreground">{item.keyword}</p>
                      <div className="flex items-center gap-4 mt-1">
                        <span className="text-sm text-muted-foreground">{item.count} detecções</span>
                        <span className="text-sm text-primary">{item.percentage}%</span>
                      </div>
                    </div>
                    <div className="w-24">
                      <Progress value={item.percentage * 5} className="h-2" />
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Challenges Tab */}
        <TabsContent value="challenges" className="space-y-4">
          {challenges.map((challenge) => (
            <Card key={challenge.id} className="border-2 border-primary/30">
              <CardHeader>
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <CardTitle>{challenge.name}</CardTitle>
                    <CardDescription className="mt-2">{challenge.description}</CardDescription>
                  </div>
                  <Badge variant="outline" className="text-accent border-accent">
                    {challenge.timeLeft}
                  </Badge>
                </div>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-muted-foreground">Progresso</span>
                    <span className="font-mono text-foreground">
                      {challenge.progress}/{challenge.total}
                    </span>
                  </div>
                  <Progress value={(challenge.progress / challenge.total) * 100} className="h-3" />
                  <p className="text-xs text-muted-foreground">
                    {((challenge.progress / challenge.total) * 100).toFixed(1)}% completo
                  </p>
                </div>
                <div className="flex items-center gap-2 p-3 bg-primary/10 rounded-lg border border-primary/30">
                  <Award className="w-5 h-5 text-primary" />
                  <div>
                    <p className="text-sm font-semibold text-foreground">Recompensa</p>
                    <p className="text-xs text-muted-foreground">{challenge.reward}</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </TabsContent>
      </Tabs>
    </div>
  )
}
