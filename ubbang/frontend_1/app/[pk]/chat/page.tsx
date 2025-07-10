'use client'

import { useParams } from 'next/navigation'
import dynamic from 'next/dynamic'
import { useEffect, useState } from 'react'

const ChatInterface = dynamic(() => import('@/components/chat-interface'), {
  ssr: false,
})

export default function ChatPage() {
  const { pk } = useParams()
  const [userInfo, setUserInfo] = useState<any | null>(null)

  useEffect(() => {
    const stored = localStorage.getItem("user")
    if (stored) {
      try {
        const user = JSON.parse(stored)

        console.log("🧩 localStorage에서 불러온 user:", user)

        if (user.pk?.toString() === pk) {
          // ✅ age가 undefined일 경우 콘솔 경고
          if (user.age === undefined) {
            console.warn("❗️user.age가 undefined입니다. localStorage 저장 시 누락된 것 같습니다.")
          }
          setUserInfo(user)
        }
      } catch (e) {
        console.error("JSON parsing error:", e)
      }
    }
  }, [pk])

  if (!userInfo) return <div>🔄 불러오는 중...</div>

  return <ChatInterface initialUserInfo={userInfo} />
}
