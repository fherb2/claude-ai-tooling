## 3.6 Das Skript

Stand (2026-09-17): Kommandosatz, Ausgabevertrag und Aufrufprinzip sind Vorschlag mit weitgehender Zustimmung; das Auswirkungsmodul ist in seinem Graphenmodell noch gesondert zu besprechen.

### 3.6.1 Ort, Name, Laufzeit

Ein Skript `files/design-doc.py` im Skill-Ordner, aufgerufen über `${CLAUDE_SKILL_DIR}/files/design-doc.py`, dazu das Modul `files/impact.py` für die Auswirkungsrechnung. Python ab 3.11, nur Standardbibliothek. Die Bibliothek networkx wird benutzt, wenn sie importierbar ist, und durch einen eingebauten Kürzeste-Wege-Algorithmus ersetzt, wenn nicht; kein Zielprojekt wird zu einer Installation gezwungen. Der Name `sdd` wurde verworfen, weil er in der Agentenwelt für Spec-Driven Development steht.

### 3.6.2 Aufrufprinzip

Ein Aufruf je Anker (Kapitel 3.1, Abschnitt 3.1.9), nicht mehrere. Jede Voraussetzung hat einen Default, wird gesucht, ihr Fehlen exakt gemeldet, und sie ist per Argument überschreibbar (Vorgabe 2.4). Kein Kommando ändert Prosa. Das Register ändern nur `supersede`, `retire`, `fp --update` und das Schreiben von Registerzeilen, das die Instanz nach freigegebenem Plan über `add` auslöst.

### 3.6.3 Ausgabevertrag

Die Ausgabe ist für die Instanz gebaut, nicht für einen Menschen am Terminal. Sie ist zeilenorientiert, jede Zeile beginnt mit einer Klasse in Großbuchstaben, danach Felder in fester Reihenfolge, getrennt durch ` | `, jedes Feld als `key: value`; Werte enthalten keinen senkrechten Strich. Schlüssel sind englisch; Werte dürfen deutsche Prosa sein. Keine Erzählung, keine Farben, keine Symbole, kein Fortschrittslog. Zahlen sind Zahlen, nicht Wörter. Eine Ausgabe hat höchstens etwa vierzig Zeilen; wird gekürzt, sagt die letzte Zeile, wie viele fehlen und mit welchem Argument sie erscheinen.

| Klasse | Bedeutung | Felder |
|---|---|---|
| `OK` | Lauf erfolgreich, ein Satz — auch wenn nichts zu berichten ist | `msg` |
| `ITEM` | ein Gegenstand einer Liste | kommandoabhängig, feste Reihenfolge |
| `FINDING` | ein Befund | `subject`, `issue`, `proposal` |
| `DECIDE` | eine Entscheidungsvorlage, die das Skript nicht mechanisch lösen kann | `subject`, `question`, `options`, `proposal` |
| `FAILED` | Abbruch | `step`, `cause`, `state`, `remedy` — die Abhilfe nennt das exakte Argument |
| `SUMMARY` | letzte Zeile jeder Ausgabe | `items`, `findings`, `decide` als Zahlen |

Exit-Codes: 0 bei `OK` ohne Befunde, 1 bei Befunden oder Entscheidungsvorlagen, 2 bei `FAILED` und bei struktureller Inkonsistenz — der Code, mit dem der Commit-Hook blockiert (Kapitel 3.7). Mit `--json` erscheint dieselbe Information als JSON-Array; die Hooks nutzen es, um `additionalContext` zu füllen. Eine unbehandelte Ausnahme ist ein Defekt; die Prüffälle enthalten absichtlich kaputte Eingaben (fehlende Klammern, falsche Schlüsselwörter, U+00A0, Dubletten), für die eine `FAILED`- oder `FINDING`-Zeile erwartet wird.

Was mechanisch entscheidbar ist, entscheidet das Skript und gibt es als `ITEM` oder `OK` aus; `DECIDE` ist die Ausnahme für das, was sich nicht kodieren lässt (Vorgabe 2.6). Die Trennung ist sichtbar: Ein `ITEM` ist Fakt, ein `DECIDE` ist Vorlage.

### 3.6.4 Kommandos

| Kommando | Liest | Gibt aus | Exit |
|---|---|---|---|
| `list [--chapter DATEI]` | Register, Marken | `ITEM` je Festlegung: `id`, `chapter` (abgeleitet), `kind`, `status`, `hardness`, `label` | 0 |
| `show ID` | Register, Doku | alle Registerzeilen der ID, Definitionsort, Zitatorte | 0 |
| `next-id` | Register | nächste freie ID | 0 |
| `add ID …` | — | schreibt eine Registerzeile in der Grammatik von Kapitel 3.2; nur nach freigegebenem Plan aufgerufen | 0 |
| `check [--summary]` | Register, Doku, geplante Schritte | `FINDING` je Abweichung: Marke ohne Eintrag, Eintrag ohne Definitionsmarke, mehrere Definitionsmarken, unlesbare Zeile, `target:` auf unbekannte ID oder Datei, `superseded` ohne Ziel, Dublette; mit `--summary` nur Zahlen | 0 keine, 1 Befunde, 2 strukturell |
| `lint --file DATEI --changed` | Git-Diff der Datei | `FINDING` je geänderter Zeile mit Normativsignal ohne Marke und je neuer Marke ohne Eintrag | 0/1 |
| `mentions ID [--code ORDNER]` | Doku, optional Code | `ITEM` je Vorkommen: Marke, Zitat, Suchschlüssel-Treffer, mit Datei und Zeile | 0 |
| `hardness ID [--word fixed|open]` | Register, geplante Schritte, Parameter | `ITEM` mit Härte und zutreffender Bedingung in Prosa (R1–R7) | 0 |
| `impact --chapter DATEI \| --ids …` | Graph aus Marken, Nähe, Suchschlüsseln | `ITEM` je Kandidat: `id`, `why` (Definition, Mitzitat, gleicher Absatz, Suchschlüssel), `distance` | 0 |
| `plan-section --ids …` | Register, Härte | Gerüst des Planabschnitts „Berührte Festlegungen" | 0 |
| `explain ID` | wie `hardness` | ein Satz für den Entwickler, ohne Prüfungsnummer | 0 |
| `fp ID [--update]` | Doku | Fingerabdruck des Definitionssatzes, Vergleich mit Register | 0/1 |
| `supersede ALT NEU` · `retire ID` | Register | schreibt die Lebenszykluszeile; listet verbleibende Zitate | 0 |

### 3.6.5 Das Auswirkungsmodul

`impact.py` kapselt Kanten, Gewichte, Kostenfunktion und Abbruch, weil genau hier später nachjustiert wird. Es beantwortet die Frage: Welche Festlegungen sind Kandidaten dafür, von einer Änderung an einer gegebenen Festlegung oder einem Kapitel berührt zu sein? Der Name folgt der Auswirkungsanalyse, die der bisherige Standard als Aufgabe von Segment 1 nennt.

**Knoten** sind Festlegungen. **Kanten** entstehen aus dem Text: zwei Festlegungen, die im selben Absatz genannt sind (Definition oder Zitat), im selben Abschnitt, in Nachbarabschnitten, im selben Kapitel; dazu Treffer der Suchschlüssel als Quelle außerhalb des Graphen. Vorschlag für die Gewichte: gleicher Absatz 0,8 · Mitzitat in einem Absatz mit Funktion `relate` 0,7 · gleicher Abschnitt 0,4 · Nachbarabschnitt 0,2 · gleiches Kapitel 0,05.

**Drei Kostenfunktionen**, austauschbar, damit die Probe sie vergleicht:

1. **Additiv**: Kosten je Kante 1/w, Weglänge Σ Kosten, Abbruch bei `impact_cutoff` — ein Kürzeste-Wege-Problem; networkx rechnet es direkt mit `single_source_dijkstra_path_length(G, source, cutoff, weight=funktion)` (belegt, Doku 3.6.1).
2. **Multiplikativ nach dem Vorschlag des Entwicklers**: Weglänge Σ(Hops) / Π(Gewichte); eine schwache Kante irgendwo im Pfad verunsichert die ganze Kette. Pfadabhängig, braucht eine eigene Suche; bei Graphen mit Hunderten Knoten unproblematisch.
3. **Produkt mit Dämpfung**: Bewertung Π w × d^Hops mit d = 0,7, Abbruch unter einer Schwelle; entspricht dem Rechenmodell im Anhang.

`impact_model: hops` ist der Sonderfall, in dem nur Kanten ab 0,7 zählen und `impact_cutoff` die Tiefe ist. Das Rechenmodell (Anhang) zeigt: Tiefe 1 bleibt in jeder Dokugröße bei einer Handvoll Kandidaten; Tiefe 2 wächst mit der Doku und liegt bei dreihundert Festlegungen im Median über zwanzig; die gewichtete Variante ist ein stetiger Regler zwischen beiden. Was das Modell nicht sagt: ob zusätzliche Kandidaten relevant sind — das misst die Probe.

### 3.6.6 Der Lint

Prüft nur geänderte Zeilen der übergebenen Datei (Git-Diff gegen den Index und gegen HEAD). Eine Zeile ist ein Befund, wenn sie ein Normativsignal trägt — Signalwörter aus `lint_signals` (Standard deutsch und englisch: muss, müssen, soll, sollen, immer, nie, niemals, darf nicht, genau, höchstens, mindestens, must, shall, always, never, at most, at least) oder einen Zahlenwert mit Einheit — und keine Marke `[D-`. Ausgenommen sind Abschnitte mit Funktion `nonbinding` und `register`, Codeblöcke, Tabellen und Zitatblöcke. Eine neue Marke ohne Registereintrag ist ebenfalls ein Befund. Der Lint schreibt nichts.

### 3.6.7 Der Fingerabdruck

Kurzhash (acht Hexzeichen aus SHA-256) des Definitionssatzes nach Normalisierung: U+00A0 zu Leerzeichen, Leerraum zusammengezogen, Satzzeichen am Ende entfernt, Kleinschreibung. `fp ID` vergleicht mit dem Register und meldet „Definition geändert"; `check` tut es für alle. Nur Meldung, nie Blockade — die Idee stammt aus Doorstops „suspect links" (Anhang).

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
> Kontext: Im Gespräch hieß der Vorgang „Kontakt"; Du wolltest etwas mit Bezug zu Graph oder Semantik. `impact` folgt der Auswirkungsanalyse des bisherigen Standards. Alternativen: `neighborhood`, `related`, `reach`.
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
