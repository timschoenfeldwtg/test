from pathlib import Path
import os, json, urllib.request, datetime

API_KEY = os.environ["WORLDTIDES_KEY"]
LAT = os.environ.get("TIDES_LAT", "53.64")
LON = os.environ.get("TIDES_LON", "8.01")
DAYS = int(os.environ.get("TIDES_DAYS", "7"))

url = f"https://www.worldtides.info/api/v3?extremes&lat={LAT}&lon={LON}&days={DAYS}&key={API_KEY}"

out_dir = Path("docs") / "data"
out_dir.mkdir(parents=True, exist_ok=True)
dst = out_dir / "tides.json"
raw_dst = out_dir / "tides_raw.json"

with urllib.request.urlopen(url, timeout=30) as r:
    raw = json.load(r)

raw_dst.write_text(json.dumps(raw, ensure_ascii=False, indent=2))

extremes = []
for e in raw.get("extremes", []):
    dt = int(datetime.datetime.fromisoformat(e["date"].replace("Z","+00:00")).timestamp())
    extremes.append({"dt": dt, "type": e.get("type",""), "height": e.get("height")})

result = {
    "fetched_at": datetime.datetime.utcnow().isoformat(timespec="seconds") + "Z",
    "lat": float(LAT), "lon": float(LON),
    "extremes": extremes
}

dst.write_text(json.dumps(result, ensure_ascii=False, indent=2))
print(f"[OK] wrote {dst} with {len(extremes)} entries and raw to {raw_dst}")
