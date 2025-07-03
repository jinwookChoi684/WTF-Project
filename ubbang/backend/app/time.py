from datetime import datetime
import pytz

def get_today_date(mode="banmal") -> str:
    """
    현재 날짜와 시간 정보를 한국 시간 기준으로 반환
    말투 모드(mode)에 따라 반말/존댓말 형태로 분기
    """
    tz = pytz.timezone("Asia/Seoul")
    now = datetime.now(tz)

    hour = now.hour
    minute = now.minute
    date_str = now.strftime("%Y년 %m월 %d일")

    # 시간 형식 보정 (예: 8시 5분 → 08시 05분)
    time_str = f"{hour:02d}시 {minute:02d}분"

    if mode == "jondaetmal":
        return f"지금은 {date_str} {time_str}입니다."
    else:
        return f"지금 {date_str} {time_str}야."
