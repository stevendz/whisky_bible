"""Liest die Whisky-Karte (PDF) und schreibt data/whiskies.json.

Aufruf: python tools/extract.py Whisky-14.10.26.pdf data/whiskies.json
Benötigt: pip install pymupdf
"""
import json
import re
import sys

import fitz

NUM = r"\d+(?:,\d+)?"
PCT = r"\d+(?:[,.]\d+)?"
FIRST_MENU_PAGE = 13
REGIONS = {
    "Die unabhängigen Abfüller /": "Unabhängige Abfüller",
    "Irland / Nordirland": "Irland",
    "New World Whiskys": "New World",
}


def read_lines(path):
    lines = []
    for pno, page in enumerate(fitz.open(path), start=1):
        spans = []
        for block in page.get_text("dict")["blocks"]:
            for line in block.get("lines", []):
                for s in line["spans"]:
                    if s["text"].strip():
                        spans.append((round(s["origin"][1], 1), s["bbox"][0], s["bbox"][2], s["text"], s["size"]))
        spans.sort(key=lambda s: (s[0], s[1]))
        rows = []
        for s in spans:
            if rows and abs(rows[-1]["y"] - s[0]) < 2.5:
                rows[-1]["spans"].append(s)
            else:
                rows.append({"y": s[0], "spans": [s]})
        for row in rows:
            row["spans"].sort(key=lambda s: s[1])
            text, prev = "", None
            for s in row["spans"]:
                if prev is not None and s[1] - prev > 1.5 and not text.endswith(" "):
                    text += "  " if s[1] - prev > 8 else " "
                text += s[3]
                prev = s[2]
            lines.append({"page": pno, "y": row["y"], "size": round(row["spans"][0][4], 1),
                          "text": text.replace(" ", " ").strip()})
    return lines


def parse_prices(rest):
    prices = {}
    m = re.search(r"1cl\s*-\s*(" + NUM + ")", rest)
    if m:
        prices["1cl"] = m.group(1)
        rest = rest[:m.start()] + rest[m.end():]
    m = re.search(r"2cl\s+(" + NUM + r")\s+4cl\s+(" + NUM + r")\s*$", rest)
    if m:
        prices["2cl"], prices["4cl"] = m.groups()
        return prices
    m = re.search(r"4cl\s+(" + NUM + r")\s*$", rest)
    if m:
        prices["4cl"] = m.group(1)
        return prices
    nums = re.findall(NUM, re.sub(r"[….]", " ", rest))
    if len(nums) >= 2:
        prices["2cl"], prices["4cl"] = nums[-2], nums[-1]
    elif nums:
        prices["2cl"] = nums[-1]
    return prices


def parse_entry(text, prefix=""):
    raw = text.replace(" ,", ",")
    head = raw.split("…", 1)[0]
    name = (prefix + " " + head.rstrip(". ")).strip()
    pct = re.findall(r"(" + PCT + r"),?\s?%", name)
    age = re.search(r"(\d+)\s?(?:yo|y\.o\.|years)\b", name)
    return {
        "name": re.sub(r",?\s*(?:ca\.\s*)?" + PCT + r",?\s?%\s*$", "", name).strip(", "),
        "pct": pct[-1].replace(".", ",") if pct else None,
        "age": age.group(1) if age else None,
        "years": re.findall(r"\b(1[89]\d\d|20[0-3]\d)\b", name),
        "prices": parse_prices(raw[len(head):]),
    }


def parse(lines):
    items, cur, region, distillery, last_y = [], None, None, None, None

    def close():
        nonlocal cur
        if cur:
            cur["notes"] = " ".join(cur["notes"]).strip(" –-")
            items.append(cur)
        cur = None

    for i, line in enumerate(lines):
        t, size, page = line["text"], line["size"], line["page"]
        if page < FIRST_MENU_PAGE:
            continue
        if re.fullmatch(r"-\s*-?\s*\d+\s*-?\s*-?", t):
            close()
        elif 30 <= size < 33:
            close()
            if not (region or "").startswith("Die unabhängigen") or "independent" not in t:
                region = t
            distillery = None
        elif 22 <= size < 30 and page == 196:
            close()
            distillery = None
        elif size >= 33:
            close()
            distillery = re.sub(r"\s+\d/\d$", "", re.split(r"\s{2,}|\s\(|\s…", t)[0]).strip()
        elif "…" in t and re.search(r"…[^…]*\d\s*$", t):
            prev = lines[i - 1]
            prefix = ""
            if prev["page"] == page and prev["text"].endswith(",") and 0 < line["y"] - prev["y"] < 20:
                prefix = prev["text"]
                if cur and cur["notes"] and cur["notes"][-1] == prefix:
                    cur["notes"].pop()
            close()
            cur = parse_entry(t, prefix) | {"region": region, "distillery": distillery, "page": page, "notes": []}
            last_y = line["y"]
        elif cur and size <= 12.5 and line["y"] - last_y < 22 and page == cur["page"]:
            if re.match(r"(Weitere|Anmerkung)", t):
                close()
            else:
                cur["notes"].append(t)
                last_y = line["y"]
        else:
            close()
    close()

    for w in items:
        w["region"] = REGIONS.get(w["region"], w["region"])
        if w["distillery"] == "Whiskylikör":
            w["region"], w["distillery"] = "Whiskylikör", None
        if w["distillery"] and w["distillery"].startswith("Gordon"):
            w["distillery"] = "Gordon & MacPhail"
        if w["page"] == 196:
            w["distillery"] = "Japanische Blends & Grains"
        if w["distillery"] in ("Blended Scotch", w["region"]):
            w["distillery"] = None
    return items


if __name__ == "__main__":
    whiskies = parse(read_lines(sys.argv[1]))
    with open(sys.argv[2], "w", encoding="utf-8") as f:
        json.dump(whiskies, f, ensure_ascii=False, separators=(",", ":"))
    print(f"{len(whiskies)} Whiskys geschrieben")
