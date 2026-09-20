## 3.6 Das Skript

Stand (2026-09-17): Kommandosatz, Ausgabevertrag und Aufrufprinzip sind Vorschlag mit weitgehender Zustimmung; das Auswirkungsmodul ist in seinem Graphenmodell noch gesondert zu besprechen.

### 3.6.1 Ort, Name, Laufzeit

Ein Skript `files/design-doc.py` im Skill-Ordner, aufgerufen über `${CLAUDE_SKILL_DIR}/files/design-doc.py`, dazu das Modul `files/impact.py` für die Auswirkungsrechnung. Python ab 3.11, sonst nur Standardbibliothek. Der Name `sdd` wurde verworfen, weil er in der Agentenwelt für Spec-Driven Development steht.

**Die eine optionale Bibliothek.** `networkx` rechnet kürzeste Wege in gewichteten Graphen direkt und deckt damit eine der drei Kostenfunktionen (3.6.5) ohne eigenen Code ab. Sie ist **nie Voraussetzung**: Fehlt sie, rechnet ein eingebauter Algorithmus von etwa dreißig Zeilen. Ihre Anwesenheit ist auf einem Entwicklungsrechner Zufall, und was niemand kennt, installiert niemand — deshalb ist ihre Benutzung eine bewusste Wahl des Entwicklers (Kapitel 1.7.4), festgehalten im Skill-Parameter `impact_lib`:

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

Exit-Codes: 0 bei `OK` ohne Befunde, 1 bei Befunden oder Entscheidungsvorlagen, 2 bei `FAILED` und bei struktureller Inkonsistenz — der Code, mit dem der Commit-Hook blockiert (Kapitel 3.7). Mit `--json` erscheint dieselbe Information als JSON-Array; die Hooks nutzen es, um `additionalContext` zu füllen. Eine unbehandelte Ausnahme ist ein Defekt; die Prüffälle enthalten absichtlich kaputte Eingaben (fehlende Klammern, falsche Schlüsselwörter, U+00A0, Dubletten), für die eine `FAILED`- oder `FINDING`-Zeile erwartet wird.

Was mechanisch entscheidbar ist, entscheidet das Skript und gibt es als `ITEM` oder `OK` aus; `DECIDE` ist die Ausnahme für das, was sich nicht kodieren lässt (Vorgabe 2.6). Die Trennung ist sichtbar: Ein `ITEM` ist Fakt, ein `DECIDE` ist Vorlage.

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
| `supersede --pairs ALT:NEU,…` · `retire --ids …` | Register | schreibt die Lebenszykluszeilen; listet je ID die verbleibenden Zitate | 0 |

**Auskunftskommandos** — für die Nachfrage des Entwicklers; sie kommen im Ablauf nicht vor und dürfen deshalb einstellig bleiben:

| Kommando | Liest | Gibt aus | Exit |
|---|---|---|---|
| `show ID` | Register, Doku | alle Registerzeilen der ID, Definitionsort, Zitatorte | 0 |
| `explain ID` | wie `hardness` | ein Satz für den Entwickler, ohne Prüfungsnummer | 0 |
| `next-id` | Register | nächste freie ID | 0 |

Was ein Kommando **nicht** hat, ist ebenso Festlegung: Es gibt kein `add` für eine einzelne Registerzeile. Registerzeilen entstehen ausschließlich über `apply` aus einem freigegebenen Plan — in einem Aufruf, nicht in zehn (Kapitel 1.3.6).


### 3.6.5 Das Auswirkungsmodul

**Wozu das Modul da ist und woran es sich rechtfertigt, steht in Kapitel 1.7.4.** Hier steht, woraus es rechnet. `impact.py` kapselt Kanten, Gewichte, Kostenfunktion und Abbruch, weil genau hier später nachjustiert wird; der Name folgt der Auswirkungsanalyse, die der Vorläufer als Aufgabe von Segment 1 nennt (Anhang A, Abschnitt A.6).

**Knoten** sind Festlegungen. **Kanten** entstehen aus dem Text: zwei Festlegungen, die im selben Absatz genannt sind (Definition oder Zitat), im selben Abschnitt, in Nachbarabschnitten, im selben Kapitel; dazu Treffer der Suchschlüssel als Quelle außerhalb des Graphen. Vorschlag für die Gewichte: gleicher Absatz 0,8 · Mitzitat in einem Absatz mit Funktion `relate` 0,7 · gleicher Abschnitt 0,4 · Nachbarabschnitt 0,2 · gleiches Kapitel 0,05.

