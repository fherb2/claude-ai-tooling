## 🚷 Inventar der bisherigen Arbeitsanweisungen (claude.ai, Sonnet 4.5/4.6)

Dieses Inventar erschließt die sieben Textdateien dieses Ordners — die Projektanweisungen, die im vergangenen Jahr auf claude.ai (Projektwissen bzw. Chat-Anfang) verwendet wurden. Zweck: Alle enthaltenen Anweisungen so nebeneinanderzustellen, dass sich die Aussagen quellenübergreifend vergleichen lassen und entschieden werden kann, was für welche künftigen Einsatzfälle (Claude Code, Skills, Projekt-CLAUDE.md, weiterhin claude.ai) in welcher Form neu zusammengestellt wird.

Aufbau: Kapitel 1 beschreibt die Quelldateien, Kapitel 2 ihre Verwandtschaft, Kapitel 3 gibt die Themenmatrix als Überblick, Kapitel 4 ist das eigentliche Inventar — jede Anweisung als eigener, nummerierter Eintrag (T1–T27) mit Fundstellen, Varianten und einer Einordnung gegenüber dem heutigen Regelwerk. Kapitel 5 fasst die Einordnungen als Entscheidungsvorlage zusammen. Die Einordnungen sind Einschätzungen als Arbeitsgrundlage, keine Entscheidungen — die trifft der Entwickler.

Erstellt am 22. August 2026. Die Nummern T1–T27 sind stabil gedacht: Wird ein Eintrag erledigt oder verworfen, behalten die übrigen ihre Nummern (analog zur Fahrplan-Nummerierungsregel des Repos).

**Erledigt und entfernt am 27. August 2026:** T2, T12, T13 (abgedeckt durch den Skill `common-code-generation`) und T16 (abgedeckt durch `temp-debug-code`, als Nachfolger mit geänderten Marken). Die zugehörigen Passagen sind auch aus den Quelldateien dieses Ordners entfernt — sie sind Arbeitsmittel und sollen nur noch tragen, was zu verwerten bleibt. Die Beschreibungen der ursprünglichen, vollständigen Fassungen in den Kapiteln 1 und 2 bleiben als historische Einordnung stehen.

**Erledigt und entfernt am 28. August 2026:** T8, T9, T10, T11 — verarbeitet im Skill `skills/web-code-editing/`, geprüft gegen den Frontend-Stand vom August 2026 statt übernommen (T11 war schon in den Quellen überholt und ist ersatzlos entfallen; T9 ist dort zeitlos neu begründet). Die zugehörigen Passagen sind aus den Quelldateien entfernt — **außer in MOD**: Dessen Verallgemeinerung von T8–T10 auf Dokument-Artefakte ist nicht verarbeitet und bleibt als mögliches eigenes Material stehen.

## 1 Die Quelldateien

| Kürzel | Datei                                                                      | Inhaltlicher Zuschnitt                                                                                                                                                                                    |
| ------- | -------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| ALLG    | `claude.ai-pro-allgemein.txt`                                              | Projektunabhängige Kurzfassung: Sprachen und Prosa-Code-Grenze. Nur 2 Absätze.                                                                                                                          |
| MOD     | `modellbahn-fahrpult.txt`                                                  | Projekt in der Findungsphase: Arbeitsmodus (Alternativen, Recherche, Generalisierbarkeit) plus Artefakt-Regeln, auf Code**und** Dokumente verallgemeinert. Kein Sprachen-, Debugging- oder Protokollteil. |
| BIRD    | `birdnet-audio-walker.txt`                                                 | Vollständiger „Allgemeine Anweisungen“-Block in der erweiterten Fassung (siehe Kapitel 2), davor die Chat-Suche-Einschränkung.                                                                        |
| CAM     | `GigE-CameraStreamingServer.txt` und `RTCP Camera Streamer and Player.txt` | **Byte-identisch** (per `cmp` geprüft, 22.08.2026) — im Folgenden als eine Quelle behandelt. „Allgemeine Anweisungen“-Block in der Basisfassung.                                                      |
| SCH‑A  | `Scheludko-Zelle allgemein.txt`                                            | Projektspezifischer Kopf (Planungsphase, Hintergrunddateien) plus „Allgemeine Anweisungen“-Block in einer eigenständigen Zwischenvariante.                                                             |
| SCH‑B  | `Scheludko-Zelle Bildverarbeitung.txt`                                     | Bis auf**einen Satz** textgleich mit BIRD (per Diff geprüft): SCH‑B ergänzt im Vorher/Ersetzen-Schema die Regel, „Vorher“/„Nachher“ vor den Block statt hinein zu schreiben.                       |

