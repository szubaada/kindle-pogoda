#!/usr/bin/env python3
"""Generator obrazu pogody dla Kindle Paperwhite 3 (1072x1448, skala szarosci).

Dane: Open-Meteo (bez klucza API). Wynik: weather.png
"""
import json
import math
import urllib.parse
import urllib.request
import datetime as dt
from zoneinfo import ZoneInfo

from PIL import Image, ImageDraw, ImageFont

# ======== USTAWIENIA - ZMIEN NA SWOJE ========
CITY = "Warszawa"
LAT, LON = 52.2297, 21.0122
TZ = "Europe/Warsaw"

# Przedzialy dnia: (nazwa, od godziny, do godziny - bez tej godziny).
# Mozesz je zmienic, np. ("Rano", 5, 9), jesli wstajesz wczesniej.
PERIODS = [("Rano", 6, 10), ("Południe", 10, 14), ("Popołudnie", 14, 18), ("Wieczór", 18, 22)]
# Po tej godzinie pokazujemy przebieg jutrzejszego dnia zamiast dzisiejszego.
SWITCH_TO_TOMORROW_AT = 21
# =============================================

W, H = 1072, 1448
OUT = "weather.png"
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONT_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

DAYS = ["Poniedziałek", "Wtorek", "Środa", "Czwartek", "Piątek", "Sobota", "Niedziela"]
MONTHS = ["stycznia", "lutego", "marca", "kwietnia", "maja", "czerwca", "lipca",
          "sierpnia", "września", "października", "listopada", "grudnia"]

# kod pogody Open-Meteo -> (opis, ikona)
CODES = {
    0: ("Bezchmurnie", "sun"), 1: ("Prawie bezchmurnie", "sun"),
    2: ("Częściowe zachmurzenie", "partly"), 3: ("Pochmurno", "cloud"),
    45: ("Mgła", "fog"), 48: ("Mgła szronowa", "fog"),
    51: ("Lekka mżawka", "rain"), 53: ("Mżawka", "rain"), 55: ("Gęsta mżawka", "rain"),
    56: ("Marznąca mżawka", "rain"), 57: ("Marznąca mżawka", "rain"),
    61: ("Lekki deszcz", "rain"), 63: ("Deszcz", "rain"), 65: ("Silny deszcz", "rain"),
    66: ("Marznący deszcz", "rain"), 67: ("Marznący deszcz", "rain"),
    71: ("Lekki śnieg", "snow"), 73: ("Śnieg", "snow"), 75: ("Silny śnieg", "snow"),
    77: ("Ziarna śniegu", "snow"),
    80: ("Przelotny deszcz", "rain"), 81: ("Przelotny deszcz", "rain"),
    82: ("Silny przelotny deszcz", "rain"),
    85: ("Przelotny śnieg", "snow"), 86: ("Przelotny śnieg", "snow"),
    95: ("Burza", "storm"), 96: ("Burza z gradem", "storm"), 99: ("Burza z gradem", "storm"),
}


def info(code):
    return CODES.get(code, ("Brak danych", "cloud"))


def fetch():
    params = (
        f"latitude={LAT}&longitude={LON}"
        "&current=temperature_2m,apparent_temperature,relative_humidity_2m,"
        "weather_code,wind_speed_10m,pressure_msl"
        "&daily=weather_code,temperature_2m_max,temperature_2m_min,"
        "precipitation_probability_max,sunrise,sunset"
        "&hourly=temperature_2m,weather_code,precipitation_probability,pressure_msl"
        f"&timezone={urllib.parse.quote(TZ, safe='')}&past_days=1&forecast_days=5"
        "&wind_speed_unit=kmh"
    )
    url = "https://api.open-meteo.com/v1/forecast?" + params
    with urllib.request.urlopen(url, timeout=30) as r:
        return json.load(r)


# ---------- ikony (czarne na bialym) ----------

def cloud(d, cx, cy, s, fill=0):
    d.ellipse([cx - 0.55 * s, cy - 0.15 * s, cx - 0.05 * s, cy + 0.35 * s], fill=fill)
    d.ellipse([cx - 0.30 * s, cy - 0.45 * s, cx + 0.30 * s, cy + 0.15 * s], fill=fill)
    d.ellipse([cx + 0.05 * s, cy - 0.25 * s, cx + 0.55 * s, cy + 0.35 * s], fill=fill)
    d.rectangle([cx - 0.30 * s, cy + 0.00 * s, cx + 0.30 * s, cy + 0.35 * s], fill=fill)


def sun(d, cx, cy, s):
    r = 0.26 * s
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=0)
    for i in range(8):
        a = math.radians(i * 45)
        x1, y1 = cx + math.cos(a) * 0.38 * s, cy + math.sin(a) * 0.38 * s
        x2, y2 = cx + math.cos(a) * 0.56 * s, cy + math.sin(a) * 0.56 * s
        d.line([x1, y1, x2, y2], fill=0, width=max(3, int(0.05 * s)))


