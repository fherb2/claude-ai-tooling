# Status Chats-Export

Ausschließlich abgearbeitete Fahrplaneinträge, je Punkt eine Zeile (§2.6 der Arbeitsanweisungen). **Keine Entscheidungen** — die stehen sofort in `implementation_doku.md`, an der Stelle, die sie normativ trägt; hier steht nur, dass und wann ein Punkt erledigt wurde.

Die Liste beginnt mit der Arbeitsphase ab dem 14. August 2026. Die davor erledigten Punkte 1 bis 13 sind hier nicht nachgetragen: Ihren einzigen Nachweis führte der `Statusueberblick.md`, eine Momentaufnahme vom 9. August, die beim Aufräumen dieser Phase entfallen ist (Punkt 20). Was von ihnen gilt, steht in der Doku; der Verlauf steht in der Git-Historie.

## 2026-08-14

- **15** Prüfpunkte an einem Ort zusammengefasst und vervollständigt. Kapitel 4 trägt jetzt Verfahren, drei Prüfarten und eine Übersicht über alle Punkte; die verstreuten Punkte aus 1.6, 3.2.5 und 1.3 sind aufgenommen.
- **16** Entscheidung gegen eine projekteigene `CLAUDE.md` für `chat-export`; die Begründung trägt die Repo-`CLAUDE.md`.

## 2026-08-17 bis 18

- **21.1** Prüfplan festgeschrieben; das Profil des Testprojekts steht in Doku 4.1.
- **21.2** Testprojekt im Pro-Konto angelegt und nach Profil gefüllt; drei Merkmale kamen dabei nicht zustande, die Ursachen stehen in 4.1.
- **21.3/21.4** Sondierungsexport ausgewertet: Projektdateien sind vom Zeitraumfilter ausgenommen, geprüft gegen ein unabhängig notiertes Datum.
- **21.5** Chatliste geholt; `parse_chat_list` erkennt sie. Dabei belegt, dass `recent_chats` den laufenden Chat nicht mitlistet (Doku 1.6, 1.7).
- **21.6** Protokoll angelegt; die Fenstergrenze zeigt auf den Projektbeginn, ohne Projektdatum verweigert das Werkzeug die Auskunft.
- **21.7** Erstlauf-Export umgewandelt. Vier Erwartungen bestanden, drei nicht; daraus drei Befunde und ein behobener Defekt in `file_references()` (Doku 1.6, 1.7, 3.1.1).
- **25** Doku-Durchgang, Schritt 1: die Schnittstellenbeschreibung des entfallenen Lese-Wegs herausgenommen, 1.2 neu gefasst, 3.2 von 67 auf 12 Zeilen gekürzt, Kapitel 4 nachgezogen. Die Doku ist von 734 auf 658 Zeilen gefallen.
- **26** Probe über die Chrome-Anbindung bestanden: beide Endpunkte erreichbar, 593 KB in einer Antwort, Sollwerte zeichengenau getroffen. Dabei ein dritter Endpunkt gefunden, der jedes Projekt mit `created_at` führt.
- **26 (Fortsetzung)** Der Weg auf die Platte geprüft: fetch je Chat, ein Blob, ein Download. Härtefall 607.083 Zeichen in 953 ms; die Nachrichten-UUIDs der Web-API und des Export-ZIP sind für denselben Chat deckungsgleich.

## 2026-08-19 bis 21

- **21.8** Beide Hälften bestanden: `protokoll.json` als Projektdatei angenommen und zeichengenau lesbar, und der Anweisungsblock wirkt — eine fremde Instanz sah von selbst im Archiv nach, mit Quellenangabe.
- **21.9/21.10/21.11** Bewegung erzeugt, zweiter Abgleich und zweiter Export über das errechnete Fenster. Der Kern der Konstruktion ist damit vorgeführt: Das Fenster fing den gewachsenen Altchat ein. Dabei zwei Befunde — der Export-Weg meldete verschwundene Chats nicht (behoben), und der Denktext wird plattformseitig nicht mehr ausgeschrieben (Doku 3.1.1).
- **21.12 erste Hälfte** Eine fremde Instanz arbeitete allein aus dem Docstring, einschließlich der Stellen, die ihr Zurückhaltung vorschreiben. Vorgabe 2.9 damit belegt.
- **21 im Ganzen abgeschlossen.** Was von den geplanten Stufen offen blieb, hing am entfallenen Lese-Weg und ist gegenstandslos: 21.12 zweite Hälfte (nicht fortsetzbar) und 21.13 (Wegegleichheit gegen `read_conversation`). Letztere ist durch den Vergleich ZIP gegen Web-Behälter ersetzt und dort schärfer belegt — dieselben Nachrichten-UUIDs für denselben Chat.
- **23 gestrichen** — die Frage war, ob der Lese-Weg in einem Team-Projekt arbeitet. Das Werkzeug gibt es nirgends mehr; für Team-Konten trägt jetzt der Web-Weg, am 22. August dort durchgespielt.
- **7 gestrichen** — die Frage galt der Gültigkeitsdauer eines `page_token`. Der Web-Weg kennt keine Paginierung, ein Chat kommt immer ganz; damit ist „Zuwachs nachladen statt ersetzen" gegenstandslos.
- **27 (Teil)** Zweite Eingangsart gebaut: `convert --bundle` und `list --web`. Wegegleichheit zwischen beiden Wegen baulich gegeben und Datei für Datei geprüft. Dabei behoben: `list` brach bei einem Projekt ohne Chats ab, statt ein leeres Protokoll zu schreiben. `SKILL.md` geschrieben.
- **27 (Teil)** Ablage geordnet: `source/` entfallen, der Konverter zum Skill, die übrigen Skripte dorthin, wo ihre Aufgabe sie hinstellt. Alle Docstrings in `tests/` so ergänzt, dass sie ohne die Doku verständlich sind.
- **28** Chrome-Anbindung systematisch vermessen; Ergebnis in `chrome-zugriff.md`. Geklärt: `@browser` je Nachricht, Connector-Schalter, angemeldete Erweiterung — und dass die Konten von Chrome und Claude Code **nicht** übereinstimmen müssen.
- **29** Doku-Durchgang, Schritt 2: acht sachliche Fehler berichtigt, drei Lücken gefüllt (3.5 zum Skill, Web-Endpunkte in der Prüfliste, 1.5 über beide Wege), mehrere Stellen entfasert. Zähler in 2.1 von siebzehn auf fünfzehn.

## 2026-08-15

- **17** Docstring von `chat_export_convert.py` mit dem Code in Übereinstimmung gebracht.
- **18** Anweisungsblock auf die drei Zielorte gebracht, gewählt über `convert --target`.
- **19** `analyse` nennt jetzt Denkschritte und Erzeugnisse; `report` zusätzlich die behaltenen Denkblöcke.
- **14** `diff` nennt die Fenstergrenze und warnt vor einem unplausiblen Projektdatum.
- **20** Doku-Durchgang: Zahlen, Dateiarten und Mengen des Echtlaufs nachgezogen, `Statusueberblick.md` entfallen, diese Datei angelegt.
