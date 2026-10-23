# Whisky Bible

Durchsuchbare, fürs Smartphone optimierte Whisky-Karte (992 Whiskys).

**Live:** https://stevendz.github.io/whisky_bible/

## Suche

Das Suchfeld sitzt am unteren Bildschirmrand. Die Ergebnisse sind immer alphabetisch sortiert.

| Feld | Beispiele |
| --- | --- |
| Alle | `glenfiddich`, `islay 46%`, `pflaume` |
| Name | `port ellen` |
| Preis (2 cl oder 4 cl) | `12`, `5-10`, `<8`, `>50` |
| Jahr | `1990`, `1970-1980` |
| Alter | `18`, `>25` |
| Prozent | `46`, `>55`, `40-43` |
| Region | `islay`, `japan`, `cadenhead` |

## Daten aktualisieren

Die Daten in `data/whiskies.json` werden aus dem PDF der Karte erzeugt:

```bash
pip install pymupdf
python tools/extract.py Whisky-14.10.26.pdf data/whiskies.json
```
