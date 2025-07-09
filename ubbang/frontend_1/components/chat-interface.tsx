"use client"

import { useState, useRef, useEffect } from "react"
import { useUser } from "@/hooks/useUser"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import { Send, Clock } from "lucide-react"
import MessageBubble from "@/components/message-bubble"
import SessionSummary from "@/components/session-summary"

import { useRouter } from "next/navigation"

interface Message {
  id: string
  content: string
  sender: "user" | "ai"
  timestamp: Date
}

interface ChatInterfaceProps {
  initialUserInfo: {
    pk: number
    name: string
    userId: string
    loginMethod: string
    gender: string
    mode: string
    worry: string
    birthDate: string
    age: number
  }
}

export default function ChatInterface({ initialUserInfo }: ChatInterfaceProps) {const router = useRouter()
  const { user } = useUser()
  const ws = useRef<WebSocket | null>(null)

  const [messages, setMessages] = useState<Message[]>([])
  const [inputMessage, setInputMessage] = useState("")
  const [isTyping, setIsTyping] = useState(false)
  const [isUserTyping, setIsUserTyping] = useState(false)
  const [currentScreen, setCurrentScreen] = useState("chat")

  const typingTimeoutRef = useRef<NodeJS.Timeout | null>(null)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLInputElement>(null)
  const hasConnectedOnce = useRef(false)

  const activeUser = user ?? initialUserInfo ?? {}
  const pk = activeUser.pk ?? 0
  const userId = activeUser.userId ?? "anonymous"
  const userName = activeUser.name ?? "사용자"
  const gender = activeUser.gender ?? "female"
  const mode = activeUser.mode ?? "banmal"
  const age = Number(activeUser.age) || 25

  useEffect(() => {
    setMessages([
      {
        id: "1",
        content: `안녕하세요 ${userName}님! 저는 우빵이입니다. 오늘 하루는 어떠셨나요? 편안하게 이야기해 주세요.`,
        sender: "ai",
        timestamp: new Date(),
      },
    ])
  }, [userName])

  useEffect(() => {
    if (!pk || hasConnectedOnce.current) return

    const timeout = setTimeout(() => {
      hasConnectedOnce.current = true
      const wsUrl = `ws://localhost:8000/ws?pk=${pk}&userId=${userId}&mode=${mode}&gender=${gender}&age=${age}&tf=T`
      console.log("📡 WebSocket 연결 URL:", wsUrl)

      if (ws.current) {
        ws.current.close()
        ws.current = null
      }

      const socket = new WebSocket(wsUrl)
      ws.current = socket

      socket.onopen = () => {
        console.log("✅ WebSocket 연결됨")
      }

      socket.onmessage = (event) => {
        const aiMessage: Message = {
          id: Date.now().toString(),
          content: event.data,
          sender: "ai",
          timestamp: new Date(),
        }
        setMessages((prev) => [...prev, aiMessage])
        setIsTyping(false)
      }

      socket.onerror = () => {
        console.log("❌ WebSocket 오류 발생")
        socket.close()
        ws.current = null

        setTimeout(() => {
          console.log("🔁 WebSocket 재연결 시도 중...")
          hasConnectedOnce.current = false
        }, 1000)
      }

      socket.onclose = () => {
        console.log("🔌 WebSocket 종료됨")
        ws.current = null
      }
    }, 300)

    return () => {
      clearTimeout(timeout)
      console.log("🧹 WebSocket cleanup")
      ws.current?.close()
      ws.current = null
    }
  }, [pk, mode, gender, age])

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }, [messages])

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setInputMessage(e.target.value)
    setIsUserTyping(true)

    if (typingTimeoutRef.current) clearTimeout(typingTimeoutRef.current)
    typingTimeoutRef.current = setTimeout(() => {
      setIsUserTyping(false)
    }, 50)
  }

  const handleSendMessage = () => {
    if (!inputMessage.trim() || isUserTyping) return

    const userMessage: Message = {
      id: Date.now().toString(),
      content: inputMessage,
      sender: "user",
      timestamp: new Date(),
    }

    ws.current?.send(inputMessage)
    setMessages((prev) => [...prev, userMessage])
    setInputMessage("")
    setTimeout(() => {
      inputRef.current?.focus()
    }, 50)
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault()
      handleSendMessage()
    }
  }

  return (
    <div className="flex flex-col h-screen bg-gradient-to-br from-amber-50 via-orange-50 to-yellow-50">
      {/* Header */}
        <div className="bg-white/80 backdrop-blur-sm border-b border-gray-200 shadow-sm">
          <div className="flex items-center justify-between p-4">
            <div className="flex items-center space-x-3">
              <img
                src="/images/bread2.png"
                alt="서포터 프로필"
                className="w-10 h-10 rounded-full border-2 border-amber-200 shadow-sm"
              />
              <div>
                <h1 className="text-lg font-semibold text-gray-800">우빵이</h1>
                <p className="text-sm text-gray-500">WhaT's your Feeling</p>
              </div>
            </div>

          <div className="flex justify-center gap-2 px-4 pb-3">
            <Button
              size="sm"
              className="bg-amber-100 hover:bg-amber-200 text-amber-800 border-amber-200"
            > 오늘도 고생했어
            </Button>
            <Button
              size="sm"
              onClick={() => router.push(`/${pk}/chat/emotion-diary`)}
              className="bg-orange-100 hover:bg-orange-200 text-orange-800 border-orange-200"
            >
              너를 추억해
            </Button>
            <Button
              size="sm"
              onClick={() => router.push(`/${pk}/chat/character-collection`)}
              className="bg-yellow-100 hover:bg-yellow-200 text-yellow-800 border-yellow-200"
            > 나 보러와
            </Button>
            <Button
              size="sm"
              onClick={() => router.push(`/${pk}/chat/profile`)}
              className="bg-amber-100 hover:bg-amber-200 text-amber-800 border-amber-200"
            >
              이게 너야
            </Button>
           </div>
          </div>
          </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        <SessionSummary />
        {messages.map((message) => (
          <MessageBubble key={message.id} message={message} />
        ))}
        {isTyping && (
          <div className="flex justify-start items-end space-x-3">
            <img
              src="/images/bread2.png"
              alt="서포터"
              className="w-8 h-8 rounded-full border border-amber-200 shadow-sm"
            />
            <div className="bg-white rounded-2xl px-4 py-3 shadow-sm border border-gray-100 max-w-xs">
              <div className="flex items-center space-x-2">
                <div className="flex space-x-1">
                  <div className="w-2 h-2 bg-amber-400 rounded-full animate-bounce" />
                  <div className="w-2 h-2 bg-amber-400 rounded-full animate-bounce" style={{ animationDelay: "0.1s" }} />
                  <div className="w-2 h-2 bg-amber-400 rounded-full animate-bounce" style={{ animationDelay: "0.2s" }} />
                </div>
                <span className="text-xs text-gray-500 ml-2">작성 중...</span>
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="bg-white/80 backdrop-blur-sm border-t border-gray-200 p-4">
        <div className="flex items-end space-x-3">
          <div className="flex-1">
            <Input
              ref={inputRef}
              value={inputMessage}
              onChange={handleInputChange}
              onKeyPress={handleKeyPress}
              placeholder="너의 이야기를 들려줘"
              className="min-h-[48px] resize-none border-gray-200 focus:border-amber-300 focus:ring-amber-200 rounded-2xl px-4 py-3"
            />
          </div>
          <Button
            onClick={handleSendMessage}
            disabled={!inputMessage.trim() || isTyping || isUserTyping}
            className="h-12 w-12 rounded-full bg-gradient-to-r from-amber-400 to-orange-400 hover:from-amber-500 hover:to-orange-500 shadow-lg transition-all duration-200"
          >
            <Send className="w-5 h-5" />
          </Button>
        </div>
      </div>
    </div>
  )
}
