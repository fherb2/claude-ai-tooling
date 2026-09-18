## 3.2 Marken und Register

Stand von Arbeitspunkt 2 (2026-09-17). Entschieden sind Trennung, Markenformen, Registerort und -grammatik, die Regel für Altes und das Prinzip der Nachmarkierung. Offen und am Ende benannt: das Graphenmodell (gesondert zu besprechen), Details der Fingerabdruck-Normalisierung, die Platzierung der Marke im Satz und die Pflicht von Zitatmarken außerhalb der Funktion `relate`.

### 3.2.1 Trennung von Prosa und Register

Die Prosa trägt je Festlegung nur eine Marke; alle Attribute, Ereignisse und der Lebenszyklus stehen im Register. Grund: Ein Absatz, der mehrere Fakten in einem Gedankengang definiert, bleibt ein Absatz mit rotem Faden. Die Zeilenform, die ein Register braucht, gehört in eine Datei, die eine Liste ist. Der Festlegungstext hat genau ein Zuhause, die Prosa; das Register kopiert ihn nicht, sondern trägt ein Kurzlabel von wenigen Worten zur Orientierung, das ausdrücklich nicht normativ ist.

### 3.2.2 Marken

Zwei Formen, beide ASCII, beide ohne Leerzeichen, in Markdown als normaler Text gerendert:

- **Definitionsmarke** `[D-0042]` — genau eine je Festlegung, am Satz, der sie ausspricht. Spannt sich eine Festlegung über mehrere Sätze, steht die Marke am Ende des letzten.
- **Zitatmarke** `[>D-0042]` — an jeder weiteren Stelle, die die Festlegung heranzieht; das `>` liest sich als „siehe".

Pflicht ist die Definitionsmarke immer und die Zitatmarke in Abschnitten mit der Funktion `relate` (Kapitel 3.3); sonst ist die Zitatmarke optional. Der Skill-Parameter `marking` kann die Pflicht ausweiten (Kapitel 3.5). Aufnahmetest, was überhaupt eine Definitionsmarke bekommt: Kann Code das verletzen? Erläuterungen, Beispiele, Herleitungen bekommen keine.

Beispiel eines Absatzes mit drei Festlegungen (die IDs und Werte sind erfunden):

> Die Eingangsqueue der Pipeline fasst 64 Einträge [D-0042], weil das Latenzbudget von 5 ms bei zwölf gleichzeitig laufenden Kernels sonst nicht zu halten ist; eine dynamische Größe scheiterte an der Fragmentierung des Shared Memory. Deshalb startet der Orchestrator Kernels nie direkt, sondern über den Starter [D-0043], der die Queue vor dem ersten Eintrag reserviert [D-0044].

Der Grund und die verworfene Alternative stehen in der Prosa, wo sie gedacht wurden; das Register verweist mit `in prose` darauf.

Offen: ob die Marke vor oder nach dem Satzzeichen steht. Vorschlag: vor dem Satzzeichen, wie im Beispiel; für `grep` ist es gleichgültig.

### 3.2.3 ID

`D-0042`: ein globaler Zähler je Register, mindestens vier Stellen, nie neu vergeben, vom Skript vergeben (`next-id`). Die ID trägt kein Kapitel und keinen Ort; das Kapitel leitet das Skript aus dem Ort der Definitionsmarke ab. Grund: Kapitel werden umnummeriert, weil inhaltlich Nahes im Dokument nahe beieinander liegen soll und eine Doku von klein auf wächst; eine Adresse, die dabei lügt, ist schlechter als keine. Das `D` steht für decision.

Wird eine Festlegung inhaltlich zu einer anderen — etwa von einer Kapitelfestlegung zu einer projektweiten Vorgabe —, ist das eine neue Festlegung mit neuer ID; die alte wird abgelöst (3.2.6).

### 3.2.4 Register — Ort

Eine Datei je Doku, Standardname `decisions.md` im Ordner der Doku. Das Skript findet sie in dieser Reihenfolge: Script-Argument `--register` → Skill-Parameterdatei → eine Zeile `[register: pfad]` in der Dokudatei → Standard im Ordner der Datei. Findet es nichts, meldet es, wo es gesucht hat und mit welchem Script-Argument der Aufrufer es hinführt (Vorgabe 2.4). Damit darf eine Doku ihr Register in einem anderen Ordner führen und aus jeder Dokudatei darauf verweisen.

### 3.2.5 Register — Grammatik

Jede Zeile, die zu einer Festlegung gehört, beginnt mit eckigen Klammern, darin zuerst die ID, dann Schlüsselwörter; nach der Klammer folgt Prosa. Jede Zeile wiederholt die ID, damit `grep` alles zu einer Festlegung liefert, egal wo die Zeile steht, und das Skript keine Nachbarschaft erkennen muss.