def icon(d, kind, cx, cy, s):
    if kind == "sun":
        sun(d, cx, cy, s)
    elif kind == "partly":
        sun(d, cx - 0.22 * s, cy - 0.22 * s, 0.75 * s)
        cloud(d, cx + 0.05 * s, cy + 0.12 * s, s * 1.14, fill=255)
        cloud(d, cx + 0.05 * s, cy + 0.12 * s, s * 1.0, fill=0)
    elif kind == "cloud":
        cloud(d, cx, cy, s)
    elif kind in ("rain", "storm"):
        cloud(d, cx, cy - 0.18 * s, s)
        if kind == "rain":
            for i in range(3):
                x = cx - 0.28 * s + i * 0.28 * s
                d.line([x, cy + 0.30 * s, x - 0.09 * s, cy + 0.58 * s],
                       fill=0, width=max(3, int(0.06 * s)))
        else:
            bx, by = cx, cy + 0.12 * s
            d.polygon([(bx + 0.05 * s, by), (bx - 0.16 * s, by + 0.30 * s),
                       (bx - 0.02 * s, by + 0.30 * s), (bx - 0.10 * s, by + 0.58 * s),
                       (bx + 0.18 * s, by + 0.22 * s), (bx + 0.04 * s, by + 0.22 * s)],
                      fill=0)
    elif kind == "snow":
        cloud(d, cx, cy - 0.18 * s, s)
        r = 0.04 * s
        for i in range(3):
            x = cx - 0.28 * s + i * 0.28 * s
            for y in (cy + 0.38 * s, cy + 0.56 * s):
                d.ellipse([x - r, y - r, x + r, y + r], fill=0)
    elif kind == "fog":
        for i in range(4):
            y = cy - 0.30 * s + i * 0.20 * s
            d.line([cx - 0.5 * s, y, cx + 0.5 * s, y], fill=0, width=max(3, int(0.06 * s)))


# ---------- pomocnicze ----------

def hhmm(iso):
    return iso[11:16]


def severity(code):
    """Im wyzsza wartosc, tym 'gorsza' pogoda (do wyboru ikony przedzialu)."""
    if code is None:
        return -1
    if code in (0, 1):
        return code
    if code == 2:
        return 2
    if code == 3:
        return 3
    if code in (45, 48):
        return 4
    if 51 <= code <= 57:
        return 5
    if 61 <= code <= 67 or 80 <= code <= 82:
        return 6
    if 71 <= code <= 77 or code in (85, 86):
        return 7
    return 8  # burze


def pressure_trend(data, now):
    """Zwraca (cisnienie, delta_3h, opis, symbol)."""
    cur = data["current"].get("pressure_msl")
    if cur is None:
        return None, None, "brak danych", "?"
    times = data["hourly"]["time"]
    key = (now - dt.timedelta(hours=3)).strftime("%Y-%m-%dT%H:00")
    delta = None
    if key in times:
        old = data["hourly"]["pressure_msl"][times.index(key)]
        if old is not None:
            delta = cur - old
    if delta is None:
        return cur, None, "brak trendu", "→"
    if delta >= 1.0:
        return cur, delta, "rośnie", "↗"
    if delta <= -1.0:
        return cur, delta, "spada", "↘"
    return cur, delta, "stabilne", "→"


def day_period(data, date_str, start, end):
    """Zwraca (srednia temp, max prawdop. opadow, kod pogody) dla przedzialu godzin."""
    h = data["hourly"]
    temps, probs, codes = [], [], []
    for hour in range(start, end):
        key = f"{date_str}T{hour:02d}:00"
        if key not in h["time"]:
            continue
        i = h["time"].index(key)
        if h["temperature_2m"][i] is not None:
            temps.append(h["temperature_2m"][i])
        if h["precipitation_probability"][i] is not None:
            probs.append(h["precipitation_probability"][i])
        if h["weather_code"][i] is not None:
            codes.append(h["weather_code"][i])
    temp = sum(temps) / len(temps) if temps else None
    prob = max(probs) if probs else None
    code = max(codes, key=severity) if codes else None
    return temp, prob, code


# ---------- render ----------

