## 3.6 Das Skript

Stand (2026-09-25): Kommandosatz, Ausgabevertrag und Aufrufprinzip sind Vorschlag mit weitgehender Zustimmung; das Graphenmodell des Auswirkungsmoduls ist entschieden (vormals Q-20, Kapitel 1.7.4), ebenso der Dateiname des Skripts (vormals Q-24) und der Name des Auswirkungskommandos (vormals Q-22).

### 3.6.1 Ort, Name, Laufzeit

Ein Skript `files/software-design-doc.py` im Skill-Ordner, aufgerufen über `${CLAUDE_SKILL_DIR}/files/software-design-doc.py`, dazu das Modul `files/impact.py` für die Auswirkungsrechnung. Python ab 3.11, sonst nur Standardbibliothek. Das Skript trägt den Namen des Skills (entschieden am 2026-09-25, vormals Q-24); `sdd` wurde verworfen, weil das Kürzel in der Agentenwelt für Spec-Driven Development steht. Folgt aus der Prüfung bei Fahrplanschritt 9 eine Umbenennung des Skills, wandert der Skriptname mit (Kapitel 1.1).

**Die eine optionale Bibliothek** (entschieden am 2026-09-20, vormals Q-25). `networkx` rechnet kürzeste Wege in gewichteten Graphen direkt und deckt damit eine der drei Kostenfunktionen (3.6.5) ohne eigenen Code ab. Sie ist **nie Voraussetzung**: Fehlt sie, rechnet ein eingebauter Algorithmus von etwa dreißig Zeilen. Ihre Anwesenheit ist auf einem Entwicklungsrechner Zufall, und was niemand kennt, installiert niemand — deshalb ist ihre Benutzung eine bewusste Wahl des Entwicklers (Kapitel 1.7.4), festgehalten im Skill-Parameter `impact_lib`:

| Wert | Bedeutung | Was die Instanz tut |
|---|---|---|
| `unknown` | Anfangszustand: weder geprüft noch gefragt | Beim ersten Lauf der Auswirkungsrechnung prüfen, ob `networkx` importierbar ist. Gelingt es, auf `on` setzen und weiterarbeiten. Gelingt es nicht, dem Entwickler in zwei Sätzen erklären, was die Bibliothek besser macht, und fragen — installieren lassen, selbst installieren, oder ablehnen. Die Antwort wird geschrieben. |
| `on` | benutzen | vorhanden oder vom Entwickler gewünscht; fehlt sie dennoch, fällt das Skript auf den eingebauten Weg zurück und meldet es einmal |
| `off` | nicht benutzen | auch dann nicht, wenn sie installiert ist |

Die Frage kommt genau einmal je Projekt. Solange sie unbeantwortet ist, arbeitet der Skill vollständig — mit dem eingebauten Weg und ohne Hinweis bei jedem Lauf.

### 3.6.2 Aufrufprinzip

**Wozu das Skript da ist und nach welchem Prinzip seine Kommandos geschnitten sind, steht in Kapitel 1.3.6.** Für die Umsetzung folgt daraus:

- **Ein Aufruf je Anker** (Kapitel 3.1, Abschnitt 3.1.9), nicht mehrere. Die Ankerkommandos sind `open`, `plan-section`, `apply`, `check` und `lint`.
- **Jedes Kommando, das mehrere Festlegungen betreffen kann, nimmt eine Liste** — `--ids D-0042,D-0057` — und nie eine einzelne ID. Das gilt auch dann, wenn im Einzelfall nur eine übergeben wird.
- **Auskunftskommandos** (`show`, `explain`, `next-id`) dürfen einstellig bleiben: Sie beantworten eine Nachfrage des Entwicklers und kommen im Ablauf nicht vor.
- **Jede Voraussetzung hat einen Default**, wird gesucht, ihr Fehlen exakt gemeldet, und sie ist per Script-Argument überschreibbar (Vorgabe 2.4).
- **Kein Kommando ändert Prosa des Entwicklers.** Geschrieben werden dürfen: das Register (`apply`, `supersede`, `retire`, `fp --update`) und Arbeitsdokumente, die der Ablauf ohnehin erzeugt (`plan-section --write`).
- **Jedes Kommando liest zuerst die Skill-Parameterdatei und endet bei `mode: off` mit `OK` ohne Befund** (entschieden am 2026-10-02). Das gilt auch aus einem Hook heraus und ist dort der einzige Weg: Die Engine kennt keine bedingte Registrierung, und der Filter eines Hooks kann keine Dateiinhalte prüfen (Kapitel 1.7.7 und 3.7). Läuft ein Kommando dabei zum ersten Mal in dieser Sitzung in ein `mode: off`, gibt es zusätzlich den einen Satz aus, der die Abwahl benennt; die Sitzung erkennt es an der Kennung aus `CLAUDE_CODE_SESSION_ID` beziehungsweise am Feld `session_id` der Hook-Eingabe und merkt sich den ersten Lauf mit einer leeren Markierungsdatei im sitzungseigenen Arbeitsverzeichnis, das die Hook-Eingabe als `scratchpad_dir` mitliefert. Diese Markierung ist keine Ausnahme von Vorgabe 2.8: Sie liegt außerhalb des Projekts, verschwindet mit der Sitzung und trägt keinen Inhalt. **Dieselbe Stille gilt, wenn das Vorhaben keine Softwareentwicklung ist** (Kapitel 3.5.5): Auch diese Prüfung steht vor jedem Kommando, aus demselben Grund — die Hooks sind registriert, sobald der Skill einmal geladen wurde, und können sich nicht selbst abschalten.