| Zeile | Form | Inhalt nach der Klammer |
|---|---|---|
| Kopf | `[ID kind status]` oder `[ID kind status pinned]` | Kurzlabel, nicht normativ |
| Grund | `[ID reason]` · `[ID reason unknown]` | Grund einer `chosen`-Festlegung, oder `in prose` |
| Quelle | `[ID source]` | Quelle einer `given`-Festlegung, oder `in prose` |
| Alternative | `[ID instead]` | eine Alternative, ein Grund der Ablehnung — eine Zeile; oder `in prose` |
| Suchschlüssel | `[ID keys]` | zwei bis vier markante Begriffe, durch Semikolon getrennt; finden unmarkierte Erwähnungen |
| Fingerabdruck | `[ID fp]` | Kurzhash des normalisierten Definitionssatzes; erkennt, dass die Definition sich geändert hat |
| Reibung | `[ID friction JJJJ-MM-TT]` | was sich gerieben hat, ein Halbsatz |
| Bestätigung | `[ID upheld JJJJ-MM-TT]` | gegen welche Idee oder welchen Befund geprüft |
| offene Frage | `[ID pending JJJJ-MM-TT]` | die Frage in Prosa; wird nach Beantwortung gelöscht |
| Ablösung | `[ID superseded JJJJ-MM-TT by ID2]` | optional ein Halbsatz |
| Stilllegung | `[ID retired JJJJ-MM-TT]` | warum die Festlegung entfällt |

Regeln: Schlüsselwörter in der Kopfzeile in fester Reihenfolge beim Schreiben (ID, `kind`, `status`, `pinned`), beim Lesen ist die Reihenfolge gleichgültig. Die Zeilen einer Festlegung stehen direkt untereinander in der Reihenfolge der Tabelle — Konvention für den Leser, der Parser hängt nicht daran. Keine Backticks, kein Fettdruck in Registerzeilen; genau dort frisst der WYSIWYG-Editor Leerzeichen. Das Skript normalisiert U+00A0 zu Leerzeichen, bevor es die Klammer zerlegt. Datum immer `JJJJ-MM-TT`. Die Kennzeichnung eines Registerabschnitts trägt die Rolle `[DS:register]` (Kapitel 3.3).

### 3.2.6 Altes: drei Fälle, eine Regel

Was alt ist, darf nicht unmarkiert in der Prosa stehen — denn genau der unmarkierte Altbestand wird als gültige Festlegung gelesen und blockiert Ideen. Ob ein alter Absatz stehen bleibt, entscheidet der Entwickler im Einzelfall: weil er als Begründung einer Änderung wirkt, weil er Kontext verwässert, weil gerade keine Zeit ist. Der Mechanismus verlangt nur die Marke.

| Fall | Was es ist | Fußabdruck | Prosa |
|---|---|---|---|
| verworfene Alternative (`instead`) | wurde nie Festlegung; beim Entscheiden erwogen und abgelehnt | in der Prosa als Teil der Begründung, sonst eine Registerzeile | bleibt, wo sie den Gedankengang trägt |
| abgelöste Festlegung (`superseded`) | war bindend, ist durch eine neue ersetzt | Registereintrag bleibt mit Datum und Nachfolger | der normative Satz wird umgeschrieben oder gestrichen; bleibt er als Begründung stehen, trägt er die Marke der abgelösten ID und ist so maschinell als Geschichte erkennbar |
| Historie (alte Reviews, Verlauf) | Beurteilungsmaterial | Anhang, Rolle `appendix` | nichts Neues |

Weil IDs stabil sind und das Register den Nachfolger kennt, löst sich jeder alte Verweis weiter auf; niemand muss quer durchs Projekt suchen, bevor er weiterarbeiten darf. Die Grenze zwischen Kapiteln und Anhang aus dem Vorläufer (Anhang A, Abschnitt A.9) bleibt unberührt: In die Prosa kommt nichts Neues; die verworfene Alternative steht dort, wo sie schon immer stand — in der Argumentation — oder als eine Zeile im Register.

### 3.2.7 Nachmarkierung einer bestehenden Doku

Nur am Berührungspunkt, nie als Gesamtinventur. Die Instanz liest das berührte Kapitel, erkennt bindende Aussagen (Aufnahmetest), bildet Annahmen über die Attribute und trägt sie in den Planabschnitt „Berührte Festlegungen" ein (Kapitel 3.1). Mit der Ausführung des freigegebenen Plans werden Marke und Registerzeilen geschrieben. Steckt der normative Satz mitten in einem Absatz, bekommt er seine Marke an seinem Ende; er wird nicht aus dem Absatz gelöst. Eine Gesamtinventur — alte Doku, Faktenliste, neue Gruppierung — bleibt ein eigener Projektschritt auf ausdrücklichen Auftrag; die Fähigkeit dazu trägt der Skill `konzept-segmentierung`.

### 3.2.8 Layout der Prosa

