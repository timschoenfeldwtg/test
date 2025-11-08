# scripts/fetch_weather.py  – nutzt Open-Meteo (kein API-Key nötig)
from pathlib import Path
import os, json, urllib.request, urllib.parse, datetime, math

LAT = os.environ.get("WX_LAT", "53.64")
LON = os.environ.get("WX_LON", "8.01")
TZ  = "Europe/Berlin"

params = {
    "latitude": LAT,
    "longitude": LON,
    "timezone": TZ,
    "current": "temperature_2m,relative_humidity_2m,apparent_temperature,wind_speed_10m,wind_direction_10m,weather_code",
    "hourly": "temperature_2m,wind_speed_10m,weather_code",
    "daily": "weather_code,temperature_2m_min,temperature_2m_max,sunrise,sunset",
    "windspeed_unit": "ms"
}
url = "https://api.open-meteo.com/v1/forecast?" + urllib.parse.urlencode(params)

out_dir = Path("docs") / "data"
out_dir.mkdir(parents=True, exist_ok=True)
dst     = out_dir / "weather.json"
raw_dst = out_dir / "weather_raw.json"

# Minimal Mapping WMO -> OpenWeather-Icon + Beschreibung
def wmo_to_icon_desc(code: int, is_day: bool=True):
    # sehr grob, reicht für Widget
    m = {
        0: ("01d","klarer Himmel"),
        1: ("02d","überwiegend klar"),
        2: ("03d","wolkig"),
        3: ("04d","bedeckt"),
        45:("50d","Nebel"),
        48:("50d","Reif-Nebel"),
        51:("09d","Nieselregen leicht"),
        53:("09d","Nieselregen"),
        55:("09d","Nieselregen stark"),
        56:("09d","gefrierender Niesel leicht"),
        57:("09d","gefrierender Niesel"),
        61:("10d","Regen leicht"),
        63:("10d","Regen"),
        65:("10d","Regen stark"),
        66:("13d","gefrierender Regen leicht"),
        67:("13d","gefrierender Regen"),
        71:("13d","Schnee leicht"),
        73:("13d","Schnee"),
        75:("13d","Schnee stark"),
        77:("13d","Schneekörner"),
        80:("09d","Regenschauer leicht"),
        81:("09d","Regenschauer"),
        82:("09d","Regenschauer stark"),
        85:("13d","Schneeschauer leicht"),
        86:("13d","Schneeschauer stark"),
        95:("11d","Gewitter"),
        96:("11d","Gewitter mit leichtem Hagel"),
        99:("11d","Gewitter mit Hagel"),
    }
    icon, desc = m.get(int(code), ("04d","bewölkt"))
    if not is_day and icon.endswith("d"):
        icon = icon.replace("d","n")
    return icon, desc

def iso_to_unix(iso: str) -> int:
    return int(datetime.datetime.fromisoformat(iso).timestamp())

# Fetch
with urllib.request.urlopen(url, timeout=30) as r:
    raw = json.load(r)

raw_dst.write_text(json.dumps(raw, ensure_ascii=False, indent=2))

# Current
cur = raw.get("current", {}) or {}
is_day = True  # grob, wir nutzen Tages-Icons
icon, desc = wmo_to_icon_desc(cur.get("weather_code", 3), is_day=is_day)
current = {
    "temp": cur.get("temperature_2m"),
    "feels_like": cur.get("apparent_temperature"),
    "humidity": cur.get("relative_humidity_2m"),
    "wind_speed": cur.get("wind_speed_10m"),
    "wind_deg": cur.get("wind_direction_10m"),
    "weather": [{"icon": icon, "description": desc}],
    "dt": int(datetime.datetime.now().timestamp())
}

# Hourly (24h)
hourly = []
hx = raw.get("hourly", {}) or {}
for i, iso in enumerate(hx.get("time", [])[:24]):
    wmo = (hx.get("weather_code") or [None]*24)[i]
    icon, desc = wmo_to_icon_desc(wmo, True)
    hourly.append({
        "dt": iso_to_unix(iso),
        "temp": (hx.get("temperature_2m") or [None]*24)[i],
        "wind_speed": (hx.get("wind_speed_10m") or [None]*24)[i],
        "weather": [{"icon": icon, "description": desc}],
    })

# Daily (7 Tage)
daily = []
dx = raw.get("daily", {}) or {}
for i, iso in enumerate(dx.get("time", [])[:7]):
    wmo = (dx.get("weather_code") or [None]*7)[i]
    icon, desc = wmo_to_icon_desc(wmo, True)
    daily.append({
        "dt": iso_to_unix(iso + "T12:00:00"),
        "sunrise": iso_to_unix((dx.get("sunrise") or [iso])[i]),
        "sunset":  iso_to_unix((dx.get("sunset")  or [iso])[i]),
        "temp": {"min": (dx.get("temperature_2m_min") or [None]*7)[i],
                 "max": (dx.get("temperature_2m_max") or [None]*7)[i]},
        "weather": [{"icon": icon, "description": desc}],
    })

result = {
    "fetched_at": datetime.datetime.utcnow().isoformat(timespec="seconds") + "Z",
    "lat": float(LAT), "lon": float(LON),
    "current": current,
    "hourly": hourly,
    "daily": daily,
}

dst.write_text(json.dumps(result, ensure_ascii=False, indent=2))
print(f"[OK] wrote {dst}  (source: Open-Meteo)")