**Die drei Rückgabewege** nach Kapitel 1.3.6 heißen im Skript: Standard ist inline. `--out DATEI` schreibt das volle Ergebnis in eine Datei und gibt inline nur Zahlen, die ersten Einträge und den Pfad zurück; die Instanz liest gezielt nach. `--write` lässt das Skript das Erzeugnis selbst an seinen Platz schreiben und gibt nur die Quittung zurück.

### 3.6.3 Ausgabevertrag

Die Ausgabe ist für die Instanz gebaut, nicht für einen Menschen am Terminal. Sie ist zeilenorientiert, jede Zeile beginnt mit einer Klasse in Großbuchstaben, danach Ausgabefelder in fester Reihenfolge, getrennt durch ` | `, jedes Feld als `key: value`; Werte enthalten keinen senkrechten Strich. Schlüssel sind englisch; Werte dürfen deutsche Prosa sein. Keine Erzählung, keine Farben, keine Symbole, kein Fortschrittslog. Zahlen sind Zahlen, nicht Wörter. Eine Ausgabe hat höchstens etwa vierzig Zeilen; wird gekürzt, sagt die letzte Zeile, wie viele fehlen und mit welchem Script-Argument sie erscheinen.

| Klasse | Bedeutung | Ausgabefelder |
|---|---|---|
| `OK` | Lauf erfolgreich, ein Satz — auch wenn nichts zu berichten ist | `msg` |
| `ITEM` | ein Gegenstand einer Liste | kommandoabhängig, feste Reihenfolge |
| `FINDING` | ein Befund | `subject`, `issue`, `proposal` |
| `DECIDE` | eine Entscheidungsvorlage, die das Skript nicht mechanisch lösen kann | `subject`, `question`, `options`, `proposal` |
| `FAILED` | Abbruch | `step`, `cause`, `state`, `remedy` — die Abhilfe nennt das exakte Script-Argument |
| `SUMMARY` | letzte Zeile jeder Ausgabe | `items`, `findings`, `decide` als Zahlen |

Exit-Codes: 0 bei `OK` ohne Befunde, 1 bei Befunden oder Entscheidungsvorlagen, 2 bei `FAILED` und bei struktureller Inkonsistenz — der Code, mit dem der Commit-Hook blockiert (Kapitel 3.7). Mit `--json` erscheint dieselbe Information als JSON-Array; die Hooks nutzen es, um `additionalContext` zu füllen. **Welche der beiden Formen der Standard ist, steht noch nicht fest** — die Entscheidungsgrundlage dazu gehört zur Vorgabe über den Ausgabevertrag und steht deshalb in Vorgabe 2.5 (seit 2026-09-25, vormals Q-23); die Beschreibung hier geht vom zeilenförmigen Standard aus. Eine unbehandelte Ausnahme ist ein Defekt; die Prüffälle enthalten absichtlich kaputte Eingaben (fehlende Klammern, falsche Schlüsselwörter, U+00A0, Dubletten), für die eine `FAILED`- oder `FINDING`-Zeile erwartet wird.

Was mechanisch entscheidbar ist, entscheidet das Skript und gibt es als `ITEM` oder `OK` aus; `DECIDE` ist die Ausnahme für das, was sich nicht kodieren lässt (Vorgabe 2.6). Die Trennung ist sichtbar: Ein `ITEM` ist Fakt, ein `DECIDE` ist Vorlage.