Die Dateisystem-Daten stammen alle vom Kopiertag und taugen nicht zur zeitlichen Einordnung. Die Chronologie der Fassungen ist unten aus Textbefunden erschlossen und entsprechend als Vermutung gekennzeichnet.

## 2 Verwandtschaft der Texte

Vier der sechs unterschiedlichen Texte (BIRD, CAM, SCH‑A, SCH‑B) tragen denselben wiederverwendeten Block „Allgemeine Anweisungen zur Projektarbeit und zum Coding“ in drei Ausbaustufen. MOD und ALLG stehen daneben: MOD übernimmt nur die Artefakt-Regeln (verallgemeinert auf Dokumente), ALLG ist eine davon unabhängige Minimalfassung für die projektübergreifende Ebene.

**Vermutete Reihenfolge der Ausbaustufen** (Textbefund, nicht belegt — bei Bedarf vom Entwickler zu bestätigen):

1. **CAM (Basisfassung):** noch keine DEBUG-Kennzeichnung, kein Vorher/Ersetzen-Schema, Status-Protokoll ohne Chat-Referenzen, Teil-Artefakt-Regel (max. ~2 A4-Seiten) aktiv, debug-Parameter als Pflicht-Dictionary mit Guard `debug is not None`.
2. **SCH‑A (Zwischenvariante):** DEBUG-Kennzeichnung und erweitertes Status-Protokoll vorhanden; die Teil-Artefakt-Regel ist ausdrücklich **ausgeklammert** („Es scheinen inzwischen auch längere Artefakte zu funktionieren“) und im Wortlaut in Klammern konserviert; statt des Vorher/Ersetzen-Schemas nur die Regel, Einfügestellen inhaltlich (Funktionsname) statt per Zeilennummer zu beschreiben; als Einzige eine Änderungs-Ausnahme für Artefakt-Snippets unter 30 Zeilen.
3. **BIRD und SCH‑B (erweiterte Fassung):** Vorher/Ersetzen-Schema ausformuliert, explizite Artefakt-Kriterien (wann Artefakt, wann Chat), DEBUG-Kennzeichnung in der ausführlichsten Form, Status-Protokoll mit Chat-Referenzen und „Nur, wenn bereits erledigt“-Klausel, Konzept-Artefakte mit Chatlängen-Vorsorge. SCH‑B ist BIRD plus ein Satz (Beschriftung außerhalb des Blocks) — mutmaßlich die jüngste Fassung des Blocks.
4. **MOD:** übernimmt die erweiterte Artefakt-Mechanik aus BIRD/SCH‑B und verallgemeinert sie durchgängig von „Code“ auf „Code/Dokumenteninhalte“ — passend zu einem Projekt, das noch keine Software schreibt.

## 3 Themenmatrix

Legende: ✓ enthalten · (✓) in abgewandelter Form enthalten · ⊘ ausdrücklich ausgeklammert · – nicht enthalten. Die Varianten stehen in Kapitel 4 beim jeweiligen Eintrag.

