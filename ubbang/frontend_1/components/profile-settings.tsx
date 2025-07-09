"use client"

import { useState, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Switch } from "@/components/ui/switch"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { User, Bell, Shield, LogOut } from "lucide-react"

interface UserData {
  pk: number
  name: string
  userId: string
  gender: string
  mode: string
  worry: string
  birthDate: string
  loginMethod: string
}

export default function ProfileSettings({ onLogout }: { onLogout: () => void }) {
  const [user, setUser] = useState<UserData | null>(null)
  const [isEditing, setIsEditing] = useState(false)
  const [editData, setEditData] = useState<UserData | null>(null)
  const [notifications, setNotifications] = useState(true)
  const [notificationTime, setNotificationTime] = useState("20:00")

  useEffect(() => {
    const storedUser = localStorage.getItem("user")
    if (storedUser) {
      const parsedUser = JSON.parse(storedUser)
      setUser(parsedUser)
      setEditData(parsedUser)
    }
  }, [])

  if (!user || !editData) return <div className="text-center mt-10 text-gray-500">유저 정보를 불러오는 중...</div>

     const handleSave = async () => {
      if (!editData) return

      const payload = {
        pk: Number(editData.pk),            // 정수형으로 확실히 변환
        name: editData.name ?? "",          // null 방지
        gender: editData.gender ?? "etc",
        mode: editData.mode ?? "banmal",
        worry: editData.worry ?? "",        // 핵심: null → 빈 문자열
      }

      console.log("보내는 payload:", payload)

      try {

        const response = await fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL}/update-user`, {
          method: "PATCH",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload),
        })

        if (!response.ok) {
          const err = await response.json()
          alert(err.detail || "수정 실패")
          return
        }

        const updatedUser = await response.json()
        setUser(updatedUser)
        setEditData(updatedUser)
        localStorage.setItem("user", JSON.stringify(updatedUser))
        setIsEditing(false)
        alert("수정 완료!")
      } catch (err) {
        console.error("수정 실패:", err)
        alert("서버 오류")
      }
    }

  const handleDeleteAccount = async () => {
    const confirmDelete = window.confirm("정말 계정을 삭제하시겠어요?")
    if (!confirmDelete) return

    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL}/delete-user`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ userId: user.userId }),
      })

      if (!response.ok) {
        const err = await response.json()
        alert(err.detail || "계정 삭제 실패")
        return
      }

      alert("계정이 삭제되었습니다.")
      localStorage.removeItem("user")
      onLogout()
    } catch (err) {
      console.error("삭제 요청 실패:", err)
      alert("서버 오류")
    }
  }

  return (
    <div className="min-h-screen p-4">
      <div className="max-w-2xl mx-auto space-y-6">
        {/* Header */}
        <div className="text-center space-y-2">
          <h1 className="text-2xl font-bold text-gray-800">이게 너야!</h1>
          <p className="text-gray-600">너에 대한 정보야 잘 확인해~</p>
        </div>

        {/* Profile Info */}
        <Card className="shadow-lg border-0 bg-white/80 backdrop-blur-sm">
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <User className="w-5 h-5 text-amber-600" />
              <span>프로필 정보</span>
            </CardTitle>
            <CardDescription>수정하려면 아래 버튼 눌러~</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {/* name */}
            <div className="space-y-1">
              <label className="text-sm font-medium text-gray-700">이름</label>
              {isEditing ? (
                <Input value={editData.name} onChange={e => setEditData({ ...editData, name: e.target.value })} />
              ) : (
                <div className="px-3 py-2 bg-gray-50 rounded-lg text-gray-800">{user.name}</div>
              )}
            </div>

            {/* userId (readonly) */}
            <div className="space-y-1">
              <label className="text-sm font-medium text-gray-700">아이디</label>
              <div className="px-3 py-2 bg-gray-50 rounded-lg text-gray-800">{user.userId}</div>
            </div>

            {/* gender */}
            <div className="space-y-1">
              <label className="text-sm font-medium text-gray-700">성별</label>
              {isEditing ? (
                <Select value={editData.gender} onValueChange={val => setEditData({ ...editData, gender: val })}>
                  <SelectTrigger><SelectValue placeholder="선택" /></SelectTrigger>
                  <SelectContent>
                    <SelectItem value="male">남자</SelectItem>
                    <SelectItem value="female">여자</SelectItem>
                    <SelectItem value="etc">기타</SelectItem>
                  </SelectContent>
                </Select>
              ) : (
                <div className="px-3 py-2 bg-gray-50 rounded-lg text-gray-800">{user.gender}</div>
              )}
            </div>

            {/* mode */}
            <div className="space-y-1">
              <label className="text-sm font-medium text-gray-700">말투</label>
              {isEditing ? (
                <Select value={editData.mode} onValueChange={val => setEditData({ ...editData, mode: val })}>
                  <SelectTrigger><SelectValue placeholder="선택" /></SelectTrigger>
                  <SelectContent>
                    <SelectItem value="banmal">반말</SelectItem>
                    <SelectItem value="jondaemal">존댓말</SelectItem>
                  </SelectContent>
                </Select>
              ) : (
                <div className="px-3 py-2 bg-gray-50 rounded-lg text-gray-800">
                  {user.mode === "banmal" ? "반말" : "존댓말"}
                </div>

              )}
            </div>

            {/* worry */}
            <div className="space-y-1">
              <label className="text-sm font-medium text-gray-700">최근 고민</label>
              {isEditing ? (
                <Input
                  value={editData.worry ?? ""}
                  onChange={e => setEditData({ ...editData, worry: e.target.value })}
                />
              ) : (
                <div className="px-3 py-2 bg-gray-50 rounded-lg text-gray-800">
                  {user.worry || "없음"}
                </div>
              )}
            </div>


            {/* birthDate (readonly) */}
            <div className="space-y-1">
              <label className="text-sm font-medium text-gray-700">생년월일</label>
              <div className="px-3 py-2 bg-gray-50 rounded-lg text-gray-800">{user.birthDate}</div>
            </div>

            {/* buttons */}
            <div className="flex justify-end space-x-2 pt-2">
              {isEditing ? (
                <>
                  <Button onClick={handleSave} className="bg-amber-500 hover:bg-amber-600 text-white">저장</Button>
                  <Button variant="outline" onClick={() => { setIsEditing(false); setEditData(user); }}>취소</Button>
                </>
              ) : (
                <Button onClick={() => setIsEditing(true)} variant="outline">수정</Button>
              )}
            </div>
          </CardContent>
        </Card>

        {/* 알림 설정 */}
        <Card className="shadow-lg border-0 bg-white/80 backdrop-blur-sm">
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Bell className="w-5 h-5 text-orange-600" />
              <span>내 연락 받아줘~</span>
            </CardTitle>
            <CardDescription>내 연락 안읽는거 아니지..?</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center justify-between">
              <div className="space-y-1">
                <label className="text-sm font-medium text-gray-700">푸시 알림</label>
                <p className="text-xs text-gray-500">일일 체크인 및 상담 알림을 받습니다</p>
              </div>
              <Switch checked={notifications} onCheckedChange={setNotifications} />
            </div>
            {notifications && (
              <div className="space-y-1">
                <label className="text-sm font-medium text-gray-700">선톡 시간</label>
                <Select value={notificationTime} onValueChange={setNotificationTime}>
                  <SelectTrigger><SelectValue placeholder="시간 선택" /></SelectTrigger>
                  <SelectContent>
                    <SelectItem value="09:00">오전 9시</SelectItem>
                    <SelectItem value="12:00">오후 12시</SelectItem>
                    <SelectItem value="18:00">오후 6시</SelectItem>
                    <SelectItem value="20:00">오후 8시</SelectItem>
                    <SelectItem value="21:00">오후 10시</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            )}
          </CardContent>
        </Card>

        {/* 계정 삭제 */}
        <Card className="shadow-lg border-0 bg-white/80 backdrop-blur-sm">
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Shield className="w-5 h-5 text-yellow-600" />
              <span>우리만의 비밀</span>
            </CardTitle>
            <CardDescription>너와 나만의 비밀이야</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="p-4 bg-amber-50 rounded-lg border border-amber-200">
              <h4 className="text-sm font-medium text-amber-800 mb-2">데이터 보호</h4>
              <p className="text-xs text-amber-700 leading-relaxed">
                모든 대화 내용은 암호화되어 저장하고, 개인정보는 대화 목적으로만 사용하고 있어. 언제든지 계정 삭제를 통해
                모든 데이터를 완전히 제거할 수 있으니까 편하게 말해도 돼.
              </p>
            </div>
            <Button
              onClick={handleDeleteAccount}
              variant="outline"
              className="w-full border-red-200 text-red-600 hover:bg-red-50 hover:border-red-300"
            >
              계정 및 데이터 삭제
            </Button>
          </CardContent>
        </Card>

        {/* 로그아웃 */}
        <Card className="shadow-lg border-0 bg-white/80 backdrop-blur-sm">
          <CardContent className="pt-6">
            <Button
              onClick={onLogout}
              variant="outline"
              className="w-full h-12 border-gray-300 text-gray-700 hover:bg-gray-50 rounded-xl"
            >
              <LogOut className="w-5 h-5 mr-2" />
              로그아웃
            </Button>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