**Befund B-07 (2026-09-25): Ein Absturz des Skripts würde den Commit blockieren.** Oben steht Exit-Code 2 für zwei verschiedene Dinge: für `FAILED`, also den Abbruch des Skripts selbst, und für strukturelle Inkonsistenz zwischen Prosa und Register. Der Hook vor dem Commit wertet genau diesen Code als Blockade — das ist die Mechanik von Claude Code, kein Entwurf von uns (Kapitel 3.7.2). Dieselbe Tabelle dort erwartet zugleich, dass ein `FAILED` mit Exit 1 zurückkommt und den Commit durchlaufen lässt. Beides zusammen geht nicht. Sachlich ist die Richtung klar, denn Kapitel 1.3.5 nennt genau einen blockierenden Eingriff des Skills, und das ist die strukturelle Inkonsistenz; ein Defekt des Skripts gehört nicht dazu, sonst hält ein Programmierfehler die Arbeit an. Zu entscheiden ist die Umsetzung: entweder zwei getrennte Codes — 2 nur für die Inkonsistenz, ein anderer für `FAILED` — oder ein eigener Hook-Modus, in dem das Skript den Unterschied selbst macht. Die Folge trifft auch die Tabelle in 3.7.2.

### 3.6.4 Kommandos

**Ankerkommandos** — je einer Handlung des Ablaufs zugeordnet, bündeln alles, was dort anfällt:

| Kommando | Anker | Liest | Gibt aus | Exit |
|---|---|---|---|---|
| `open --chapter DATEI…` | Bereich öffnen | Register, Marker, Doku | `ITEM` je Festlegung: `id`, `chapter` (abgeleitet), `kind`, `status`, `hardness` mit Bedingung, `label`; dazu `FINDING` je Abweichung zwischen Prosa und Register | 0/1 |
| `plan-section --ids … [--collide …] [--write DATEI]` | Plan schreiben | Register, Härte, geplante Schritte, Erwähnungen | den fertigen Abschnitt „Berührte Festlegungen": je Festlegung ID, Kapitel, `kind`, Grund, `status`, Härte mit Bedingung und **Umbaukosten als Zahl**; für die mit `--collide` genannten zusätzlich das Gerüst des geparkten Satzes | 0 |
| `apply --from DATEI` | Plan ausführen | die im Plan beschlossenen Änderungen | schreibt **alle** Registerzeilen eines Plans in einem Zug — Kopfzeilen, Gründe, Suchschlüssel, Fingerabdrücke, Ereignis- und Lebenszykluszeilen; Quittung mit Zahlen | 0/2 |
| `check [--summary]` | Commit, Sitzungsstart | Register, Doku, geplante Schritte | `FINDING` je Abweichung: Marker ohne Eintrag, Eintrag ohne Definitionsmarker, mehrere Definitionsmarker, unlesbare Zeile, `target:` auf unbekannte ID oder Datei, `superseded` ohne Ziel, Dublette, geänderter Definitionssatz; mit `--summary` nur Zahlen | 0 keine, 1 Befunde, 2 strukturell |
| `lint --file DATEI --changed` | nach Doku-Edit | Git-Diff der Datei | `FINDING` je geänderter Zeile mit Normativsignal ohne Marker und je neuem Marker ohne Eintrag | 0/1 |

**Arbeitskommandos** — nehmen immer Listen, auch wenn nur ein Element übergeben wird:

| Kommando | Liest | Gibt aus | Exit |
|---|---|---|---|
| `impact --chapter DATEI \| --ids …` | Graph aus Markern, Nähe, Suchschlüsseln | `ITEM` je Kandidat: `id`, `why` (Definition, Mitzitat, gleicher Absatz, Suchschlüssel), `distance` | 0 |
| `mentions --ids … [--code ORDNER] [--out DATEI]` | Doku, optional Code | je ID die Zahl der Fundorte und die Fundorte selbst; mit `--out` nur Zahlen und Pfad | 0 |
| `hardness --ids … [--word fixed\|open]` | Register, geplante Schritte, Skill-Parameter | `ITEM` je ID mit Härte und zutreffender Bedingung in Prosa (R1–R7) | 0 |
| `fp --ids … [--update]` | Doku | je ID Fingerabdruck und Vergleich mit dem Register | 0/1 |
| `notes [--class open] [--chapter DATEI] [--ids …] [--since COMMIT] [--out DATEI]` | Commit-Verlauf | `ITEM` je Notiz: Klasse, Art, Ort, Wiederfindehinweis, Grund, Sitzung, Commit, Datum | 0 |
| `supersede --pairs ALT:NEU,…` · `retire --ids …` | Register | schreibt die Lebenszykluszeilen; listet je ID die verbleibenden Zitate | 0 |

