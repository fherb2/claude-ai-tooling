## 🚷 Inventar der bisherigen Arbeitsanweisungen (claude.ai, Sonnet 4.5/4.6)

Dieses Inventar erschließt die acht Dateien dieses Ordners — die Projektanweisungen, die im vergangenen Jahr auf claude.ai (Projektwissen bzw. Chat-Anfang) verwendet wurden, und die Vorlage, aus der sie hervorgingen. Zweck: Alle enthaltenen Anweisungen so nebeneinanderzustellen, dass sich die Aussagen quellenübergreifend vergleichen lassen und entschieden werden kann, was für welche künftigen Einsatzfälle (Claude Code, Skills, Projekt-CLAUDE.md, weiterhin claude.ai) in welcher Form neu zusammengestellt wird.

Aufbau: Kapitel 1 beschreibt die Quelldateien, Kapitel 2 ihre Verwandtschaft, Kapitel 3 gibt die Themenmatrix als Überblick, Kapitel 4 ist das eigentliche Inventar — jede noch offene Anweisung als eigener, nummerierter Eintrag mit Fundstellen, Varianten und einer Einordnung gegenüber dem heutigen Regelwerk. Kapitel 5 fasst die Einordnungen als Entscheidungsvorlage zusammen, Kapitel 6 sammelt die bereits verarbeiteten Einträge. Die Einordnungen sind Einschätzungen als Arbeitsgrundlage, keine Entscheidungen — die trifft der Entwickler.

Erstellt am 22. August 2026. Die Nummern T1–T27 sind stabil: Ein Eintrag behält seine Nummer für immer, auch wenn er erledigt ist und nach Kapitel 6 wandert (analog zur Fahrplan-Nummerierungsregel des Repos). Jede Nummer kommt genau einmal vor — in Kapitel 4 oder in Kapitel 6.

**Verarbeitete Einträge stehen in Kapitel 6, nicht mehr hier in Kapitel 4.** Betroffen sind T1, T2, T3, T4, T5, T6, T7, T8, T9, T10, T11, T12, T13, T14, T15 und T16.

## 1 Die Quelldateien

| Kürzel | Datei                                                                      | Inhaltlicher Zuschnitt                                                                                                                                                                                    |
| ------- | -------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| ALLG    | `claude.ai-pro-allgemein.txt`                                              | Projektunabhängige Kurzfassung: Sprachen und Prosa-Code-Grenze. Nur 2 Absätze.                                                                                                                          |
| MOD     | `modellbahn-fahrpult.txt`                                                  | Projekt in der Findungsphase: Arbeitsmodus (Alternativen, Recherche, Generalisierbarkeit) plus Artefakt-Regeln, auf Code**und** Dokumente verallgemeinert. Kein Sprachen-, Debugging- oder Protokollteil. |
| BIRD    | `birdnet-audio-walker.txt`                                                 | Vollständiger „Allgemeine Anweisungen“-Block in der erweiterten Fassung (siehe Kapitel 2), davor die Chat-Suche-Einschränkung.                                                                        |
| CAM     | `GigE-CameraStreamingServer.txt` und `RTCP Camera Streamer and Player.txt` | **Byte-identisch** (per `cmp` geprüft, 22.08.2026) — im Folgenden als eine Quelle behandelt. „Allgemeine Anweisungen“-Block in der Basisfassung.                                                      |
| MUSTER  | `muster-fuer-projektanweisungen.md`                                        | Die **Vorlage**, die der Entwickler pflegte und in neue Projekte kopierte — keine Anweisung eines einzelnen Projekts. **Byte-identisch mit CAM** (per `cmp` geprüft, 29.08.2026) und deshalb ohne eigene Spalte in der Themenmatrix; ihr Beitrag ist die Herkunft, nicht der Inhalt. |
| SCH‑A  | `Scheludko-Zelle allgemein.txt`                                            | Projektspezifischer Kopf (Planungsphase, Hintergrunddateien) plus „Allgemeine Anweisungen“-Block in einer eigenständigen Zwischenvariante.                                                             |
| SCH‑B  | `Scheludko-Zelle Bildverarbeitung.txt`                                     | Bis auf**einen Satz** textgleich mit BIRD (per Diff geprüft): SCH‑B ergänzt im Vorher/Ersetzen-Schema die Regel, „Vorher“/„Nachher“ vor den Block statt hinein zu schreiben.                       |
| LOK     | `CLAUDE_lokal.md`                                                          | Neuaufbau der globalen `~/.claude/CLAUDE.md` vom 31. August 2026: oben Snippets und stille Trigger (der verteilte Lösungsstand), darunter „NOCH EINZUORDNEN“ — **nur dieser Teil ist Inventar** (T28–T50 und T22). |
| WEB     | `CLAUDE_web.md`                                                            | Neuaufbau der Anweisungsfelder beider claude.ai-Konten (Pro und Team führen denselben Text), gleicher Aufbau; Inventar ist auch hier nur der „NOCH EINZUORDNEN“-Teil. |

**Stand der Dateien:** Die sechs ursprünglichen Quelldateien sind abgearbeitet und aus dem Arbeitsordner entfernt — die beiden byte-gleichen CAM-Dateien am 27. August 2026, ALLG, MOD, BIRD, SCH‑A und SCH‑B am 31. August 2026, jeweils nachdem ihre letzten Posten einzeln entschieden waren. Ihre unveränderten Fassungen liegen weiter in `original/`. Im Arbeitsordner verblieben ist `muster-fuer-projektanweisungen.md` mit dem Testblock T17–T19.

Die Dateisystem-Daten stammen alle vom Kopiertag und taugen nicht zur zeitlichen Einordnung. Die Chronologie der Fassungen ist unten aus Textbefunden erschlossen und entsprechend als Vermutung gekennzeichnet.

## 2 Verwandtschaft der Texte

Vier der sechs unterschiedlichen Texte (BIRD, CAM, SCH‑A, SCH‑B) tragen denselben wiederverwendeten Block „Allgemeine Anweisungen zur Projektarbeit und zum Coding“ in drei Ausbaustufen. MOD und ALLG stehen daneben: MOD übernimmt nur die Artefakt-Regeln (verallgemeinert auf Dokumente), ALLG ist eine davon unabhängige Minimalfassung für die projektübergreifende Ebene.

MUSTER zählt nicht als siebter Text, sondern erklärt die Verwandtschaft: Es ist die Vorlage, die der Entwickler pflegte und beim Anlegen eines Projekts hineinkopierte — und es ist byte-identisch mit CAM. Damit ist belegt, dass die beiden Kamera-Projekte die Vorlage unverändert übernahmen; die Basisfassung des Blocks entstand also nicht in einem Projekt, sondern war die Vorlage selbst. Die späteren Ausbaustufen wuchsen umgekehrt in den Projekten und flossen nicht in die Vorlage zurück — sonst stünden sie heute in MUSTER.

**Vermutete Reihenfolge der Ausbaustufen** (Textbefund, nicht belegt — bei Bedarf vom Entwickler zu bestätigen):

1. **CAM (Basisfassung, byte-identisch mit der Vorlage MUSTER):** noch keine DEBUG-Kennzeichnung, kein Vorher/Ersetzen-Schema, Status-Protokoll ohne Chat-Referenzen, Teil-Artefakt-Regel (max. ~2 A4-Seiten) aktiv, debug-Parameter als Pflicht-Dictionary mit Guard `debug is not None`.
2. **SCH‑A (Zwischenvariante):** DEBUG-Kennzeichnung und erweitertes Status-Protokoll vorhanden; die Teil-Artefakt-Regel ist ausdrücklich **ausgeklammert** („Es scheinen inzwischen auch längere Artefakte zu funktionieren“) und im Wortlaut in Klammern konserviert; statt des Vorher/Ersetzen-Schemas nur die Regel, Einfügestellen inhaltlich (Funktionsname) statt per Zeilennummer zu beschreiben; als Einzige eine Änderungs-Ausnahme für Artefakt-Snippets unter 30 Zeilen.
3. **BIRD und SCH‑B (erweiterte Fassung):** Vorher/Ersetzen-Schema ausformuliert, explizite Artefakt-Kriterien (wann Artefakt, wann Chat), DEBUG-Kennzeichnung in der ausführlichsten Form, Status-Protokoll mit Chat-Referenzen und „Nur, wenn bereits erledigt“-Klausel, Konzept-Artefakte mit Chatlängen-Vorsorge. SCH‑B ist BIRD plus ein Satz (Beschriftung außerhalb des Blocks) — mutmaßlich die jüngste Fassung des Blocks.
4. **MOD:** übernimmt die erweiterte Artefakt-Mechanik aus BIRD/SCH‑B und verallgemeinert sie durchgängig von „Code“ auf „Code/Dokumenteninhalte“ — passend zu einem Projekt, das noch keine Software schreibt.

LOK und WEB stehen außerhalb dieser Verwandtschaft: Sie sind am 31. August 2026 aus den Snippets des Repos und dem Restbestand der alten Anweisungen neu aufgebaut worden und sind die jüngsten Quellen dieses Inventars.

## 3 Themenmatrix

Legende der Quellenspalten: ✓ enthalten · (✓) in abgewandelter Form enthalten · ⊘ ausdrücklich ausgeklammert · – nicht enthalten. Die Varianten stehen beim jeweiligen Eintrag — in Kapitel 4, für die verarbeiteten Themen in Kapitel 6.

Die schmale Spalte ohne Überschrift hinter der Nummer ist der Erledigt-Vermerk: **✅ heißt abgearbeitet** — der Posten ist in einen Skill überführt (oder bewusst verworfen), und seine Passagen sind aus den Quelldateien entfernt. Ohne Vermerk steht er noch offen.

