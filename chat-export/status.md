# Status Chats-Export

Abgearbeitete Fahrplaneinträge, je Punkt eine Zeile (§2.6 der Arbeitsanweisungen). **Keine Entscheidungen** — die stehen in `implementation_doku.md`, an der Stelle, die sie normativ trägt; hier steht nur, dass und wann ein Punkt erledigt wurde.

Geführt wird **nicht** jeder erledigte Schritt, sondern der, dessen Ergebnis heute noch trägt. Reine Aufräumarbeit an der Doku, Umbenennungen und Verfahren, die sich später als entbehrlich erwiesen haben, sind ersatzlos entfernt: Ihr Ergebnis steht in der Doku, und ihr Verlauf in der Git-Historie. Die vor dem 14. August 2026 erledigten Punkte 1 bis 13 sind ebenso nicht nachgetragen.

## 2026-08-14 bis 15

- **14** `diff` nennt die Fenstergrenze und warnt vor einem unplausiblen Projektdatum — dieselbe Rechnung wie `list`, aber ohne frische Chatliste.
- **15** Prüfliste gegen Anthropic-Änderungen an einem Ort zusammengeführt: Kapitel 4 trägt Verfahren, die drei Prüfarten und die Übersicht über alle Punkte.
- **18** Anweisungsblock auf die drei Zielorte gebracht, gewählt über `convert --target`.
- **19** `analyse` und `report` nennen dieselben Posten; die Drift zwischen Vorschau und Bericht ist seither testgesichert.

## 2026-08-17 bis 18

- **21.1/21.2** Testprojekt im Pro-Konto gebaut und nach Profil gefüllt. Das Profil steht in Doku 4.1 und verbraucht sich nicht; drei Rezepte scheiterten dabei und sind dort korrigiert.
- **21.3/21.4** Projektdateien sind vom Zeitraumfilter des Exports ausgenommen und tragen den Projektbeginn — geprüft gegen ein unabhängig notiertes Datum. Trägt die Fensterrechnung für Konten ohne Web-Weg.
- **21.5** `recent_chats` listet den laufenden Chat nicht mit (Doku 1.6, 1.7). Daraus die Regel, die Chatliste in einem Wegwerfchat zu holen — nötig nur noch dort, wo die Liste aus claude.ai kommt.
- **21.6** Protokoll angelegt; ohne Projektdatum verweigert das Werkzeug die Auskunft statt zu schätzen.
- **21.7** Erstlauf-Export umgewandelt. Vier Erwartungen bestanden, drei nicht; daraus drei Befunde und ein behobener Defekt in `file_references()`, der Verlust überzeichnete (Doku 1.6, 3.1.1).

## 2026-08-19 bis 22

- **21.8** Der Anweisungsblock wirkt: Eine fremde Instanz sah von selbst im Archiv nach, mit Quellenangabe. Der einzige Beleg, dass dieses Werkzeug im Zielprojekt fortwirkt. Dazu der Rückweg des Protokolls, zeichengenau lesbar.
- **21.9 bis 21.11** Bewegung erzeugt, zweiter Abgleich, zweiter Export über das errechnete Fenster — der Kern der Konstruktion, vorgeführt: Das Fenster fing den gewachsenen Altchat ein. Zwei Befunde dabei: der Export-Weg meldete verschwundene Chats nicht (behoben), und der Denktext wird plattformseitig nicht mehr ausgeschrieben (Doku 3.1.1).
- **21.12 erste Hälfte** Eine fremde Instanz arbeitete allein aus dem Docstring, einschließlich der Stellen, die ihr Zurückhaltung vorschreiben — Vorgabe 2.9 belegt. Das trägt heute die `SKILL.md`, auch wenn das damals geprüfte Skript nicht mehr lauffähig ist.
- **21 abgeschlossen.** Offen blieb allein, was am entfallenen Lese-Weg hing: 21.12 zweite Hälfte und 21.13. Letztere ist durch den Vergleich ZIP gegen Web-Behälter ersetzt und dort schärfer belegt — dieselben Nachrichten-UUIDs für denselben Chat.
- **26** Die Web-Endpunkte sind über die Chrome-Anbindung erreichbar und liefern mehr als der Export: 607.083 Zeichen in einer Antwort ohne Paginierung, Sollwerte zeichengenau getroffen, Anhänge mit Inhalt, `created_at` und `project_uuid` je Chat. Dazu der Weg auf die Platte — `fetch` je Chat, ein Blob, ein Download.
- **27 (Teil)** Zweite Eingangsart gebaut: `convert --bundle` und `list --web`. Die Wegegleichheit ist damit baulich gegeben und Datei für Datei geprüft. Dabei behoben: `list` brach bei einem Projekt ohne Chats ab, statt ein leeres Protokoll zu schreiben. `SKILL.md` geschrieben.
- **28** Chrome-Anbindung systematisch vermessen (`chrome-zugriff.md`): `@browser` je Nachricht, Connector-Schalter auf claude.ai, angemeldete Erweiterung — und die Konten von Chrome und Claude Code müssen **nicht** übereinstimmen.
- **23 gestrichen** — die Frage war, ob der Lese-Weg in einem Team-Projekt arbeitet. Das Werkzeug gibt es nirgends mehr; für Team-Konten trägt der Web-Weg, am 22. August dort durchgespielt.
- **7 gestrichen** — die Frage galt der Gültigkeitsdauer eines `page_token`. Der Web-Weg kennt keine Paginierung, ein Chat kommt immer ganz; „Zuwachs nachladen statt ersetzen" ist damit gegenstandslos.