**Auskunftskommandos** — für die Nachfrage des Entwicklers; sie kommen im Ablauf nicht vor und dürfen deshalb einstellig bleiben:

| Kommando | Liest | Gibt aus | Exit |
|---|---|---|---|
| `show ID` | Register, Doku | alle Registerzeilen der ID, Definitionsort, Zitatorte | 0 |
| `explain ID` | wie `hardness` | ein Satz für den Entwickler, ohne Prüfungsnummer | 0 |
| `next-id` | Register | nächste freie ID | 0 |

Was ein Kommando **nicht** hat, ist ebenso Festlegung: Es gibt kein `add` für eine einzelne Registerzeile. Registerzeilen entstehen ausschließlich über `apply` aus einem freigegebenen Plan — in einem Aufruf, nicht in zehn (Kapitel 1.3.6).

**Das Kommando `notes` liest die Notizen aus dem Commit-Verlauf** (entschieden am 2026-09-25). Wozu sie da sind, steht in Kapitel 1.3.5, ihre Form in 3.2.9. Für die Umsetzung gilt dreierlei.

Es ist **allgemein gehalten**: Ohne Argumente liefert es alles, was der Trailer-Vorlage entspricht — jede `ADoc-`-Klasse, nicht nur die heute einzige. Der Filter `--class` grenzt auf eine Klasse ein, `--chapter` und `--ids` auf einen Bereich. So muss die Instanz nicht wissen, wo sie suchen soll: Sie fragt einmal quer über alles und entscheidet dann selbst, was zur aktuellen Frage gehört. Kommen später weitere Klassen dazu, erscheinen sie ohne Änderung am Kommando.

Es sucht **immer über den vollständigen Verlauf**, sofern nicht `--since` etwas anderes sagt. Die Messung (3.2.9) macht jede Begrenzung überflüssig, und eine Begrenzung wäre die häufigste Ursache dafür, dass ein alter Faden nicht mehr gefunden wird.

**Die Ausgabe ist zum Durchsuchen gebaut, nicht zum Lesen.** Sie folgt dem zweiten Rückgabeweg aus Kapitel 1.3.6: Bei mehr als einer Handvoll Einträgen schreibt das Skript das volle Ergebnis in eine Datei und gibt inline nur die Zahlen, die ersten Einträge und den Pfad zurück; die Instanz sucht dann in der Datei mit `grep` oder liest gezielt nach, statt alles in den Kontext zu kopieren. Die Datei trägt eine Zeile je Notiz mit denselben Feldern wie der Trailer, ergänzt um Commit und Datum — durchsuchbar nach Datei, nach ID und nach Art.

**Wann es läuft:** beim Öffnen eines Bereichs zusammen mit dem Abgleich, der dort ohnehin stattfindet — bei diesen Laufzeiten gibt es keinen Grund, daraus einen zweiten Aufruf zu machen (Vorgabe 2.7) —, und auf Nachfrage, wenn jemand wissen will, was insgesamt offen ist.

### 3.6.5 Das Auswirkungsmodul

**Wozu das Modul da ist und woran es sich rechtfertigt, steht in Kapitel 1.7.4.** Hier steht, woraus es rechnet. `impact.py` kapselt Kanten, Gewichte, Kostenfunktion und Abbruch, weil genau hier später nachjustiert wird; der Name folgt der Auswirkungsanalyse, die der Vorläufer als Aufgabe von Segment 1 nennt (Anhang A, Abschnitt A.6).

**Knoten** sind Festlegungen. **Kanten** entstehen aus dem Text: zwei Festlegungen, die im selben Absatz genannt sind (Definition oder Zitat), im selben Abschnitt, in Nachbarabschnitten, im selben Kapitel; dazu Treffer der Suchschlüssel als Quelle außerhalb des Graphen. Vorschlag für die Gewichte: gleicher Absatz 0,8 · Mitzitat in einem Absatz mit Funktion `relate` 0,7 · gleicher Abschnitt 0,4 · Nachbarabschnitt 0,2 · gleiches Kapitel 0,05.