| Nr. |  | Thema                                    | ALLG | MOD  | BIRD | CAM  | SCH‑A | SCH‑B | LOK | WEB |
| --- | --- | ---------------------------------------- | ---- | ---- | ---- | ---- | ------ | ------ | --- | --- |
| T1  | ✅ | Chat Deutsch, Duzen                      | (✓) | –   | ✓   | ✓   | ✓     | ✓     | –   | –   |
| T2  | ✅ | Code Englisch (inkl. Kommentare)         | (✓) | –   | ✓   | ✓   | ✓     | ✓     | –   | –   |
| T3  | ✅ | Dokumentsprache Deutsch/projektabhängig | ✓   | –   | –   | –   | –     | –     | –   | –   |
| T4  | ✅ | Chat-Suche nur im Projekt                | –   | –   | ✓   | –   | ✓     | ✓     | –   | –   |
| T5  | ✅ | Vorwissen-Definition                     | –   | –   | ✓   | –   | ✓     | ✓     | –   | –   |
| T6  | ✅ | Ankündigen + Freigabe vor Artefakt      | –   | ✓   | ✓   | ✓   | ✓     | ✓     | –   | –   |
| T7  | ✅ | Offene Fragen vor Artefaktbeginn klären | –   | ✓   | ✓   | (✓) | ✓     | ✓     | –   | –   |
| T8  | ✅ | Wann Artefakt, wann Chat                 | –   | (✓) | ✓   | (✓) | (✓)   | ✓     | –   | –   |
| T9  | ✅ | Artefakte nicht nachträglich ändern    | –   | (✓) | ✓   | (✓) | (✓)   | ✓     | –   | –   |
| T10 | ✅ | Vorher/Ersetzen-Schema                   | –   | (✓) | ✓   | –   | –     | (✓)   | –   | –   |
| T11 | ✅ | Teil-Artefakte ab ~2 A4-Seiten           | –   | –   | –   | ✓   | ⊘     | –     | –   | –   |
| T12 | ✅ | Nur besprochenen, notwendigen Code       | –   | –   | ✓   | ✓   | ✓     | ✓     | –   | –   |
| T13 | ✅ | Funktionsumfang nie ungefragt erweitern  | –   | –   | ✓   | ✓   | ✓     | ✓     | –   | –   |
| T14 | ✅ | Debug-Einzeiler`python -c`               | –   | –   | ✓   | ✓   | ✓     | ✓     | –   | –   |
| T15 | ✅ | Umfassendes Debugging als eigenes Skript | –   | –   | ✓   | ✓   | ✓     | ✓     | –   | –   |
| T16 | ✅ | DEBUG-Kennzeichnung von Probe-Code       | –   | –   | ✓   | –   | (✓)   | ✓     | –   | –   |
| T17 |  | pytest: CI-fähig und CLI-startbar       | –   | –   | ✓   | ✓   | ✓     | ✓     | –   | –   |
| T18 |  | Testfreundliche Funktionsanlage          | –   | –   | ✓   | ✓   | ✓     | ✓     | –   | –   |
| T19 |  | debug-Parameter-Konvention               | –   | –   | ✓   | (✓) | ✓     | ✓     | –   | –   |
| T20 | ✅ | Status Protokoll                         | –   | –   | ✓   | (✓) | ✓     | ✓     | –   | –   |
| T21 | ✅ | Konzept-Artefakte                        | –   | –   | ✓   | (✓) | (✓)   | ✓     | –   | –   |
| T22 |  | Prosa-Code-Grenze                        | ✓   | –   | –   | –   | –     | –     | ✓   | ✓   |
| T23 | ✅ | Findungsphase: Alternativen erwünscht   | –   | ✓   | –   | –   | –     | –     | –   | –   |
| T24 | ✅ | Planungsphase: erklären statt kodieren  | –   | –   | –   | –   | ✓     | –     | –   | –   |
| T25 | ✅ | Generalisierbarkeit von Lösungen        | –   | ✓   | –   | –   | –     | –     | –   | –   |
| T26 | ✅ | Alte Chats und Internet als Quellen      | –   | ✓   | –   | –   | –     | –     | –   | –   |
| T27 | ✅ | Projektspezifische Hintergrunddateien    | –   | –   | –   | –   | ✓     | –     | –   | –   |
| T28 |  | Projekt-CLAUDE.md ergänzt, kopiert nicht | –   | –   | –   | –   | –     | –     | ✓   | –   |
| T29 |  | Computer-Fragen zuerst verorten          | –   | –   | –   | –   | –     | –     | ✓   | ✓   |
| T30 |  | Änderungen außerhalb nur mit Freigabe    | –   | –   | –   | –   | –     | –     | ✓   | ✓   |
| T31 |  | LFS-Prüfung beim ersten Git-Kontakt      | –   | –   | –   | –   | –     | –     | ✓   | –   |
| T32 |  | Markdown: ein Absatz, eine Zeile         | –   | –   | –   | –   | –     | –     | ✓   | –   |
| T33 |  | Deutsche Prosa nicht per Heredoc         | –   | –   | –   | –   | –     | –     | ✓   | –   |
| T34 |  | Projektwurzel aufgeräumt                 | –   | –   | –   | –   | –     | –     | ✓   | –   |
| T35 |  | Projektordner .claude/                   | –   | –   | –   | –   | –     | –     | ✓   | –   |
| T36 |  | Plan vor Ausführung                      | –   | –   | –   | –   | –     | –     | ✓   | ✓   |
| T37 |  | Abweichung heißt anhalten                | –   | –   | –   | –   | –     | –     | ✓   | ✓   |
| T38 |  | Rückfragen                               | –   | –   | –   | –   | –     | –     | ✓   | –   |
| T39 |  | Erlaubt / nie ohne Zustimmung            | –   | –   | –   | –   | –     | –     | ✓   | –   |
| T40 |  | Werkbank-Modell (Commits und Branches)   | –   | –   | –   | –   | –     | –     | ✓   | –   |
| T41 |  | Kleinigkeiten: Regel statt Rückfrage     | –   | –   | –   | –   | –     | –     | ✓   | –   |
| T42 |  | Kontext-Haushalt                         | –   | –   | –   | –   | –     | –     | ✓   | –   |
| T43 |  | Anthropic-Werkzeuge: Beleglage           | –   | –   | –   | –   | –     | –     | ✓   | –   |
| T44 |  | Umgang mit importierten Chats            | –   | –   | –   | –   | –     | –     | ✓   | –   |
| T45 |  | Ablage/Format fremder Chat-Quellen       | –   | –   | –   | –   | –     | –     | ✓   | –   |
| T46 |  | Methodik: Geltung und Phasen             | –   | –   | –   | –   | –     | –     | ✓   | –   |
| T47 |  | Dokumentstruktur                         | –   | –   | –   | –   | –     | –     | ✓   | –   |
| T48 |  | Die drei Segmente                        | –   | –   | –   | –   | –     | –     | ✓   | –   |
| T49 |  | Arbeitsschleife der Implementierung      | –   | –   | –   | –   | –     | –     | ✓   | –   |
| T50 |  | Fahrplan und Status                      | –   | –   | –   | –   | –     | –     | ✓   | –   |

Die Matrix ist vollständig und bleibt es: Sie bildet ab, was die Quelldateien ursprünglich enthielten, unabhängig davon, ob ein Thema inzwischen verarbeitet und aus ihnen entfernt ist. Wer den ursprünglichen Wortlaut braucht, findet ihn im Unterordner `original/`. Die Einträge der abgehakten Posten stehen in Kapitel 6.

## 4 Die Anweisungen im Einzelnen

Jeder Eintrag nennt die Kernaussage, die Fundstellen mit ihren Varianten und eine Einordnung gegenüber dem heutigen Regelwerk (globale `~/.claude/CLAUDE.md`, hier „§…“, und die Skills dieses Repos). Die Einordnung trägt eine von vier Kategorien: **[claude.ai-Mechanik]** — an das Web-Frontend gebunden, in Claude Code gegenstandslos; **[abgedeckt]** — inhaltlich im heutigen Regelwerk enthalten; **[teilweise abgedeckt]**; **[nicht abgedeckt]** — Kandidat für eine Neuzusammenstellung.

Seit dem 31. August 2026 ist die globale `~/.claude/CLAUDE.md` selbst inventarisiert (Quelle LOK). Die „§…“-Verweise älterer Einträge zeigen damit in Inventar-Material: §1.9 ist T42, §2.1 ist T46, §2.2 ist T22.

### D Debugging und Tests

#### T17 Unit-Tests mit pytest: CI-fähig und von der Kommandozeile startbar

**Aussage:** Für implementierte (nicht-experimentelle) Funktionen weist der Nutzer Unit-Tests für pytest an. Der Testcode muss in CI laufen **und** einzeln von der Kommandozeile startbar sein; für Letzteres darf er Diagnoseinformationen ausgeben (auch wenn CI sie mit ausgibt).

**Fundstellen:** BIRD, CAM, SCH‑A, SCH‑B im Kern wortgleich.

**Einordnung:** **[nicht abgedeckt]** — weder die globale CLAUDE.md noch ein vorhandener Skill regelt Test-Konventionen. Kandidat für einen neuen Skill (etwa „Python-Test-Konventionen“), zusammen mit T18 und T19.

#### T18 Testfreundliche Funktionsanlage

