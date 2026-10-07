from datetime import date, datetime
from zoneinfo import ZoneInfo

from lunar_python import Solar

KST = ZoneInfo("Asia/Seoul")


def _to_kst(dt: datetime) -> datetime:
    if dt.tzinfo is None:
        return dt.replace(tzinfo=KST)
    return dt.astimezone(KST)


def pillars(dt: datetime) -> dict[str, str]:
    """년·월·일·시 간지. naive 는 KST 로 간주, aware 는 KST 로 바꿔 계산한다.

    자시(23:00~23:59) 규칙은 lunar_python 기본값을 그대로 쓴다.
    """
    k = _to_kst(dt)
    ec = Solar.fromYmdHms(k.year, k.month, k.day, k.hour, k.minute, k.second).getLunar().getEightChar()
    return {
        "year": ec.getYear(),
        "month": ec.getMonth(),
        "day": ec.getDay(),
        "hour": ec.getTime(),
    }


def day_pillar_of(d: date) -> str:
    """해당 날짜 정오의 일진."""
    return pillars(datetime(d.year, d.month, d.day, 12, 0))["day"]