Ob ein Absatz eine Zeile ist oder nach einer festen Breite umbricht und Absätze durch Leerzeilen getrennt sind, berührt den Mechanismus nicht: Marken sind Inline-Text, das Register ist eine eigene Datei. Das Layout wird beim Skillstart aus der vorhandenen Doku abgelesen oder erfragt (Kapitel 3.5) und bestimmt nur, wie die Instanz Prosa schreibt.

### 3.2.9 Rückfalloption ohne Marken

Wo ein Entwickler keine Klammern im Text will, ankert das Register die Festlegung über Datei und Wortlaut eines Kernsatzes. Das ist fragiler — ein editierter Satz bricht den Anker, `check` meldet es — und lässt die Prosa unberührt. Die Wahl trifft der Skillstart; der Standard sind Marken.

### 3.2.10 Entscheidungsgrundlagen

Das Graphenmodell — was eine Kante ist und wie sie gewichtet wird — ist in Kapitel 3.6 als [Q-20] geführt und wird gesondert besprochen.

> **[Q-03] Entscheidungsgrundlage — Platzierung der Marke im Satz**
> Kontext: Die Definitionsmarke steht am Satz, der die Festlegung ausspricht. Für `grep` ist die Position gleichgültig; für das Lesen nicht.
> Optionen: (a) vor dem Satzzeichen — „… fasst 64 Einträge [D-0042]." wie im Beispiel in 3.2.2; (b) nach dem Satzzeichen — „… fasst 64 Einträge. [D-0042]".
> Vorschlag: (a) — die Marke liest sich als Teil des Satzes, und ein Satz mit mehreren Festlegungen bleibt eindeutig zuordenbar.
> Gewicht: klein · Blockiert: Fahrplanschritt 1
> Antwort:

> **[Q-04] Entscheidungsgrundlage — Fingerabdruck: ob und wie**
> Kontext: Der Fingerabdruck erkennt, dass ein Definitionssatz geändert wurde, und löst die Meldung „Zitatstellen prüfen" aus (Idee aus Doorstops „suspect links"). Er kostet je Festlegung eine Registerzeile und erzeugt bei kosmetischen Edits Rauschen, das nur die Normalisierung dämpft (U+00A0, Leerraum, Satzzeichen am Ende, Kleinschreibung).
> Optionen: (a) in Stufe 2 des Skripts bauen und in der Probe messen; (b) weglassen, Änderungspropagation nur über Marken und Suchschlüssel; (c) erst nach der Probe entscheiden.
> Vorschlag: (a); die Probe misst das Rauschen (Kapitel 3.8).
> Gewicht: mittel · Blockiert: Fahrplanschritt 5
> Antwort:

> **[Q-05] Entscheidungsgrundlage — Suchschlüssel**
> Kontext: Zwei bis vier markante Begriffe je Festlegung im Register finden unmarkierte Erwähnungen (`mentions`) und liefern Kandidaten außerhalb des Graphen (`impact`). Wer sie wählt und pflegt, entscheidet über ihre Qualität.
> Optionen: (a) die Instanz wählt sie beim Anlegen der Festlegung, Pflege nur bei Reibung oder wenn `mentions` sichtbar Erwähnungen verfehlt; (b) der Entwickler bestätigt sie im Planabschnitt wie die übrigen Attribute; (c) ohne Suchschlüssel, nur Marken.
> Vorschlag: (a), mit Anzeige im Planabschnitt, damit Du sie korrigieren kannst, ohne dass sie eine eigene Frage kosten.
> Gewicht: mittel · Blockiert: Fahrplanschritt 1
> Antwort:

> **[Q-06] Entscheidungsgrundlage — Zitatmarken außerhalb der Funktion `relate`**
> Kontext: Pflicht sind Zitatmarken nur in Abschnitten mit Funktion `relate`; in Bausteinkapiteln untereinander sind sie optional. Ob `mentions` ohne sie zu viel übersieht, kann erst die Probe zeigen.
> Optionen: (a) bei „optional" bleiben und die Probe entscheiden lassen; (b) von vornherein Pflicht überall (Skill-Parameter `marking: full` als Standard).
> Vorschlag: (a).
> Gewicht: klein · Blockiert: nichts vor der Probe
> Antwort:

> **[Q-07] Entscheidungsgrundlage — Rückfalloption ohne Marken (Wortlaut-Anker)**
> Kontext: 3.2.9 erlaubt, das Register über Datei und Wortlaut eines Kernsatzes zu ankern, wenn ein Entwickler keine Klammern im Text will. Das ist fragiler und kostet im Skript einen zweiten Ankermechanismus.
> Optionen: (a) beibehalten als Wahl beim Skillstart; (b) streichen — Marken sind der einzige Weg; (c) auf später verschieben.
> Vorschlag: (c) — erst bauen, wenn ein Projekt es braucht; im Regeltext als Möglichkeit nennen.
> Gewicht: klein · Blockiert: Fahrplanschritt 3
> Antwort:
