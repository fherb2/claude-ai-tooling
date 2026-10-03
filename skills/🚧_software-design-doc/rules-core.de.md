# Festlegungen — Marker, Register und Härte

> **In Arbeit.** Dieser Text ist der Zieltext des Skills und noch nicht fertig: Verweise der Form „Kapitel 1.3.2" oder „Anhang A" zeigen auf die Entwicklungsdoku des Vorhabens und sind vor der Auslieferung durch die Zielstruktur zu ersetzen. Dieser Block entfällt beim Zusammensetzen (Fahrplanschritt 7).

## 1 Zweck

Die entwicklungsbegleitende Doku hält Festlegungen fest. Ob eine Festlegung in der aktuellen Arbeit bindet oder zur Disposition steht, wägst Du nicht ab — Du schlägst es nach: Aus wenigen Feldern an der Festlegung und aus den geplanten Schritten folgt ihre Härte; aus Härte und Lage der Sitzung folgt Dein Verhalten. Nichts davon wird kombiniert oder gewichtet.

## 2 Begriffe und Werte

| Begriff | Bedeutung | Werte |
|---|---|---|
| Festlegung | Eintrag der Doku, der etwas bindend festhält | — |
| ID | stabiler, eindeutiger Schlüssel je Festlegung; wird nie neu vergeben; trägt kein Kapitel (Abschnitt 13) | `D-0042` |
| `kind` | Herkunft der Festlegung | `given` — von außen vorgegeben (Physik, Hardware, Fremdschnittstelle, Norm), mit Quelle · `chosen` — von uns entschieden, mit Grund und verworfener Alternative |
| `reason` | Grund einer `chosen`-Festlegung | Freitext · `in prose` — steht in der Prosa · `unknown` — endgültig nicht mehr bekannt |
| `hardness` | wie bindend die Festlegung jetzt ist; wird bei jedem Kontakt abgeleitet, nie gespeichert | `fixed` — nicht zur Diskussion · `decided` — gilt, darf hinterfragt werden · `open` — steht zur Disposition |
| `pinned` | ausdrückliche Entscheidung des Entwicklers, eine `chosen`-Festlegung nicht wieder aufzumachen; das Einzige, was an Härte gespeichert wird | ja/nein |
| `status` | wie die Attribute zustande kamen (Fußabdruck) | `assumed` — Lesart der Instanz, vom Entwickler nicht bestätigt · `accepted` — stand in einem freigegebenen Plan, nicht einzeln angesprochen · `confirmed` — vom Entwickler selbst bestätigt oder korrigiert |
| Ereigniszeile | datierte Zeile im Register zur Festlegung | `friction` — Arbeit musste um die Festlegung herum gebaut werden · `upheld` — gegen eine Idee oder einen Befund geprüft und bestätigt · `pending` — eine Frage an den Entwickler ist offen |
| geplanter Schritt | noch offener Schritt der Projektplanung, wo immer er steht (Fahrplandatei, Abschnitt „Offen" einer README, Notiz); eine Fahrplandatei wird nicht vorausgesetzt | nennt sein Umbauziel: IDs oder die Kennung eines Bereichs (Kapitel 3.4) |
| `mode` | wie die Sitzung die Doku liest | `execute` — Beschlossenes umsetzen · `design` — etwas neu denken, Alternativen suchen |
| `friction_threshold` | Zahl der `friction`-Zeilen, ab der eine Festlegung `open` wird | Skill-Parameter, Standard 2; für Festlegungen aus Abschnitten mit der Funktion `global` gilt eine Stufe höher (Standard 3) |
| `assumptions_on_approval` | was die Freigabe eines Plans mit den darin gelisteten Annahmen tut | `accept` (Standard) — sie werden `accepted` · `keep` — sie bleiben `assumed` |

Beide sind Skill-Parameter und wohnen in der Skill-Parameterdatei (Kapitel 3.5). Fehlen sie, gilt der Standard.

## 3 Rollen und ihre Funktionen

Jeder Abschnitt einer Doku trägt an seiner Überschrift eine **Rolle**, die benennt, worum es in ihm geht. Der Skill ordnet jeder Rolle intern eine oder zwei **Funktionen** zu, und an diesen Funktionen — nicht an der Rolle selbst — hängen die Regeln dieses Textes: die Pflicht zum Zitatmarker an `relate` (Abschnitt 12), die erhöhte Reibungsschwelle an `global` (Abschnitt 2), und von der Markerprüfung ausgenommen sind `nonbinding` und `register`.

**Tabelle: Rollen und ihre Funktionen**

| Rolle | Funktion |
|---|---|
| `goals` | `define`, `relate` |
| `constraints` | `define`, `global` |
| `context` | `relate` |
| `strategy` | `relate` |
| `building-blocks` | `define` (Standard) |
| `runtime` | `relate` |
| `deployment` | `define` |
| `crosscutting` | `define`, `global` |
| `decisions` | `define` |
| `quality` | `define`, `relate` |
| `risks` | `nonbinding` |
| `glossary` | `nonbinding` |
| `plan` | `plan` |
| `status` | `nonbinding` |
| `concept` | `nonbinding` |
| `appendix` | `nonbinding` |
| `register` | `register` |

Ein Projekt benutzt, was es braucht; keine Rolle ist Pflicht. Was ein Abschnitt der jeweiligen Rolle beschreibt und wie Du dem Entwickler eine Rolle vorschlägst, steht in Kapitel 1.3.3.

## 4 Kontakt und Vollständigkeit

**Kontakt.** Eine Festlegung ist kontaktiert, wenn sie im Plan des aktuellen Schritts oder in der Auswirkungsliste der aktuellen Idee genannt werden müsste — weil sie die Änderung begrenzt oder von ihr betroffen ist. Nicht kontaktiert ist, was nur im selben Kapitel steht. Alles Folgende gilt nur für kontaktierte Festlegungen. Kandidaten liefert das Skript aus dem Graphen der Marker (Kapitel 3.6); Du beantwortest je Kandidat, ob er berührt ist.

**Unmarkierte Aussagen.** Findet `grep` im berührten Kapitel keine Marker, liest Du das Kapitel — die Arbeitsschleife des Vorläufers verlangt das ohnehin (Anhang A, Abschnitt A.8). Als unmarkierte Festlegung zählt eine Aussage nur, wenn sie als Anforderung oder Entscheidung formuliert ist: muss, soll, immer, nie, ein festgelegter Wert. Erläuterungen und Beispiele zählen nicht. Aufnahmetest: Kann Code das verletzen? Jede Aussage, die Du als bindend behandelst, nennst Du im Plan im Wortlaut; liest Du etwas hinein, sieht der Entwickler es dort.

**Annahmen statt Fragen.** Fehlt der Marker oder der Grund, bildest Du aus der Prosa selbst eine Annahme über `kind` und `reason` oder Quelle und trägst sie mit `status: assumed` in den Plan ein. Du fragst den Entwickler nur, wo Du keine Annahme bilden kannst; dann steht im Plan eine `pending`-Zeile mit der Frage. Bis zur Antwort gilt vorläufig `decided`.

**Fragen an den Entwickler** — für die Vollständigkeitsfrage und für den Satz aus Prüfung R3 gelten vier Regeln:

1. Ohne Skill-Vokabular. Nicht `given`/`chosen`, nicht „Härte", nicht „Marker". Sondern: „Ist das eine Vorgabe von außen — Hardware, Norm, Fremdschnittstelle — oder haben wir das so entschieden? Falls entschieden: Was war der Grund, und was wäre die Alternative gewesen?"
2. Mit Anlass. Nenne die Festlegung im Wortlaut, wo sie steht, und in einem Satz, was jetzt von der Antwort abhängt.
3. Nichtwissen ist zulässig. Drei Antwortformen: Antwort → Attribute werden `confirmed`. „Später" → `pending` bleibt, `decided` gilt vorläufig, Du arbeitest unter dieser Annahme weiter und sagst das; in dieser Sitzung fragst Du nicht erneut, in einer späteren nur beim nächsten Kontakt; „Was ist offen?" listet alle `pending`-Zeilen. „Lass uns das durchgehen" → Gespräch über so viele Turns wie nötig; am Ende fasst Du zusammen, was Du festhalten würdest, und schreibst erst nach Bestätigung.
4. „Grund nicht mehr bekannt" ist eine Antwort → `reason: unknown`, keine weitere Frage; in `design` sagt der geparkte Satz „Grund nicht überliefert".

## 5 Härte ableiten: die Entscheidungsliste

Die Prüfungen R1 bis R7 stellst Du Dir selbst und beantwortest sie durch Nachschlagen in Register, Ereigniszeilen und geplanten Schritten — das Skript tut es für Dich (`hardness`, Kapitel 3.6). Keine davon wird dem Entwickler gestellt. Von oben nach unten; die erste zutreffende Prüfung bestimmt die Härte, danach wird nicht weitergelesen. Jede Prüfung ist eine einzelne Prüfung; nichts wird kombiniert oder gewichtet.

| | Prüfung | Härte | Anmerkung |
|---|---|---|---|
| R1 | Der Entwickler hat in dieser Sitzung zu dieser ID oder ihrem Bereich „hart" oder „offen" gesagt. | `fixed` bzw. `open` | Gilt für die Sitzung. Soll es bleiben: „offen" → ein geplanter Schritt (dann greift R2); „hart" → `pinned` (dann greift R4); beides über einen Plan. |
| R2 | Ein geplanter Schritt nennt diese ID als Umbauziel. | `open` | Jüngste Entscheidung des Entwicklers; öffnet auch Gegebenes und Festgeschriebenes. |
| R3 | `kind` ist `given` und `status` ist `accepted` oder `confirmed`. | `fixed` | Stehen dennoch mindestens `friction_threshold` `friction`-Zeilen da, bleibt sie `fixed`; Du sagst einen Satz nach den Regeln aus 3.1.3: Quelle noch aktuell? |
| R4 | `pinned` und `status` ist `accepted` oder `confirmed`. | `fixed` | |
| R5 | Ein geplanter Schritt nennt den Bereich, in dem sie steht, als Umbauziel. | `open` | Gröber als R2; öffnet nicht, was R3 oder R4 gebunden haben. |
| R6 | Seit der jüngsten `upheld`-Zeile stehen mindestens `friction_threshold` `friction`-Zeilen (Funktion `global`: eine Stufe höher). Fehlt eine `upheld`-Zeile, zählen alle. | `open` | Zählung per Kommando, nie per Blick. |
| R7 | — | `decided` | Der Normalfall. |

Reihenfolge: oben die Entscheidung des Entwicklers (R1, R2), dann das von Natur aus Gebundene (R3, R4), dann was die Planung grob öffnet (R5), dann was die Erfahrung öffnet (R6), unten der Normalfall.

Annahmen machen nie `fixed`: R3 und R4 verlangen `accepted` oder `confirmed`. Eine angenommene `given`-Festlegung bleibt `decided`; in `design` sagt der geparkte Satz „vermutlich von außen vorgegeben — stimmt das?".

Fehlende Felder blockieren nie — sie machen die Prüfung stumm, die sie bräuchte; die Liste endet dann bei R7 (3.1.7).

## 6 Verhalten: Härte × Lage

| | `execute` | `design` |
|---|---|---|
| `fixed` | einhalten | einhalten; als Randbedingung nennen; öffnen nur auf Wort des Entwicklers |
| `decided` | einhalten; Kollision → anhalten und fragen | Gedanke zu Ende führen; Kollision wird geparkt |
| `open` | vor dem Bauen gegen sie: anhalten, Entscheidung einholen | frei; Alternativen ausarbeiten |

**Lage.** Geplanter Schritt oder konkreter Änderungsauftrag → `execute`. Idee, Bitte um Alternativen, „was wäre wenn" → `design` für den genannten Bereich. Unklar → einmal fragen. Wählst Du `design`, sagst Du es („Ich lese die Doku hier als Stand, nicht als Vorgabe").

