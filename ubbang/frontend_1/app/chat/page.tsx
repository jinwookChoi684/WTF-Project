// app/chat/page.tsx
"use client"

import dynamic from "next/dynamic"
import { useEffect, useState } from "react"

// ✅ ChatInterface는 dynamic import 필요 (SSR 방지)
const ChatInterface = dynamic(() => import("@/components/chat-interface"), {
  ssr: false,
})

export default function ChatPage() {
  const [initialUserInfo, setInitialUserInfo] = useState(null)

  useEffect(() => {
    const stored = localStorage.getItem("user")
    if (stored) {
      try {
        const user = JSON.parse(stored)
        setInitialUserInfo(user)
      } catch (err) {
        console.warn("❗ 유저 데이터 파싱 실패", err)
      }
    }
  }, [])

  if (!initialUserInfo) return <div>🔄 유저 정보 불러오는 중...</div>

  return <ChatInterface initialUserInfo={initialUserInfo} />
}
