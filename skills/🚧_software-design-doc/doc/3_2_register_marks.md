## 3.2 Marker und Register

Stand von Arbeitspunkt 2 (2026-09-17). Entschieden sind Trennung, Markerformen, Registerort und -grammatik, die Regel für Altes und das Prinzip der Nachmarkierung. Am 2026-09-21 entschieden: die Platzierung des Markers im Satz (vormals Q-03). Am 2026-09-25 entschieden: Der zweite Ankermechanismus über Datei und Wortlaut eines Kernsatzes — 2026-09-21 als Rückfalloption zurückgestellt (vormals Q-07) — ist verworfen, weil er die Adresse einer Festlegung an einen Dateinamen bindet (Vorgabe 2.3); die Begründung steht in Kapitel 1.3.3. Der Abschnitt, der ihn beschrieb, ist entfallen; unter 3.2.9 stehen jetzt die Notizen im Commit, ebenfalls am 2026-09-25 entschieden. Am 2026-09-24 entschieden: der Fingerabdruck (vormals Q-04), die Suchschlüssel (vormals Q-05), die Zitatmarkerpflicht außerhalb `relate` (vormals Q-06) und das Graphenmodell (vormals Q-20) — siehe `status.md`; die Entscheidungen stehen an ihren Funktionsstellen in Kapitel 1.

### 3.2.1 Trennung von Prosa und Register

> Die Prosa trägt je Festlegung nur einen Marker; alle Attribute, Ereignisse und der Lebenszyklus stehen im Register. Warum die Trennung so verläuft, steht in Kapitel 1.3.2. Für die Umsetzung folgt daraus: Der Festlegungstext hat genau ein Zuhause, die Prosa; das Register kopiert ihn nicht, sondern trägt ein Kurzlabel von wenigen Worten zur Orientierung, das ausdrücklich nicht normativ ist und von keiner Prüfung gelesen wird.

### 3.2.2 Marker

> Ein **Marker** ist ein Feld in der Prosa: Der Zeichenbereich von seiner öffnenden bis zu seiner schließenden Klammer ist sein **Marker-Feld** — ein Feld im Sinne der Textverarbeitung, also ein Abschnitt, den nicht der Schreibende füllt, sondern das Werkzeug (Vorgabe 2.10). Gefüllt wird er mit einer Adresse und mit nichts sonst.
>
> Zwei Formen, beide ASCII, beide ohne Leerzeichen, in Markdown als normaler Text gerendert:
>
> - **Definitionsmarker** `[D-0042]` — genau eine je Festlegung, am Satz, der sie ausspricht. Spannt sich eine Festlegung über mehrere Sätze, steht der Marker am Ende des letzten.
> - **Zitatmarker** `[>D-0042]` — an jeder weiteren Stelle, die die Festlegung heranzieht; das `>` liest sich als „siehe".
>
> Pflicht ist der Definitionsmarker immer, der Zitatmarker in Abschnitten mit der Funktion `relate` (Kapitel 1.3.3); sonst ist der Zitatmarker optional. Der Skill-Parameter `marking` kann die Pflicht ausweiten (Kapitel 3.5). Jeder einzelne Marker steht dabei als Vorschlag im Plan und kann abgelehnt werden; die Pflicht sagt, wo ein Marker vorzuschlagen ist, nicht dass er gegen den Willen des Entwicklers entsteht (Kapitel 1.3.3). Aufnahmetest, was überhaupt einen Definitionsmarker bekommt: Kann Code das verletzen? Erläuterungen, Beispiele, Herleitungen bekommen keinen.
>
> Beispiel eines Absatzes mit drei Festlegungen (die IDs und Werte sind erfunden):

> Die Eingangsqueue der Pipeline fasst 64 Einträge [D-0042], weil das Latenzbudget von 5 ms bei zwölf gleichzeitig laufenden Kernels sonst nicht zu halten ist; eine dynamische Größe scheiterte an der Fragmentierung des Shared Memory. Deshalb startet der Orchestrator Kernels nie direkt, sondern über den Starter [D-0043], der die Queue vor dem ersten Eintrag reserviert [D-0044].

> Der Grund und die verworfene Alternative stehen in der Prosa, wo sie gedacht wurden; das Register verweist mit `in prose` darauf. Der Marker steht **vor** dem Satzzeichen, wie im Beispiel: Er liest sich als Teil des Satzes, und ein Satz mit mehreren Festlegungen bleibt eindeutig zuordenbar. Für `grep` ist die Position gleichgültig.

### 3.2.3 ID