| Nr. | Thema                                    | ALLG | MOD  | BIRD | CAM  | SCH‑A | SCH‑B |
| --- | ---------------------------------------- | ---- | ---- | ---- | ---- | ------ | ------ |
| T1  | Chat Deutsch, Duzen                      | (✓) | –   | ✓   | ✓   | ✓     | ✓     |
| T3  | Dokumentsprache Deutsch/projektabhängig | ✓   | –   | –   | –   | –     | –     |
| T4  | Chat-Suche nur im Projekt                | –   | –   | ✓   | –   | ✓     | ✓     |
| T5  | Vorwissen-Definition                     | –   | –   | ✓   | –   | ✓     | ✓     |
| T6  | Ankündigen + Freigabe vor Artefakt      | –   | ✓   | ✓   | ✓   | ✓     | ✓     |
| T7  | Offene Fragen vor Artefaktbeginn klären | –   | ✓   | ✓   | (✓) | ✓     | ✓     |
| T14 | Debug-Einzeiler`python -c`               | –   | –   | ✓   | ✓   | ✓     | ✓     |
| T15 | Umfassendes Debugging als eigenes Skript | –   | –   | ✓   | ✓   | ✓     | ✓     |
| T17 | pytest: CI-fähig und CLI-startbar       | –   | –   | ✓   | ✓   | ✓     | ✓     |
| T18 | Testfreundliche Funktionsanlage          | –   | –   | ✓   | ✓   | ✓     | ✓     |
| T19 | debug-Parameter-Konvention               | –   | –   | ✓   | (✓) | ✓     | ✓     |
| T20 | Status Protokoll                         | –   | –   | ✓   | (✓) | ✓     | ✓     |
| T21 | Konzept-Artefakte                        | –   | –   | ✓   | (✓) | (✓)   | ✓     |
| T22 | Prosa-Code-Grenze                        | ✓   | –   | –   | –   | –     | –     |
| T23 | Findungsphase: Alternativen erwünscht   | –   | ✓   | –   | –   | –     | –     |
| T24 | Planungsphase: erklären statt kodieren  | –   | –   | –   | –   | ✓     | –     |
| T25 | Generalisierbarkeit von Lösungen        | –   | ✓   | –   | –   | –     | –     |
| T26 | Alte Chats und Internet als Quellen      | –   | ✓   | –   | –   | –     | –     |
| T27 | Projektspezifische Hintergrunddateien    | –   | –   | –   | –   | ✓     | –     |

## 4 Die Anweisungen im Einzelnen

Jeder Eintrag nennt die Kernaussage, die Fundstellen mit ihren Varianten und eine Einordnung gegenüber dem heutigen Regelwerk (globale `~/.claude/CLAUDE.md`, hier „§…“, und die Skills dieses Repos). Die Einordnung trägt eine von vier Kategorien: **[claude.ai-Mechanik]** — an das Web-Frontend gebunden, in Claude Code gegenstandslos; **[abgedeckt]** — inhaltlich im heutigen Regelwerk enthalten; **[teilweise abgedeckt]**; **[nicht abgedeckt]** — Kandidat für eine Neuzusammenstellung.

### A Sprache und Kontextquellen

#### T1 Chat auf Deutsch, Duzen

**Aussage:** Chat auf Deutsch; „wir duzen uns“.

**Fundstellen:** BIRD, CAM, SCH‑A, SCH‑B wortgleich. ALLG nur „Chat auf Deutsch“, ohne Duzen.

**Einordnung:** **[abgedeckt]** für die Sprache (§1.1). Das Duzen ist nirgends im heutigen Regelwerk festgehalten — falls es weiterhin gelten soll, wäre es ein Ein-Satz-Zusatz für §1.1.

#### T3 Dokumentsprache Deutsch, projektabhängig änderbar

**Aussage:** Dokumente auf Deutsch, sofern nicht anders gefordert; die Sprache von Konzept-/Implementationsdokumenten wird projektabhängig festgelegt, und bei bestehenden Dokumenten erkennt Claude sie selbst.

**Fundstellen:** nur ALLG.

**Einordnung:** **[abgedeckt]** durch §1.1 („Dokumentation: Deutsch, wenn … nicht anders festgelegt“). Der Zusatz „bei bestehendem Dokument Sprache selbst erkennen“ steht dort nicht wörtlich, ist aber gelebte Praxis; kaum regelungsbedürftig.

#### T4 Chat-Suche nur innerhalb des Projekts

**Aussage:** Die Chats-durchsuchen-Funktion soll nur Chats innerhalb des claude.ai-Projekts berücksichtigen, nie Chats anderer Projekte oder außerhalb von Projekten.

**Fundstellen:** BIRD, SCH‑A, SCH‑B wortgleich, jeweils als vorangestellter Einzelpunkt.

**Einordnung:** **[claude.ai-Mechanik]**. In Claude Code ist der Projektkontext strukturell das Repository; für historische Chats gelten §1.11/§1.12 und das Vorhaben `chat-export/`. Der dahinterstehende Grundsatz — nur den Kontext des Projekts als Vorwissen zulassen — ist damit strukturell erfüllt. Bleibt claude.ai im Einsatz, gehört der Punkt in die dortige Projektanweisung.

#### T5 Definition des Vorwissens

**Aussage:** Vorwissen sind Projektdateien, zum Chatanfang hochgeladene Dateien und die Chats im Projekt; Chats außerhalb des Projekts zählen nie dazu, auch wenn sie inhaltlich passen.

