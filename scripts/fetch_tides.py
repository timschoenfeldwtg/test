# scripts/fetch_tides.py
from pathlib import Path
import os, json, urllib.request, urllib.parse, datetime

API_KEY = os.environ["WORLDTIDES_KEY"]
LAT = os.environ.get("TIDES_LAT", "53.64")
LON = os.environ.get("TIDES_LON", "8.01")
DAYS = int(os.environ.get("TIDES_DAYS", "7"))

params = { "extremes": "", "lat": LAT, "lon": LON, "days": DAYS, "key": API_KEY }
url = "https://www.worldtides.info/api/v3?" + urllib.parse.urlencode(params)

out_dir = Path("docs"); out_dir.mkdir(parents=True, exist_ok=True)
dst = out_dir / "tides.json"

with urllib.request.urlopen(url) as r:
    raw = json.load(r)

extremes = []
for e in raw.get("extremes", []):
    dt = int(datetime.datetime.fromisoformat(e["date"].replace("Z","+00:00")).timestamp())
    extremes.append({ "dt": dt, "type": e.get("type",""), "height": e.get("height") })

result = {
    "fetched_at": datetime.datetime.utcnow().isoformat(timespec="seconds") + "Z",
    "lat": float(LAT), "lon": float(LON),
    "extremes": extremes
}

dst.write_text(json.dumps(result, ensure_ascii=False, indent=2))
print(f"[OK] Wrote {dst} with {len(extremes)} entries")