> `D-0042`: ein globaler Zähler je Register, mindestens vier Stellen, nie neu vergeben, vom Skript vergeben (`next-id`). Die ID trägt kein Kapitel und keinen Ort; das Kapitel leitet das Skript aus dem Ort des Definitionsmarkers ab. Dass sie keins tragen darf, ist Bedingung 2 in Kapitel 2.2 — Kapitel werden umnummeriert, und eine Adresse, die dabei lügt, ist schlechter als keine. Das `D` steht für decision.
>
> Wird eine Festlegung inhaltlich zu einer anderen — etwa von einer Kapitelfestlegung zu einer projektweiten Vorgabe —, ist das eine neue Festlegung mit neuer ID; die alte wird abgelöst (3.2.6).

### 3.2.4 Register — Ort

> Eine Datei je Doku, Standardname `decisions.md` im Ordner der Doku. Das Skript findet sie in dieser Reihenfolge: Script-Argument `--register` → Skill-Parameterdatei → eine Zeile `[register: pfad]` in der Dokudatei → Standard im Ordner der Datei. Findet es nichts, meldet es, wo es gesucht hat und mit welchem Script-Argument der Aufrufer es hinführt (Vorgabe 2.4). Damit darf eine Doku ihr Register in einem anderen Ordner führen und aus jeder Dokudatei darauf verweisen.

### 3.2.5 Register — Grammatik

> Jede Zeile, die zu einer Festlegung gehört, beginnt mit eckigen Klammern, darin zuerst die ID, dann Schlüsselwörter; nach der Klammer folgt Prosa. Jede Zeile wiederholt die ID, damit `grep` alles zu einer Festlegung liefert, egal wo die Zeile steht, und das Skript keine Nachbarschaft erkennen muss.
>
> | Zeile | Form | Inhalt nach der Klammer |
> |---|---|---|
> | Kopf | `[ID kind status]` oder `[ID kind status pinned]` | Kurzlabel, nicht normativ |
> | Grund | `[ID reason]` · `[ID reason unknown]` | Grund einer `chosen`-Festlegung, oder `in prose` |
> | Quelle | `[ID source]` | Quelle einer `given`-Festlegung, oder `in prose` |
> | Alternative | `[ID instead]` | eine Alternative, ein Grund der Ablehnung — eine Zeile; oder `in prose` |
> | Suchschlüssel | `[ID keys]` | zwei bis vier markante Begriffe, durch Semikolon getrennt; finden unmarkierte Erwähnungen |
> | Fingerabdruck | `[ID fp]` | Kurzhash des normalisierten Definitionssatzes; erkennt, dass die Definition sich geändert hat |
> | Reibung | `[ID friction JJJJ-MM-TT]` | was sich gerieben hat, ein Halbsatz |
> | Bestätigung | `[ID upheld JJJJ-MM-TT]` | gegen welche Idee oder welchen Befund geprüft |
> | offene Frage | `[ID pending JJJJ-MM-TT]` | die Frage in Prosa; wird nach Beantwortung gelöscht |
> | Ablösung | `[ID superseded JJJJ-MM-TT by ID2]` | optional ein Halbsatz |
> | Stilllegung | `[ID retired JJJJ-MM-TT]` | warum die Festlegung entfällt |
>
> Regeln: Schlüsselwörter in der Kopfzeile in fester Reihenfolge beim Schreiben (ID, `kind`, `status`, `pinned`), beim Lesen ist die Reihenfolge gleichgültig. Die Zeilen einer Festlegung stehen direkt untereinander in der Reihenfolge der Tabelle — Konvention für den Leser, der Parser hängt nicht daran. Keine Backticks, kein Fettdruck in Registerzeilen; genau dort frisst der WYSIWYG-Editor Leerzeichen. Das Skript normalisiert U+00A0 zu Leerzeichen, bevor es die Klammer zerlegt. Datum immer `JJJJ-MM-TT`. Die Kennzeichnung eines Registerabschnitts trägt die Rolle `[DS:register]` (Kapitel 1.3.3).

### 3.2.6 Altes: drei Fälle, eine Regel