**Fundstellen:** BIRD, SCH‑A, SCH‑B wortgleich.

**Einordnung:** **[claude.ai-Mechanik]**, Begründung wie T4. Bemerkenswert als Konzept: Die explizite Vorwissen-Definition wird in T20 (Status Protokoll) wiederverwendet („referenziere das Vorwissen, statt es auszuschreiben“) — dieses Prinzip lebt heute in §2.6 (Fahrplan/Status als Übergabemedium) weiter.

### B Artefakt-Arbeitsweise (claude.ai-Web-Frontend)

Von den Einträgen T6–T11 dieser Gruppe sind T8–T11 am 28. August 2026 im Skill `skills/web-code-editing/` verarbeitet und hier entfernt (siehe Erledigt-Notiz oben). T6 und T7 stehen mit doppelter Rolle: Im Web-Skill sind sie als „Bevor Du schreibst" verarbeitet; als Referenzmaterial für die noch ausstehende Durcharbeitung der globalen CLAUDE.md (§1.3–1.5) bleiben sie hier.

#### T6 Ankündigen und Freigabe vor jedem Artefakt

**Aussage:** Vor dem Erstellen oder Ändern eines Artefakts erst erklären, was getan werden soll; der Nutzer entscheidet, ob es ausgeführt wird.

**Fundstellen:** MOD, BIRD, CAM, SCH‑A, SCH‑B — im Kern wortgleich; MOD verallgemeinert auf Dokument-Artefakte.

**Einordnung:** **[abgedeckt]** und deutlich verschärft durch §1.3 (vollständiger, erklärender Plan je Datei und Stelle statt bloßer Ankündigung) und §1.4 (Abweichung heißt anhalten). Historisch interessant: Dies ist der direkte Vorläufer der heutigen Plan-vor-Ausführung-Regel.

#### T7 Offene Fragen vor Artefaktbeginn klären

**Aussage:** Vor dem Schreiben eines Artefakts oder einer Code-Änderung prüfen, ob noch Fragen offen sind; erst schreiben, wenn alle geklärt sind.

**Fundstellen:** MOD, BIRD, SCH‑A, SCH‑B in der ausführlichen Form („…lasse alle Fragen geklärt sein, bevor Du tatsächlich anfängst“); CAM in einer knapperen Frühform.

**Einordnung:** **[abgedeckt]** sinngemäß durch §1.3/§1.5 — der Plan-Zustimmungs-Zyklus erzwingt die Klärung vor der Ausführung.

### D Debugging und Tests

#### T14 Kurze Ursachensuche als `python -c`-Einzeiler

**Aussage:** Kurze Debuggings zur Ursachensuche als Kommandozeilen-Einzeiler (`python -c "..."`) formulieren; der Nutzer führt sie aus und gibt das Ergebnis in den Chat zurück.

**Fundstellen:** BIRD, CAM, SCH‑A, SCH‑B wortgleich.

**Einordnung:** **[claude.ai-Mechanik]** in der Form (der Umweg über den Nutzer entfällt — Claude Code führt kurzlaufende Analysen nach §1.6 selbst aus). Der methodische Kern — die kleinste reproduzierende Probe vor der großen Instrumentierung — ist im heutigen Regelwerk nirgends festgehalten und wäre ein möglicher Baustein eines Debugging-Methodik-Skills.

#### T15 Umfassenderes Debugging als eigenes Skript

**Aussage:** Größere Debugging-Aufbauten als eigenes Skript/Artefakt liefern, das im Projekt ausgeführt wird.

**Fundstellen:** BIRD, CAM, SCH‑A, SCH‑B wortgleich.

**Einordnung:** **[claude.ai-Mechanik]** in der Form, Kern wie T14. In Claude Code übernimmt das Scratchpad bzw. das Repo diese Rolle.

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

**Einordnung:** **[nicht abgedeckt]** — Kandidat für den Test-Skill (T17/T18). Zu klären ist dabei auch das Verhältnis zum Skill `temp-debug-code` (vormals T16): T19 beschreibt **dauerhaft** im Code verbleibende Debug-Pfade, die der Skill `temp-debug-code` ausdrücklich von seinen Regeln ausnimmt — die beiden ergänzen sich, überschneiden sich also nicht.

### E Projektgedächtnis über Chat-Grenzen

#### T20 Das „Status Protokoll“

