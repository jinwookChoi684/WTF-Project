"use client"

import { useEffect, useState } from "react"
import { useRouter, useParams } from "next/navigation"
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"
import { MessageCircle, BookOpen, Gift, Users, Heart, Sparkles, Sun, Coffee } from "lucide-react"

export default function ProloguePage() {
  const router = useRouter()
  const params = useParams()
  const pk = params.pk as string

  const [user, setUser] = useState<any>(null)
  const [currentTime, setCurrentTime] = useState("")

  useEffect(() => {
    const userStr = typeof window !== "undefined" ? localStorage.getItem("user") : null
    if (userStr) {
      const userData = JSON.parse(userStr)
      setUser(userData)
    }

    // Set current time
    const now = new Date()
    const timeString = now.toLocaleTimeString("ko-KR", {
      hour: "2-digit",
      minute: "2-digit",
      hour12: false,
    })
    setCurrentTime(timeString)
  }, [])

  const getGreeting = () => {
    const hour = new Date().getHours()
    if (hour < 12) return "좋은 아침이야!"
    if (hour < 18) return "좋은 오후야!"
    return "좋은 저녁이야!"
  }

  const navigationItems = [
    {
      id: "chat",
      title: "오늘도 고생했어",
      description: "우빵이와 따뜻한 대화를 나눠보세요",
      icon: MessageCircle,
      color: "from-amber-400 to-orange-400",
      bgColor: "bg-amber-50",
      textColor: "text-amber-800",
      route: `/${pk}/chat`,
    },
    {
      id: "diary",
      title: "너를 추억해",
      description: "감정 일기로 하루를 되돌아보세요",
      icon: BookOpen,
      color: "from-orange-400 to-red-400",
      bgColor: "bg-orange-50",
      textColor: "text-orange-800",
      route: `/${pk}/chat/emotion-diary`,
    },
    {
      id: "collection",
      title: "나 보러와",
      description: "귀여운 빵 친구들을 모아보세요",
      icon: Gift,
      color: "from-yellow-400 to-amber-400",
      bgColor: "bg-yellow-50",
      textColor: "text-yellow-800",
      route: `/${pk}/chat/character-collection`,
    },
    {
      id: "community",
      title: "우리 함께해",
      description: "다른 사람들과 경험을 나누어보세요",
      icon: Users,
      color: "from-pink-400 to-rose-400",
      bgColor: "bg-pink-50",
      textColor: "text-pink-800",
      route: `/${pk}/community`,
    },
  ]

  if (!user) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-amber-50 via-orange-50 to-yellow-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-amber-500 mx-auto mb-4"></div>
          <p className="text-gray-600">로딩 중...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-amber-50 via-orange-50 to-yellow-50">
      {/* Header */}
      <div className="relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-r from-amber-200/20 to-orange-200/20"></div>
        <div className="relative px-6 py-8">
          <div className="max-w-4xl mx-auto text-center">
            <div className="flex justify-center mb-6">
              <div className="relative">
                <div className="w-20 h-20 bg-gradient-to-br from-amber-300 to-orange-300 rounded-full flex items-center justify-center shadow-lg">
                  <Heart className="w-10 h-10 text-white" />
                </div>
                <div className="absolute -top-1 -right-1 w-6 h-6 bg-yellow-400 rounded-full flex items-center justify-center animate-pulse">
                  <Sparkles className="w-3 h-3 text-white" />
                </div>
              </div>
            </div>

            <h1 className="text-3xl font-bold text-gray-800 mb-2">{getGreeting()}</h1>
            <p className="text-lg text-gray-600 mb-2">{user.name}님, 오늘 하루는 어떠셨나요?</p>
            <div className="flex items-center justify-center space-x-2 text-sm text-amber-700">
              <Sun className="w-4 h-4" />
              <span>{currentTime}</span>
              <Coffee className="w-4 h-4" />
              <span>따뜻한 시간</span>
            </div>
          </div>
        </div>
      </div>

      {/* Navigation Grid */}
      <div className="max-w-4xl mx-auto px-6 pb-8">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {navigationItems.map((item) => {
            const IconComponent = item.icon
            return (
              <Card
                key={item.id}
                className="group cursor-pointer transition-all duration-300 hover:scale-105 hover:shadow-xl border-0 bg-white/80 backdrop-blur-sm overflow-hidden"
                onClick={() => router.push(item.route)}
              >
                <CardContent className="p-0">
                  <div className={`${item.bgColor} p-6 transition-all duration-300 group-hover:bg-opacity-80`}>
                    <div className="flex items-start space-x-4">
                      <div
                        className={`w-12 h-12 bg-gradient-to-br ${item.color} rounded-xl flex items-center justify-center shadow-lg group-hover:scale-110 transition-transform duration-300`}
                      >
                        <IconComponent className="w-6 h-6 text-white" />
                      </div>
                      <div className="flex-1">
                        <h3 className={`text-lg font-semibold ${item.textColor} mb-2 group-hover:text-opacity-90`}>
                          {item.title}
                        </h3>
                        <p className="text-gray-600 text-sm leading-relaxed group-hover:text-gray-700">
                          {item.description}
                        </p>
                      </div>
                    </div>

                    <div className="mt-4 flex justify-end">
                      <Button
                        size="sm"
                        className={`bg-gradient-to-r ${item.color} hover:shadow-lg text-white border-0 transition-all duration-300 group-hover:scale-105`}
                      >
                        시작하기
                      </Button>
                    </div>
                  </div>
                </CardContent>
              </Card>
            )
          })}
        </div>

        {/* Quick Stats */}
        <div className="mt-8 grid grid-cols-3 gap-4">
          <Card className="bg-white/60 backdrop-blur-sm border-0 shadow-sm">
            <CardContent className="p-4 text-center">
              <div className="text-2xl font-bold text-amber-600">7</div>
              <div className="text-xs text-gray-600">함께한 날</div>
            </CardContent>
          </Card>
          <Card className="bg-white/60 backdrop-blur-sm border-0 shadow-sm">
            <CardContent className="p-4 text-center">
              <div className="text-2xl font-bold text-orange-600">23</div>
              <div className="text-xs text-gray-600">나눈 대화</div>
            </CardContent>
          </Card>
          <Card className="bg-white/60 backdrop-blur-sm border-0 shadow-sm">
            <CardContent className="p-4 text-center">
              <div className="text-2xl font-bold text-yellow-600">5</div>
              <div className="text-xs text-gray-600">모은 친구</div>
            </CardContent>
          </Card>
        </div>

        {/* Daily Quote */}
        <Card className="mt-6 bg-gradient-to-r from-amber-100 to-orange-100 border-amber-200 shadow-lg">
          <CardContent className="p-6 text-center">
            <div className="flex justify-center mb-3">
              <div className="w-8 h-8 bg-amber-300 rounded-full flex items-center justify-center">
                <Heart className="w-4 h-4 text-white" />
              </div>
            </div>
            <p className="text-amber-800 font-medium mb-2">오늘의 따뜻한 한마디</p>
            <p className="text-amber-700 text-sm italic">
              "힘든 하루였지만, 그래도 여기까지 온 너 자신을 칭찬해줘. 내일은 더 좋은 날이 될 거야."
            </p>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
