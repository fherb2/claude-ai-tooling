# 🚧 tiefen-recherche — Recherche, die nicht zu früh aufgibt

🚧 Erstfassung der `SKILL.md` geschrieben und am 23. August 2026 im **Inhaltstest bestanden** (A/B-Vergleich, headless auf Sonnet — Ergebnis unten). Noch nicht zur Installation freigegeben: Die Trigger-Messung mit Negativkontrolle steht aus, siehe „Stand und Offenes".

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
- **Quellenkarte:** eine wachsende Datei `quellenkarte.md` mit bewährten Nischenquellen — **projektgebunden, nicht Teil des Skills** (Festlegung des Entwicklers vom 23. August 2026). Sie liegt im jeweiligen Projekt und ist dadurch automatisch themenrein; im projektlosen Chat entfällt sie ersatzlos. Vor der Nutzung wird sie dem Nutzer vorgelegt, Neueinträge nur mit seiner Zustimmung. Bewusst **nicht** im Skill-Ordner: Eine globale Karte trüge fachfremde Quellen in jede neue Recherche (verwässert) und erzeugte nach einer Installation zwei auseinanderdriftende Fassungen. Preis der Entscheidung: kein automatischer Lerntransfer über Projektgrenzen — verschmerzbar, weil wiederkehrende Themen ohnehin im selben Projekt wohnen. Beispiel-Einträge, wie sie im ersten Test verdient wurden (Format-Muster): „zobodat.at — zoologisch-botanische Literatur Mitteleuropas; PDFs nach Schema `zobodat.at/pdf/<Zeitschrift>_<Band>_<Seiten>.pdf`; weist automatisierte PDF-Abrufe teils mit HTTP 403 ab" und „og-bayern.de — Register des Ornithologischen Anzeigers; HTML-Register besser durchsuchbar als die Register-PDFs".
- **Tiefen-Verabredung:** Vor einer größeren Recherche wird die Suchtiefe kurz geklärt (Schnellauskunft / gründlich / erschöpfend mit Frontier-Bericht), denn eine Frontier-Recherche kostet spürbar Zeit und Kontext.

## Prüffälle und Messergebnis

Die Sitzung vom 23. August 2026 liefert zwei Messfälle nach dem Verfahren aus `implementation_doku.md` Kapitel 4:

- **Prüffall A (muss gefunden werden):** „Finde eine Literaturquelle zur lokal hohen Siedlungsdichte des Neuntöters im Ammersee-Gebiet." Ohne Skill wurde die Quelle erst nach Nutzer-Nachhaken gefunden; mit Skill soll der Ebenenwechsel (Registersuche bei der Fachgesellschaft) sie regelhaft finden.
- **Prüffall B (darf nicht konfabuliert werden):** Dieselbe Frage zur Langzeitstudie 2002–2016. Die Quelle ist über allgemeine Websuche nicht auffindbar; erwartet wird keine erfundene Antwort, sondern ein sauberer Frontier-Bericht, der Spezialdatenbanken als offenen Faden benennt.

**Kontaminationswarnung:** Beide Prüffälle samt Lösungen stehen in dieser README. Ein gültiger Test läuft deshalb in einem isolierten Wegwerf-Projekt (Verfahren nach Kapitel 4.2), in dessen Kontext diese README nicht liegt — nie in einer Sitzung, die diesen Ordner gelesen hat.

### Messergebnis vom 23. August 2026 (Beobachtung am laufenden System)

Aufbau: vier headless-Läufe (`claude -p`, Modell Sonnet, freigegeben nur WebSearch/WebFetch) in vier isolierten Wegwerf-Projekten im Scratchpad; „mit Skill" heißt `SKILL.md` samt `quellenkarte.md` als Projekt-Skill installiert. Ausgewertet wurde am `stream-json`-Transkript, nicht an der Selbstauskunft. Je Bedingung ein Lauf — Richtungsbefund, kein Beweis.

| Lauf | Ergebnis | Aufwand |
| --- | --- | --- |
| A ohne Skill | Quelle gefunden (nach zehn Suchanläufen samt Autoren-Irrweg schließlich über das Register); Zitat aus dem Register abgeschrieben, Inhalt eingestandenermaßen nicht verifiziert | 207 s, 15 Züge |
| A mit Skill | Trigger feuerte von selbst über die Description; Quelle gefunden **und am gescannten Original verifiziert** — vollständigeres Zitat (Wink, Ursula 2008, Ornithol. Anz. 47, S. 66–76) samt Abstract-Inhalt; Status „belegt" korrekt gekennzeichnet | 154 s, 13 Züge |
| B ohne Skill | **kein Ergebnis**: 22 hartnäckige Suchanläufe, dann Sackgasse — der Lauf endete mit einer Rückfrage nach einer Bash-Freigabe, die headless niemand beantworten kann. Immerhin: nichts erfunden | 280 s, 36 Züge |
| B mit Skill | Trigger feuerte; **Studie gefunden**: Wink, U., „Bestandsabnahmen beim Neuntöter …, Langzeitstudie 2002–2016", Ornithol. Anz. Bd. 55, Heft 2/3 (2016/2017), belegt am Inhaltsverzeichnis des Herausgebers. Fundweg über die Operatoren: Autorin des 2008er-Artikels als Faden verfolgt, Herausgeber-Inhaltsverzeichnisse durchsucht, Zobodat-URLs nach Schema konstruiert. Kursierende Revierzahlen („81→34") wurden gesehen und korrekt als **unbestätigt** gekennzeichnet statt übernommen; Rest-Frontier sauber benannt (fehlende Seitenzahl; Zobodat weist automatisierte PDF-Abrufe mit HTTP 403 ab) | 523 s, 62 Züge |