**Aussage:** Auf Wunsch des Nutzers (dann aber konsequent) wird ein Protokoll geführt — Artefaktname immer „Status Protokoll“, Datei `status_protokoll.md`, Markdown. Zweck: Erhalt des Bearbeitungsstands über mehrere Chats. Es wird **ausschließlich angehängt**, bestehende Einträge bleiben unverändert. Inhalt je Eintrag: die nächste anstehende Aufgabe; wo schon definiert, Funktions-/Klassenrümpfe als API-Beschreibung des nächsten Schritts; erledigte Teilschritte und Fehlschläge (nur wenn tatsächlich geschehen); Aufgaben-/Konzeptänderungen; Erfahrungen, die zum Verständnis der Lösung nötig sind. Beim Übergeben eines Protokolls: vollständig lesen, Stand analysieren, **Chronologie beachten** — was oben „offen“ ist, kann unten erledigt sein. Formulierung so ausführlich, dass spätere Missverständnisse ohne zusätzliches Vorwissen ausgeschlossen sind; vorhandenes Vorwissen (T5) wird referenziert statt ausgeschrieben.

**Fundstellen:** CAM in der Basisfassung (ohne Chat-Referenzen, ohne „Nur, wenn bereits erledigt“, „Aufgabenänderungen“ statt „Aufgaben-/Konzeptänderungen“); BIRD, SCH‑A, SCH‑B in der erweiterten Fassung (Chat-Namen als Referenz zur Entlastung des Protokolls; „immer nur wird angehangen“; Referenzieren des Vorwissens, „damit Du an der richtigen Stelle suchst“).

**Einordnung:** **[teilweise abgedeckt]** — der Zweck (Übergabemedium zwischen Sitzungen) lebt heute in Fahrplan und Status (§2.6, §1.9) und im Vorhaben `software-dev-doc-fh` weiter. Der **Mechanismus ist aber gegenläufig**: Das Status Protokoll war append-only und chronologisch — der Leser musste die Chronologie auflösen; Fahrplan/Status arbeiten ersetzend — Erledigtes fliegt raus, Nummern bleiben stabil. Die alten Detailregeln (Referenzieren statt Ausschreiben; „so ausführlich, dass ohne Vorwissen kein Missverständnis möglich ist“; Funktionsrümpfe als API-Beschreibung des nächsten Schritts) sind erprobtes Vergleichsmaterial für den weiteren Ausbau von `software-dev-doc-fh`.

#### T21 Konzept-Artefakte

**Aussage:** Beim Erarbeiten eines Konzepts (Code-Strukturen, APIs) entsteht spätestens am Ende der Konzipierung ein Konzept-Artefakt (Markdown). Der Auftrag kommt vom Nutzer, Claude darf es aber vorschlagen. Nicht zu früh anlegen (wegen des Artefakt-Änderungsproblems, vormals T9 — im Skill `web-code-editing` zeitlos neu gefasst); in der erweiterten Fassung zusätzlich: rechtzeitig **vor** Erreichen des Chatlängen-Limits sichern, mit Reserve von einigen Chat-Blöcken für die Besprechung des Konzepts.

**Fundstellen:** CAM und SCH‑A in der Basisfassung; BIRD und SCH‑B erweitert („in der Regel“, „Vielleicht habe ich es nur vergessen“, Chatlängen-Vorsorge).

**Einordnung:** **[abgedeckt]** der Sache nach: Das Phasenmodell §2.1 (Findung → Fixierung → Segmentierung) ist der ausgebaute Nachfolger des Konzept-Artefakts, und die Chatlängen-Vorsorge entspricht exakt §1.9 (vor jeder Komprimierung den Fahrplan detaillieren). Der Timing-Gedanke „nicht zu früh festschreiben“ lebt in §2.1 als Findungsphase weiter.

#### T22 Prosa-Code-Grenze in Konzept- und Implementationsdokumenten

**Aussage:** Konzept- und Implementationsdokumente (auch Fahrplan-/Statusdokumente) enthalten keinen Implementierungscode. Genau zwei Ausnahmen: final beschlossene API-Signaturen sowie Nutzungs- **und Code-Style-Beispiele**.

**Fundstellen:** nur ALLG.