def render(data):
    now = dt.datetime.now(ZoneInfo(TZ))
    cur, daily = data["current"], data["daily"]

    img = Image.new("L", (W, H), 255)
    d = ImageDraw.Draw(img)
    f = lambda path, size: ImageFont.truetype(path, size)

    # --- naglowek ---
    d.text((W // 2, 62), CITY, font=f(FONT_B, 64), fill=0, anchor="mm")
    date_txt = f"{DAYS[now.weekday()]}, {now.day} {MONTHS[now.month - 1]}"
    d.text((W // 2, 128), date_txt, font=f(FONT, 38), fill=0, anchor="mm")
    d.line([60, 170, W - 60, 170], fill=0, width=4)

    # --- aktualna pogoda ---
    desc, kind = info(cur["weather_code"])
    icon(d, kind, 235, 340, 245)
    d.text((440, 325), f"{round(cur['temperature_2m'])}°", font=f(FONT_B, 200),
           fill=0, anchor="lm")
    d.text((W // 2, 490), desc, font=f(FONT_B, 50), fill=0, anchor="mm")
    details = (f"Odczuwalna {round(cur['apparent_temperature'])}°  ·  "
               f"Wilgotność {round(cur['relative_humidity_2m'])}%  ·  "
               f"Wiatr {round(cur['wind_speed_10m'])} km/h")
    d.text((W // 2, 548), details, font=f(FONT, 32), fill=0, anchor="mm")

    p, delta, p_word, p_sym = pressure_trend(data, now)
    if p is not None:
        p_txt = f"Ciśnienie {round(p)} hPa   {p_sym} {p_word}"
        if delta is not None:
            dr = round(delta)
            sign = "+" if dr > 0 else ("−" if dr < 0 else "")
            p_txt += f" ({sign}{abs(dr)} hPa / 3 h)"
    else:
        p_txt = "Ciśnienie: brak danych"
    d.text((W // 2, 602), p_txt, font=f(FONT_B, 36), fill=0, anchor="mm")

    pi = daily["time"].index(now.strftime("%Y-%m-%d"))
    sun_txt = f"Wschód {hhmm(daily['sunrise'][pi])}   ·   Zachód {hhmm(daily['sunset'][pi])}"
    d.text((W // 2, 656), sun_txt, font=f(FONT, 32), fill=0, anchor="mm")
    d.line([60, 700, W - 60, 700], fill=0, width=4)

    # --- przebieg dnia (rano / poludnie / popoludnie / wieczor) ---
    if now.hour >= SWITCH_TO_TOMORROW_AT:
        target = now.date() + dt.timedelta(days=1)
        title = "Jutro w ciągu dnia"
    else:
        target = now.date()
        title = "Dziś w ciągu dnia"
    d.text((60, 740), title, font=f(FONT_B, 38), fill=0, anchor="lm")

    col_w = (W - 120) / len(PERIODS)
    for n, (name, start, end) in enumerate(PERIODS):
        cx = int(60 + col_w * n + col_w / 2)
        temp, prob, code = day_period(data, target.isoformat(), start, end)
        d.text((cx, 800), name, font=f(FONT_B, 34), fill=0, anchor="mm")
        d.text((cx, 838), f"{start}–{end}", font=f(FONT, 28), fill=90, anchor="mm")
        icon(d, info(code)[1], cx, 925, 105)
        t_txt = f"{round(temp)}°" if temp is not None else "-"
        d.text((cx, 1012), t_txt, font=f(FONT_B, 50), fill=0, anchor="mm")
        r_txt = f"opady {round(prob)}%" if prob is not None else "opady -"
        d.text((cx, 1062), r_txt, font=f(FONT, 28), fill=0, anchor="mm")
        if n:
            x = int(60 + col_w * n)
            d.line([x, 780, x, 1085], fill=170, width=2)
    d.line([60, 1110, W - 60, 1110], fill=0, width=4)

    # --- kolejne 3 dni ---
    t_idx = daily["time"].index(target.isoformat())
    y0, row = 1118, 92
    for k in range(1, 4):
        i = t_idx + k
        if i >= len(daily["time"]):
            break
        yc = y0 + (k - 1) * row + row // 2
        day = dt.date.fromisoformat(daily["time"][i])
        _, ik = info(daily["weather_code"][i])
        d.text((60, yc), DAYS[day.weekday()], font=f(FONT_B, 38), fill=0, anchor="lm")
        icon(d, ik, 470, yc, 70)
        tmax = round(daily["temperature_2m_max"][i])
        tmin = round(daily["temperature_2m_min"][i])
        d.text((600, yc), f"{tmax}° / {tmin}°", font=f(FONT_B, 44), fill=0, anchor="lm")
        pr = daily["precipitation_probability_max"][i]
        d.text((W - 60, yc), f"{round(pr)}%" if pr is not None else "-",
               font=f(FONT, 38), fill=0, anchor="rm")
        if k < 3:
            d.line([60, y0 + k * row, W - 60, y0 + k * row], fill=150, width=2)

    d.text((W // 2, 1425), f"Aktualizacja: {now:%H:%M}", font=f(FONT, 26),
           fill=90, anchor="mm")

    img.save(OUT)  # 8-bit skala szarosci, bez kanalu alfa
    print("Zapisano", OUT, img.size, img.mode)


if __name__ == "__main__":
    render(fetch())