Diese Gewichte und die Dämpfung heißen **Graphenparameter**: Sie parametrisieren den funktionalen Zusammenhang der Auswirkungsrechnung. Sie sind **keine Skill-Parameter** — sie stehen im Skill, entweder direkt im Modul oder in einer Datei des Skill-Ordners, nie in der Projektkonfiguration. Grund: Der Entwickler kann sie nicht beurteilen; ob eine Kante „gleicher Abschnitt" 0,4 oder 0,35 wiegt, ist keine Eigenschaft seines Projekts, sondern des Verfahrens. Sie ändern sich nach einer Messung (Kapitel 3.8) und dann für alle Projekte. Was ein Projekt davon einstellt, sind allein die zwei groben Griffe `impact_model` und sein Abbruchwert — eng oder weit, nicht einzelne Gewichte (Entscheidung des Entwicklers vom 2026-09-18).

**Drei Kostenfunktionen**, austauschbar, damit die Probe sie vergleicht:

1. **Additiv**: Kosten je Kante 1/w, Weglänge Σ Kosten, Abbruch bei `impact_cutoff` — ein Kürzeste-Wege-Problem; networkx rechnet es direkt mit `single_source_dijkstra_path_length(G, source, cutoff, weight=funktion)` (belegt, Doku 3.6.1).
2. **Multiplikativ nach dem Vorschlag des Entwicklers**: Weglänge Σ(Hops) / Π(Gewichte); eine schwache Kante irgendwo im Pfad verunsichert die ganze Kette. Pfadabhängig, braucht eine eigene Suche; bei Graphen mit Hunderten Knoten unproblematisch.
3. **Produkt mit Dämpfung**: Bewertung Π w × d^Hops mit d = 0,7, Abbruch unter einer Schwelle; entspricht dem Rechenmodell in Anhang B.

Der Skill-Parameter `impact_model: hops` ist der Sonderfall, in dem nur Kanten ab 0,7 zählen und `impact_cutoff` die Tiefe ist. Das Rechenmodell (Anhang B) zeigt: Tiefe 1 bleibt in jeder Dokugröße bei einer Handvoll Kandidaten; Tiefe 2 wächst mit der Doku und liegt bei dreihundert Festlegungen im Median über zwanzig; die gewichtete Variante ist ein stetiger Regler zwischen beiden. Was das Modell nicht sagt: ob zusätzliche Kandidaten relevant sind — das misst die Probe.

### 3.6.6 Der Lint

Prüft nur geänderte Zeilen der übergebenen Datei (Git-Diff gegen den Index und gegen HEAD). Eine Zeile ist ein Befund, wenn sie ein Normativsignal trägt — Signalwörter aus `lint_signals` (Standard deutsch und englisch: muss, müssen, soll, sollen, immer, nie, niemals, darf nicht, genau, höchstens, mindestens, must, shall, always, never, at most, at least) oder einen Zahlenwert mit Einheit — und keinen Marker `[D-`. Ausgenommen sind Abschnitte mit Funktion `nonbinding` und `register`, Codeblöcke, Tabellen und Zitatblöcke. Ein neuer Marker ohne Registereintrag ist ebenfalls ein Befund. Der Lint schreibt nichts.

### 3.6.7 Der Fingerabdruck

Kurzhash (acht Hexzeichen aus SHA-256) des Definitionssatzes nach Normalisierung: U+00A0 zu Leerzeichen, Leerraum zusammengezogen, Satzzeichen am Ende entfernt, Kleinschreibung. `fp ID` vergleicht mit dem Register und meldet „Definition geändert"; `check` tut es für alle. Nur Meldung, nie Blockade — die Idee stammt aus Doorstops „suspect links" (Anhang B).

### 3.6.8 Prüffälle

Eine Fixture-Doku mit Register, geplanten Schritten und Code-Kommentaren (Kapitel 3.8) und dazu absichtlich beschädigte Varianten. Für jedes Kommando: erwartete `ITEM`-Zeilen auf der guten Fixture, erwartete `FINDING`- oder `FAILED`-Zeilen auf den beschädigten. „Keine Befunde" gilt erst als belegt, wenn die beschädigten Varianten gefunden werden.

