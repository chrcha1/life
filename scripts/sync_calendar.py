"""Pull external calendars (Google / Apple ICS feeds) into events.json.

Runs in GitHub Actions. Feed URLs come from the ICS_URLS secret —
one URL per line (or comma-separated). Google: calendar settings →
"Secret address in iCal format". Apple: iCloud Calendar → share →
public calendar link (webcal://...).
"""
import json
import os
import sys
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

import requests
import recurring_ical_events
from icalendar import Calendar

TZ = ZoneInfo("America/Los_Angeles")
LOOKBACK_DAYS = 1
LOOKAHEAD_DAYS = 45
OUT = "events.json"


def fetch(url):
    url = url.strip().replace("webcal://", "https://")
    r = requests.get(url, timeout=30)
    r.raise_for_status()
    return Calendar.from_ical(r.content)


def main():
    raw = os.environ.get("ICS_URLS", "")
    urls = [u.strip() for chunk in raw.splitlines() for u in chunk.split(",") if u.strip()]
    events = []
    errors = 0

    start = date.today() - timedelta(days=LOOKBACK_DAYS)
    end = date.today() + timedelta(days=LOOKAHEAD_DAYS)

    for i, url in enumerate(urls):
        try:
            cal = fetch(url)
        except Exception as e:
            print(f"calendar {i}: fetch failed: {type(e).__name__}", file=sys.stderr)
            errors += 1
            continue
        for ev in recurring_ical_events.of(cal).between(start, end):
            summary = str(ev.get("SUMMARY", "")).strip() or "(untitled)"
            dtstart = ev["DTSTART"].dt
            dtend = ev.get("DTEND")
            if isinstance(dtstart, datetime):
                local = dtstart.astimezone(TZ) if dtstart.tzinfo else dtstart.replace(tzinfo=TZ)
                item = {"date": local.date().isoformat(), "time": local.strftime("%H:%M")}
                if dtend is not None and isinstance(dtend.dt, datetime):
                    e = dtend.dt.astimezone(TZ) if dtend.dt.tzinfo else dtend.dt.replace(tzinfo=TZ)
                    item["end"] = e.strftime("%H:%M")
            else:  # all-day
                item = {"date": dtstart.isoformat(), "time": None}
            item["title"] = summary
            item["cal"] = i
            events.append(item)

    # dedupe + stable sort
    seen = set()
    unique = []
    for ev in sorted(events, key=lambda e: (e["date"], e["time"] or "99:99", e["title"])):
        key = (ev["date"], ev["time"], ev["title"].lower())
        if key in seen:
            continue
        seen.add(key)
        unique.append(ev)

    out = {
        "updated": datetime.now(tz=TZ).isoformat(timespec="seconds"),
        "calendars": len(urls),
        "errors": errors,
        "events": unique,
    }
    with open(OUT, "w") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
        f.write("\n")
    print(f"{len(unique)} events from {len(urls)} calendar(s), {errors} error(s)")
    if urls and errors == len(urls):
        sys.exit(1)  # every feed failed — surface it as a red run


if __name__ == "__main__":
    main()
