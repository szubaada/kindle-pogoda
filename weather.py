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
        "weather_code,wind_speed_10m"
        "&daily=weather_code,temperature_2m_max,temperature_2m_min,"
        "precipitation_probability_max,sunrise,sunset"
        f"&timezone={urllib.parse.quote(TZ, safe='')}&forecast_days=5&wind_speed_unit=kmh"
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


# ---------- render ----------

def hhmm(iso):
    return iso[11:16]


def render(data):
    now = dt.datetime.now(ZoneInfo(TZ))
    cur, daily = data["current"], data["daily"]

    img = Image.new("L", (W, H), 255)
    d = ImageDraw.Draw(img)
    f = lambda path, size: ImageFont.truetype(path, size)

    # nagłówek
    d.text((W // 2, 85), CITY, font=f(FONT_B, 70), fill=0, anchor="mm")
    date_txt = f"{DAYS[now.weekday()]}, {now.day} {MONTHS[now.month - 1]}"
    d.text((W // 2, 160), date_txt, font=f(FONT, 42), fill=0, anchor="mm")
    d.line([60, 210, W - 60, 210], fill=0, width=4)

    # aktualna pogoda
    desc, kind = info(cur["weather_code"])
    icon(d, kind, 280, 455, 320)
    d.text((520, 410), f"{round(cur['temperature_2m'])}°", font=f(FONT_B, 230),
           fill=0, anchor="lm")
    d.text((W // 2, 640), desc, font=f(FONT_B, 56), fill=0, anchor="mm")
    details = (f"Odczuwalna {round(cur['apparent_temperature'])}°  ·  "
               f"Wilgotność {round(cur['relative_humidity_2m'])}%  ·  "
               f"Wiatr {round(cur['wind_speed_10m'])} km/h")
    d.text((W // 2, 720), details, font=f(FONT, 34), fill=0, anchor="mm")
    sun_txt = f"Wschód {hhmm(daily['sunrise'][0])}   ·   Zachód {hhmm(daily['sunset'][0])}"
    d.text((W // 2, 780), sun_txt, font=f(FONT, 34), fill=0, anchor="mm")
    d.line([60, 840, W - 60, 840], fill=0, width=4)

    # prognoza na 4 kolejne dni
    y0, row = 850, 130
    for i in range(1, 5):
        yc = y0 + (i - 1) * row + row // 2
        day = dt.date.fromisoformat(daily["time"][i])
        _, k = info(daily["weather_code"][i])
        d.text((60, yc), DAYS[day.weekday()], font=f(FONT_B, 40), fill=0, anchor="lm")
        icon(d, k, 480, yc, 100)
        tmax = round(daily["temperature_2m_max"][i])
        tmin = round(daily["temperature_2m_min"][i])
        d.text((610, yc), f"{tmax}° / {tmin}°", font=f(FONT_B, 46), fill=0, anchor="lm")
        p = daily["precipitation_probability_max"][i]
        p_txt = f"{round(p)}%" if p is not None else "-"
        d.text((W - 60, yc), p_txt, font=f(FONT, 40), fill=0, anchor="rm")
        if i < 4:
            d.line([60, y0 + i * row, W - 60, y0 + i * row], fill=128, width=2)

    d.text((W // 2, 1420), f"Aktualizacja: {now:%H:%M}", font=f(FONT, 28),
           fill=90, anchor="mm")

    img.save(OUT)  # 8-bit skala szarosci, bez kanalu alfa
    print("Zapisano", OUT, img.size, img.mode)


if __name__ == "__main__":
    render(fetch())
