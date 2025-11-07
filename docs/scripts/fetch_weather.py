# scripts/fetch_weather.py
from pathlib import Path
import os, json, urllib.request, urllib.parse, datetime

KEY = os.environ["f8751e289d9ec82e10da922edec795df"]          # GitHub Secret
LAT = os.environ.get("WX_LAT", "53.64")          # z.B. Hooksiel
LON = os.environ.get("WX_LON", "8.01")
URL = "https://api.openweathermap.org/data/3.0/onecall?" + urllib.parse.urlencode({
    "lat": LAT, "lon": LON, "units": "metric", "lang": "de", "appid": KEY
})

out = Path("data"); out.mkdir(parents=True, exist_ok=True)
dst = out / "weather.json"

with urllib.request.urlopen(URL) as r:
    raw = json.load(r)

result = {
    "fetched_at": datetime.datetime.utcnow().isoformat(timespec="seconds") + "Z",
    "lat": raw.get("lat"), "lon": raw.get("lon"),
    "current": raw.get("current"),
    "hourly": (raw.get("hourly") or [])[:24],
    "daily": (raw.get("daily") or [])[:7]
}
dst.write_text(json.dumps(result, ensure_ascii=False, indent=2))
print(f"[OK] {dst} geschrieben")