**Aussage:** Funktionen so anlegen, dass sie leicht testbar sind: Funktionen, die ohne Klasse auskommen, auf die oberste Modulebene; verschachtelte Funktionsdefinitionen vermeiden — außer die Funktion ist so simpel, dass ein eigener Test unnötig ist.

**Fundstellen:** BIRD, CAM, SCH‑A, SCH‑B wortgleich.

**Einordnung:** **[nicht abgedeckt]** — Kandidat, zusammen mit T17/T19. Inhaltlich benachbart zu `common-code-generation` (dort könnte es als Abschnitt ebenso hinpassen wie in einen eigenen Test-Skill — Zuordnungsentscheidung offen).

#### T19 Konvention für einen optionalen debug-Parameter

**Aussage:** Wenn zusätzlicher Test-/Debug-Code in einer Funktion sinnvoll ist, bekommt sie über `**kwargs` am Schnittstellenende einen optionalen Parameter `debug` (ein Dictionary, das beliebige testspezifische Werte transportiert, ohne die normale Schnittstelle zu verändern). Der Testcode in der Funktion wird mit einem `if __debug__ and …:`-Guard eingefasst, damit `python -O` ihn nicht kompiliert.

**Fundstellen und Varianten — die beiden Fassungen sind untereinander unverträglich:**

- **CAM (Frühform):** an `debug` ist **immer ein Dictionary** zu übergeben (für einfache Fälle ein leeres); Guard: `if __debug__ and debug is not None:`.
- **BIRD, SCH‑A, SCH‑B (spätere Form):** als Wert sind **None oder ein Dictionary** zulässig; Guard: `if __debug__ and "debug" in kwargs:`.

Die Guards verhalten sich unterschiedlich, sobald `debug=None` übergeben wird (die spätere Form aktiviert den Testcode dann, die frühe nicht), und die frühe Fassung prüft eine lokale Variable, wo die spätere den kwargs-Eintrag prüft. Vor einer Übernahme ist genau eine Fassung festzulegen.

**Einordnung:** **[nicht abgedeckt]** — Kandidat für den Test-Skill (T17/T18). Zu klären ist dabei auch das Verhältnis zu T16 (Kapitel 6), heute im Skill `temp-debug-code`: T19 beschreibt **dauerhaft** im Code verbleibende Debug-Pfade, die dieser Skill ausdrücklich von seinen Regeln ausnimmt — die beiden ergänzen sich, überschneiden sich also nicht.

### G Anweisungsebenen und Projektspezifik

#### T28 Projekt-CLAUDE.md ergänzt, kopiert nicht

**Aussage:** Die projekteigene `<projekt>/.claude/CLAUDE.md` ist keine Kopie der globalen Datei, sondern enthält ausschließlich Abweichendes und Zusätzliches; projektspezifische Festlegungen stehen nie global, sondern dort bzw. in Segment 2 der Implementierungsdoku.

**Fundstellen:** nur LOK (Rest der alten Vorrede).

**Einordnung:** **[teilweise abgedeckt]** — das Snippet „Vorrang der Anweisungsebenen" regelt, welche Ebene gewinnt, aber nicht, was auf welche Ebene **gehört**. Der zweite Teil ist die eigentliche Hygiene-Regel und nirgends sonst festgehalten.

### H Umgebung und Wirkungsgrenzen

#### T29 Computer-Fragen zuerst verorten

**Aussage:** Bei einer Frage oder einem Problem zu einem Computer zuerst klären, ob der Computer gemeint ist, auf dem diese Instanz läuft, bevor selbständig darauf gesucht wird.

**Fundstellen:** LOK (Allgemeine Regeln) und WEB, wortverwandt.

**Einordnung:** **[nicht abgedeckt]** — einer der wenigen Posten, die in beiden Umgebungen wörtlich gebraucht werden.

#### T30 Keine Änderungen außerhalb des freigegebenen Bereichs

**Aussage:** Änderungen außerhalb des freigegebenen Ordners bzw. der Projektwurzel und Konfigurationsänderungen an Software oder laufenden Systemkomponenten nur nach Erklärung und ausdrücklicher Freigabe.

**Fundstellen:** LOK (Allgemeine Regeln und 1.2, dort in der am 31. August verallgemeinerten Fassung) und WEB.

