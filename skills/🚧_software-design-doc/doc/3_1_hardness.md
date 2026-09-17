# 3 Einheiten

## 3.1 Härte einer Festlegung — Ableitung und Wirkung

Finaler Stand von Arbeitspunkt 1 (2026-09-17), mit zwei nachträglichen Anpassungen aus Arbeitspunkt 2: Die Ereigniszeile „bestätigt" heißt `upheld` statt `confirmed`, weil `confirmed` zugleich ein Statuswert ist (Kapitel 3.2); und „Segment 2" ist ersetzt durch „Abschnitte mit der Funktion `global`" (Kapitel 3.3). Dieser Text wird später wörtlich der Regelteil `rules-hardness.md` des Skills; Adressat ist dort die Instanz („Du"), der Mensch heißt „der Entwickler".

> **[Q-02] Entscheidungsgrundlage — Umbenennung der Ereigniszeile in `upheld`**
> Kontext: Im finalen Text von Arbeitspunkt 1 hieß die Ereigniszeile „gegen eine Idee geprüft und bestätigt" `confirmed` — dasselbe Wort wie der Statuswert `confirmed` (vom Entwickler bestätigt). In einer Grammatik, in der beides in derselben Klammer stehen kann, ist das eine echte Mehrdeutigkeit für Leser und `grep`. Ich habe die Ereigniszeile in diesem Text bereits `upheld` genannt.
> Optionen: (a) `upheld` beibehalten; (b) anderes Wort für die Ereigniszeile; (c) den Statuswert umbenennen und die Ereigniszeile `confirmed` lassen.
> Vorschlag: (a) — „die Festlegung hat der Anfechtung standgehalten"; der Status behält das natürlichere Wort.
> Gewicht: klein · Blockiert: Fahrplanschritt 1
> Antwort:

### 3.1.1 Zweck

Die entwicklungsbegleitende Doku hält Festlegungen fest. Ob eine Festlegung in der aktuellen Arbeit bindet oder zur Disposition steht, wägst Du nicht ab — Du schlägst es nach: Aus wenigen Feldern an der Festlegung und aus den geplanten Schritten folgt ihre Härte; aus Härte und Lage der Sitzung folgt Dein Verhalten. Nichts davon wird kombiniert oder gewichtet.

### 3.1.2 Begriffe und Werte

