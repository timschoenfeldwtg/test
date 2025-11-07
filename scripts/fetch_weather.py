from pathlib import Path
import os, json, urllib.request, urllib.parse, datetime

KEY = os.environ["OPENWEATHER_API_KEY"]
LAT = os.environ.get("WX_LAT", "53.64")
LON = os.environ.get("WX_LON", "8.01")

# One Call **2.5** statt 3.0 (free plan)
url = "https://api.openweathermap.org/data/2.5/onecall?" + urllib.parse.urlencode({
    "lat": LAT, "lon": LON, "units": "metric", "lang": "de", "appid": KEY
})

out_dir = Path("docs") / "data"
out_dir.mkdir(parents=True, exist_ok=True)
dst = out_dir / "weather.json"
raw_dst = out_dir / "weather_raw.json"

try:
    with urllib.request.urlopen(url, timeout=30) as r:
        raw = json.load(r)
except urllib.error.HTTPError as e:
    # Fehlerkörper mitschreiben für Debug
    body = e.read().decode("utf-8", errors="ignore")
    (out_dir / "weather_error.txt").write_text(f"{e}\n\n{body}")
    raise

# Raw speichern (Debug)
raw_dst.write_text(json.dumps(raw, ensure_ascii=False, indent=2))

result = {
    "fetched_at": datetime.datetime.utcnow().isoformat(timespec="seconds") + "Z",
    "lat": raw.get("lat"), "lon": raw.get("lon"),
    "current": raw.get("current"),
    "hourly": (raw.get("hourly") or [])[:24],
    "daily": (raw.get("daily") or [])[:7]
}

dst.write_text(json.dumps(result, ensure_ascii=False, indent=2))
print(f"[OK] wrote {dst} and raw to {raw_dst}")