### 3.6.9 Entscheidungsgrundlagen

> **[Q-20] Entscheidungsgrundlage — Das Graphenmodell (gesondert zu besprechen)**
> Kontext: Du hast die Aussage „eine Kante entsteht, wenn zwei Festlegungen im selben Absatz genannt werden" als allgemeingültige Definition angezweifelt und eine gesonderte Besprechung gewünscht. 3.6.5 ist der Vorschlagsstand: Knoten sind Festlegungen; Kanten entstehen aus gemeinsamem Vorkommen (Absatz, Abschnitt, Nachbarabschnitt, Kapitel) mit abnehmenden Gewichten; Suchschlüssel-Treffer sind eine Quelle außerhalb des Graphen. Offen ist grundsätzlich: Was soll eine Kante bedeuten — „steht im Text nahe" oder „hängt inhaltlich zusammen"? Beides deckt sich nur teilweise, und nur das Erste ist mechanisch.
> Optionen: hier nur Sammelstelle für Gesichtspunkte; die Besprechung führt zur Festlegung.
> Vorschlag: keiner vorab.
> Gewicht: groß · Blockiert: Fahrplanschritt 5
> Antwort:

> **[Q-21] Entscheidungsgrundlage — Kostenfunktion der Auswirkungsrechnung**
> Kontext: Drei Kostenfunktionen sind vorgesehen (additiv 1/w; Deine Σ Hops / Π Gewichte; Produkt mit Dämpfung). Die Probe soll sie vergleichen; eine Vorabpräferenz würde die Reihenfolge der Umsetzung bestimmen.
> Optionen: (a) alle drei bauen, Probe entscheidet; (b) nur additiv (Bibliotheksunterstützung) und Deine Formel; (c) nur eine, Deine.
> Vorschlag: (a); der Mehraufwand ist ein Modul mit drei kurzen Funktionen.
> Gewicht: klein · Blockiert: Fahrplanschritt 5
> Antwort:

> **[Q-22] Entscheidungsgrundlage — Name `impact` statt „Kontakt"**
> Kontext: Im Gespräch hieß der Vorgang „Kontakt"; Du wolltest etwas mit Bezug zu Graph oder Semantik. `impact` folgt der Auswirkungsanalyse des Vorläufers (Anhang A). Alternativen: `neighborhood`, `related`, `reach`.
> Optionen: (a) `impact`; (b) eine der Alternativen; (c) ein anderes Wort.
> Vorschlag: (a).
> Gewicht: klein · Blockiert: Fahrplanschritt 4
> Antwort:

> **[Q-23] Entscheidungsgrundlage — Standardausgabe Zeilen oder JSON**
> Kontext: 3.6.3 macht die Zeilenform zum Standard und JSON zur Option für Hooks. Für die Instanz ist die Zeilenform bei kurzen Listen billiger zu lesen; JSON ist eindeutiger, aber länger.
> Optionen: (a) Zeilen als Standard, `--json` auf Anforderung; (b) JSON als Standard, Zeilen auf Anforderung.
> Vorschlag: (a).
> Gewicht: klein · Blockiert: Fahrplanschritt 4
> Antwort:

> **[Q-24] Entscheidungsgrundlage — Dateiname des Skripts**
> Kontext: `design-doc.py` und `impact.py` im Ordner `files/` des Skills. `sdd.py` wurde verworfen (Spec-Driven Development).
> Optionen: (a) `design-doc.py`; (b) `software-design-doc.py` wie der Skill; (c) anderer Name.
> Vorschlag: (a).
> Gewicht: klein · Blockiert: Fahrplanschritt 4
> Antwort:

> **[Q-25] Entscheidungsgrundlage — networkx optional oder Voraussetzung**
> Kontext: networkx rechnet die additive Kostenfunktion direkt; ein eingebauter Kürzeste-Wege-Algorithmus ist etwa dreißig Zeilen. Optional heißt zwei Codepfade, Voraussetzung heißt eine Installation in jedem Zielprojekt.
> Optionen: (a) optional — benutzen, wenn importierbar, sonst eingebaut; (b) Voraussetzung; (c) gar nicht, immer eingebaut.
> Vorschlag: (c) — ein Codepfad, keine Abhängigkeit; networkx bleibt Referenz für die Prüffälle.
> Gewicht: klein · Blockiert: Fahrplanschritt 5
> Antwort:
