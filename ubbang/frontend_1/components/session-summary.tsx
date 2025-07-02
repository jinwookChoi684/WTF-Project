"use client"

import { useState } from "react"
import { Card, CardContent } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { ChevronDown, ChevronUp, FileText, X } from "lucide-react"

export default function SessionSummary() {
  const [isExpanded, setIsExpanded] = useState(false)
  const [isVisible, setIsVisible] = useState(true)

  if (!isVisible) return null

  return (
    <Card className="bg-gradient-to-r from-amber-50 to-orange-50 border-amber-200 shadow-sm">
      <CardContent className="p-4">
        <div className="flex items-start justify-between">
          <div className="flex items-center space-x-2 mb-2">
            <FileText className="w-4 h-4 text-amber-600" />
            <h3 className="text-sm font-medium text-amber-800">지난 대화 요약</h3>
          </div>
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setIsVisible(false)}
            className="h-6 w-6 p-0 text-amber-600 hover:text-amber-700 hover:bg-amber-100"
          >
            <X className="w-4 h-4" />
          </Button>
        </div>

        <div className="text-sm text-amber-700 leading-relaxed">
          <p>
            최근 폭염이 기승입니다.
            {isExpanded && (
              <span>
                {" "}
                낮에 최고 36도까지 올라가는 무더위가 기승을 부리고 있는데, 건강 유의하세요~~😂😂
              </span>
            )}
          </p>
        </div>

        <Button
          variant="ghost"
          size="sm"
          onClick={() => setIsExpanded(!isExpanded)}
          className="mt-2 h-6 text-xs text-amber-600 hover:text-amber-700 hover:bg-amber-100 p-0"
        >
          {isExpanded ? (
            <>
              <ChevronUp className="w-3 h-3 mr-1" />
              접기
            </>
          ) : (
            <>
              <ChevronDown className="w-3 h-3 mr-1" />
              더보기
            </>
          )}
        </Button>
      </CardContent>
    </Card>
  )
}
