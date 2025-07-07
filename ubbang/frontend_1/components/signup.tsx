"use client"

import { useState } from "react"
import { useRouter } from "next/navigation"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { ArrowLeft, User, Mail, Lock, Calendar, MessageCircle, Heart } from "lucide-react"
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover"
import { Calendar as CalendarIcon } from "lucide-react"
import { Calendar as DatePicker } from "@/components/ui/calendar"

export default function Signup() {
  const router = useRouter()
  const [formData, setFormData] = useState({
    name: "",
    userId: "",
    password: "",
    confirmPassword: "",
    email: "",
    socialId: "",
    age: "",
    gender: "",
    worry: "",
    birthDate: "",
    mode: "",
    currentConcern: "",
  })

  const [errors, setErrors] = useState<Record<string, string>>({})
  const [step, setStep] = useState<"form" | "submitting" | "complete">("form")

  const handleInputChange = (field: string, value: string) => {
    setFormData((prev) => ({ ...prev, [field]: value }))
    if (errors[field]) {
      setErrors((prev) => ({ ...prev, [field]: "" }))
    }
  }

  const validateForm = () => {
    const newErrors: Record<string, string> = {}

    if (!formData.userId.trim()) newErrors.userId = "아이디를 입력해주세요"
    else if (formData.userId.length < 4) newErrors.userId = "아이디는 4자 이상이어야 합니다"

    if (!formData.password.trim()) newErrors.password = "비밀번호를 입력해주세요"
    else if (formData.password.length < 6) newErrors.password = "비밀번호는 6자 이상이어야 합니다"

    if (formData.password !== formData.confirmPassword) {
      newErrors.confirmPassword = "비밀번호가 일치하지 않습니다"
    }

    if (!formData.email.trim()) newErrors.email = "이메일을 입력해주세요"
    else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
      newErrors.email = "올바른 이메일 형식이 아닙니다"
    }

    if (!formData.age) newErrors.age = "나이를 선택해주세요"
    if (!formData.mode) newErrors.mode = "말투를 선택해주세요"
    if (!formData.gender) newErrors.gender = "성별을 선택해주세요"

    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleSubmit = async () => {
    if (!validateForm()) return

    setStep("submitting")

    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL}/users/signup`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          name: formData.name,
          userId: formData.userId,
          password: formData.password,
          email: formData.email,
          gender: formData.gender,
          birthDate: formData.birthDate,
          socialId: formData.socialId || null,
          mode: formData.mode,
          worry: formData.currentConcern || null,
          age: Number(formData.age),
        }),
      })

      if (response.ok) {
        const data = await response.json()

        const localStorageUserData = {
          pk: data.pk,
          userId: data.userId,
          name: data.name,
          gender: data.gender,
          mode: data.mode,
          worry: data.worry,
          birthDate: data.birthDate,
          loginMethod: "이메일 계정",
        }

        localStorage.setItem("user", JSON.stringify(localStorageUserData))
        setStep("complete")

        setTimeout(() => {
          router.push("/chat")
        }, 1500)
      } else {
        const text = await response.text()
        console.error("❌ 회원가입 실패:", text)
        alert("회원가입 중 오류가 발생했습니다.")
        setStep("form")
      }
    } catch (error) {
      console.error("❌ 서버 연결 실패:", error)
      alert("서버에 연결할 수 없습니다.")
      setStep("form")
    }
  }

  const generateAgeOptions = () => {
    const options = []
    for (let i = 13; i <= 80; i++) {
      options.push(
        <SelectItem key={i} value={i.toString()}>
          {i}세
        </SelectItem>
      )
    }
    return options
  }

  return (
    <div className="min-h-screen flex items-center justify-center p-4 bg-gradient-to-br from-amber-50 via-orange-50 to-yellow-50">
      <div className="w-full max-w-md space-y-6">
        <div className="flex items-center space-x-4">
          <Button variant="ghost" size="sm" onClick={() => router.push("/")} className="text-gray-600 hover:text-gray-800">
            <ArrowLeft className="w-4 h-4 mr-2" />
            돌아가기
          </Button>
        </div>

        {/* 이후 UI 구성은 기존과 동일하게 유지 */}
        {step === "form" && (
          <>
            <div className="text-center space-y-4">
              <div className="flex justify-center">
                <div className="w-16 h-16 bg-gradient-to-br from-amber-200 to-orange-200 rounded-full flex items-center justify-center shadow-lg">
                  <User className="w-8 h-8 text-amber-600" />
                </div>
              </div>
              <div>
                <h1 className="text-2xl font-bold text-gray-800 mb-2">회원가입</h1>
                <p className="text-gray-600">우빵이와 함께 시작해보세요</p>
              </div>
            </div>

            <Card className="shadow-xl border-0 bg-white/80 backdrop-blur-sm">
              <CardHeader className="text-center pb-4">
                <CardTitle className="text-lg text-gray-800">계정 정보</CardTitle>
                <CardDescription className="text-gray-600">안전하고 개인화된 상담을 위한 정보입니다</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">

                {/* User Name */}
                <div className="space-y-1">
                  <label className="text-sm font-medium text-gray-700 flex items-center">
                    <User className="w-4 h-4 mr-2 text-amber-600" />
                    이름
                  </label>
                  <Input
                    autoComplete="off"
                    value={formData.name}
                    onChange={(e) => handleInputChange("name", e.target.value)}
                    placeholder="사용할 이름을 입력하세요"
                    className={`h-12 border-gray-200 focus:border-amber-300 focus:ring-amber-200 rounded-xl ${
                      errors.name ? "border-red-300" : ""
                    }`}
                  />
                  {errors.name && <p className="text-xs text-red-600">{errors.name}</p>}
                </div>


                {/* User ID */}
                {/* 아이디 입력 */}
                <div className="space-y-1">
                  <label className="text-sm font-medium text-gray-700 flex items-center">
                    <User className="w-4 h-4 mr-2 text-amber-600" />
                    아이디
                  </label>
                  <Input
                    type="text"
                    name="username"
                    autoComplete="off"
                    value={formData.userId}
                    onChange={(e) => handleInputChange("userId", e.target.value)}
                    placeholder="사용할 아이디를 입력하세요"
                    className={`h-12 border-gray-200 focus:border-amber-300 focus:ring-amber-200 rounded-xl ${
                      errors.userId ? "border-red-300" : ""
                    }`}
                  />
                  {errors.userId && <p className="text-xs text-red-600 mt-1">{errors.userId}</p>}
                </div>

                {/* 비밀번호 입력 */}
                <div className="space-y-1">
                  <label className="text-sm font-medium text-gray-700 flex items-center">
                    <Lock className="w-4 h-4 mr-2 text-amber-600" />
                    비밀번호
                  </label>
                  <Input
                    type="password"
                    name="password"
                    autoComplete="new-password"
                    value={formData.password}
                    onChange={(e) => handleInputChange("password", e.target.value)}
                    placeholder="6자 이상의 비밀번호"
                    className={`h-12 border-gray-200 focus:border-amber-300 focus:ring-amber-200 rounded-xl ${
                      errors.password ? "border-red-300" : ""
                    }`}
                  />
                  {errors.password && <p className="text-xs text-red-600 mt-1">{errors.password}</p>}
                </div>

                {/* Confirm Password */}
                <div className="space-y-1">
                  <label className="text-sm font-medium text-gray-700 flex items-center">
                    <Lock className="w-4 h-4 mr-2 text-amber-600" />
                    비밀번호 확인
                  </label>
                  <Input
                    autoComplete="off"
                    type="password"
                    value={formData.confirmPassword}
                    onChange={(e) => handleInputChange("confirmPassword", e.target.value)}
                    placeholder="비밀번호를 다시 입력하세요"
                    className={`h-12 border-gray-200 focus:border-amber-300 focus:ring-amber-200 rounded-xl ${
                      errors.confirmPassword ? "border-red-300" : ""
                    }`}
                  />
                  {errors.confirmPassword && <p className="text-xs text-red-600">{errors.confirmPassword}</p>}
                </div>

                {/* Email */}
                <div className="space-y-1">
                  <label className="text-sm font-medium text-gray-700 flex items-center">
                    <Mail className="w-4 h-4 mr-2 text-amber-600" />
                    이메일 주소
                  </label>
                  <Input
                    autoComplete="off"
                    type="email"
                    value={formData.email}
                    onChange={(e) => handleInputChange("email", e.target.value)}
                    placeholder="example@email.com"
                    className={`h-12 border-gray-200 focus:border-amber-300 focus:ring-amber-200 rounded-xl ${
                      errors.email ? "border-red-300" : ""
                    }`}
                  />
                  {errors.email && <p className="text-xs text-red-600">{errors.email}</p>}
                </div>

                {/* Social ID (Optional) */}
                <div className="space-y-1">
                  <label className="text-sm font-medium text-gray-700 flex items-center">
                    <MessageCircle className="w-4 h-4 mr-2 text-amber-600" />
                    소셜 계정 ID (선택사항)
                  </label>
                  <Input
                    value={formData.socialId}
                    onChange={(e) => handleInputChange("socialId", e.target.value)}
                    placeholder="카카오톡, 네이버 등의 계정 ID"
                    className="h-12 border-gray-200 focus:border-amber-300 focus:ring-amber-200 rounded-xl"
                  />
                </div>

                {/* 생년월일 */}
                <div className="space-y-1">
                  <label className="text-sm font-medium text-gray-700 flex items-center">
                    <CalendarIcon className="w-4 h-4 mr-2 text-amber-600" />
                    생년월일
                  </label>
                  <Popover>
                    <PopoverTrigger asChild>
                      <Button
                        variant="outline"
                        className={`w-full justify-start text-left h-12 border-gray-200 rounded-xl ${
                          errors.birthDate ? "border-red-300" : ""
                        }`}
                      >
                        {formData.birthDate ? formData.birthDate : "생년월일을 선택해주세요"}
                      </Button>
                    </PopoverTrigger>
                    <PopoverContent>
                      <DatePicker
                        mode="single"
                        captionLayout="dropdown"
                        fromYear={1940}
                        toYear={2020}
                        onSelect={(date: Date | undefined) => {
                          if (date) {
                            handleInputChange("birthDate", date.toISOString().split("T")[0])
                          }
                        }}
                      />
                    </PopoverContent>
                  </Popover>
                  {errors.birthDate && <p className="text-xs text-red-600">{errors.birthDate}</p>}
                </div>

                {/* Age Selection */}
                <div className="space-y-2">
                  <label className="text-sm font-medium text-gray-700 flex items-center">
                    <Calendar className="w-4 h-4 mr-2 text-amber-600" />
                    나이
                  </label>
                  <Select value={formData.age} onValueChange={(value) => handleInputChange("age", value)}>
                    <SelectTrigger className="h-12 border-gray-200 focus:border-amber-300 focus:ring-amber-200 rounded-xl">
                      <SelectValue placeholder="나이를 선택해주세요" />
                    </SelectTrigger>
                    <SelectContent className="max-h-60">{generateAgeOptions()}</SelectContent>
                  </Select>
                </div>

                {/* 성별 */}
                <div className="space-y-1">
                  <label className="text-sm font-medium text-gray-700 flex items-center">
                    <User className="w-4 h-4 mr-2 text-amber-600" />
                    성별
                  </label>
                  <Select value={formData.gender} onValueChange={(value) => handleInputChange("gender", value)}>
                    <SelectTrigger
                      className={`h-12 border-gray-200 focus:border-amber-300 focus:ring-amber-200 rounded-xl ${
                        errors.gender ? "border-red-300" : ""
                      }`}
                    >
                      <SelectValue placeholder="성별을 선택해주세요" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="male">남성</SelectItem>
                      <SelectItem value="female">여성</SelectItem>
                    </SelectContent>
                  </Select>
                  {errors.gender && <p className="text-xs text-red-600">{errors.gender}</p>}
                </div>

                {/* Mode (반말/존댓말) */}
                <div className="space-y-1">
                  <label className="text-sm font-medium text-gray-700 flex items-center">
                    말투
                  </label>
                  <Select
                    value={formData.mode}
                    onValueChange={(value) => handleInputChange("mode", value)}
                  >
                    <SelectTrigger
                      className={`h-12 border-gray-200 focus:border-amber-300 focus:ring-amber-200 rounded-xl`}
                    >
                      <SelectValue placeholder="말투를 선택해주세요" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="banmal">반말</SelectItem>
                      <SelectItem value="jondaetmal">존댓말</SelectItem>
                    </SelectContent>
                  </Select>
                  {errors.mode && <p className="text-xs text-red-600">{errors.mode}</p>}
                </div>

                {/* Current Concern */}
                <div className="space-y-1">
                  <label className="text-sm font-medium text-gray-700 flex items-center">
                    <Heart className="w-4 h-4 mr-2 text-amber-600" />
                    현재 고민 (선택사항)
                  </label>
                  <Textarea
                    value={formData.currentConcern}
                    onChange={(e) => handleInputChange("currentConcern", e.target.value)}
                    placeholder="현재 가지고 있는 고민이나 상담받고 싶은 내용을 간단히 적어주세요"
                    className="min-h-[80px] border-gray-200 focus:border-amber-300 focus:ring-amber-200 rounded-xl"
                  />
                </div>

                <Button
                  onClick={handleSubmit}
                  className="w-full h-12 bg-gradient-to-r from-amber-400 to-orange-400 hover:from-amber-500 hover:to-orange-500 text-white rounded-xl shadow-lg transition-all duration-200 mt-6"
                >
                  회원가입 완료
                </Button>

                <div className="bg-amber-50 p-4 rounded-lg border border-amber-200 mt-4">
                  <p className="text-xs text-amber-800 leading-relaxed">
                    🔒 개인정보 보호: 입력하신 모든 정보는 암호화되어 안전하게 저장되며, 상담 서비스 제공 목적으로만
                    사용됩니다. 언제든지 계정 삭제 및 정보 삭제가 가능합니다.
                  </p>
                </div>
              </CardContent>
            </Card>
          </>
        )}

        {step === "submitting" && (
          <Card className="shadow-xl border-0 bg-white/80 backdrop-blur-sm">
            <CardContent className="p-8 text-center">
              <div className="w-16 h-16 bg-gradient-to-br from-amber-200 to-orange-200 rounded-full flex items-center justify-center mx-auto mb-4 animate-pulse">
                <User className="w-8 h-8 text-amber-600" />
              </div>
              <h3 className="text-lg font-semibold text-gray-800 mb-2">계정 생성 중</h3>
              <p className="text-gray-600">안전한 계정을 생성하고 있습니다...</p>
            </CardContent>
          </Card>
        )}

        {step === "complete" && (
          <Card className="shadow-xl border-0 bg-white/80 backdrop-blur-sm">
            <CardContent className="p-8 text-center">
              <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <Heart className="w-8 h-8 text-green-600" />
              </div>
              <h3 className="text-lg font-semibold text-gray-800 mb-2">가입 완료!</h3>
              <p className="text-gray-600">WTF에 오신 것을 환영합니다</p>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  )
}