Diese Gewichte und die Dämpfung heißen **Graphenparameter**: Sie parametrisieren den funktionalen Zusammenhang der Auswirkungsrechnung. Sie sind **keine Skill-Parameter** — sie stehen im Skill, entweder direkt im Modul oder in einer Datei des Skill-Ordners, nie in der Projektkonfiguration. Grund: Der Entwickler kann sie nicht beurteilen; ob eine Kante „gleicher Abschnitt" 0,4 oder 0,35 wiegt, ist keine Eigenschaft seines Projekts, sondern des Verfahrens. Sie ändern sich nach einer Messung (Kapitel 3.8) und dann für alle Projekte. Was ein Projekt davon einstellt, sind allein die zwei groben Griffe `impact_model` und sein Abbruchwert — eng oder weit, nicht einzelne Gewichte (Entscheidung des Entwicklers vom 2026-09-18).

**Drei Kostenfunktionen**, austauschbar, damit die Probe sie vergleicht. Welche am Ende bleibt, ist keine Entscheidungsgrundlage für den Entwickler, sondern ein Messergebnis (seit 2026-09-25, vormals Q-21): Keine der drei ist erkennbar richtig, und was zählt, ist allein die Brauchbarkeit der Kandidatenliste — nicht so kurz, dass Betroffenes fehlt, nicht so lang, dass die Instanz die Hälfte verwirft. Deshalb werden alle drei gebaut; der Mehraufwand sind drei kurze Funktionen in einem Modul, dessen Umgebung ohnehin dieselbe ist. Der Vergleich gehört zum Ablauf der Probe (Kapitel 3.8.3), die Entscheidung zu ihrem Entscheidungstor (3.8.5).

1. **Additiv**: Kosten je Kante 1/w, Weglänge Σ Kosten, Abbruch bei `impact_cutoff` — ein Kürzeste-Wege-Problem; networkx rechnet es direkt mit `single_source_dijkstra_path_length(G, source, cutoff, weight=funktion)` (belegt, Doku 3.6.1).
2. **Multiplikativ nach dem Vorschlag des Entwicklers**: Weglänge Σ(Hops) / Π(Gewichte); eine schwache Kante irgendwo im Pfad verunsichert die ganze Kette. Pfadabhängig, braucht eine eigene Suche; bei Graphen mit Hunderten Knoten unproblematisch.
3. **Produkt mit Dämpfung**: Bewertung Π w × d^Hops mit d = 0,7, Abbruch unter einer Schwelle; entspricht dem Rechenmodell in Anhang B.

Der Skill-Parameter `impact_model: hops` ist der Sonderfall, in dem nur Kanten ab 0,7 zählen und `impact_cutoff` die Tiefe ist. Das Rechenmodell (Anhang B) zeigt: Tiefe 1 bleibt in jeder Dokugröße bei einer Handvoll Kandidaten; Tiefe 2 wächst mit der Doku und liegt bei dreihundert Festlegungen im Median über zwanzig; die gewichtete Variante ist ein stetiger Regler zwischen beiden. Was das Modell nicht sagt: ob zusätzliche Kandidaten relevant sind — das misst die Probe.

### 3.6.6 Der Lint

Prüft nur geänderte Zeilen der übergebenen Datei (Git-Diff gegen den Index und gegen HEAD). Eine Zeile ist ein Befund, wenn sie ein Normativsignal trägt — Signalwörter aus `lint_signals` (Standard deutsch und englisch: muss, müssen, soll, sollen, immer, nie, niemals, darf nicht, genau, höchstens, mindestens, must, shall, always, never, at most, at least) oder einen Zahlenwert mit Einheit — und keinen Marker `[D-`. Ausgenommen sind Abschnitte und Absätze mit Funktion `nonbinding` und `register`, Codeblöcke, Tabellen und Zitatblöcke. Ein neuer Marker ohne Registereintrag ist ebenfalls ein Befund. Der Lint schreibt nichts.

### 3.6.7 Der Fingerabdruck

Kurzhash (acht Hexzeichen aus SHA-256) des Definitionssatzes nach Normalisierung: U+00A0 zu Leerzeichen, Leerraum zusammengezogen, Satzzeichen am Ende entfernt, Kleinschreibung. `fp ID` vergleicht mit dem Register und meldet „Definition geändert"; `check` tut es für alle. Nur Meldung, nie Blockade — die Idee stammt aus Doorstops „suspect links" (Anhang B).