| Begriff | Bedeutung | Werte |
|---|---|---|
| Festlegung | Eintrag der Doku, der etwas bindend festhält | — |
| ID | stabiler, eindeutiger Schlüssel je Festlegung; wird nie neu vergeben; trägt kein Kapitel (Kapitel 3.2) | `D-0042` |
| `kind` | Herkunft der Festlegung | `given` — von außen vorgegeben (Physik, Hardware, Fremdschnittstelle, Norm), mit Quelle · `chosen` — von uns entschieden, mit Grund und verworfener Alternative |
| `reason` | Grund einer `chosen`-Festlegung | Freitext · `in prose` — steht in der Prosa · `unknown` — endgültig nicht mehr bekannt |
| `hardness` | wie bindend die Festlegung jetzt ist; wird bei jedem Kontakt abgeleitet, nie gespeichert | `fixed` — nicht zur Diskussion · `decided` — gilt, darf hinterfragt werden · `open` — steht zur Disposition |
| `pinned` | ausdrückliche Entscheidung des Entwicklers, eine `chosen`-Festlegung nicht wieder aufzumachen; das Einzige, was an Härte gespeichert wird | ja/nein |
| `status` | wie die Attribute zustande kamen (Fußabdruck) | `assumed` — Lesart der Instanz, vom Entwickler nicht bestätigt · `accepted` — stand in einem freigegebenen Plan, nicht einzeln angesprochen · `confirmed` — vom Entwickler selbst bestätigt oder korrigiert |
| Ereigniszeile | datierte Zeile im Register zur Festlegung | `friction` — Arbeit musste um die Festlegung herum gebaut werden · `upheld` — gegen eine Idee oder einen Befund geprüft und bestätigt · `pending` — eine Frage an den Entwickler ist offen |
| geplanter Schritt | noch offener Schritt der Projektplanung, wo immer er steht (Fahrplandatei, Abschnitt „Offen" einer README, Notiz); eine Fahrplandatei wird nicht vorausgesetzt | nennt sein Umbauziel: IDs oder ein Kapitel (Kapitel 3.4) |
| `mode` | wie die Sitzung die Doku liest | `execute` — Beschlossenes umsetzen · `design` — etwas neu denken, Alternativen suchen |
| `friction_threshold` | Zahl der `friction`-Zeilen, ab der eine Festlegung `open` wird | Parameter, Standard 2; für Festlegungen aus Abschnitten mit der Funktion `global` gilt eine Stufe höher (Standard 3) |
| `assumptions_on_approval` | was die Freigabe eines Plans mit den darin gelisteten Annahmen tut | `accept` (Standard) — sie werden `accepted` · `keep` — sie bleiben `assumed` |

Beide Parameter wohnen in der Parameterdatei (Kapitel 3.5). Fehlen sie, gilt der Standard.

### 3.1.3 Schritt 1 — Kontakt und Vollständigkeit

**Kontakt.** Eine Festlegung ist kontaktiert, wenn sie im Plan des aktuellen Schritts oder in der Auswirkungsliste der aktuellen Idee genannt werden müsste — weil sie die Änderung begrenzt oder von ihr betroffen ist. Nicht kontaktiert ist, was nur im selben Kapitel steht. Alles Folgende gilt nur für kontaktierte Festlegungen. Kandidaten liefert das Skript aus dem Graphen der Marken (Kapitel 3.6); Du beantwortest je Kandidat, ob er berührt ist.

**Unmarkierte Aussagen.** Findet `grep` im berührten Kapitel keine Marken, liest Du das Kapitel — die Arbeitsschleife verlangt das ohnehin. Als unmarkierte Festlegung zählt eine Aussage nur, wenn sie als Anforderung oder Entscheidung formuliert ist: muss, soll, immer, nie, ein festgelegter Wert. Erläuterungen und Beispiele zählen nicht. Aufnahmetest: Kann Code das verletzen? Jede Aussage, die Du als bindend behandelst, nennst Du im Plan im Wortlaut; liest Du etwas hinein, sieht der Entwickler es dort.

**Annahmen statt Fragen.** Fehlt der Marker oder der Grund, bildest Du aus der Prosa selbst eine Annahme über `kind` und `reason` oder Quelle und trägst sie mit `status: assumed` in den Plan ein. Du fragst den Entwickler nur, wo Du keine Annahme bilden kannst; dann steht im Plan eine `pending`-Zeile mit der Frage. Bis zur Antwort gilt vorläufig `decided`.

**Fragen an den Entwickler** — für die Vollständigkeitsfrage und für den Satz aus Prüfung R3 gelten vier Regeln:

1. Ohne Skill-Vokabular. Nicht `given`/`chosen`, nicht „Härte", nicht „Marke". Sondern: „Ist das eine Vorgabe von außen — Hardware, Norm, Fremdschnittstelle — oder haben wir das so entschieden? Falls entschieden: Was war der Grund, und was wäre die Alternative gewesen?"
2. Mit Anlass. Nenne die Festlegung im Wortlaut, wo sie steht, und in einem Satz, was jetzt von der Antwort abhängt.
3. Nichtwissen ist zulässig. Drei Antwortformen: Antwort → Attribute werden `confirmed`. „Später" → `pending` bleibt, `decided` gilt vorläufig, Du arbeitest unter dieser Annahme weiter und sagst das; in dieser Sitzung fragst Du nicht erneut, in einer späteren nur beim nächsten Kontakt; „Was ist offen?" listet alle `pending`-Zeilen. „Lass uns das durchgehen" → Gespräch über so viele Turns wie nötig; am Ende fasst Du zusammen, was Du festhalten würdest, und schreibst erst nach Bestätigung.
4. „Grund nicht mehr bekannt" ist eine Antwort → `reason: unknown`, keine weitere Frage; in `design` sagt der geparkte Satz „Grund nicht überliefert".

### 3.1.4 Schritt 2 — Härte ableiten: die Entscheidungsliste

Die Prüfungen R1 bis R7 stellst Du Dir selbst und beantwortest sie durch Nachschlagen in Register, Ereigniszeilen und geplanten Schritten — das Skript tut es für Dich (`hardness`, Kapitel 3.6). Keine davon wird dem Entwickler gestellt. Von oben nach unten; die erste zutreffende Prüfung bestimmt die Härte, danach wird nicht weitergelesen. Jede Prüfung ist eine einzelne Prüfung; nichts wird kombiniert oder gewichtet.

| | Prüfung | Härte | Anmerkung |
|---|---|---|---|
| R1 | Der Entwickler hat in dieser Sitzung zu dieser ID oder ihrem Bereich „hart" oder „offen" gesagt. | `fixed` bzw. `open` | Gilt für die Sitzung. Soll es bleiben: „offen" → ein geplanter Schritt (dann greift R2); „hart" → `pinned` (dann greift R4); beides über einen Plan. |
| R2 | Ein geplanter Schritt nennt diese ID als Umbauziel. | `open` | Jüngste Entscheidung des Entwicklers; öffnet auch Gegebenes und Festgeschriebenes. |
| R3 | `kind` ist `given` und `status` ist `accepted` oder `confirmed`. | `fixed` | Stehen dennoch mindestens `friction_threshold` `friction`-Zeilen da, bleibt sie `fixed`; Du sagst einen Satz nach den Regeln aus 3.1.3: Quelle noch aktuell? |
| R4 | `pinned` und `status` ist `accepted` oder `confirmed`. | `fixed` | |
| R5 | Ein geplanter Schritt nennt ihr Kapitel als Umbauziel. | `open` | Gröber als R2; öffnet nicht, was R3 oder R4 gebunden haben. |
| R6 | Seit der jüngsten `upheld`-Zeile stehen mindestens `friction_threshold` `friction`-Zeilen (Funktion `global`: eine Stufe höher). Fehlt eine `upheld`-Zeile, zählen alle. | `open` | Zählung per Kommando, nie per Blick. |
| R7 | — | `decided` | Der Normalfall. |

Reihenfolge: oben die Entscheidung des Entwicklers (R1, R2), dann das von Natur aus Gebundene (R3, R4), dann was die Planung grob öffnet (R5), dann was die Erfahrung öffnet (R6), unten der Normalfall.

Annahmen machen nie `fixed`: R3 und R4 verlangen `accepted` oder `confirmed`. Eine angenommene `given`-Festlegung bleibt `decided`; in `design` sagt der geparkte Satz „vermutlich von außen vorgegeben — stimmt das?".

Fehlende Felder blockieren nie — sie machen die Prüfung stumm, die sie bräuchte; die Liste endet dann bei R7 (3.1.7).

### 3.1.5 Schritt 3 — Verhalten: Härte × Lage

| | `execute` | `design` |
|---|---|---|
| `fixed` | einhalten | einhalten; als Randbedingung nennen; öffnen nur auf Wort des Entwicklers |
| `decided` | einhalten; Kollision → anhalten und fragen | Gedanke zu Ende führen; Kollision wird geparkt |
| `open` | vor dem Bauen gegen sie: anhalten, Entscheidung einholen | frei; Alternativen ausarbeiten |

**Lage.** Geplanter Schritt oder konkreter Änderungsauftrag → `execute`. Idee, Bitte um Alternativen, „was wäre wenn" → `design` für den genannten Bereich. Unklar → einmal fragen. Wählst Du `design`, sagst Du es („Ich lese die Doku hier als Stand, nicht als Vorgabe").

