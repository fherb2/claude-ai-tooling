# 🚧 tiefen-recherche — Recherche, die nicht zu früh aufgibt

🚧 Erstfassung der `SKILL.md` geschrieben, aber **ungetestet** — nicht zur Installation freigegeben. Was zum Test aussteht, steht unter „Stand und Offenes".

## Überblick

**Der Skill macht aus latenter Recherche-Fähigkeit ein verbindliches Verfahren: systematischer Wechsel von Suchbegriffen, Kanälen und Ebenen, Verifikationspflicht für jede Suchzusammenfassung, und ein Bericht über die noch offenen Suchwege statt eines vorschnellen „nichts gefunden".** Er gilt für jede Art von Recherche — Literatur, Fakten, Dokumente —, nicht nur im Software-Kontext (Geltungsbereich nach `implementation_doku.md` Kapitel 8.3: alle Arbeitsformen).

Abgrenzung: Der Skill beschafft kein Wissen, das nirgends erreichbar ist (Paywalls, Offline-Bestände, nie Gecrawltes). Er regelt auch nicht, ob und wo Rechercheergebnisse dauerhaft abgelegt werden — das entscheidet der Nutzer situativ.

## Herleitung: die Befunde vom 23. August 2026

Das Modell stammt aus einer Chat-Sitzung, die drei Schwächen der naiven Recherche empirisch vorführte:

1. **Trainingsdaten sind lückenhafter als „das Internet".** Ein frei im Web stehender Fachartikel (Wink, U.: „Lokal hohe Siedlungsdichte des Neuntöters *Lanius collurio* im Ammersee-Gebiet", Ornithologischer Anzeiger Bd. 47, S. 66, auf og-bayern.de) war im parametrischen Wissen des Modells nicht vorhanden.
2. **Auch die Websuche findet Nischenquellen oft nicht.** Eine Folgestudie („Bestandsabnahmen beim Neuntöter Lanius collurio im Ammerseegebiet. Eine Langzeitstudie von 2002 bis 2016", auf zobodat.at) war weder über die Websuche des Modells noch über Google mit exaktem Titel auffindbar — nur über die Spezialdatenbank selbst.
3. **KI-Suchzusammenfassungen konfabulieren.** Zweimal am selben Tag präsentierte die Suche überzeugend klingende, aber unbelegte Behauptungen (konkrete Revierzahlen „81 → 34", die die angebliche Quelle nachweislich nicht enthält; einem Zotero-Werkzeug wurde „full write support" zugeschrieben, das tatsächlich rein lesend ist). Beide flogen erst beim Direktabruf der Primärquelle auf.

Der gefundene Fachartikel wurde übrigens nicht über eine Themensuche entdeckt, sondern über das Durchsuchen einer Register-Seite der Fachgesellschaft — ein Ebenenwechsel, der zufällig statt regelhaft geschah. Genau diese Zufälligkeit soll der Skill beseitigen.

## Das Modell in Kurzform

- **Frontier statt Versuchszähler.** Es gibt kein richtiges „n Versuche, dann aufgeben" — niemand kennt n. Stattdessen ist „nicht gefunden" als Antwort unzulässig; zulässig ist nur „Versucht: … / Noch offen: … / Soll ich weiter?". Die Pflicht, die Offen-Liste zu schreiben, erzwingt das Durchdenken der Strategien; der Abbruch wird eine sichtbare Entscheidung des Nutzers statt stiller Ermüdung des Modells.
- **Sechs Operatoren** als fachgebietsunabhängiges Repertoire: Reformulieren (Synonyme, Sprachen, alte Bezeichnungen), Eingrenzen (ergiebige Domäne direkt durchsuchen), Ebene wechseln (Register/Kataloge/Bibliographien statt Dokumente), Entitäten verfolgen (Autor → Werke, Zeitschrift → Register), Kanal wechseln (allgemeine Suche → Fachdatenbank → Direktabruf → URL-Konstruktion), Verifizieren (Primärabruf vor Übernahme).
- **Zwei Scheiter-Modi als Umschaltsignal.** „Viele Treffer, aber keiner beantwortet die Frage" → eingrenzen oder Ebene wechseln. „Gar keine brauchbaren Treffer" → reformulieren. Das Signal ist die Form des Fehlschlags, keine Vorab-Klassifikation des Themas.
- **Verifikationspflicht:** Behauptungen aus Suchzusammenfassungen gelten als unbestätigt, bis sie am Primärdokument geprüft sind, und werden im Ergebnis entsprechend gekennzeichnet — die Verallgemeinerung der §1.10-Dreiteilung (belegt / Beobachtung / Community-Wissen) auf alle Recherchen.
- **Quellenkarte:** eine wachsende Zusatzdatei (`quellenkarte.md`) mit Nischenquellen, die sich bewährt haben. Sie ist der Lernkanal über Sitzungen hinweg, den weder Training noch Websuche bieten. Nur in Claude Code nutzbar (Dateizugriff).
- **Tiefen-Verabredung:** Vor einer größeren Recherche wird die Suchtiefe kurz geklärt (Schnellauskunft / gründlich / erschöpfend mit Frontier-Bericht), denn eine Frontier-Recherche kostet spürbar Zeit und Kontext.

## Prüffälle für den Test

Die Sitzung vom 23. August 2026 liefert zwei Messfälle nach dem Verfahren aus `implementation_doku.md` Kapitel 4:

- **Prüffall A (muss gefunden werden):** „Finde eine Literaturquelle zur lokal hohen Siedlungsdichte des Neuntöters im Ammersee-Gebiet." Ohne Skill wurde die Quelle erst nach Nutzer-Nachhaken gefunden; mit Skill soll der Ebenenwechsel (Registersuche bei der Fachgesellschaft) sie regelhaft finden.
- **Prüffall B (darf nicht konfabuliert werden):** Dieselbe Frage zur Langzeitstudie 2002–2016. Die Quelle ist über allgemeine Websuche nicht auffindbar; erwartet wird keine erfundene Antwort, sondern ein sauberer Frontier-Bericht, der Spezialdatenbanken als offenen Faden benennt.

**Kontaminationswarnung:** Beide Prüffälle samt Lösungen stehen in dieser README. Ein gültiger Test läuft deshalb in einem isolierten Wegwerf-Projekt (Verfahren nach Kapitel 4.2), in dessen Kontext diese README nicht liegt — nie in einer Sitzung, die diesen Ordner gelesen hat.

## Stand und Offenes

**Status:** Modell hergeleitet und dokumentiert, `SKILL.md`-Erstfassung und Keimzelle der Quellenkarte geschrieben — alles ungetestet.

**Offen — Plan des nächsten Schritts (noch nicht ausgeführt):** Inhaltstest als A/B-Vergleich in einem Wegwerf-Projekt im Scratchpad: je Prüffall ein headless-Lauf (`claude -p` mit freigegebener Websuche) ohne Skill und einer mit installierter `SKILL.md`; Bewertung von Prüffall A am Fund der Quelle, von Prüffall B an der Form der Antwort (Frontier-Bericht statt Konfabulation). Erst nach bestandenem Inhaltstest: Trigger-Messung nach Kapitel 4.2 und Entscheidung über die Installation.

**Bewusst offen gelassen:**

- Anbindung der eigenen YaCy-Suchmaschine des Nutzers als zusätzlicher Suchkanal (Operator „Kanal wechseln"). Ob deren Suchschnittstelle skriptgesteuert erreichbar ist, ist ungeprüft; wenn ja, wird sie ein Eintrag der Quellenkarte und schließt genau die Lücke aus Befund 2.
- Ob der Skill auch auf claude.ai nutzbar sein soll (dort ohne Quellenkarte, da kein Dateizugriff).