> Was alt ist, darf nicht unmarkiert in der Prosa stehen — denn genau der unmarkierte Altbestand wird als gültige Festlegung gelesen und blockiert Ideen. Ob ein alter Absatz stehen bleibt, entscheidet der Entwickler im Einzelfall: weil er als Begründung einer Änderung wirkt, weil er Kontext verwässert, weil gerade keine Zeit ist. Der Mechanismus verlangt nur den Marker.
>
> | Fall | Was es ist | Fußabdruck | Prosa |
> |---|---|---|---|
> | verworfene Alternative (`instead`) | wurde nie Festlegung; beim Entscheiden erwogen und abgelehnt | in der Prosa als Teil der Begründung, sonst eine Registerzeile | bleibt, wo sie den Gedankengang trägt |
> | abgelöste Festlegung (`superseded`) | war bindend, ist durch eine neue ersetzt | Registereintrag bleibt mit Datum und Nachfolger | der normative Satz wird umgeschrieben oder gestrichen; bleibt er als Begründung stehen, trägt er den Marker der abgelösten ID und ist so maschinell als Geschichte erkennbar |
> | Historie (alte Reviews, Verlauf) | Beurteilungsmaterial | Anhang, Rolle `appendix` | nichts Neues |
>
> Weil IDs stabil sind und das Register den Nachfolger kennt, löst sich jeder alte Verweis weiter auf; niemand muss quer durchs Projekt suchen, bevor er weiterarbeiten darf. In die Prosa kommt nichts Neues; die verworfene Alternative steht dort, wo sie schon immer stand — in der Argumentation — oder als eine Zeile im Register.

### 3.2.7 Nachmarkierung einer bestehenden Doku

> Nur am Berührungspunkt, nie als Gesamtinventur. Die Instanz liest das berührte Kapitel, erkennt bindende Aussagen (Aufnahmetest), bildet Annahmen über die Attribute und trägt sie in den Planabschnitt „Berührte Festlegungen" ein (Kapitel 3.1). Mit der Ausführung des freigegebenen Plans werden Marker und Registerzeilen geschrieben. Steckt der normative Satz mitten in einem Absatz, bekommt er seinen Marker an seinem Ende; er wird nicht aus dem Absatz gelöst. Eine Gesamtinventur — alte Doku, Faktenliste, neue Gruppierung — bleibt ein eigener Projektschritt auf ausdrücklichen Auftrag; die Fähigkeit dazu trägt der Skill `konzept-segmentierung`.

### 3.2.8 Layout der Prosa

> Ob ein Absatz eine Zeile ist oder nach einer festen Breite umbricht und Absätze durch Leerzeilen getrennt sind, berührt den Mechanismus nicht: Marker sind Inline-Text, das Register ist eine eigene Datei. Das Layout wird beim Skillstart aus der vorhandenen Doku abgelesen oder erfragt (Kapitel 3.5) und bestimmt nur, wie die Instanz Prosa schreibt.

### 3.2.9 Notizen im Commit

Warum es diese Notizen gibt und welche zwei Regeln für sie gelten, steht in Kapitel 1.3.5. Hier steht ihre Form. Die Grammatik folgt dem Git-Trailer, weil Git Trailer selbst zerlegt (`%(trailers:key=…)`) und dafür kein eigener Parser für Commit-Texte nötig ist; gemessen am Repository dieses Vorhabens dauert ein Lauf über den vollständigen Verlauf von knapp fünfhundert Commits zwischen acht und siebzehn Millisekunden, der Aufwand wächst linear. Eine Begrenzung der Suchtiefe ist deshalb nirgends nötig.

> Bleibt beim Committen etwas offen, trägt die Commit-Nachricht am Ende eine Trailer-Zeile. Ihr Schlüssel beginnt mit `ADoc-` — für die projektbegleitende Doku —, danach folgt die Klasse der Notiz. Bisher gibt es eine Klasse: `ADoc-open` für ein offenes Ende. Weitere Klassen bekommen einen eigenen Schlüssel und brechen die vorhandenen nicht.
>
>> `ADoc-open: marker | dev-doc/pipeline.md | Eingangsqueue 64 Einträge | vom Entwickler abgelehnt | 9d95e659`
>>
>> `ADoc-open: register | dev-doc/pipeline.md | D-0043 | Sitzung abgebrochen, Registerzeile fehlt | 9d95e659`
>
> Nach dem Schlüssel stehen fünf Felder in fester Reihenfolge, getrennt durch ` | `:
>
> | Feld | Inhalt |
> |---|---|
> | Art | `marker` — ein bindender Satz trägt keinen Definitionsmarker · `register` — Marker gesetzt, Registerzeile fehlt · `succession` — abgelöste Festlegung ohne Nachfolger im Register · `inconsistent` — trotz Blockade committet |
> | Ort | die Datei, in der es steht |
> | Wiederfindehinweis | die ID, wo es eine gibt; sonst wenige Worte aus dem betroffenen Satz |
> | Grund | ein Halbsatz für den Menschen: abgelehnt, abgebrochen, bewusst mitgenommen |
> | Sitzung | Kennung der Sitzung, in der es geschah — aus `CLAUDE_CODE_SESSION_ID`, in einem Hook aus dem Feld `session_id`; ist sie nicht zu ermitteln, steht `-` |
>
> Mehrere offene Punkte eines Commits ergeben mehrere Zeilen. Schreibe eine Notiz nur, wenn tatsächlich ein Eingriff in die Doku ausgeblieben ist — nicht vorsorglich und nicht als Arbeitsbericht. Halte sie knapp: Was zum Verstehen nötig ist, steht ohnehin im Commit selbst und in der Sitzung, auf die das letzte Feld zeigt.