**Kollision.** Eine geplante Änderung oder eine Idee verletzt eine Festlegung.

**Parken.** Ein Satz je Festlegung: was sie festlegt, ihr Grund (oder „Grund nicht überliefert" oder „vermutlich von außen vorgegeben — stimmt das?"), und die gemessenen Umbaukosten — Zahl der abhängigen Stellen aus `mentions` (Kapitel 3.6). Der Gedanke wird weder abgebrochen noch ausgeführt. Formulierung: „Das berührt X, weil …" — nie „Das geht nicht wegen X".

**Auswirkungsliste** (bei `open` in `design`): je berührter Festlegung ihr Grund und eine von drei Bewertungen — Grund fällt mit der Idee (kein Hindernis, wird mitgeändert) · Grund trägt weiter (echte Randbedingung; benennen, Idee anpassen oder Randbedingung mit zur Disposition stellen) · Grund nicht dokumentiert (Frage an den Entwickler). Festlegungen aus Abschnitten mit der Funktion `global` kennzeichnest Du als projektweit.

## 7 Der Planabschnitt „Berührte Festlegungen"

Jeder Plan trägt diesen Abschnitt. Er ist der Zwischenspeicher aller Annahmen bis zur Freigabe und der Ort, an dem der Entwickler sie sieht. Das Skript liefert sein Gerüst (`plan-section`, Kapitel 3.6).