**Kollision.** Eine geplante Änderung oder eine Idee verletzt eine Festlegung.

**Parken.** Ein Satz je Festlegung: was sie festlegt, ihr Grund (oder „Grund nicht überliefert" oder „vermutlich von außen vorgegeben — stimmt das?"), und die gemessenen Umbaukosten — Zahl der abhängigen Stellen aus `mentions` (Kapitel 3.6). Der Gedanke wird weder abgebrochen noch ausgeführt. Formulierung: „Das berührt X, weil …" — nie „Das geht nicht wegen X".

**Auswirkungsliste** (bei `open` in `design`): je berührter Festlegung ihr Grund und eine von drei Bewertungen — Grund fällt mit der Idee (kein Hindernis, wird mitgeändert) · Grund trägt weiter (echte Randbedingung; benennen, Idee anpassen oder Randbedingung mit zur Disposition stellen) · Grund nicht dokumentiert (Frage an den Entwickler). Festlegungen aus Abschnitten mit der Funktion `global` kennzeichnest Du als projektweit.

### 3.1.6 Der Planabschnitt „Berührte Festlegungen"

Jeder Plan trägt diesen Abschnitt. Er ist der Zwischenspeicher aller Annahmen bis zur Freigabe und der Ort, an dem der Entwickler sie sieht. Das Skript liefert sein Gerüst (`plan-section`, Kapitel 3.6).

**Je Eintrag:** ID (oder Wortlaut, wenn noch keine ID existiert), Kapitel, `kind`, `reason` oder Quelle, `status`, abgeleitete Härte mit der zutreffenden Bedingung in Prosa, und — bei Kollision — der geparkte Satz. Bei `pending` die Frage in Prosa.

**Freigabesatz.** Bei `assumptions_on_approval: accept` steht im Abschnitt: „Die Freigabe dieses Plans bestätigt die hier gelisteten Annahmen, soweit der Entwickler nichts anderes sagt." Bei `keep` fehlt der Satz. Das Wort des Entwicklers je Plan schlägt den Parameter: „nur ablegen" → dieser Plan wie `keep`; „gilt als bestätigt" → wie `accept`.

**Korrektur in Prosa.** Sagt der Entwickler etwas zu einem Eintrag („das ist eine Hardwaregrenze", „das haben wir wegen der Latenz so entschieden"), übersetzst Du das in die Attribute und zeigst die Zuordnung, bevor Du schreibst.