**Einordnung:** **[teilweise abgedeckt]** — das Freigaben-Snippet regelt die Freigabe-Semantik, nicht die räumliche Grenze. Schutzregel-Charakter: Nach der Begründungslinie von `common-code-generation` („ein Skill wird nur wahrscheinlich geladen, eine Schutzregel muss sicher greifen") ist das eher Anweisungs- als Skill-Material.

#### T31 LFS-Prüfung beim ersten Git-Kontakt

**Aussage:** In jeder Sitzung bei der ersten Anwendung eines Git-Befehls prüfen, ob das Projekt LFS vorsieht (`.gitattributes`); wenn ja und git-lfs fehlt, dringend hinweisen und die Installation anbieten.

**Fundstellen:** nur LOK.

**Einordnung:** **[nicht abgedeckt]** — Kandidat für `parallel-sessions` ist es nicht (anderes Thema); denkbar als Mini-Baustein eines künftigen Git-Skills oder als Snippet.

#### T34 Projektwurzel aufgeräumt

**Aussage:** Werkzeug- und Konfigurationsdateien liegen in ihren Unterordnern (`.claude/`, `.vscode/`, …); in der Wurzel steht nur, was seinen Ablageort nicht wählen kann (`.gitignore`, …).

**Fundstellen:** nur LOK (1.2, Fassung vom 31. August).

**Einordnung:** **[nicht abgedeckt]**.

#### T35 Der Projektordner `.claude/`

**Aussage:** `<projekt>/.claude/` darf angelegt werden; `arbeitsdaten.json` trägt sitzungsübergreifende Angaben (deutscher Name bewusst, gegen Kollision mit Engine-Dateien); der Ordner wird mitversioniert (Arbeit über mehrere Rechner), die `.gitignore` darf ihn nicht ausschließen; Credentials gehören nicht hinein, Funde werden sofort gemeldet; zwischen Rechnern zu teilende Berechtigungen gehören in `.claude/settings.json`, nicht in `settings.local.json` (Workspace-Trust, nicht-interaktiver Modus).

**Fundstellen:** nur LOK (1.2).

**Einordnung:** **[nicht abgedeckt]** — hängt an T40: `arbeitsdaten.json` dient dort dem Namen des Hauptpfads. Fällt T40, ist der Rest eigenständig tragfähig.

### A Sprache und Kontextquellen — wieder geöffnet am 31. August 2026

Die Gruppe war mit T1, T3 und T4 geschlossen; die neuen Quelldateien tragen zwei weitere Sprach- und Schreibregeln.

#### T32 Markdown-Formatierung: ein Absatz, eine Zeile

**Aussage:** Markdown-Dateien standardmäßig mit einem Absatz je Zeile; CLAUDE.md-Dateien ausgenommen (von Hand sinnvoll umbrochen).

**Fundstellen:** nur LOK (1.1).

**Einordnung:** **[nicht abgedeckt]** als Anweisung — die `.markdownlint.jsonc` dieses Repos setzt die Folge (MD013 aus) bereits um, aber nur hier. Kandidat für ein Snippet oder einen Schreibregel-Skill.

#### T33 Deutsche Prosa nicht durch Heredocs

**Aussage:** Deutsche Prosa wird mit dem Write-/Edit-Werkzeug in Dateien geschrieben, nie über ein Skript in einem Heredoc — deutsche Anführungszeichen und Gedankenstriche beenden dort Zeichenketten vorzeitig (dreimal passiert am 13./14. August 2026); deutsche Anführungszeichen immer paarweise.

**Fundstellen:** nur LOK (1.1).

**Einordnung:** **[nicht abgedeckt]** — Kandidat für `common-code-generation` ist es nur bedingt (es geht um Prosa in Dateien, nicht um Code); tragfähig auch als Snippet. Die Erfahrung dieses Repos bestätigt die Regel laufend.

### I Plan-, Frage- und Freigabedisziplin

#### T36 Plan vor Ausführung

**Aussage:** Keine Dateiänderung ohne vorgelegten, vollständigen und erklärenden Plan. Vollständig heißt: je Datei, je Stelle — was entfällt, was hinzukommt, warum, mit unmittelbaren und mittelbaren Auswirkungen, ausdrücklich auch über das Arbeitsziel hinaus. Der Plan beschreibt Absicht und Wirkung, nicht den Wortlaut (Dokumente: Passage für Passage; Code: adressierbare Einheiten statt Kontrollfluss); ist das nicht möglich, ist der Schritt zu groß. Der Plan umfasst genau den nächsten Schritt. WEB ergänzt: Ob der Plan als Datei oder im Chat vorgelegt wird, entscheidet der Nutzer — vorher fragen.

**Fundstellen:** LOK (1.3) ausführlich; WEB als Kurzfassung mit dem Ablage-Zusatz. In beiden ist der Freigabe-Teil bereits durch Verweis auf das Snippet ersetzt (31. August 2026).

**Einordnung:** **[teilweise abgedeckt]** — die Freigabe-Semantik trägt das Snippet „Freigaben werden erteilt, nicht gefolgert"; die Plan-Pflicht selbst, die Vollständigkeitsdefinition und die Prosa-statt-Code-Regel stehen nirgends sonst. Schutzregel-Charakter wie T30.

#### T37 Abweichung heißt anhalten

**Aussage:** Trägt der zugestimmte Plan bei der Ausführung nicht: anhalten, Lage schildern, neu fragen — nie stillschweigend abweichen.

**Fundstellen:** LOK (1.4) und WEB.

**Einordnung:** **[nicht abgedeckt]** — Gegenstück zum Freigaben-Snippet, dort aber nicht enthalten.

#### T38 Rückfragen

**Aussage:** Vor jeder Rückfrage prüfen, ob die Projektdokumentation antwortet; Mehrdeutigkeit der Doku ist ein Defekt (benennen, Korrektur vorschlagen); widersprechen sich Code und Doku: anhalten und fragen — beide Seiten können falsch sein.

**Fundstellen:** nur LOK (1.5).

**Einordnung:** **[nicht abgedeckt]**.

#### T39 Ohne Rückfrage erlaubt / nie ohne Zustimmung

**Aussage:** Erlaubt ohne Nachfrage: Lesen, Suchen, Tests, kurzlaufende Analysen ohne Seiteneffekte, Checkpoint-Commits auf der Werkbank (T40). Nie ohne Zustimmung: push, Pakete installieren/aktualisieren, Container bauen, langlaufende Jobs (insbesondere GPU), Dateien löschen. Projekte dürfen verschärfen.

**Fundstellen:** nur LOK (1.6).

**Einordnung:** **[teilweise abgedeckt]** — `parallel-sessions` führt für Worktree-Projekte eigene, vorgehende Freigabestufen; die konkreten Listen hier gelten darüber hinaus und stehen nirgends sonst. Der Werkbank-Punkt hängt an T40.

#### T41 Wiederkehrende Kleinigkeiten: Regel statt Rückfrage

**Aussage:** Keine Plan-Ausnahme für Trivialänderungen; wiederholt sich dieselbe Kleinigkeit, wird die zugrunde liegende Regel einmal geklärt und am dafür vorgesehenen Ort festgeschrieben — danach entfällt die Rückfrage dauerhaft.

**Fundstellen:** nur LOK (1.8).

**Einordnung:** **[nicht abgedeckt]**.

### J Git-Arbeitsmodell ohne Worktree-Vereinbarung

#### T40 Commits und Branches: das Werkbank-Modell

**Aussage:** Für Projekte ohne `.claude/git-worktree-model.json`: zwei Branches (Hauptpfad des Nutzers, Werkbank `claude-workbench` für Claude), fünf Prüfschritte vor jedem Wechsel auf die Werkbank (fetch/status, Hauptpfad erfragen, Vorsprung prüfen, Unverschmolzenes melden, Hauptpfadname in `arbeitsdaten.json`), Checkpoint-Commits nur auf der Werkbank, Abschluss als Squash-Merge mit anschließendem Neuableiten der Werkbank samt `push -u` (Upstream-Falle vom 13. August 2026).

**Fundstellen:** nur LOK (1.7) — der mit Abstand längste Restposten.

**Einordnung:** **[teilweise abgedeckt]** — in Worktree-Projekten vollständig durch `parallel-sessions` ersetzt, und die Datei sagt das selbst. Für Projekte **ohne** das Modell trägt der Skill nur die Schreibhoheits-Sofortregel; das Werkbank-Verfahren ist nirgends übernommen. Zu entscheiden: als zweiter Regelzweig in `parallel-sessions`, als eigener Skill — oder sterben lassen, wenn künftig jedes betroffene Projekt das Worktree-Modell bekommt.

### E Projektgedächtnis über Chat-Grenzen — wieder geöffnet am 31. August 2026

Die Gruppe war mit T20, T21 und T22 geschlossen; die neuen Quelldateien tragen drei weitere Posten desselben Feldes.

#### T42 Kontext-Haushalt

**Aussage:** Führt das Projekt Fahrplan und Statusdatei, ist bei knapp werdendem Kontext die nächste Handlung die Detaillierung des Fahrplans — vor jeder Komprimierung, nie danach, nicht weiterkodieren. Am Ende jeder Arbeitssitzung Fahrplan und Status aktualisieren: Sie sind das Übergabemedium zwischen Maschinen und Sessions.

**Fundstellen:** nur LOK (1.9).

**Einordnung:** **[nicht abgedeckt]** — und tragend: Mehrere frühere Schließungen (T21, zuvor T5-Umfeld) berufen sich auf genau diese Regel als „§1.9". Wird sie zu einem Skill, müssen die Verweise der Kapitel-6-Einträge ihr Ziel behalten.

#### T44 Umgang mit importierten Chats

**Aussage:** Ein Chat-Import ist nur das Hinzufügen durchsuchbaren Inhalts — keine Widerspruchsprüfung beim Import; Chats sind historische Information. Chronologie zuerst über Benennung, dann über Inhalt, sonst den Nutzer fragen (Dateidatum nur als Hilfsangabe). Kollisionsprüfung ausschließlich auf Anfrage; Auflösung innerhalb der Chats ist Weiterentwicklung, keine Kollision; gegen Doku/Code gibt es keinen automatischen Vorrang. Ob eine Aussage Festlegung oder Zwischenstand ist, entscheidet die Chronologie.

**Fundstellen:** nur LOK (1.11).

**Einordnung:** **[nicht abgedeckt]** — der Skill `chat-export` holt Chats, regelt aber ihre Deutung nicht. Dessen Implementierungsdoku sieht in 3.3 ausdrücklich einen **eigenen künftigen Skill** für das Durchsuchen eines vorhandenen Archivs vor; T44 ist das inhaltliche Material dafür.

#### T45 Ablage und Format importierter Chats aus fremden Quellen

**Aussage:** Für claude.ai-Chats gilt der Skill `chat-export` (Verweis steht seit dem 31. August in der Quelldatei selbst). Für Chats aus anderen Quellen: Ablage unter `<projekt>/.claude/imported_chats/` (mitversioniert), Überführung nach JSON mit `role` user/assistant, `metadata`-Objekt mit `chat_date`, `imported_at`, `predecessor`/`successor` (nur wenn zweifelsfrei; nachträgliche Ergänzung erlaubt), Beispielschema im Wortlaut.

**Fundstellen:** nur LOK (1.12).

**Einordnung:** **[teilweise abgedeckt]** — der claude.ai-Fall ist durch den Skill erledigt; offen ist allein das Schema für fremde Quellen. Kandidat: derselbe künftige Archiv-Skill wie bei T44.

### K Anthropic-Werkzeuge und Beleglage

#### T43 Aussagen über Claude Code und die Anthropic-Werkzeuge

**Aussage:** Fragen zu Anthropic-Werkzeugen nie aus dem Basiswissen beantworten, sondern gegen die aktuelle offizielle Dokumentation recherchieren, mit Quellenangabe. Belegte Fakten, eigene Beobachtung und Community-Wissen getrennt ausweisen. Die Doku kann veraltet sein: Widerspricht sie der Beobachtung, wird der Widerspruch benannt, nicht stillschweigend gegen die Beobachtung aufgelöst.

**Fundstellen:** nur LOK (1.10).

**Einordnung:** **[nicht abgedeckt]** — verwandt mit `in-depth-online-literature-research` (Verifikationspflicht), aber eine andere Regel: dort Recherchemethode, hier ein Antwortverbot aus Basiswissen samt Beleglage-Trennung. Die Beleglage-Trennung ist zugleich Vorgabe 2.1 der chat-export-Doku — dieselbe Denkfigur, unabhängig formuliert. Kandidat für einen eigenen kleinen Skill oder ein Snippet.

### L Projektmethodik: Konzept- und Implementierungsdoku

Der zusammenhängende Block der Softwareprojekt-Methodik — Kandidat ist das Vorhaben `software-dev-doc-fh` (Fahrplan-Schritt 5), das genau diesen Standard kodifizieren soll; die lokal installierten Werkzeug-Skills `konzept-segmentierung` und `konsistenzpruefung` setzen Teile davon bereits um, ihre Zugehörigkeit klärt derselbe Fahrplanschritt.

#### T46 Geltungsbereich und Phasen

**Aussage:** Die Methodik gilt nur für Vorhaben, in denen Quellcode entsteht; Vorhaben ohne Quellcode wählen eine einfachere Form und benennen die Abweichung in der projekteigenen CLAUDE.md. Vier Phasen: Findung (offen, Prosa, nichts ist Festlegung), Fixierung (Ideen werden Vorgaben, erste finale APIs), Segmentierung (Neuschreiben als dreigeteiltes Dokument, Skill `/segmentierung`, erster Fahrplan), Implementierung (Doku wird parallel zum Code gepflegt).

**Fundstellen:** nur LOK (Vorrede-Rest und 2.1).

**Einordnung:** **[nicht abgedeckt]** als verteilbarer Skill; `/segmentierung` existiert nur lokal beim Entwickler.

#### T22 Prosa-Code-Grenze — wiedereröffnet am 31. August 2026

Am 30. August ohne Skill-Zuhause geschlossen („die Regel gilt bereits über §2.2 und bleibt dort"); der Eintrag samt Begründung stand in Kapitel 6. Wiedereröffnet, weil die Anweisungsdateien, in denen die Regel lebt, jetzt selbst Inventar sind: Werden sie zu Skills durchgearbeitet, braucht auch diese Regel ein Zuhause. Die am 30. August entschiedenen Streitpunkte bleiben entschieden — zwei Ausnahmen, keine Code-Style-Beispiele, keine Ausdehnung auf Fahrplan und Status; die WEB-Fassung ist am 31. August entsprechend angeglichen worden.

**Aussage:** Konzept- und Implementierungsdokumente enthalten keinen Implementierungscode. Genau zwei Ausnahmen: final beschlossene API-Signaturen und Nutzungsbeispiele bzw. -beispielschnipsel. Begründung (bindend): Code im Konzept macht die Prüfung von Code gegen Konzept wertlos; Prosa hält den mitgedachten Kontext; aus Prosa entsteht die Anwenderdokumentation.

**Fundstellen:** LOK (2.2) und WEB, seit dem 31. August wortgleich in der Sache. Historisch ALLG (Wortlaut in `original/`).

**Einordnung:** **[nicht abgedeckt]** als Skill — Teil des Methodik-Blocks dieser Gruppe.

#### T47 Dokumentstruktur

**Aussage:** Ordner `running_implementation_doc/` (anpassbar); eine Datei je Segment 1 und 2, eine je Hauptkapitel von Segment 3, dazu Fahrplan und Status; numerische Präfixe in Leseordnung; Segmente als Überschriften 1. Ordnung so gesetzt, dass das Verketten in Dateireihenfolge ein gültiges Gesamtdokument ergibt.

**Fundstellen:** nur LOK (2.3).

**Einordnung:** **[nicht abgedeckt]** — mit bekannter, dokumentierter Abweichung in diesem Repo (Dateiname `work-plan.md` statt `fahrplan.md`, Projekt-CLAUDE.md).

#### T48 Die drei Segmente

**Aussage:** Segment 1 Zusammenhänge (Workflow-Sicht, Querverweise als Suchweg, Quelle der Anwenderdoku); Segment 2 Vorgaben (projektweite, prüfbare Festlegungen — Aufnahmetest: auf eine Datei zeigen und „das verletzt diese Vorgabe" sagen können); Segment 3 Einheiten (je Hauptkapitel eine geschlossene Einheit). Jede Aussage hat genau ein normatives Zuhause.

**Fundstellen:** nur LOK (2.4).

**Einordnung:** **[nicht abgedeckt]** als verteilbarer Skill; praktisch umgesetzt in den Implementierungsdokus dieses Repos.

#### T49 Arbeitsschleife der Implementierung

**Aussage:** Tagesaufgabe aus dem Fahrplan; betroffene Segment-3-Sektion vollständig laden, Segment 1 gezielt durchsuchen, Segment 2 gilt parallel; bei übergreifenden Entscheidungen über Segment 1 die betroffenen Sektionen finden und Auswirkungen rückwärts einpflegen; zu jedem Codierungsschritt gehört der Doku-Vorschlag in den Plan — Doku und Code im Wechsel.

**Fundstellen:** nur LOK (2.5).

**Einordnung:** **[nicht abgedeckt]**.

#### T50 Fahrplan und Status

**Aussage:** Fahrplan: die nächsten Schritte in aufgabenangemessener Detaillierung, Erledigtes fliegt raus, Detaillierung vor jeder Kompression vertiefen. Status: ausschließlich abgearbeitete Fahrplaneinträge, keine Entscheidungen — die gehören sofort in das zuständige Segment.

**Fundstellen:** nur LOK (2.6).

**Einordnung:** **[nicht abgedeckt]** — bildet mit T42 ein Paar (T42 sagt wann, T50 sagt was); eine spätere Skill-Fassung sollte beide zusammen denken.

## 5 Zusammenfassung für die Neuzusammenstellung

### 5.1 claude.ai-Mechanik — in Claude Code gegenstandslos

T8–T11 sind am 28. August 2026 in `skills/web-code-editing/` verarbeitet und stehen in Kapitel 6. **T4 ist am 29. August 2026 geschlossen** (Entscheidung des Entwicklers): Die damals offene Prüffrage, ob die Chat-Suche projektübergreifend arbeitet, ist beantwortet — auf claude.ai durchsucht sie ohnehin nur die Chats des eigenen Projekts. Der Punkt braucht also kein Zuhause; sein Eintrag steht in Kapitel 6. **T5 ist am selben Tag geschlossen:** Die Vorwissen-Definition wird für die Arbeit mit Claude nicht mehr gebraucht; auch sein Eintrag steht in Kapitel 6. **T14 und T15 sind am 30. August 2026 geschlossen:** Ihre Form war claude.ai-Mechanik, ihr methodischer Kern ist in die Regeldatei `rules-handover` des Skills `temp-debug-code` eingegangen. Damit ist diese Gruppe vollständig abgearbeitet.

### 5.2 Bereits abgedeckt — mit den festgestellten Abweichungen

Derzeit leer. Die letzten Einträge (T21, T22) sind am 30./31. August 2026 geschlossen worden; ihre Abweichungen stehen bei den Einträgen in Kapitel 6. Die Rubrik bleibt stehen: Sie füllt sich wieder, sobald die Durcharbeitung der neuen Anweisungsdateien Posten liefert, die das Regelwerk bereits abdeckt.

### 5.3 Nicht oder nur teilweise abgedeckt — Kandidaten

- **Python-Test-Konventionen (T17, T18, T19):** der größte ungenutzte Block — pytest CI+CLI, testfreundliche Funktionsanlage, debug-Parameter. Kandidat für einen neuen Skill; bei T19 vorher genau eine der zwei unverträglichen Fassungen festlegen. Abgrenzung zu `temp-debug-code` ist sauber (dauerhafter vs. temporärer Debug-Code).

- **Projektmethodik-Block (T46–T50, T22):** Kandidat ist `software-dev-doc-fh` (Fahrplan-Schritt 5); die lokalen Werkzeug-Skills `konzept-segmentierung` und `konsistenzpruefung` setzen Teile bereits um. T42 und T50 bilden ein Paar und gehören zusammen gedacht.
- **Archiv-Skill für importierte Chats (T44, T45):** In der Implementierungsdoku von `chat-export` (3.3) ist ein eigener Skill für das Durchsuchen eines vorhandenen Archivs bereits vorgesehen — T44/T45 sind sein Material.
- **Werkbank-Modell (T40):** als zweiter Regelzweig von `parallel-sessions`, als eigener Skill — oder sterben lassen, wenn betroffene Projekte künftig das Worktree-Modell bekommen.
- **Einzelposten (T31 LFS, T33 Heredoc, T43 Beleglage):** je klein; als Snippet oder Mini-Skill denkbar, Zuschnitt offen.

### 5.4 Offene Fragen an den Entwickler

1. Stimmt die in Kapitel 2 vermutete Reihenfolge der Fassungen (CAM → SCH‑A → BIRD → SCH‑B; MOD als Ableger)? Antwort: Diese Reihenfolge spielt keine entscheidende Rolle.
2. T22: Sind Code-Style-Beispiele in Konzept-/Implementierungsdokumenten weiterhin erlaubte Ausnahme? Antwort: Erledigt am 30. August 2026 mit dem Abhaken von T22 — es entsteht kein Skill, damit gilt §2.2 unverändert und die Ausnahmeliste bleibt zweigliedrig. Näheres im Eintrag zu T22 in Kapitel 6.
3. T19: Welche der beiden debug-Parameter-Fassungen gilt, falls der Test-Skill entsteht? Antwort: Wird geklärt, wenn der entsprechende Punkt in ein Skill überführt wird.

## 6 Erledigte Einträge

Hier stehen die abgearbeiteten Einträge — die meisten, weil aus ihnen ein Skill entstanden ist; einzelne auch, weil entschieden wurde, dass sie in keinen gehören, oder weil sie sich erledigt hatten. Was das im Einzelfall war, sagt die erste Zeile des Eintrags. Sie sind damit vom Tisch, aber nicht wertlos: Sie belegen, woher eine Regel kommt und was bei ihrer Übernahme bewusst geändert wurde. Wer wissen will, warum ein Skill von seiner Vorlage abweicht, findet die Antwort hier — und der nächste Durchgang muss nicht neu herleiten, was schon entschieden ist.

Die Einträge waren am 27. und 28. August 2026 samt ihren Passagen in den Quelldateien gelöscht worden. Der Entwickler hat das am 29. August 2026 als Fehleinschätzung verworfen — was das Inventar angeht, endgültig: **Die Einträge bleiben hier stehen.** Erledigtes wird verschoben statt entfernt. Der Wortlaut unten ist der ursprüngliche; angepasst wurden allein die Ordnerbezeichnungen, damit der Verweis auf den heutigen Skill trägt.

Die **Passagen in den Quelldateien** sind noch am selben Tag erneut entfernt worden, diesmal nach einem anderen Verfahren: Jeder Posten wurde einzeln vorgelegt und Stelle für Stelle gegen den übernehmenden Skill gehalten, der Skill wurde dabei mehrfach verbessert, und gelöscht wurde erst nach ausdrücklicher Freigabe des Entwicklers. Was daran anders ist als am 27./28. August, ist nicht das Ergebnis, sondern der Weg dorthin — und dass das Belegmaterial jetzt gesichert ist: Die unveränderten Quelldateien liegen im Unterordner `original/`.

#### T1 Chat auf Deutsch, Duzen

**Entschieden:** Kein Skill-Zuhause, 29. August 2026 · Gruppe A (Sprache und Kontextquellen). Ob geduzt und in welcher Sprache geschrieben wird, entscheidet jeder Nutzer für sich. Das gehört in seine eigene `CLAUDE.md` beziehungsweise in das Anweisungsfeld auf claude.ai — nicht in einen Skill, der weitergegeben wird.

**Aussage:** Chat auf Deutsch; „wir duzen uns“.

**Fundstellen:** BIRD, CAM, SCH‑A, SCH‑B wortgleich. ALLG nur „Chat auf Deutsch“, ohne Duzen.

**Einordnung:** **[abgedeckt]** für die Sprache (§1.1). Das Duzen ist nirgends im heutigen Regelwerk festgehalten — falls es weiterhin gelten soll, wäre es ein Ein-Satz-Zusatz für §1.1.

#### T2 Code auf Englisch, einschließlich Kommentaren

**Verarbeitet:** Skill `common-code-generation`, 27. August 2026 · Gruppe A (Sprache und Kontextquellen).

**Aussage:** Code in Englisch, inklusive Kommentaren.

**Fundstellen:** BIRD, CAM, SCH‑A, SCH‑B wortgleich („Code in Englisch, inkl. Kommentaren“). ALLG präziser: „Code-Identifier, Kommentare **und Docstrings** auf Englisch“ — die einzige Quelle, die Docstrings ausdrücklich nennt.

**Einordnung:** **[abgedeckt]** durch den Skill `common-code-generation` („Alles, was im Quelltext steht — Bezeichner, Kommentare und Docstrings —, schreibst Du auf Englisch“), der zusätzlich das Vorschlagen von Benennungen regelt. Die ALLG-Präzisierung ist dort bereits übernommen.

#### T3 Dokumentsprache Deutsch, projektabhängig änderbar

**Entschieden:** Kein Skill-Zuhause, 29. August 2026 · Gruppe A (Sprache und Kontextquellen). Die Dokumentsprache hängt am Nutzer und am einzelnen Projekt; sie festzulegen ist Sache der jeweiligen `CLAUDE.md` beziehungsweise des Projekts selbst, nicht die eines Skills.

**Aussage:** Dokumente auf Deutsch, sofern nicht anders gefordert; die Sprache von Konzept-/Implementationsdokumenten wird projektabhängig festgelegt, und bei bestehenden Dokumenten erkennt Claude sie selbst.

**Fundstellen:** nur ALLG.

**Einordnung:** **[abgedeckt]** durch §1.1 („Dokumentation: Deutsch, wenn … nicht anders festgelegt“). Der Zusatz „bei bestehendem Dokument Sprache selbst erkennen“ steht dort nicht wörtlich, ist aber gelebte Praxis; kaum regelungsbedürftig.

#### T4 Chat-Suche nur innerhalb des Projekts

**Entschieden:** Kein Zuhause nötig, 29. August 2026 · Gruppe A (Sprache und Kontextquellen). Der Punkt ist von Haus aus erfüllt: Auf claude.ai durchsucht die Chat-Suche ohnehin nur die Chats des eigenen Projekts. Damit beantwortet sich zugleich die Prüffrage, die in 5.1 offenstand.

**Aussage:** Die Chats-durchsuchen-Funktion soll nur Chats innerhalb des claude.ai-Projekts berücksichtigen, nie Chats anderer Projekte oder außerhalb von Projekten.

**Fundstellen:** BIRD, SCH‑A, SCH‑B wortgleich, jeweils als vorangestellter Einzelpunkt.

**Einordnung:** **[claude.ai-Mechanik]**. In Claude Code ist der Projektkontext strukturell das Repository; für historische Chats gelten §1.11/§1.12 und das Vorhaben `chat-export/`. Der dahinterstehende Grundsatz — nur den Kontext des Projekts als Vorwissen zulassen — ist damit strukturell erfüllt. Bleibt claude.ai im Einsatz, gehört der Punkt in die dortige Projektanweisung.

#### T5 Definition des Vorwissens

**Entschieden:** Entfällt, 29. August 2026 · Gruppe A (Sprache und Kontextquellen). Die Vorwissen-Definition wird für die Arbeit mit Claude nicht mehr gebraucht. Der Eintrag bleibt hier stehen, weil T20 auf ihn Bezug nimmt („referenziere das Vorwissen, statt es auszuschreiben“) — der Faden ist also nicht durchtrennt.

**Aussage:** Vorwissen sind Projektdateien, zum Chatanfang hochgeladene Dateien und die Chats im Projekt; Chats außerhalb des Projekts zählen nie dazu, auch wenn sie inhaltlich passen.

**Fundstellen:** BIRD, SCH‑A, SCH‑B wortgleich.

**Einordnung:** **[claude.ai-Mechanik]**, Begründung wie T4. Bemerkenswert als Konzept: Die explizite Vorwissen-Definition wird in T20 (Status Protokoll) wiederverwendet („referenziere das Vorwissen, statt es auszuschreiben“) — dieses Prinzip lebt heute in §2.6 (Fahrplan/Status als Übergabemedium) weiter.

#### T6 Ankündigen und Freigabe vor jedem Artefakt

**Verarbeitet:** Skill `skills/web-code-editing/` („Bevor Du schreibst“), 28. August 2026 · Gruppe B (Artefakt-Arbeitsweise); abgehakt am 29. August 2026. Der Posten lebt zugleich verschärft in §1.3/§1.4 weiter. Als Herkunftsbeleg für diese Regel bleibt der Eintrag hier vollständig stehen — dafür muss er nicht in Kapitel 4 bleiben.

**Aussage:** Vor dem Erstellen oder Ändern eines Artefakts erst erklären, was getan werden soll; der Nutzer entscheidet, ob es ausgeführt wird.

**Fundstellen:** MOD, BIRD, CAM, SCH‑A, SCH‑B — im Kern wortgleich; MOD verallgemeinert auf Dokument-Artefakte.

**Einordnung:** **[abgedeckt]** und deutlich verschärft durch §1.3 (vollständiger, erklärender Plan je Datei und Stelle statt bloßer Ankündigung) und §1.4 (Abweichung heißt anhalten). Historisch interessant: Dies ist der direkte Vorläufer der heutigen Plan-vor-Ausführung-Regel.

#### T7 Offene Fragen vor Artefaktbeginn klären

**Verarbeitet:** Skill `skills/web-code-editing/` („Bevor Du schreibst“), 28. August 2026 · Gruppe B (Artefakt-Arbeitsweise); abgehakt am 29. August 2026. Zugleich in §1.3 und §1.5 abgedeckt, und dort über den Posten hinausgehend: §1.5 sagt auch, **wann nicht zu fragen ist** — wenn die Projektdokumentation die Frage bereits beantwortet.

**Aussage:** Vor dem Schreiben eines Artefakts oder einer Code-Änderung prüfen, ob noch Fragen offen sind; erst schreiben, wenn alle geklärt sind.

**Fundstellen:** MOD, BIRD, SCH‑A, SCH‑B in der ausführlichen Form („…lasse alle Fragen geklärt sein, bevor Du tatsächlich anfängst“); CAM in einer knapperen Frühform.

**Einordnung:** **[abgedeckt]** sinngemäß durch §1.3/§1.5 — der Plan-Zustimmungs-Zyklus erzwingt die Klärung vor der Ausführung.

#### T8 Wann Artefakt, wann Chat

**Verarbeitet:** Skill `skills/web-code-editing/`, 28. August 2026 · Gruppe B (Artefakt-Arbeitsweise).

**Aussage (erweiterte Fassung):** Artefakte nur für neuen Code oder Code, der Altes in sehr großen Stücken vollständig ersetzt; ganze Dateien immer als Artefakt; ganze Funktionen/Klassen dürfen als Artefakt; alles andere als Änderungsanweisung im Chat (T10).

**Fundstellen:** BIRD, SCH‑B mit den vollen Kriterien; MOD dieselben Kriterien, verallgemeinert auf „Code/Dokumenteninhalte“; CAM und SCH‑A nur die Kurzregel „kurze Codestücke direkt im Chat, ohne Artefakt“.

**Einordnung:** **[claude.ai-Mechanik]** — in Claude Code entscheidet niemand mehr zwischen Artefakt und Chat, geschrieben wird direkt in Dateien. Rohmaterial für `skills/web-code-editing/`.

#### T9 Artefakte nach Erstellung nicht mehr ändern

**Verarbeitet:** Skill `skills/web-code-editing/`, 28. August 2026 · Gruppe B. Dort zeitlos neu begründet: nicht mehr mit den Frontend-Fehlern von 2025, sondern damit, dass die gültige Fassung längst beim Nutzer liegt.

**Aussage:** Einmal erstellte Artefakte normalerweise nicht mehr ändern (Grund: Web-Frontend-Fehler zerstören Artefakte; der Inhalt ist ohnehin schon auf den Rechner kopiert). Änderungen stattdessen als Einfüge-/Ersetzungsanweisung mitteilen — missverständnisfrei lokalisiert, mit exakter Einrückung.

**Fundstellen:** alle außer ALLG. Varianten: CAM ohne die Ausnahme „es sei denn, ich bitte Dich darum“; BIRD/SCH‑B/MOD mit dieser Ausnahme und den Präzisierungen zu Einfügeort und Einrückung; SCH‑A zusätzlich mit einer Änderungs-Ausnahme für kurze, übersichtliche Snippets **unter 30 Zeilen** und der Regel, Positionen inhaltlich (z. B. Funktionsname) statt per Zeilennummer zu beschreiben.

**Einordnung:** **[claude.ai-Mechanik]**. Die SCH‑A-Ausklammerung von T11 zeigt zudem, dass diese Regeln als Reaktion auf konkrete Frontend-Zustände entstanden und mit dem Frontend altern — ein Argument, sie bei einer Neuauflage für claude.ai gegen den heutigen Stand des Frontends zu prüfen, statt sie zu übernehmen.

#### T10 Vorher/Ersetzen-Schema für Änderungen im Chat

**Verarbeitet:** Skill `skills/web-code-editing/`, 28. August 2026 · Gruppe B. Lebt dort als Chat-Schema für kleine Änderungen weiter, neben dem mechanischen Rückweg über einen Download.

**Aussage:** Änderungen im Chat folgen einem festen Schema: ein „Vorher“-Block mit den zu ändernden Zeilen exakt so, wie sie die Editor-Suche findet, dann ein „Ersetzen-mit“-Block mit dem neuen Inhalt; originale Einrückung zwingend; **niemals Zeilennummern** zur Ortsangabe.

**Fundstellen:** BIRD (Grundform); SCH‑B ergänzt: „Vorher“/„Nachher“ **vor** den Block schreiben, nicht hinein; MOD wie SCH‑B, verallgemeinert auf Dokumenteninhalte. CAM und SCH‑A haben das Schema nicht (SCH‑A stattdessen die inhaltliche Positionsbeschreibung, siehe T9).

**Einordnung:** **[claude.ai-Mechanik]** — das Schema ist der Sache nach ein von Hand ausgeführtes Suchen-und-Ersetzen und entspricht exakt dem, was in Claude Code das Edit-Werkzeug maschinell tut (alter String → neuer String, keine Zeilennummern). Als Erkenntnis bleibt: Das Prinzip „Ortsangabe über Inhalt, nie über Zeilennummern“ hat sich unabhängig vom Werkzeug bewährt. Rohmaterial für `skills/web-code-editing/`.

#### T11 Teil-Artefakte bei Überlänge

**Verarbeitet:** Skill `skills/web-code-editing/`, 28. August 2026 · Gruppe B — **ersatzlos entfallen**. Die Regel war schon in den Quellen überholt und ist im Skill bewusst nicht aufgenommen worden.

**Aussage:** Artefakte, die länger als etwa zwei kleingedruckte A4-Seiten würden, in mehreren Teil-Artefakten liefern (Grund: Unterbrechung durch „Fortsetzen“, Zerstörungsgefahr beim Weiterschreiben).

**Fundstellen:** CAM aktiv. SCH‑A: ausdrücklich **ausgeklammert** mit Begründung „Es scheinen inzwischen auch längere Artefakte zu funktionieren“, Wortlaut in Klammern konserviert. BIRD, SCH‑B, MOD: nicht mehr enthalten.

**Einordnung:** **[claude.ai-Mechanik]**, schon innerhalb der Quellen selbst überholt. Für die Chronologie-Vermutung in Kapitel 2 ist dieser Eintrag das stärkste Indiz.

#### T12 Nur besprochenen, wirklich notwendigen Code erzeugen

**Verarbeitet:** Skill `common-code-generation`, 27. August 2026 · Gruppe C (Code-Inhalt).

**Aussage:** Nur Code erzeugen, der besprochen und notwendig ist; Nice-to-have-Funktionen und nicht abgesprochene Qualitäts-Optimierungen erst nachträglich; Vorschläge dafür sind erwünscht und werden vom Nutzer „angewählt“.

**Fundstellen:** BIRD, CAM, SCH‑A, SCH‑B; BIRD/SCH‑B mit dem präzisierenden Einschub „die nicht explizit abgesprochen sind“.

**Einordnung:** **[abgedeckt]** — nahezu wortgleich in den Skill `common-code-generation` übernommen (Abschnitt „Schreiben von Code allgemein“), dort ergänzt um „schlage solche Erweiterungen immer frühzeitig vor“.

#### T13 Funktionsumfang nie ungefragt erweitern

**Verarbeitet:** Skill `common-code-generation`, 27. August 2026 · Gruppe C.

**Aussage:** Den bereits realisierten Funktionsumfang nie erweitern, wenn das nicht vorher einzeln festgelegt wurde.

**Fundstellen:** BIRD, CAM, SCH‑A, SCH‑B; CAM ohne „bereits realisierten“.

**Einordnung:** **[abgedeckt]** — wortgleich in `common-code-generation` enthalten.

#### T14 Kurze Ursachensuche als `python -c`-Einzeiler

**Verarbeitet:** Skill `temp-debug-code`, Regeldatei `rules-handover`, 30. August 2026 · Gruppe D (Debugging und Tests). Die claude.ai-Mechanik ist dort nicht übernommen, sondern ersetzt: Nicht mehr „gib dem Nutzer einen Einzeiler“, sondern erst die Frage, **wo der Fehler lebt** — reicht die Logik, führt Claude die Probe selbst aus; hängt sie an der Umgebung des Nutzers, gehört sie auf seinen Rechner. Die Form des Einzeilers ist dabei eine von drei sprachabhängigen Ausprägungen geworden.

**Aussage:** Kurze Debuggings zur Ursachensuche als Kommandozeilen-Einzeiler (`python -c "..."`) formulieren; der Nutzer führt sie aus und gibt das Ergebnis in den Chat zurück.

**Fundstellen:** BIRD, CAM, SCH‑A, SCH‑B wortgleich.

**Einordnung:** **[claude.ai-Mechanik]** in der Form (der Umweg über den Nutzer entfällt — Claude Code führt kurzlaufende Analysen nach §1.6 selbst aus). Der methodische Kern — die kleinste reproduzierende Probe vor der großen Instrumentierung — ist im heutigen Regelwerk nirgends festgehalten und wäre ein möglicher Baustein eines Debugging-Methodik-Skills.

#### T15 Umfassenderes Debugging als eigenes Skript

**Verarbeitet:** Skill `temp-debug-code`, Regeldatei `rules-handover`, 30. August 2026 · Gruppe D (Debugging und Tests). Das eigene Skript ist dort Stufe 3 der Eskalationsleiter — es kommt, wenn ein einzelner Aufruf nicht mehr trägt. Neu gegenüber der Quelle ist die Stufe darüber: Erst wenn auch ein Skript von außen nicht herankommt, wird in den Quelltext eingegriffen, und ab dort greift die Kennzeichnung.

**Aussage:** Größere Debugging-Aufbauten als eigenes Skript/Artefakt liefern, das im Projekt ausgeführt wird.

**Fundstellen:** BIRD, CAM, SCH‑A, SCH‑B wortgleich.

**Einordnung:** **[claude.ai-Mechanik]** in der Form, Kern wie T14. In Claude Code übernimmt das Scratchpad bzw. das Repo diese Rolle.

#### T16 Kennzeichnung von temporärem Probe-Code

**Verarbeitet:** Skill `temp-debug-code`, 27. August 2026 · Gruppe D (Debugging und Tests) — als Nachfolger mit geänderten Marken, nicht als Kopie.

**Aussage:** Debug-Code, der als „Probe“ eingefügt und später wieder entfernt wird, sowie zum Testen stillgelegter Code werden markiert: bei 1–3 Zeilen `# DEBUG` hinter jeder Zeile (vorhandener Kommentar folgt danach mit neuem `#`); ab 4 Zeilen oder bei Auskommentierungen ein Block aus `# DEBUG ---------------` davor und `# DEBUG END ------------` danach; Blöcke dürfen sich verschachteln, werden aber nicht extra eingerückt — die Einrückung folgt der Programmstruktur.

**Fundstellen:** BIRD und SCH‑B in der ausführlichsten Fassung (mit „hinter jede (!) Zeile“ und dem Hinweis, dass die Marke auch Folge-Chats das Wiederfinden erleichtert); SCH‑A in einer etwas knapperen Frühform. CAM hat noch keine Kennzeichnungsregel.

**Einordnung:** **[abgedeckt]** durch den Skill `temp-debug-code` — aber als **Nachfolger mit bewusst geänderten Festlegungen**, nicht als Kopie. Die Abweichungen im Einzelnen, damit niemand die alten Marken für die gültigen hält: Markensyntax heute `# DEBUG #` (mit schließender Raute, sprachunabhängig suchbar); neue eigene Marke `# DEBUG: ORIGINAL #` für stillgelegten Originalcode (in den alten Fassungen nicht unterschieden); Blockmarken heute `# DEBUG: START ------------ #`/`# DEBUG: END ------------ #`; Blockgrenze heute **ab 5** Zeilen statt ab 4; dazu neu: verpflichtender grep-Selbsttest und Regeln für das Entfernen. Die alten Fassungen sind damit vollständig überholt; ihr Wert ist dokumentarisch.

#### T25 Generalisierbarkeit von Lösungen

**Entschieden:** Kein Skill-Zuhause, 30. August 2026 · Gruppe F (Projektphase und Arbeitsmodus). Generalisierbarkeit bleibt bei den Skills unberücksichtigt — sie ist Sache des einzelnen Projekts und gehört in dessen `CLAUDE.md`, nicht in eine allgemeine Regel.

**Aussage:** Lösungen bevorzugen, die auch für andere Nutzer und Hardware generalisierbar sind: Funktioniert eine Lösung mit geringem Mehraufwand auch auf anderer Hardware, ist sie einer voll spezialisierten vorzuziehen — „Wer weiß, was in 10 Jahren ist.“

**Fundstellen:** nur MOD, ein Absatz.

**Einordnung:** **[nicht abgedeckt]** — weder die CLAUDE.md noch `common-code-generation` enthalten ein Generalisierbarkeits-Kriterium. Zur Wahl standen: als allgemeine Design-Leitlinie in `common-code-generation` aufnehmen oder bewusst projektspezifisch lassen. Geprüft wurde dabei auch das im Inventar vermutete Spannungsfeld zu T12/T13 — es besteht so nicht: Jene Posten schützen vor ungefragtem **Funktionsumfang**, T25 betrifft die **Bauform bei gleichem Umfang**, und für Vorschläge dieser Art hat `common-code-generation` bereits ein Verfahren. Den Ausschlag gab deshalb nicht ein Widerspruch, sondern die Herkunft: Die Aussage stammt aus einem einzelnen Hobbyprojekt und ist dort eine Vorliebe des Entwicklers, keine allgemeine Regel. Als solche formuliert, hätte sie zu Vorratsabstraktion eingeladen.

#### T23 Findungsphase: Alternativen und eigene Ideen ausdrücklich erwünscht

**Entschieden:** Kein Skill-Zuhause, 30. August 2026 · Gruppe F (Projektphase und Arbeitsmodus). Zusammen mit T24 und T26 als Kandidat für einen Phasen-Skill geprüft und verworfen — siehe die gemeinsame Begründung bei T26.

**Aussage:** Kurz nach der Findungsphase werden weiter Ideen gesammelt, abgewogen und verglichen; Claude soll immer auch Alternativen und eigene Ideen einbringen, „um … Lösungen nicht zu früh in feste Bahnen zu manövrieren“.

**Fundstellen:** nur MOD, ein Absatz.

**Einordnung:** **[teilweise abgedeckt]** — §2.1 definiert die Findungsphase (sammeln, verwerfen, nichts ist Festlegung), verlangt das aktive Einbringen von Alternativen aber nicht ausdrücklich.

#### T24 Planungsphase der Algorithmik: erklären statt kodieren

**Entschieden:** Kein Skill-Zuhause, 30. August 2026 · Gruppe F (Projektphase und Arbeitsmodus). Siehe die gemeinsame Begründung bei T26.

**Aussage:** Während der Planungsphase nur ausnahmsweise mit sehr kurzen Codesnippets arbeiten; stattdessen mehr erklären, strukturieren, Literaturquellen finden und wo nötig schematisch mit Markdown und Schriftzeichen zeichnen.

**Fundstellen:** nur SCH‑A, zwei Aufzählungspunkte.

**Einordnung:** **[nicht abgedeckt]** als Verhaltensregel — §2.2 regelt zwar, dass kein Code in die **Dokumente** gehört, aber nicht, dass in frühen Phasen der **Chat** prosalastig bleiben soll. Anders als T23 und T26 spricht dieser Posten vom **Planungs**-Zeitpunkt, nicht von der Findungsphase; die beiden sind in §2.1 verschiedene Phasen. Auch das gemeinsame Zuhause wäre also erst zu bestimmen gewesen.

#### T26 Alte Chats aufgreifen, Internet-Recherche erwünscht

**Entschieden:** Kein Skill-Zuhause, 30. August 2026 · Gruppe F (Projektphase und Arbeitsmodus). **Hier steht die gemeinsame Begründung für T23, T24 und T26.**

Die drei wurden zusammen als Kandidat für einen Phasen-Skill geprüft — so führt sie auch 5.3 — und zusammen verworfen. Der Grund ist zuerst der Umfang: Vier Absätze aus zwei Quellen, keine zehn Zeilen, sind zu wenig für einen eigenen Skill, und einen Skill um seiner selbst willen aufzufüllen hieße, Regeln zu erfinden, die niemand aufgestellt hat.

Dazu kommt, dass wenig Eigenes übrig bleibt. Von T26 ist der Umgang mit alten Chats bereits in §1.11 geregelt, und zwar strenger als hier (historische Information, Kollisionsprüfung nur auf Anfrage); die Internet-Recherche ist in Claude Code eine Werkzeug- und Berechtigungsfrage, und für die gründliche Form gibt es `in-depth-online-literature-research`. T23 ergänzt §2.1 um einen Halbsatz. Und T24 betrifft eine andere Phase als die beiden anderen.

Was bleibt, ist Arbeitsmodus eines einzelnen Projekts in einer bestimmten Lage — richtig aufgehoben in der `CLAUDE.md` des jeweiligen Projekts, nicht in einer allgemeinen Regel.

**Aussage:** Claude darf in bisherige Chats sehen und Inhalte wieder aufgreifen und darf im Internet nach Lösungsvorschlägen anderer Bastler suchen.

**Fundstellen:** nur MOD, ein Absatz.

**Einordnung:** **[teilweise abgedeckt]** — siehe oben.

#### T20 Das „Status Protokoll“

**Entschieden:** Kein Skill-Zuhause, 31. August 2026 · Gruppe E (Projektgedächtnis über Chat-Grenzen). Der Mechanismus ist durch Fahrplan und Status (§2.6, §1.9) bewusst abgelöst, und zwar gegenläufig: append-only und chronologisch dort, ersetzend hier — ihn in einen Skill zu heben, hieße die Ablösung zurückzunehmen. Die erprobten Detailregeln (Referenzieren statt Ausschreiben, Missverständnisfestigkeit ohne Vorwissen, Funktions-/Klassenrümpfe als API-Beschreibung des nächsten Schritts) bleiben als Vergleichsmaterial für den Ausbau von `software-dev-doc-fh` — der Wortlaut steht in diesem Eintrag, ein offener Posten ist dafür nicht nötig.

**Aussage:** Auf Wunsch des Nutzers (dann aber konsequent) wird ein Protokoll geführt — Artefaktname immer „Status Protokoll“, Datei `status_protokoll.md`, Markdown. Zweck: Erhalt des Bearbeitungsstands über mehrere Chats. Es wird **ausschließlich angehängt**, bestehende Einträge bleiben unverändert. Inhalt je Eintrag: die nächste anstehende Aufgabe; wo schon definiert, Funktions-/Klassenrümpfe als API-Beschreibung des nächsten Schritts; erledigte Teilschritte und Fehlschläge (nur wenn tatsächlich geschehen); Aufgaben-/Konzeptänderungen; Erfahrungen, die zum Verständnis der Lösung nötig sind. Beim Übergeben eines Protokolls: vollständig lesen, Stand analysieren, **Chronologie beachten** — was oben „offen“ ist, kann unten erledigt sein. Formulierung so ausführlich, dass spätere Missverständnisse ohne zusätzliches Vorwissen ausgeschlossen sind; vorhandenes Vorwissen (T5) wird referenziert statt ausgeschrieben.

**Fundstellen:** CAM in der Basisfassung (ohne Chat-Referenzen, ohne „Nur, wenn bereits erledigt“, „Aufgabenänderungen“ statt „Aufgaben-/Konzeptänderungen“); BIRD, SCH‑A, SCH‑B in der erweiterten Fassung (Chat-Namen als Referenz zur Entlastung des Protokolls; „immer nur wird angehangen“; Referenzieren des Vorwissens, „damit Du an der richtigen Stelle suchst“).

**Einordnung:** **[teilweise abgedeckt]** — der Zweck (Übergabemedium zwischen Sitzungen) lebt in Fahrplan und Status weiter. Nicht abgedeckt war allein der Halbsatz „dann aber auch konsequent nutzen“ — die Pflicht, ein einmal begonnenes Dokument durchzuhalten; der Entwickler hat entschieden, ihn nicht zu übernehmen.

#### T21 Konzept-Artefakte

**Entschieden:** Kein Skill-Zuhause, 31. August 2026 · Gruppe E (Projektgedächtnis über Chat-Grenzen). Der Sache nach abgedeckt: Das Phasenmodell §2.1 ist der ausgebaute Nachfolger des Konzept-Artefakts, die Chatlängen-Vorsorge entspricht §1.9. Die eine Nuance, die T21 ausdrücklicher fasste — der **Vorlauf**: „einige Chat-Blöcke übrig“ statt §1.9s „wird der Kontext knapp“ —, wurde im Chat besprochen; der Entwickler hat entschieden, dass §1.9 das trägt.

**Aussage:** Beim Erarbeiten eines Konzepts (Code-Strukturen, APIs) entsteht spätestens am Ende der Konzipierung ein Konzept-Artefakt (Markdown). Der Auftrag kommt vom Nutzer, Claude darf es aber vorschlagen. Nicht zu früh anlegen (wegen des Artefakt-Änderungsproblems T9 — im Skill `web-code-editing` zeitlos neu gefasst); in der erweiterten Fassung zusätzlich: rechtzeitig **vor** Erreichen des Chatlängen-Limits sichern, mit Reserve von einigen Chat-Blöcken für die Besprechung des Konzepts.

**Fundstellen:** CAM und SCH‑A in der Basisfassung; BIRD und SCH‑B erweitert („in der Regel“, „Vielleicht habe ich es nur vergessen“, Chatlängen-Vorsorge).

**Einordnung:** **[abgedeckt]** — der Timing-Gedanke „nicht zu früh festschreiben“ lebt in §2.1 als Findungsphase weiter.

#### T27 Projektspezifische Hintergrunddateien als Kontext

**Entschieden:** Kein Skill-Zuhause, 31. August 2026 · Gruppe F (Projektphase und Arbeitsmodus). Reine Projektspezifik, dieselbe Begründungslinie wie T25: Welche Dateien eines konkreten Projekts Hintergrund sind und welche das neue Entwicklungsziel tragen, gehört in die Anweisungen des jeweiligen Projekts, nicht in eine allgemeine Regel.

**Aussage:** Bestimmte Projektdateien („Grob-Analyse v1.md“ als grundlegender Kontext, „closedLoop7_1_hifiberry.py“ für Details der bisherigen Methoden) beschreiben Zweck und alte Herangehensweise, **nicht** das neue Entwicklungsziel — neue Erkenntnisse dürfen die dort beschriebenen Schritte ersetzen; die während der Chats entstehenden Dateien sind Teil des neuen Ziels.

**Fundstellen:** nur SCH‑A.

**Einordnung:** **[nicht abgedeckt]** als allgemeine Regel — und bewusst nicht aufgenommen. Der verallgemeinerbare Kern (Hintergrund von Ziel unterscheiden) wäre erst dann ein Kandidat, wenn er in mehr als einem Projekt gebraucht würde.