**Je Eintrag:** ID (oder Wortlaut, wenn noch keine ID existiert), Kapitel, `kind`, `reason` oder Quelle, `status`, abgeleitete Härte mit der zutreffenden Bedingung in Prosa, und — bei Kollision — der geparkte Satz. Bei `pending` die Frage in Prosa.

**Suchschlüssel unter der Tabelle.** Unmittelbar unter den Einträgen steht ein Block mit je einer Zeile — `D-0042: Eingangsqueue; Blockgröße; 64` —, und zwar nur für Festlegungen, die dieser Plan **neu anlegt** oder deren Schlüssel er ändert. Für die übrigen sind sie längst gewählt; sie erneut zu zeigen wäre Lärm. Der Block steht dort, damit Du den Entwickler die Begriffe korrigieren lassen kannst, ohne ihn zu fragen: Er überfliegt sie und sagt etwas, oder er sagt nichts und die Freigabe nimmt sie mit. Eigene Spalte und Anhang an den Grund sind dafür verworfen — Schlüssel beurteilt man als Menge, nicht einzeln, und nur im Block fällt auf, wenn zwei Festlegungen dieselben tragen oder keine den eigentlichen Gegenstand nennt.

**Freigabesatz.** Bei `assumptions_on_approval: accept` steht im Abschnitt: „Die Freigabe dieses Plans bestätigt die hier gelisteten Annahmen, soweit der Entwickler nichts anderes sagt." Bei `keep` fehlt der Satz. Das Wort des Entwicklers je Plan schlägt den Skill-Parameter: „nur ablegen" → dieser Plan wie `keep`; „gilt als bestätigt" → wie `accept`.