**Die Normalisierung nimmt auch Markdown-Auszeichnung heraus** (`*`, `_`, Backticks). Ohne das gilt `**64**` gegenüber `64` als Änderung, obwohl sich nur die Hervorhebung geändert hat — im Prototyp der erste Fehlalarm.

**Was die Meldung enthält** (entschieden am 2026-09-25, vormals Q-04; die Edit-Distanz-Vorprüfung eines früheren Entwurfs ist damit verworfen). Weicht der Fingerabdruck ab, meldet das Skript — immer, ohne Schwelle und ohne Unterdrückung. Warum nicht unterdrückt wird, steht in Kapitel 1.7.6. Die Meldung wird stattdessen entscheidungsfertig gemacht und trägt dreierlei:

- **Den Wortdiff.** `difflib.SequenceMatcher` über die wortweise zerlegten, normalisierten Sätze liefert die unterscheidenden Stellen; ausgegeben wird je Stelle `alt → neu`, bei Einfügung oder Streichung mit einem Zeichen für die leere Seite. Aus „Definition geändert" wird damit „64 → 128".
- **Das Kennzeichen „Zahlen betroffen".** Wahr, wenn ein geändertes Wort eine Ziffer enthält — **oder wenn unmittelbar vor der geänderten Stelle eine Zahl steht**. Die zweite Bedingung ist nicht verzichtbar: Ohne sie rutscht `5 ms → 5 s` durch, weil das geänderte Wort selbst keine Ziffer trägt. Mit ihr erkennt dieselbe Regel auch `64 Einträge → 64 Blöcke`, wo die Zahl bleibt und ihr Bezug sich ändert.
- **Das Kennzeichen „Normativsignal betroffen".** Wahr, wenn ein geändertes Wort in der Signalliste steht, die der Lint ohnehin führt (`lint_signals`), oder wenn sich das Vorkommen einer der zweiteiligen Wendungen ändert — „darf nicht", „at most", „at least".

Beides ist mit der Standardbibliothek zu bauen; `re`, `difflib` und `unicodedata` genügen, der Kern sind etwa fünfunddreißig Zeilen. Eine Fremdbibliothek ist nicht nötig, und der Kandidat aus Abschnitt 3.6.1 hat damit nichts zu tun.

**Was die Kennzeichen nicht leisten.** Sie sind Lesehilfe, keine Entscheidung. Eine ausgeschriebene Zahl wird nur erfasst, solange die Ziffernform an der Änderung beteiligt ist; die Signalliste ist nie vollständig; und eine Präzisierung wie `queue → eingangsqueue` erscheint ohne Kennzeichen, obwohl sie Bedeutung tragen kann. Das ist hinnehmbar, weil die Meldung in allen drei Fällen trotzdem kommt — die Instanz sieht den Diff und urteilt.

**Geschrieben wird erst nach dem Urteil.** `fp --update` und `apply` schreiben den neuen Wert; der Abgleich selbst schreibt nie, auch nicht, wenn er in einem Hook läuft (Vorgabe 2.8). Damit endet das Wiederholen derselben Meldung nach einer Beurteilung, ohne dass ein Hook eine Datei anfasst.

**Belegt am Prototyp** (2026-09-25, elf Fälle): richtig gemeldet wurden Zahländerung, Einheitenwechsel, Bezugswechsel, Signalwortwechsel, weggefallene Verneinung und ausgeschriebene Zahl; ohne Kennzeichen blieben Tippfehlerkorrektur, Satzumstellung, Wortpräzisierung und entferntes Komma; eine reine Auszeichnungsänderung erzeugte gar keine Meldung. Die beiden Fehler, die der erste Entwurf hatte — fehlende Markdown-Normalisierung und fehlende Zahl-Nachbarschaft —, sind dabei aufgefallen und oben eingearbeitet.

### 3.6.8 Prüffälle

Eine Fixture-Doku mit Register, geplanten Schritten und Code-Kommentaren (Kapitel 3.8) und dazu absichtlich beschädigte Varianten. Für jedes Kommando: erwartete `ITEM`-Zeilen auf der guten Fixture, erwartete `FINDING`- oder `FAILED`-Zeilen auf den beschädigten. „Keine Befunde" gilt erst als belegt, wenn die beschädigten Varianten gefunden werden.
