# Status Chats-Export

Ausschließlich abgearbeitete Fahrplaneinträge, je Punkt eine Zeile (§2.6 der Arbeitsanweisungen). **Keine Entscheidungen** — die stehen sofort in `implementation_doku.md`, an der Stelle, die sie normativ trägt; hier steht nur, dass und wann ein Punkt erledigt wurde.

Die Liste beginnt mit der Arbeitsphase ab dem 14. August 2026. Die davor erledigten Punkte 1 bis 13 sind hier nicht nachgetragen: Ihren einzigen Nachweis führte der `Statusueberblick.md`, eine Momentaufnahme vom 9. August, die beim Aufräumen dieser Phase entfallen ist (Punkt 20). Was von ihnen gilt, steht in der Doku; der Verlauf steht in der Git-Historie.

## 2026-08-14

- **15** Prüfpunkte an einem Ort zusammengefasst und vervollständigt. Kapitel 4 trägt jetzt Verfahren, drei Prüfarten und eine Übersicht über alle Punkte; die verstreuten Punkte aus 1.6, 3.2.5 und 1.3 sind aufgenommen.
- **16** Entscheidung gegen eine projekteigene `CLAUDE.md` für `chats-export`; die Begründung trägt die Repo-`CLAUDE.md`.

## 2026-08-15

- **17** Docstring von `chat_export_convert.py` mit dem Code in Übereinstimmung gebracht.
- **18** Anweisungsblock auf die drei Zielorte gebracht, gewählt über `convert --target`.
- **19** `analyse` nennt jetzt Denkschritte und Erzeugnisse; `report` zusätzlich die behaltenen Denkblöcke.
- **14** `diff` nennt die Fenstergrenze und warnt vor einem unplausiblen Projektdatum.
- **20** Doku-Durchgang: Zahlen, Dateiarten und Mengen des Echtlaufs nachgezogen, `Statusueberblick.md` entfallen, diese Datei angelegt.