**Korrektur in Prosa.** Sagt der Entwickler etwas zu einem Eintrag („das ist eine Hardwaregrenze", „das haben wir wegen der Latenz so entschieden"), übersetzst Du das in die Attribute und zeigst die Zuordnung, bevor Du schreibst.

**Schreiben bei Ausführung.** Marker und Registerzeilen werden mit der Ausführung des Plans geschrieben — Doku und Code im Wechsel. Status: vom Entwickler angesprochen → `confirmed`; nicht angesprochen und Plan wie `accept` → `accepted`; nicht angesprochen und Plan wie `keep`, oder „später" → `assumed`. Ab jetzt findet `grep` sie; die Liste läuft ohne erneutes Lesen.

**Wiedervorlage.** Eine `assumed`-Festlegung steht bei jedem weiteren Kontakt erneut im Abschnitt, gekennzeichnet als Annahme, ohne erneute Frage. Bei `accept` hebt die nächste Freigabe sie auf `accepted`; bei `keep` bleibt sie, bis der Entwickler sie anspricht.

Die Länge des Abschnitts ist ein Maß für die Schrittgröße: Nennt ein Plan mehr als etwa fünfzehn Festlegungen, ist der Schritt zu groß — zerlegen, wie es der Vorläufer für Kontrollfluss im Plan schon verlangt (Anhang A, Abschnitt A.4).

## 8 Fehlende und unlesbare Felder

| Was fehlt | Stumm | Ergebnis | Auffangnetz |
|---|---|---|---|
| kein Marker | R3, R4, R6 | `decided` | 3.1.3 bildet beim Kontakt die Annahme; der Plan zeigt sie |
| Marker ohne Grund | — | `decided`, in `design` mit Vermerk „Grund fehlt" | Annahme oder `pending`; `unknown` beendet das Fragen |
| keine Ereigniszeilen | R6 | nichts durch Erfahrung geöffnet | Zählung beginnt mit der ersten `friction`-Zeile |
| geplante Schritte ohne Umbauziel | R2, R5 | nichts durch Planung geöffnet; nur R1 öffnet | berührt ein Schritt erkennbar den Bereich, fragst Du einmal, ob er als Umbau gemeint ist, und trägst das Ziel nach (Kapitel 3.4) |
| Registerzeile unlesbar (Schlüsselwort falsch, Datum fehlt) | die jeweilige Prüfung | wie „fehlt" | `check` meldet die Zahl nicht lesbarer Zeilen (Kapitel 3.6) |
| Doku schweigt zum Bereich | alle | nichts bindet | Du erfindest keine Festlegung; entsteht eine, hältst Du sie fest (Kapitel 3.5) |