**Die Sitzungskennung ist der Zugang zum Kontext, den die Notiz selbst nicht trägt.** Wird die Entwicklung im Gespräch geführt, liegt dort der Gedankengang, der zum Abbruch oder zur Ablehnung führte — ausführlicher, als eine Trailer-Zeile ihn je fassen könnte.

**Woher die Instanz die eigene Kennung nimmt** (recherchiert am 2026-09-25 gegen die offizielle Dokumentation von Claude Code). Zwei Wege stehen zur Verfügung, und sie sind verschieden belastbar. Die Eingabe eines Hooks trägt das Feld `session_id`; es steht in der Hook-Dokumentation unter den gemeinsamen Eingabefeldern und ist damit zugesagt. Für die Instanz selbst ist die Umgebungsvariable `CLAUDE_CODE_SESSION_ID` gesetzt — am 2026-09-25 im Bash-Subprozess beobachtet, ihr Wert stimmte mit dem Namen der Transkriptdatei überein. **Dokumentiert ist sie nicht:** In der Referenz der Umgebungsvariablen kommt sie nicht vor, und die Hook-Dokumentation sagt für Hooks ausdrücklich, die Kennung werde nur über die Eingabe übergeben. Sie kann also mit einer Version verschwinden. Der Regelteil nennt sie trotzdem als ersten Weg, weil sie heute funktioniert und nichts kostet; findet die Instanz sie nicht, schreibt sie `-` in das Feld, und die Notiz bleibt über den Commit weiter brauchbar. Verschwindet die Variable, meldet die Instanz das — mehr lässt sich an dieser Stelle nicht vorsorgen.

**Was mit der Kennung geschieht — und was nicht.** Die Transkripte liegen nach der Dokumentation unter `~/.claude/projects/<projekt>/<sitzungskennung>.jsonl`, wobei der Projektteil aus dem Arbeitsverzeichnis entsteht; Ablageort und Projektname sind über Umgebungsvariablen verstellbar, der Pfad ist also keine Gewissheit. Vor allem aber sagt dieselbe Seite ausdrücklich, das Zeilenformat sei intern und ändere sich zwischen Versionen, weshalb Skripte, die diese Dateien direkt zerlegen, mit jeder Auslieferung brechen können. **Der Skill zerlegt deshalb kein Transkript.** Wo der Kontext einer früheren Sitzung wirklich gebraucht wird, gibt es einen zugesagten Weg: eine Frage an die gespeicherte Sitzung über `claude -p --resume <kennung>`, deren Antwort als strukturierte Ausgabe zurückkommt. Das kostet einen eigenen Lauf und geschieht deshalb nie von selbst, sondern nur, wenn der Entwickler es will. Der billigere Weg bleibt, dass ein Mensch die Sitzung öffnet.

Belege: [Hooks — gemeinsame Eingabefelder](https://code.claude.com/docs/en/hooks), [Sitzungen verwalten — Ablage und Zugriff aus Skripten](https://code.claude.com/docs/en/sessions), [Umgebungsvariablen](https://code.claude.com/docs/en/env-vars).

**Zur Abgrenzung von Vorgabe 2.3.** Die Notiz nennt einen Dateinamen und einen Textausschnitt, also das, was der verworfene zweite Ankermechanismus getan hätte (Kapitel 1.3.3). Der Unterschied ist, dass hier nichts daran hängt: Bricht die Adresse, weil die Datei umbenannt oder der Satz umformuliert wurde, findet die Suche nichts und die Instanz arbeitet weiter wie ohne Notiz. Ein Anker hätte die Identität einer Festlegung getragen; dieser Hinweis trägt nichts. Deshalb ist er kein Verstoß.

**Committet der Entwickler selbst**, ohne die Instanz, entsteht keine Notiz. Das ist hinzunehmen — solange die Information noch im Kontext der Instanz steht, trägt sie sie beim nächsten Commit nach. Wer die Zusammenarbeit mit der Instanz so knapp hält, dass das regelmäßig danebengeht, ist mit diesem Skill nicht gut bedient (Festlegung des Entwicklers vom 2026-09-25). Auf Lückenlosigkeit der Notizen darf sich deshalb nichts verlassen; sie sind Hilfe, nicht Quelle.

Die Grenze zwischen Kapiteln und Anhang aus dem Vorläufer (Anhang A, Abschnitt A.9) bleibt für 3.2.6 unberührt — dort nachzulesen, wo diese Doku selbst die Grenze noch nach altem Schema führt.