**Einordnung:** **[abgedeckt]** durch §2.2 — mit **einer inhaltlichen Abweichung**: §2.2 nennt als Ausnahmen API-Signaturen und Nutzungsbeispiele; die Code-Style-Beispiele aus ALLG kommen dort nicht vor. Zu entscheiden: Ist das ein bewusster Wegfall oder beim Übertragen verloren gegangen? (`common-code-generation` erwähnt Code-Styling-Vorgaben als primär geltend, regelt aber nicht deren Dokumentation per Beispiel.)

### F Projektphase und Arbeitsmodus

#### T23 Findungsphase: Alternativen und eigene Ideen ausdrücklich erwünscht

**Aussage:** Kurz nach der Findungsphase werden weiter Ideen gesammelt, abgewogen und verglichen; Claude soll immer auch Alternativen und eigene Ideen einbringen, „um … Lösungen nicht zu früh in feste Bahnen zu manövrieren“.

**Fundstellen:** nur MOD.

**Einordnung:** **[teilweise abgedeckt]** — §2.1 definiert die Findungsphase (sammeln, verwerfen, nichts ist Festlegung), verlangt das aktive Einbringen von Alternativen aber nicht ausdrücklich. Der Satz wäre ein guter Ein-Zeilen-Zusatz zur Findungsphasen-Definition oder Baustein eines Phasen-Skills.

#### T24 Planungsphase der Algorithmik: erklären statt kodieren

**Aussage:** Während der Planungsphase nur ausnahmsweise mit sehr kurzen Codesnippets arbeiten; stattdessen mehr erklären, strukturieren, Literaturquellen finden und wo nötig schematisch mit Markdown und Schriftzeichen zeichnen.

**Fundstellen:** nur SCH‑A.

**Einordnung:** **[nicht abgedeckt]** als Verhaltensregel — §2.2 regelt zwar, dass kein Code in die **Dokumente** gehört, aber nicht, dass in frühen Phasen der **Chat** prosalastig bleiben soll (Erklären, Literatur, Schemata). Kandidat für einen Konzeptphasen-Baustein; verwandt mit T23.

#### T25 Generalisierbarkeit von Lösungen

**Aussage:** Lösungen bevorzugen, die auch für andere Nutzer und Hardware generalisierbar sind: Funktioniert eine Lösung mit geringem Mehraufwand auch auf anderer Hardware, ist sie einer voll spezialisierten vorzuziehen — „Wer weiß, was in 10 Jahren ist.“

**Fundstellen:** nur MOD.

**Einordnung:** **[nicht abgedeckt]** — weder CLAUDE.md noch `common-code-generation` enthalten ein Generalisierbarkeits-Kriterium. Zu entscheiden: als allgemeine Design-Leitlinie in `common-code-generation` aufnehmen, oder bewusst projektspezifisch lassen (im Spannungsfeld zu den Regeln aus `common-code-generation` — vormals T12/T13 —, die vor ungefragtem Mehrumfang schützen; Generalisierung ist genau die Art Erweiterung, die dort der Absprache bedarf).

#### T26 Alte Chats aufgreifen, Internet-Recherche erwünscht

**Aussage:** Claude darf in bisherige Chats sehen und Inhalte wieder aufgreifen und darf im Internet nach Lösungsvorschlägen anderer Bastler suchen.

**Fundstellen:** nur MOD.

**Einordnung:** **[teilweise abgedeckt]** — der Umgang mit alten Chats ist über §1.11 geregelt (dort restriktiver: historische Information, Kollisionsprüfung nur auf Anfrage); Internet-Recherche ist in Claude Code eine Werkzeug-/Berechtigungsfrage und keine Anweisung. Der eigentliche Gehalt — in der Findungsphase fremde Lösungen **aktiv** einbeziehen — gehört als Erwünschtheit zum selben Phasen-Baustein wie T23.

#### T27 Projektspezifische Hintergrunddateien als Kontext

**Aussage:** Bestimmte Projektdateien („Grob-Analyse v1.md“ als grundlegender Kontext, „closedLoop7_1_hifiberry.py“ für Details der bisherigen Methoden) beschreiben Zweck und alte Herangehensweise, **nicht** das neue Entwicklungsziel — neue Erkenntnisse dürfen die dort beschriebenen Schritte ersetzen; die während der Chats entstehenden Dateien sind Teil des neuen Ziels.

**Fundstellen:** nur SCH‑A.