Deutung: Prüffall A trennt schwach — die Frageformulierung liegt nahe am Titel, beide Bedingungen fanden die Quelle; der Skill brachte dort Effizienz und Verifikationstiefe. Prüffall B ist der eigentliche Beleg: Fund statt Nichts, dazu nachgewiesene Konfabulationsfestigkeit und ein regelkonformer Frontier-Bericht. Das übertrifft die Erwartung (erwartet war für B nur der saubere Frontier-Bericht). Nebenbefund: Der Trigger feuerte in beiden mit-Läufen ungefragt auf Sonnet — das ersetzt aber keine Negativkontrolle.

### Zweiter Test vom 23. August 2026: fremdes Fachgebiet, offene Sammelaufgabe

Ein Einzellauf (headless Sonnet, mit Skill; zusätzlich Write freigegeben) zu einer Sammelrecherche in fremdem Feld und fremder Sprache: Gartenbahnen in Tschechien, Spur-1-Anlagen, Gartenbahn-/„Großbahn"-Treffen; Ergebnis als Markdown-Liste mit Erklärtext und Link je Fund. Dauer 731 s, 59 Züge, 22 Suchen, 26 Abrufe.

**Was funktionierte:** Der Sprachwechsel ins Tschechische kam mit der allerersten Suche („zahradní železnice", „rozchod", „sraz"), durchgehend dreisprachig weitergeführt; Entitätenverfolgung und `site:`-Eingrenzung nachweisbar; das Ergebnisdokument unterschied fachlich sauber Spur G von Spur 1 (gleiche 45-mm-Schiene, anderer Maßstab) und Modell- von befahrbaren Parkbahnen; Widersprüche in Quellen (Maßstab „1:29" vs. „1:32") wurden benannt statt geglättet; die Frontier nannte konkrete nächste Schritte (Kontaktadresse, Facebook als nicht durchsuchter Kanal, G1MRA-Anfrage). Nebenbefund zur Umgebung: WebFetch rüstet HTTP zwingend auf HTTPS auf — reine HTTP-Altseiten (hier `steamer.cz`) sind damit unerreichbar; der Lauf hat das erkannt, erklärt und den Fund korrekt herabgestuft statt ihn zu verlieren.

**Gefundene Schwäche — Etiketten-Inflation bei „belegt":** Ein mechanischer Abgleich aller 23 Dokument-Links gegen die tatsächlich abgerufenen URLs zeigt: 8 Links wurden nie abgerufen, und bei etwa 4 Einträgen (u. a. Drásov, Zásmuky, G1MRA) steht trotzdem „belegt" — die Angaben stammen dort nur aus Suchtreffer-Zusammenfassungen. Erfunden war nichts, und viele Einträge waren korrekt konservativ gekennzeichnet; aber die Kennzeichnungsdisziplin lässt bei Sammellisten messbar nach. Möglicher Fix (noch nicht beschlossen, siehe Offen): eine Selbsttest-Klausel analog zum Marken-Selbsttest von temp-debug-code — vor Abgabe prüft die Instanz für jeden als „belegt" markierten Fund, ob dessen Quelle in diesem Lauf tatsächlich abgerufen wurde.

## Stand und Offenes

**Status:** Modell dokumentiert, `SKILL.md`-Erstfassung geschrieben, zwei Inhaltstests gelaufen (Auffinde-Härtefall bestanden; Sammelrecherche gut mit einer gefundenen Schwäche). Quellenkarte per Festlegung vom 23. August 2026 aus dem Skill-Ordner entfernt und auf Projektbindung umgestellt.

**Offen:**

- Entscheidung über die Selbsttest-Klausel gegen Etiketten-Inflation (siehe zweiter Test): „belegt" nur, wenn die Quelle im Lauf abgerufen wurde — mechanisch prüfbar vor Abgabe.
- Trigger-Messung nach Kapitel 4.2 vervollständigen: Negativkontrolle (themenfremder Prompt darf nicht feuern) und implizite Stufe (Rechercheauftrag ohne Wortlaut-Nähe zur Description). Die Positivfälle sind durch die Inhaltstests bereits abgedeckt.
- Danach Installationsentscheidung (Zielort, Emoji-Präfix entfällt beim Fertigwerden) und Entscheidung, ob ein stiller Trigger nötig ist oder die Description trägt.

**Bewusst offen gelassen:**

- Anbindung der eigenen YaCy-Suchmaschine des Nutzers als zusätzlicher Suchkanal (Operator „Kanal wechseln"). Ob deren Suchschnittstelle skriptgesteuert erreichbar ist, ist ungeprüft; wenn ja, wird sie ein Eintrag der Quellenkarte und schließt genau die Lücke aus Befund 2.
- Ob der Skill auch auf claude.ai nutzbar sein soll (dort ohne Quellenkarte, da kein Dateizugriff).
