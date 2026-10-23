# Whisky Bible

Durchsuchbare, fürs Smartphone optimierte Whisky-Karte (992 Whiskys).

**Live:** https://stevendz.github.io/whisky_bible/

## Suche

Das Suchfeld sitzt am unteren Bildschirmrand und durchsucht immer alles: Name, Preis, Jahr, Alter, Prozent, Brennerei und Region. Mehrere Begriffe müssen alle passen, z. B. `islay 46%` oder `cadenhead 1991`. Die Ergebnisse sind immer alphabetisch sortiert.

## Warenkorb

Jeder Whisky hat Buttons für 2 cl und 4 cl. Ein Tipp legt ein Glas in den Warenkorb, mehrfaches Tippen erhöht die Menge. Der Warenkorb öffnet sich über den Button oben rechts und bleibt erhalten, solange der Browser-Tab offen ist.

## Daten aktualisieren

Die Daten in `data/whiskies.json` werden aus dem PDF der Karte erzeugt:

```bash
pip install pymupdf
python tools/extract.py Whisky-14.10.26.pdf data/whiskies.json
```