**Einordnung:** kein wiederverwendbarer Inhalt, aber ein wiederverwendbares **Muster**: die ausdrückliche Statuszuweisung an Kontextdateien („Hintergrund, nicht Vorgabe“ vs. „Teil des Ziels“). In der Claude-Code-Welt ist das die Rolle der Projekt-CLAUDE.md bzw. von Segment 1 der Implementierungsdoku. Als Muster festhaltenswert, als Text obsolet.

## 5 Zusammenfassung für die Neuzusammenstellung

### 5.1 claude.ai-Mechanik — in Claude Code gegenstandslos

T14 (Form) und T15 (Form) — ihr methodischer Kern steht in 5.3. T8–T11 sind am 28. August 2026 in `skills/web-code-editing/` verarbeitet und entfernt. **T4 und T5 gehen einen eigenen Weg** (Entscheidung des Entwicklers vom 28. August 2026): Sie sind keine Artefakt-Mechanik, sondern eine Projektanweisung für claude.ai (Vorwissen-Abgrenzung) — sie gehören, falls weiter gewollt, in das dortige Anweisungsfeld, und vorher ist ihre Aktualität zu prüfen: Ob die Chat-Suche heute noch projektübergreifend arbeitet, ist offen.

### 5.2 Bereits abgedeckt — mit den festgestellten Abweichungen

| Einträge    | Heutiger Ort                  | Abweichung/Anmerkung                                                                                                                    |
| ------------ | ----------------------------- | --------------------------------------------------------------------------------------------------------------------------------------- |
| T1           | §1.1                         | Duzen nirgends festgehalten.                                                                                                            |
| T3           | §1.1                         | —                                                                                                                                      |
| T6, T7       | §1.3–§1.5                  | verschärft weitergeführt.                                                                                                             |
| T21          | §2.1, §1.9                  | —                                                                                                                                      |
| T22          | §2.2                         | ALLG nennt zusätzlich Code-Style-Beispiele als Ausnahme; §2.2 nicht. Klären: bewusst entfallen oder verloren?                        |

### 5.3 Nicht oder nur teilweise abgedeckt — Kandidaten

- **Python-Test-Konventionen (T17, T18, T19):** der größte ungenutzte Block — pytest CI+CLI, testfreundliche Funktionsanlage, debug-Parameter. Kandidat für einen neuen Skill; bei T19 vorher genau eine der zwei unverträglichen Fassungen festlegen. Abgrenzung zu `temp-debug-code` ist sauber (dauerhafter vs. temporärer Debug-Code).
- **Konzept-/Findungsphasen-Arbeitsmodus (T23, T24, T26-Kern):** Alternativen aktiv einbringen, erklären statt kodieren, fremde Lösungen recherchieren. Kandidat als Zusatz zu §2.1 oder als eigener Phasen-Baustein/Skill.
- **Generalisierbarkeit (T25):** Design-Leitlinie; Zuordnung offen (in `common-code-generation` oder projektspezifisch belassen), Spannungsfeld zu dessen Regeln gegen ungefragten Mehrumfang (vormals T12/T13) beachten.
- **Debugging-Methodik-Kern (T14/T15):** „kleinste reproduzierende Probe zuerst“ — kleiner möglicher Baustein, falls je ein Debugging-Methodik-Skill entsteht.
- **Status-Protokoll-Detailregeln (T20):** Vergleichsmaterial für den Ausbau von `software-dev-doc-fh` (Referenzieren statt Ausschreiben, Missverständnisfestigkeit, API-Rümpfe als Schrittbeschreibung); der append-only-Mechanismus selbst ist durch Fahrplan/Status bewusst abgelöst.
- **Kleinigkeiten:** Duzen (T1), ggf. Code-Style-Beispiel-Ausnahme (T22).

### 5.4 Offene Fragen an den Entwickler

1. Stimmt die in Kapitel 2 vermutete Reihenfolge der Fassungen (CAM → SCH‑A → BIRD → SCH‑B; MOD als Ableger)? Sie beruht allein auf Textbefunden.
2. Soll claude.ai weiterhin als Arbeitsumgebung bedient werden? Davon hängt ab, ob die Einträge aus 5.1 in `web-code-editing` einfließen oder nur dokumentarisch bleiben.
3. T22: Sind Code-Style-Beispiele in Konzept-/Implementierungsdokumenten weiterhin erlaubte Ausnahme?
4. T19: Welche der beiden debug-Parameter-Fassungen gilt, falls der Test-Skill entsteht?