## 9 Was der Entwickler sieht

Bei `fixed` oder `decided` in `execute`: nichts. Bei einer Kollision in `design`: ein Satz je geparkter Festlegung. Bei `open`: die Auswirkungsliste (in `design`) oder die Frage vor dem Bauen (in `execute`). Im Plan: den Abschnitt „Berührte Festlegungen". Auf die Frage, warum etwas `open` ist: die Bedingung in Prosa („zweimal Reibung seit Juli, keine Bestätigung") — nie eine Prüfungsnummer.

## 10 Anker — wann was geschieht

| Anker | Handlung |
|---|---|
| Bereich öffnen (Kapitel für einen Schritt oder eine Idee laden) | Festlegungen des Bereichs per Skript listen; Abweichungen zwischen Prosa und Register melden. Die Liste macht sichtbar, löst aber keine Fragen aus. |
| Plan schreiben | Abschnitt „Berührte Festlegungen" füllen. Enthält der Plan einen Sonderfall, eine Ausnahme oder einen Umweg, der nur wegen einer Festlegung existiert → `friction`-Zeile an dieser Festlegung, mit Datum und einem Halbsatz. |
| Entwickler nennt Reibung („das ist umständlich wegen …") oder ein Review-Befund nennt eine Festlegung | `friction`-Zeile. |
| Idee verworfen oder Befund abgelehnt, nachdem eine Festlegung dagegen geprüft wurde | `upheld`-Zeile mit Datum und Bezug (welche Idee, welcher Befund). |
| Umbau eines Bereichs wird geplant | Der geplante Schritt nennt sein Umbauziel. Ist er erledigt, werden die betroffenen Festlegungen neu gesetzt; ihre Härte folgt wieder der Liste. |
| Neue Einheit wird gegen eine Festlegung gebaut | Härte lesen; nur bei `open` oder vorhandener Reibung ein Satz, sonst Schweigen. |

## 11 Trennung von Prosa und Register

Die Prosa trägt je Festlegung nur einen Marker; alle Attribute, Ereignisse und der Lebenszyklus stehen im Register. Warum die Trennung so verläuft, steht in Kapitel 1.3.2. Für die Umsetzung folgt daraus: Der Festlegungstext hat genau ein Zuhause, die Prosa; das Register kopiert ihn nicht, sondern trägt ein Kurzlabel von wenigen Worten zur Orientierung, das ausdrücklich nicht normativ ist und von keiner Prüfung gelesen wird.

## 12 Marker

Ein **Marker** ist ein Feld in der Prosa: Der Zeichenbereich von seiner öffnenden bis zu seiner schließenden Klammer ist sein **Marker-Feld** — ein Feld im Sinne der Textverarbeitung, also ein Abschnitt, den nicht der Schreibende füllt, sondern das Werkzeug (Vorgabe 2.10). Gefüllt wird er mit einer Adresse und mit nichts sonst.

Zwei Formen, beide ASCII, beide ohne Leerzeichen, in Markdown als normaler Text gerendert:

- **Definitionsmarker** `[D-0042]` — genau eine je Festlegung, am Satz, der sie ausspricht. Spannt sich eine Festlegung über mehrere Sätze, steht der Marker am Ende des letzten.
- **Zitatmarker** `[>D-0042]` — an jeder weiteren Stelle, die die Festlegung heranzieht; das `>` liest sich als „siehe".

Pflicht ist der Definitionsmarker immer, der Zitatmarker in Abschnitten mit der Funktion `relate` (Abschnitt 3); sonst ist der Zitatmarker optional. Der Skill-Parameter `marking` kann die Pflicht ausweiten (Kapitel 3.5). Jeder einzelne Marker steht dabei als Vorschlag im Plan und kann abgelehnt werden; die Pflicht sagt, wo ein Marker vorzuschlagen ist, nicht dass er gegen den Willen des Entwicklers entsteht. Aufnahmetest, was überhaupt einen Definitionsmarker bekommt: Kann Code das verletzen? Erläuterungen, Beispiele, Herleitungen bekommen keinen.

Beispiel eines Absatzes mit drei Festlegungen (die IDs und Werte sind erfunden):
Die Eingangsqueue der Pipeline fasst 64 Einträge [D-0042], weil das Latenzbudget von 5 ms bei zwölf gleichzeitig laufenden Kernels sonst nicht zu halten ist; eine dynamische Größe scheiterte an der Fragmentierung des Shared Memory. Deshalb startet der Orchestrator Kernels nie direkt, sondern über den Starter [D-0043], der die Queue vor dem ersten Eintrag reserviert [D-0044].
Der Grund und die verworfene Alternative stehen in der Prosa, wo sie gedacht wurden; das Register verweist mit `in prose` darauf. Der Marker steht **vor** dem Satzzeichen, wie im Beispiel: Er liest sich als Teil des Satzes, und ein Satz mit mehreren Festlegungen bleibt eindeutig zuordenbar. Für `grep` ist die Position gleichgültig.

## 13 ID

`D-0042`: ein globaler Zähler je Register, mindestens vier Stellen, nie neu vergeben, vom Skript vergeben (`next-id`). Die ID trägt kein Kapitel und keinen Ort; das Kapitel leitet das Skript aus dem Ort des Definitionsmarkers ab. Dass sie keins tragen darf, ist Bedingung 2 in Kapitel 2.2 — Kapitel werden umnummeriert, und eine Adresse, die dabei lügt, ist schlechter als keine. Das `D` steht für decision.

Wird eine Festlegung inhaltlich zu einer anderen — etwa von einer Kapitelfestlegung zu einer projektweiten Vorgabe —, ist das eine neue Festlegung mit neuer ID; die alte wird abgelöst (Abschnitt 16).

## 14 Register — Ort

Eine Datei je Doku, Standardname `decisions.md` im Ordner der Doku. Das Skript findet sie in dieser Reihenfolge: Script-Argument `--register` → Skill-Parameterdatei → eine Zeile `[register: pfad]` in der Dokudatei → Standard im Ordner der Datei. Findet es nichts, meldet es, wo es gesucht hat und mit welchem Script-Argument der Aufrufer es hinführt (Vorgabe 2.4). Damit darf eine Doku ihr Register in einem anderen Ordner führen und aus jeder Dokudatei darauf verweisen.

## 15 Register — Grammatik

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

Regeln: Schlüsselwörter in der Kopfzeile in fester Reihenfolge beim Schreiben (ID, `kind`, `status`, `pinned`), beim Lesen ist die Reihenfolge gleichgültig. Die Zeilen einer Festlegung stehen direkt untereinander in der Reihenfolge der Tabelle — Konvention für den Leser, der Parser hängt nicht daran. Keine Backticks, kein Fettdruck in Registerzeilen; genau dort frisst der WYSIWYG-Editor Leerzeichen. Das Skript normalisiert U+00A0 zu Leerzeichen, bevor es die Klammer zerlegt. Datum immer `JJJJ-MM-TT`. Die Kennzeichnung eines Registerabschnitts trägt die Rolle `[DS:register]` (Abschnitt 3).

## 16 Altes: drei Fälle, eine Regel

Was alt ist, darf nicht unmarkiert in der Prosa stehen — denn genau der unmarkierte Altbestand wird als gültige Festlegung gelesen und blockiert Ideen. Ob ein alter Absatz stehen bleibt, entscheidet der Entwickler im Einzelfall: weil er als Begründung einer Änderung wirkt, weil er Kontext verwässert, weil gerade keine Zeit ist. Der Mechanismus verlangt nur den Marker.

| Fall | Was es ist | Fußabdruck | Prosa |
|---|---|---|---|
| verworfene Alternative (`instead`) | wurde nie Festlegung; beim Entscheiden erwogen und abgelehnt | in der Prosa als Teil der Begründung, sonst eine Registerzeile | bleibt, wo sie den Gedankengang trägt |
| abgelöste Festlegung (`superseded`) | war bindend, ist durch eine neue ersetzt | Registereintrag bleibt mit Datum und Nachfolger | der normative Satz wird umgeschrieben oder gestrichen; bleibt er als Begründung stehen, trägt er den Marker der abgelösten ID und ist so maschinell als Geschichte erkennbar |
| Historie (alte Reviews, Verlauf) | Beurteilungsmaterial | Anhang, Rolle `appendix` | nichts Neues |

Weil IDs stabil sind und das Register den Nachfolger kennt, löst sich jeder alte Verweis weiter auf; niemand muss quer durchs Projekt suchen, bevor er weiterarbeiten darf. In die Prosa kommt nichts Neues; die verworfene Alternative steht dort, wo sie schon immer stand — in der Argumentation — oder als eine Zeile im Register.

## 17 Nachmarkierung einer bestehenden Doku

Nur am Berührungspunkt, nie als Gesamtinventur. Die Instanz liest das berührte Kapitel, erkennt bindende Aussagen (Aufnahmetest), bildet Annahmen über die Attribute und trägt sie in den Planabschnitt „Berührte Festlegungen" ein (Abschnitt 7). Mit der Ausführung des freigegebenen Plans werden Marker und Registerzeilen geschrieben. Steckt der normative Satz mitten in einem Absatz, bekommt er seinen Marker an seinem Ende; er wird nicht aus dem Absatz gelöst. Eine Gesamtinventur — alte Doku, Faktenliste, neue Gruppierung — bleibt ein eigener Projektschritt auf ausdrücklichen Auftrag; die Fähigkeit dazu trägt der Skill `konzept-segmentierung`.

## 18 Layout der Prosa

Ob ein Absatz eine Zeile ist oder nach einer festen Breite umbricht und Absätze durch Leerzeilen getrennt sind, berührt den Mechanismus nicht: Marker sind Inline-Text, das Register ist eine eigene Datei. Das Layout wird beim Skillstart aus der vorhandenen Doku abgelesen oder erfragt (Kapitel 3.5) und bestimmt nur, wie die Instanz Prosa schreibt.

## 19 Notizen im Commit

Bleibt beim Committen etwas offen, trägt die Commit-Nachricht am Ende eine Trailer-Zeile. Ihr Schlüssel beginnt mit `ADoc-` — für die projektbegleitende Doku —, danach folgt die Klasse der Notiz. Bisher gibt es eine Klasse: `ADoc-open` für ein offenes Ende. Weitere Klassen bekommen einen eigenen Schlüssel und brechen die vorhandenen nicht.

> `ADoc-open: marker | dev-doc/pipeline.md | Eingangsqueue 64 Einträge | vom Entwickler abgelehnt | 9d95e659`
>
> `ADoc-open: register | dev-doc/pipeline.md | D-0043 | Sitzung abgebrochen, Registerzeile fehlt | 9d95e659`

Nach dem Schlüssel stehen fünf Felder in fester Reihenfolge, getrennt durch ` | `:

| Feld | Inhalt |
|---|---|
| Art | `marker` — ein bindender Satz trägt keinen Definitionsmarker · `register` — Marker gesetzt, Registerzeile fehlt · `succession` — abgelöste Festlegung ohne Nachfolger im Register · `inconsistent` — trotz Blockade committet |
| Ort | die Datei, in der es steht |
| Wiederfindehinweis | die ID, wo es eine gibt; sonst wenige Worte aus dem betroffenen Satz |
| Grund | ein Halbsatz für den Menschen: abgelehnt, abgebrochen, bewusst mitgenommen |
| Sitzung | Kennung der Sitzung, in der es geschah — aus `CLAUDE_CODE_SESSION_ID`, in einem Hook aus dem Feld `session_id`; ist sie nicht zu ermitteln, steht `-` |

Mehrere offene Punkte eines Commits ergeben mehrere Zeilen. Schreibe eine Notiz nur, wenn tatsächlich ein Eingriff in die Doku ausgeblieben ist — nicht vorsorglich und nicht als Arbeitsbericht. Halte sie knapp: Was zum Verstehen nötig ist, steht ohnehin im Commit selbst und in der Sitzung, auf die das letzte Feld zeigt.

## 20 Bewusst nicht Teil dieses Regelteils

Das Skript berechnet keine Altersgröße, es reicht Umbaukosten nur als Zahl in den geparkten Satz durch, es summiert und gewichtet die Prüfungen nicht, und es prüft nicht, ob ein Grund noch gilt — Letzteres ist Gegenstand des Skills `konsistenzpruefung`.
