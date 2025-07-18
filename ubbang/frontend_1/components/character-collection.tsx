"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"
import { Progress } from "@/components/ui/progress"
import { Gift } from "lucide-react"
import CharacterCard from "@/components/character-card"
import CharacterUnlock from "@/components/character-unlock"

interface Character {
  id: string
  name: string
  description: string
  rarity: "common" | "rare" | "epic" | "legendary"
  imageUrl: string
  unlocked: boolean
  unlockedAt?: Date
  requiredChats: number
  category: "sweet" | "savory" | "special"
}

interface CharacterCollectionProps {
  user: {
    nickname: string
    loginMethod: string
    isAnonymous: boolean
  }
}

export default function CharacterCollection({ user }: CharacterCollectionProps) {
  const [characters, setCharacters] = useState<Character[]>([
    // Sweet Breads
    {
      id: "1",
      name: "소금이",
      description: "버터향 가득 짭짤 소금빵 친구",
      rarity: "common",
      imageUrl: "/images/breads/salt_bread.png",
      unlocked: true,
      unlockedAt: new Date(),
      requiredChats: 1,
      category: "sweet",
    },
    {
      id: "2",
      name: "초코링",
      description: "초콜릿이 가득한 도넛",
      rarity: "common",
      imageUrl: "/images/breads/choco_bread.png",
      unlocked: true,
      unlockedAt: new Date(),
      requiredChats: 3,
      category: "sweet",
    },
    {
      id: "3",
      name: "딸기공주",
      description: "딸기잼이 들어간 특별한 빵",
      rarity: "common",
      imageUrl: "/images/breads/strawberry_bread.png",
      unlocked: true,
      unlockedAt: new Date(),
      requiredChats: 5,
      category: "sweet",
    },
    {
      id: "4",
      name: "초코머핀",
      description: "초코칩이 콕콕 들어있는 달콤하고 부드러운 빵",
      rarity: "common",
      imageUrl: "/images/breads/chocomuffin.png",
      unlocked: true,
      requiredChats: 10,
      category: "sweet",
    },
    {
      id: "5",
      name: "블루베리파이",
      description: "상콤달콤한 블루베리가 듬뿍 들어간 파이",
      rarity: "common",
      imageUrl: "/images/breads/blueberry_pie.png",
      unlocked: true,
      requiredChats: 15,
      category: "sweet",
    },

    // Savory Breads
    {
      id: "6",
      name: "에그타르트",
      description: "부드러운 에그필링이 듬뿍 들어간 타르트",
      rarity: "common",
      imageUrl: "/images/breads/egg_tart.png",
      unlocked: false,
      requiredChats: 2,
      category: "savory",
    },
    {
      id: "7",
      name: "헤이즐넛빵",
      description: "달콤 고소한 헤이즐넛의 풍미가 가득한 빵",
      rarity: "common",
      imageUrl: "/images/breads/hazelnut_bread.png",
      unlocked: false,
      requiredChats: 7,
      category: "savory",
    },
    {
      id: "8",
      name: "레몬마들렌",
      description: "상큼하고 부드러운 레몬향의 마들렌",
      rarity: "common",
      imageUrl: "/images/breads/lemon_bread.png",
      unlocked: true,
      requiredChats: 12,
      category: "savory",
    },

    // Special Breads
    {
      id: "9",
      name: "팬케익",
      description: "겹겹이 쌓인 팬케익과 버터의 조합",
      rarity: "common",
      imageUrl: "/images/breads/pancake.png",
      unlocked: true,
      requiredChats: 30,
      category: "special",
    },
    {
      id: "10",
      name: "치즈빵",
      description: "치즈가 쭉쭉 늘어나는 빵",
      rarity: "common",
      imageUrl: "/images/breads/cheese_bread.png",
      unlocked: true,
      requiredChats: 50,
      category: "special",
    },
{
      id: "11",
      name: "피자빵",
      description: "부드러운 푸딩이 들어간 빵",
      rarity: "common",
      imageUrl: "/images/breads/pizza_bread.png",
      unlocked: false,
      requiredChats: 6,
      category: "sweet",
    },
    {
      id: "12",
      name: "롤케익",
      description: "돌돌 말린 부드러운 식감의 빵",
      rarity: "common",
      imageUrl: "/images/breads/rollcake.png",
      unlocked: false,
      requiredChats: 25,
      category: "sweet",
    },
    {
      id: "13",
      name: "딸기케익",
      description: "상큼한 딸기와 부드러운 생크림의 조합은 실패할 수가 없지",
      rarity: "common",
      imageUrl: "/images/breads/strawberrycake.png",
      unlocked: false,
      requiredChats: 12,
      category: "sweet",
    },
    {
      id: "14",
      name: "카스테라",
      description: "부드럽고 달콤한 카스테라",
      rarity: "common",
      imageUrl: "/images/breads/castella_bread.png",
      unlocked: false,
      requiredChats: 7,
      category: "sweet",
    },
    {
      id: "15",
      name: "핫도그",
      description: "길쭉한 소시지와 머스타트 케찹의 조화. 여기가 바로 뉴욕?",
      rarity: "common",
      imageUrl: "/images/breads/hotdog.png",
      unlocked: false,
      requiredChats: 60,
      category: "sweet",
    },
    {
      id: "16",
      name: "햄버거",
      description: "양상추 위에 순쇠고기 패티 두 장 특별한 소스 양상추 치즈 피클 양파까지",
      rarity: "common",
      imageUrl: "/images/breads/hamburger_bread.png",
      unlocked: false,
      requiredChats: 2,
      category: "savory",
    },
    {
      id: "17",
      name: "허니베어",
      description: "꿀이 뚝뚝 떨어지는 귀여운 곰 모양의 빵",
      rarity: "rare",
      imageUrl: "/images/breads/bear_bread.png",
      unlocked: false,
      requiredChats: 7,
      category: "savory",
    },
    {
      id: "18",
      name: "옥수수빵",
      description: "옥수수가 들어간 달콤 오독 옥수수모양의 빵",
      rarity: "rare",
      imageUrl: "/images/breads/corn_bread.png",
      unlocked: true,
      requiredChats: 12,
      category: "savory",
    },
    {
      id: "19",
      name: "베이컨롤",
      description: "바삭한 베이컨이 들어간 롤",
      rarity: "rare",
      imageUrl: "/images/breads/bacon_bread.png",
      unlocked: false,
      requiredChats: 3,
      category: "savory",
    },
    {
      id: "20",
      name: "후르츠샌드",
      description: "달콤한 여러가지 과일과 생크림 조합의 샌드위치. 피크닉 갈까?",
      rarity: "rare",
      imageUrl: "/images/breads/fruitsand.png",
      unlocked: false,
      requiredChats: 4,
      category: "savory",
    },
    {
      id: "21",
      name: "라임마카롱",
      description: "상큼하고 향긋한 라임 맛의 마카롱",
      rarity: "rare",
      imageUrl: "/images/breads/lime_macaron.png",
      unlocked: false,
      requiredChats: 5,
      category: "savory",
    },
    {
      id: "22",
      name: "바닐라 킹",
      description: "이렇게 큰 바닐라 슈 보신적 있으십니까?? 얼려먹어도 맛있는 바닐라 슈",
      rarity: "rare",
      imageUrl: "/images/breads/vanila_bread.png",
      unlocked: false,
      requiredChats: 9,
      category: "savory",
    },
    {
      id: "23",
      name: "바게트빵",
      description: "길쭉한 바게트빵 들고 마틸다 따라해보기.. 어떠신가요?",
      rarity: "rare",
      imageUrl: "/images/breads/baugette.png",
      unlocked: false,
      requiredChats: 11,
      category: "savory",
    },
    {
      id: "24",
      name: "푸딩",
      description: "상콤하고 달콤한 푸딩! 먹지마세요. 피부에 양보하세요.",
      rarity: "rare",
      imageUrl: "/images/breads/pudding.png",
      unlocked: false,
      requiredChats: 6,
      category: "savory",
    },
    {
      id: "25",
      name: "야채고로케",
      description: "야~! 그거 고로케 하는거 아니야~! 야채고로케",
      rarity: "rare",
      imageUrl: "/images/breads/croquette.png",
      unlocked: false,
      requiredChats: 18,
      category: "savory",
    },
    {
      id: "26",
      name: "아이스크림 와플",
      description: "부드러운 아이스크림과.. 와플의 조합.. 와플대학 전액장확생 노려봅니다.",
      rarity: "rare",
      imageUrl: "/images/breads/waffle.png",
      unlocked: false,
      requiredChats: 22,
      category: "savory",
    },
    {
      id: "27",
      name: "휘낭시에",
      description: "겉바속쫀의 대명사... 휘낭시에",
      rarity: "rare",
      imageUrl: "/images/breads/financier.png",
      unlocked: false,
      requiredChats: 40,
      category: "savory",
    },
    {
      id: "28",
      name: "민트초코쿠키",
      description: "민트와 초코의 조합! 난 치약맛이 아니라구!",
      rarity: "rare",
      imageUrl: "/images/breads/mintchoco.png",
      unlocked: false,
      requiredChats: 45,
      category: "savory",
    },
    {
      id: "29",
      name: "공주빵",
      description: "queen never cry... but i'm a princess",
      rarity: "epic",
      imageUrl: "/images/breads/princess.png",
      unlocked: false,
      requiredChats: 55,
      category: "savory",
    },
    {
      id: "30",
      name: "왕자빵",
      description: "알 유 프린스쏭? 예아~!",
      rarity: "epic",
      imageUrl: "/images/breads/prince.png",
      unlocked: true,
      requiredChats: 70,
      category: "savory",
    },
    {
      id: "31",
      name: "무지개빵",
      description: "7가지 색깔의 신비한 빵",
      rarity: "epic",
      imageUrl: "/images/breads/rainbow_bread.png",
      unlocked: true,
      requiredChats: 30,
      category: "special",
    },
    {
      id: "32",
      name: "별빛빵",
      description: "별처럼 반짝이는 마법의 빵",
      rarity: "epic",
      imageUrl: "/images/breads/star_bread.png",
      unlocked: true,
      requiredChats: 50,
      category: "special",
    },
    {
      id: "33",
      name: "솜사탕빵",
      description: "후후 불면은... 구멍이 생기는 커다란 솜!사!탕!",
      rarity: "epic",
      imageUrl: "/images/breads/cottoncandy.png",
      unlocked: false,
      requiredChats: 35,
      category: "special",
    },
    {
      id: "34",
      name: "고양이빵",
      description: "거미로 그물쳐서 물고기 잡으러~!!! 나는.. 낭만고양이",
      rarity: "epic",
      imageUrl: "/images/breads/cat.png",
      unlocked: true,
      requiredChats: 65,
      category: "special",
    },
    {
      id: "35",
      name: "트리쿠키",
      description: "연말의 포근한 분위기까지 그대로 담은 크리스마스 트리모양의 쿠키",
      rarity: "epic",
      imageUrl: "/images/breads/cristmastree_cookie.png",
      unlocked: false,
      requiredChats: 28,
      category: "special",
    },
    {
      id: "36",
      name: "태양빵",
      description: "너의 눈,코,입~ 그 태양 아닙니다. 온 세상을 밝혀주는 태양빵",
      rarity: "epic",
      imageUrl: "/images/breads/sun.png",
      unlocked: false,
      requiredChats: 32,
      category: "special",
    },
    {
      id: "37",
      name: "용가리빵",
      description: "라떼는... 내가 이 세계 짱 이였다 이거야! 크아아아앙",
      rarity: "legendary",
      imageUrl: "/images/breads/legend_dragon_bread.png",
      unlocked: true,
      requiredChats: 38,
      category: "special",
    },
    {
      id: "38",
      name: "달토끼빵",
      description: "달에서 열심히 떡을 만들고 있는 달토끼입니다.",
      rarity: "legendary",
      imageUrl: "/images/breads/legend_moonrabbit.png",
      unlocked: true,
      requiredChats: 75,
      category: "special",
    },
    {
      id: "39",
      name: "티벳여우빵",
      description: "묘하게 생신 티벳 여우입니다. 새앙토끼의 천적이죠.",
      rarity: "legendary",
      imageUrl: "/images/breads/dayeon.png",
      unlocked: true,
      requiredChats: 80,
      category: "special",
    },
    {
      id: "40",
      name: "비숑빵",
      description: "구름? 아닙니다. 술떡? 아닙니다. 검은콩 3개 박힌 듯한.. 귀여운 강쥐.. 비숑이지요",
      rarity: "legendary",
      imageUrl: "/images/breads/minkyu.png",
      unlocked: true,
      requiredChats: 100,
      category: "special",
    },
  ])

  const [selectedCategory, setSelectedCategory] = useState<"all" | "sweet" | "savory" | "special">("all")
  const [showUnlock, setShowUnlock] = useState<Character | null>(null)
  const [userStats, setUserStats] = useState({
    totalChats: 8,
    unlockedCount: characters.filter((c) => c.unlocked).length,
    totalCharacters: 40,
  })

  const filteredCharacters = characters.filter(
    (char) => selectedCategory === "all" || char.category === selectedCategory,
  )

  const getRarityColor = (rarity: string) => {
    switch (rarity) {
      case "common":
        return "bg-gray-100 text-gray-800"
      case "rare":
        return "bg-blue-100 text-blue-800"
      case "epic":
        return "bg-purple-100 text-purple-800"
      case "legendary":
        return "bg-yellow-100 text-yellow-800"
      default:
        return "bg-gray-100 text-gray-800"
    }
  }

  const getRarityLabel = (rarity: string) => {
    switch (rarity) {
      case "common":
        return "일반"
      case "rare":
        return "레어"
      case "epic":
        return "에픽"
      case "legendary":
        return "전설"
      default:
        return "일반"
    }
  }

  const getCategoryLabel = (category: string) => {
    switch (category) {
      case "sweet":
        return "달콤한 빵"
      case "savory":
        return "고소한 빵"
      case "special":
        return "특별한 빵"
      default:
        return "전체"
    }
  }

  const handleCharacterClick = (character: Character) => {
    if (!character.unlocked && userStats.totalChats >= character.requiredChats) {
      // Unlock character
      const updatedCharacters = characters.map((char) =>
        char.id === character.id ? { ...char, unlocked: true, unlockedAt: new Date() } : char,
      )
      setCharacters(updatedCharacters)
      setUserStats((prev) => ({ ...prev, unlockedCount: prev.unlockedCount + 1 }))
      setShowUnlock(character)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-amber-50 via-orange-50 to-yellow-50 p-4">
      <div className="max-w-6xl mx-auto space-y-6">
        {/* Header */}
        <div className="text-center space-y-4">
          <div className="flex justify-center">
            <div className="w-16 h-16 bg-gradient-to-br from-yellow-200 to-orange-200 rounded-full flex items-center justify-center shadow-lg">
              <Gift className="w-8 h-8 text-yellow-600" />
            </div>
          </div>
          <div>
            <h1 className="text-3xl font-bold text-gray-800 mb-2">빵 캐릭터 컬렉션</h1>
            <p className="text-gray-600">대화를 통해 다양한 빵 친구들을 모아보세요!</p>
          </div>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <Card className="bg-white/80 backdrop-blur-sm border-0 shadow-lg">
            <CardContent className="p-4 text-center">
              <div className="text-2xl font-bold text-amber-600">{userStats.unlockedCount}</div>
              <div className="text-sm text-gray-600">수집한 캐릭터</div>
              <Progress value={(userStats.unlockedCount / userStats.totalCharacters) * 100} className="mt-2" />
            </CardContent>
          </Card>
          <Card className="bg-white/80 backdrop-blur-sm border-0 shadow-lg">
            <CardContent className="p-4 text-center">
              <div className="text-2xl font-bold text-orange-600">{userStats.totalChats}</div>
              <div className="text-sm text-gray-600">총 대화 수</div>
            </CardContent>
          </Card>
          <Card className="bg-white/80 backdrop-blur-sm border-0 shadow-lg">
            <CardContent className="p-4 text-center">
              <div className="text-2xl font-bold text-yellow-600">
                {Math.round((userStats.unlockedCount / userStats.totalCharacters) * 100)}%
              </div>
              <div className="text-sm text-gray-600">수집 완성도</div>
            </CardContent>
          </Card>
        </div>

        {/* Category Filter */}
        <Card className="bg-white/80 backdrop-blur-sm border-0 shadow-lg">
          <CardContent className="p-4">
            <div className="flex flex-wrap gap-2">
              {["all", "sweet", "savory", "special"].map((category) => (
                <Button
                  key={category}
                  variant={selectedCategory === category ? "default" : "outline"}
                  size="sm"
                  onClick={() => setSelectedCategory(category as any)}
                  className={
                    selectedCategory === category
                      ? "bg-gradient-to-r from-amber-400 to-orange-400 text-white"
                      : "border-gray-300"
                  }
                >
                  {getCategoryLabel(category)}
                </Button>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Character Grid */}
        <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-5 gap-4">
          {filteredCharacters.map((character) => (
            <CharacterCard
              key={character.id}
              character={character}
              userChats={userStats.totalChats}
              onClick={() => handleCharacterClick(character)}
            />
          ))}
        </div>

        {/* Unlock Modal */}
        {showUnlock && <CharacterUnlock character={showUnlock} onClose={() => setShowUnlock(null)} />}
      </div>
    </div>
  )
}