**Schreiben bei Ausführung.** Marken und Registerzeilen werden mit der Ausführung des Plans geschrieben — Doku und Code im Wechsel. Status: vom Entwickler angesprochen → `confirmed`; nicht angesprochen und Plan wie `accept` → `accepted`; nicht angesprochen und Plan wie `keep`, oder „später" → `assumed`. Ab jetzt findet `grep` sie; die Liste läuft ohne erneutes Lesen.

**Wiedervorlage.** Eine `assumed`-Festlegung steht bei jedem weiteren Kontakt erneut im Abschnitt, gekennzeichnet als Annahme, ohne erneute Frage. Bei `accept` hebt die nächste Freigabe sie auf `accepted`; bei `keep` bleibt sie, bis der Entwickler sie anspricht.

Die Länge des Abschnitts ist ein Maß für die Schrittgröße: Nennt ein Plan mehr als etwa fünfzehn Festlegungen, ist der Schritt zu groß — zerlegen, wie es der Standard für Kontrollfluss im Plan schon verlangt.

### 3.1.7 Fehlende und unlesbare Felder

| Was fehlt | Stumm | Ergebnis | Auffangnetz |
|---|---|---|---|
| kein Marker | R3, R4, R6 | `decided` | 3.1.3 bildet beim Kontakt die Annahme; der Plan zeigt sie |
| Marker ohne Grund | — | `decided`, in `design` mit Vermerk „Grund fehlt" | Annahme oder `pending`; `unknown` beendet das Fragen |
| keine Ereigniszeilen | R6 | nichts durch Erfahrung geöffnet | Zählung beginnt mit der ersten `friction`-Zeile |
| geplante Schritte ohne Umbauziel | R2, R5 | nichts durch Planung geöffnet; nur R1 öffnet | berührt ein Schritt erkennbar den Bereich, fragst Du einmal, ob er als Umbau gemeint ist, und trägst das Ziel nach (Kapitel 3.4) |
| Registerzeile unlesbar (Schlüsselwort falsch, Datum fehlt) | die jeweilige Prüfung | wie „fehlt" | `check` meldet die Zahl nicht lesbarer Zeilen (Kapitel 3.6) |
| Doku schweigt zum Bereich | alle | nichts bindet | Du erfindest keine Festlegung; entsteht eine, hältst Du sie fest (Kapitel 3.5) |

### 3.1.8 Was der Entwickler sieht

Bei `fixed` oder `decided` in `execute`: nichts. Bei einer Kollision in `design`: ein Satz je geparkter Festlegung. Bei `open`: die Auswirkungsliste (in `design`) oder die Frage vor dem Bauen (in `execute`). Im Plan: den Abschnitt „Berührte Festlegungen". Auf die Frage, warum etwas `open` ist: die Bedingung in Prosa („zweimal Reibung seit Juli, keine Bestätigung") — nie eine Prüfungsnummer.

### 3.1.9 Anker — wann was geschieht

| Anker | Handlung |
|---|---|
| Bereich öffnen (Kapitel für einen Schritt oder eine Idee laden) | Festlegungen des Bereichs per Skript listen; Abweichungen zwischen Prosa und Register melden. Die Liste macht sichtbar, löst aber keine Fragen aus. |
| Plan schreiben | Abschnitt „Berührte Festlegungen" füllen. Enthält der Plan einen Sonderfall, eine Ausnahme oder einen Umweg, der nur wegen einer Festlegung existiert → `friction`-Zeile an dieser Festlegung, mit Datum und einem Halbsatz. |
| Entwickler nennt Reibung („das ist umständlich wegen …") oder ein Review-Befund nennt eine Festlegung | `friction`-Zeile. |
| Idee verworfen oder Befund abgelehnt, nachdem eine Festlegung dagegen geprüft wurde | `upheld`-Zeile mit Datum und Bezug (welche Idee, welcher Befund). |
| Umbau eines Bereichs wird geplant | Der geplante Schritt nennt sein Umbauziel. Ist er erledigt, werden die betroffenen Festlegungen neu gesetzt; ihre Härte folgt wieder der Liste. |
| Neue Einheit wird gegen eine Festlegung gebaut | Härte lesen; nur bei `open` oder vorhandener Reibung ein Satz, sonst Schweigen. |

### 3.1.10 Bewusst nicht Teil dieses Regelteils

Alter der Entscheidung — Zeitregeln sind fragil; eine Festlegung ist „frisch", bis ihre erste `friction`-Zeile kommt. Umbaukosten als Eingang — sie entscheiden nicht, ob ein Gedanke verfolgt wird; sie stehen als Zahl im geparkten Satz. Gewichtung jeder Art — die Liste kennt nur Reihenfolge. Neues Wissen, das einen Grund kippt — ist live nicht erkennbar; gehört als Durchgang „Gründe noch gültig?" in die Konsistenzprüfung (Skill `konsistenzpruefung`).
