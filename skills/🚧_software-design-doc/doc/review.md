# Review: Herleitung vom Ziel zur Umsetzung

*Arbeitsdokument, angelegt am 2026-10-05. Es ersetzt nichts und ist selbst keine Festlegung.*

## Zweck und Methode

Anlass war die Beobachtung, dass die Arbeit am Vorhaben seit einiger Zeit aus dem Lösen von Diskrepanzen besteht — Befund, Korrektur, neue Regel, neuer Befund — statt aus der Detaillierung einer Kette, die vom Ziel her gezogen ist. Dieses Dokument zieht die Kette neu: vom Ziel des Skills über seine Grundfunktionen zu den Mechanismen, die sie brauchen, und zu den Vorgaben, die dafür getroffen wurden. In jeder Stufe steht, woraus sie folgt.

Die Richtung ist die Methode. Gelesen wurden als **Quelle** ausschließlich Kapitel 1 (Zusammenhänge), Kapitel 2 (Vorgaben), die Entscheidungstabelle in `status.md` und der Fahrplan. Kapitel 3 und die Zieltexte (`SKILL.de.md`, `rules-*.de.md`, `CLAUDE-snippet.de.md`) wurden gelesen, aber ausschließlich als **Umsetzungsversuch**: Von jeder Vorgabe aus wurde nachgesehen, ob und wo sie dort angekommen ist. Nie wurde aus der Umsetzung eine Vorgabe abgeleitet. Was in der Umsetzung steht und von keiner Vorgabe her erreicht wird, kommt im Hauptteil nicht vor und steht gesammelt im Anhang „Fehlumsetzungen".

Lücken sind das erwartete Ergebnis. Sie werden benannt, nicht gefüllt — weder mit einer neuen Vorgabe noch mit dem Hinweis, die Umsetzung regle das schon. Drei Arten: eine Leistung oder ein Mechanismus ohne tragende Vorgabe; eine Vorgabe, die von keiner Leistung her erreicht wird; ein Widerspruch zwischen Vorgaben. Sie sind durchnummeriert (L-nn) und am Ende gesammelt; im Text stehen sie dort, wo die Kette reißt.

## Ebene 0 — Das Ziel

**Das Problem, aus dem der Skill entsteht**, hat Kapitel 1.2 in zwei Fehlbildern beschrieben, die derselben Ursache entspringen. Der Vorläufer — ein Dokumentationsstandard als Abschnitt der globalen Anweisungsdatei — war in jeder Sitzung geladen und kannte nur eine Lesart der Doku: als Vorgabe. Daraus das **Fehlbild Intensität**: Struktur wird verlangt, wo nichts zu halten ist, in jedem Projekt gleich. Und das **Fehlbild Gesetz**: Jede Festlegung in einer Doku bindet, jede Idee stößt an eine und wird verworfen; mit wachsender Doku wird die Instanz unkreativ.

**Darunter liegt eine gemessene Eigenschaft der Instanz**: Anweisungen, die eine Haltung beschreiben, feuern nicht zuverlässig; an eine Handlung gebundene feuern. Und die Instanz wägt mehrere Dimensionen nicht zuverlässig gegeneinander ab. Jedes Verfahren, das Abwägung verlangt, scheitert hier.

**Das Ziel in einem Satz:** Eine entwicklungsbegleitende Doku, die mit dem Projekt wächst statt ihm Struktur aufzuzwingen, und in der die Instanz ohne Abwägung erkennt, was jetzt bindet und was zur Disposition steht — damit Ideen zu Ende gedacht werden, statt an Bestehendem abzuprallen.

**Die Leitidee** (Kapitel 1.3) macht daraus drei Sätze, die alles Weitere tragen: Die Instanz wägt nicht, sie schlägt nach. Alles, was sie zum Nachschlagen braucht, steht außerhalb der Prosa des Entwicklers. Der Entwickler schreibt seine Doku für Menschen; der Skill fügt ihr Adressen hinzu, keine Logik.

**Die Rollenverteilung** (Kapitel 1.3.4): Der Entwickler schreibt Prosa und entscheidet. Die Instanz führt Buch. Skript und Hooks kontrollieren. Der Entwickler muss weder Grammatik noch Schlüsselwörter kennen; sein Preis sind Klammern im Text, eine Registerdatei neben der Doku und ein Abschnitt in jedem Plan.

**Die Größenschranke** (Kapitel 1.10, Vorgabe 2.2): ein Skill, ein Skript. Keine Oberfläche, keine Editor-Erweiterung, keine fremde Infrastruktur je Projekt. Sieben Bedingungen halten das; jede nennt, was ohne sie nötig würde.

Diese Ebene ist vollständig und in sich geschlossen. Jede Aussage trägt einen Prüfvermerk des Entwicklers.

## Ebene 1 — Die Leistungen

Kapitel 1.7 nennt sieben Leistungen. Über allen steht der Grundsatz **„Die Doku wächst an Festlegungen, nicht an Pflichten"**, und daraus folgt die Zurückhaltung: Erstanlage nur auf Auftrag, Einstieg nur am Berührungspunkt, Prüfung nur an benannten Handlungen, und **gefragt wird nur, wenn die Antwort etwas bewirkt** (vormals Q-15).

| | Leistung | Folgt aus | Trägt zum Ziel bei |
|---|---|---|---|
| 1 | Erstanlage | Fehlbild Intensität: Gerüst nur auf Auftrag, in der Größe des Vorhabens | wächst statt zwingt |
| 2 | Einstieg in vorhandene Doku | Fehlbild Intensität: keine Gesamtmigration, kein Umbau fremder Struktur | wächst statt zwingt |
| 3 | Laufende Pflege | Vorläufer (Arbeitsschleife) + Buchführung, die dabei mitläuft | hält die Felder aktuell, aus denen Härte folgt |
| 4 | Auswirkungen finden | Vorläufer verlangte Handarbeit (Segment 1 als Suchweg); die trägt nicht | Vollständigkeit der Vorlage bei der Mechanik |
| 5 | Einen Bereich neu denken | **Fehlbild Gesetz — die Leistung, um derentwillen das Vorhaben begonnen wurde** | Ideen zu Ende denken |
| 6 | Prüfen und Aufräumen | Rollenverteilung: Kontrolle bei Skript und Hooks, nicht bei der Erinnerung | hält die Buchführung konsistent |
| 7 | Nichts tun | Fehlbild Intensität: ein Projekt, das den Skill nicht braucht, zahlt nichts | wächst statt zwingt |

Die Ableitung aller sieben aus Ebene 0 ist tragfähig. Was auffällt, ist das Gewicht ihrer Ausarbeitung in Kapitel 1: Leistung 1 (Erstanlage) füllt den längsten Abschnitt mit drei Gliederungsformen, sechs Planpunkten und einer Liste von Ordnernamen; Leistung 5, die Gründungsleistung, hat drei Sätze.

> **L-01 — Die Gründungsleistung hat keine tragende Vorgabe.** Leistung 5 ist der Grund des Vorhabens. Was sie verlangt — Kollisionen parken statt als Ablehnung formulieren, den Gedanken zu Ende führen, die Doku als Stand statt als Vorgabe lesen —, steht in Kapitel 1.7.5 in drei Sätzen und als Messgröße der Probe („Parken statt Abschuss"). In Kapitel 2 steht nichts dazu. Der einzige Ort, an dem das Verhalten ausformuliert ist, ist die Umsetzung (Härte-mal-Lage-Tabelle, Parken, Auswirkungsliste). Damit ist die Leistung, an der sich das Design laut Kapitel 1.9 entscheidet, die am dünnsten festgelegte.

## Ebene 2 — Die Mechanismen

Aus Leitidee und Leistungen folgt, welche Mechanismen der Skill braucht. Es sind neun; jede Leistung stützt sich auf mehrere davon.

| Mechanismus | Folgt aus | Dient den Leistungen |
|---|---|---|
| A Härte | Leitidee 1: nachschlagen, wann etwas bindet | 3, 5, 2 |
| B Marker und Register | Leitidee 2: Felder außerhalb der Prosa, Adresse im Text | alle |
| C Rollen | Kapitel 1.3.3: der Skill muss wissen, in welcher Textart er steht | 2, 4, 6 |
| D Geplante Schritte und Umbauziel | Härte braucht die Planung: Was umgebaut wird, ist offen | 3, 5 |
| E Auswirkungsrechnung | Leistung 4 | 4 |
| F Prüfung, Hooks, Wiederaufnahme | Kapitel 1.3.5: Einhaltung sichern nicht durch Anweisung | 6, 3 |
| G Skript | Kapitel 1.3.6: zählen, ableiten, einsammeln, abgleichen ist Mechanik | alle |
| H Ablauf an Ankern | gemessene Eigenschaft: handlungsgebunden feuert, haltungsbeschreibend nicht | alle |
| I Konfiguration und Abwahl | Leistung 7, Vorgabe 2.13: kein Zwang, kein Formular | 7, 1 |

Die folgenden Abschnitte gehen jeden Mechanismus durch: woraus er folgt, was dafür festgelegt ist und woher die Festlegung stammt, wo sie umgesetzt ist, und wo die Kette reißt.

### A — Härte

**Woraus sie folgt.** Fehlbild Gesetz verlangt eine Unterscheidung zwischen „bindet jetzt" und „steht zur Disposition". Die Instanz darf sie nicht abwägen (gemessene Eigenschaft), also muss sie aus Feldern folgen, die nachschlagbar sind. Aus Härte und **Lage** der Sitzung (ausführen oder entwerfen) folgt das Verhalten.

**Was festgelegt ist.**
- Drei Härtewerte `fixed`, `decided`, `open`; zwei Lagen `execute`, `design`; sechs Zellen Verhalten (Kapitel 1.3.1, 1.4).
- Die Eingangsgrößen: Art, Grund, Status, Ereigniszeilen, Umbauziele geplanter Schritte (1.3.1).
- Die geordnete Prüfliste R1–R7: erste zutreffende gewinnt, nichts wird gewichtet (1.3.1, seit 2026-10-04 dort).
- Was bewusst nicht einfließt: Alter, Umbaukosten, Gewichtung, neues Wissen (1.3.1).
- Annahmen machen nie `fixed` (Vorgabe 2.11).
- Fehlende Felder blockieren nie (Vorgabe 2.10).
- `pinned` als einzige gespeicherte Härte; `upheld` als Name der Bestätigungszeile (Q-02).
- Reibungsschwelle als Skill-Parameter, für `global` eine Stufe höher (1.3.3, 2.9).

**Wo umgesetzt.** `rules-core.de.md` Abschnitte 1, 2, 4–6, 8, 9; Kommando `hardness` (Kapitel 3.6.4).

**Wo die Kette reißt.**

> **L-02 — Das Schlüsselwort `mode` trägt zwei Bedeutungen.** Die Lage heißt in Kapitel 1.4 und im Zieltext `mode` mit den Werten `execute`/`design`. Der Skill-Parameter für die Abwahl heißt ebenfalls `mode` mit den Werten `on`/`off`/`null`. Vorgabe 2.1 verlangt, dass ein Schlüsselwort ein Name ist und niemand zwei Zustände unter einem Wort lesen darf; genau dieser Grund hat Q-02 die Ereigniszeile von `confirmed` zu `upheld` umbenannt. Hier steht derselbe Fehler unbemerkt.

> **L-03 — Die Lage erreicht das Skript nicht.** Kapitel 1.7.4 verspricht, der Abbruchwert der Auswirkungsrechnung sei „eng in der Lage `execute`, weiter in der Lage `design`". Es gibt aber einen einzigen Skill-Parameter `impact_cutoff`, und kein Kommando nimmt die Lage als Argument. Die Härte-mal-Lage-Tabelle ist Verhalten der Instanz und braucht das nicht; die versprochene Lageabhängigkeit der Rechnung hat keinen Weg.

### B — Marker und Register

**Woraus es folgt.** Leitidee 2: Die Felder gehören zur Festlegung, stehen aber nicht bei ihr im Text. Also ein Register daneben und in der Prosa nur eine Adresse. Leitidee 3: Der Entwickler schreibt für Menschen — kein Attribut, kein Zustand im Dokument.

**Was festgelegt ist.**
- Zwei Marker: Definitionsmarker `[D-0042]` genau einmal je Festlegung, Zitatmarker `[>D-0042]` an Stellen, die sie heranziehen (1.4, 2.10).
- Marker vor dem Satzzeichen (Q-03); Pflicht am Definitionsort und in `relate`-Texten, sonst optional (Bedingung 1, Q-06).
- ID global je Register, nie neu vergeben, trägt kein Kapitel (1.4, Bedingung 2).
- Die Felder des Registers mit allen Werten (1.4): Art, Grund/Quelle, Alternative, Status, Festgeschrieben, Suchschlüssel, Fingerabdruck, Ereigniszeilen, Lebenszyklus.
- Marker werden vorgeschlagen, nicht verfügt; Ablehnung trifft den Marker, nicht den Mechanismus; dazwischen gibt es nichts (1.3.3, Q-07).
- Zweiter Ankermechanismus über Wortlaut verworfen (Q-07, Vorgabe 2.3).
- Im Dokument des Entwicklers stehen vom Skill nur Adressen (Vorgabe 2.3).
- Was überholt ist, darf nicht unmarkiert dastehen: `superseded … by` oder `retired` (1.7.6).
- Aufnahmetest einer Festlegung: Kann Code das verletzen? (1.4, 1.3.7)
- Was die Prosa festhält und was Code, Docstrings und andere Doku tragen (1.3.7).

**Wo umgesetzt.** `rules-core.de.md` Abschnitte 11–17; Registersyntax in Kapitel 3.6.4 bei `apply`; Kommandos `apply`, `show`, `next-id`, `supersede`, `retire`.

**Wo die Kette reißt.**

> **L-04 — Wer schreibt die Marker in die Prosa?** Kapitel 1.3.4 sagt: die Instanz, mit der Ausführung des Plans. Kapitel 3.6.2 sagt: kein Kommando ändert Prosa des Entwicklers. Die Ergänzung zu Vorgabe 2.6 vom 2026-10-04 sagt: `apply` schreibt die Markerformen in die Prosa. Drei Stellen, drei Antworten. Die dritte widerspricht Bedingung 6 (kein automatisches Umschreiben von Prosa), wenn man sie wörtlich nimmt.

> **L-05 — Eine dritte Adressart ist nicht erklärt.** Vorgabe 2.3 kennt im Dokument des Entwicklers genau zwei Dinge vom Skill: Marker an Festlegungen und Rollen an Überschriften oder Absätzen. Vorgabe 2.10 kennt vier Feldsorten. Die Zeile `[register: pfad]` in einer Dokudatei (Q-19, Kapitel 3.5.4) ist weder das eine noch das andere — ein Konfigurationszeiger im Dokument, den keine Vorgabe vorsieht.

### C — Rollen

**Woraus sie folgen.** Kapitel 1.3.3: Der Skill muss wissen, in welcher Art Text er steht — sechs Textarten, sechs Verhaltensweisen. Erkennen darf er sie nicht an Nummern oder Überschriften (Bedingung 2, Vorgabe 2.3), also an einem Etikett. Das Etikett nennt den Inhalt, nicht das Verhalten, weil der Entwickler es an seinen Überschriften lesen und bestätigen muss.

**Was festgelegt ist.**
- Sechs Funktionen `define`, `relate`, `global`, `nonbinding`, `plan`, `register` mit ihrer Wirkung (1.3.3, Q-10).
- Siebzehn Rollen — zwölf aus arc42, fünf aus der Projektarbeit — mit ihrer Funktion (1.3.3, Q-08); `decisions` neben dem Register (Q-09); `concept` als Denkraum.
- Rollenmarker `[DS:rolle]` am Ende der Überschrift, gilt bis zur nächsten gleicher oder höherer Ordnung; Wechsel auch am Absatz, nicht feiner; Definitionsmarker geht der Rolle vor (Q-11).
- Ohne Rolle gilt `building-blocks`; der Skill schlägt vor, verlangt nicht (1.3.3).
- Bereichskennung `S-nn` im Rollenmarker für Umbauziele, nur wo gebraucht (1.7.3, Vorgabe 2.3).

**Wo umgesetzt.** `rules-core.de.md` Abschnitt 3 (zweispaltig); Form des Markers in Kapitel 3.3.1; Kennung in 3.3.2.

**Wo die Kette reißt.**

> **L-06 — Die Begründung für siebzehn Rollen trägt nicht mehr.** Q-08 wählte den vollen Satz mit dem Satz „die Tabelle kostet nichts". Gemessen am 2026-10-04: die vollständige Tabelle kostet rund 725 Token je Skillstart, die zweispaltige 161. Die Entscheidung mag richtig sein; ihre Begründung ist es nicht mehr, und die Frage, wohin die dritte Spalte gehört, steht seit dem Neuschnitt offen im Fahrplan.

### D — Geplante Schritte und Umbauziel

**Woraus es folgt.** Härte braucht zu wissen, was gerade umgebaut wird: Ohne Umbauziel bindet alles, was einmal entschieden wurde (1.7.3). Geplante Schritte gibt es in jedem Projekt irgendwo; der Skill setzt keine Fahrplandatei voraus (Leitidee 3, Vorgabe 2.3).

**Was festgelegt ist.**
- Ein geplanter Schritt ist ein offener Schritt der Planung, wo immer er steht (1.4).
- Umbauziel `target:` nennt IDs oder eine Bereichskennung, nie einen Ort; ID öffnet kompromisslos, Bereich öffnet vorsichtig (1.7.3, 2026-10-02).
- Keine eigenen Schrittkennungen (Q-14).
- Inhalt eines Schritts: Ziel, Dringlichkeit, Umbauziel, Verweis auf die Planung — nicht der Weg (Q-12).
- Wo eine Planung steht: drei Orte nach Länge und Haltbarkeit (Q-12).
- Ausnahme von 2.3: Registerpfad als Qualifier bei mehreren Registern (2.3, benannt).

**Wo umgesetzt.** `rules-planning.de.md`; Kommandos lesen `target:` für R2 und R5.

**Wo die Kette reißt.**

> **L-07 — Die Planungsort-Regel ist aus einem lokalen Konflikt abgeleitet, nicht aus dem Ziel.** Kapitel 1.7.3 begründet, warum der Skill festlegen *muss*, wo eine Planung steht: „Die bestehenden Anweisungen widersprechen sich" — die globale und die Projekt-`CLAUDE.md` des Entwicklers. Das ist ein Konflikt in den Anweisungsdateien eines Nutzers, und der Skill soll für alle Projekte gelten. Dass geplante Schritte ein Umbauziel tragen, folgt aus dem Ziel; dass eine Planung je nach Länge an einem von drei Orten steht, folgt aus einem Vorfall vom 22. August und gehört zum Standard des Vorläufers (`standard.de.md`), nicht zum Mechanismus des Skills.

### E — Auswirkungsrechnung

**Woraus sie folgt.** Leistung 4. Die gefährlichen Fälle nennen den geänderten Gegenstand nicht; sie sind nur über den Zusammenhang erreichbar, in dem beide gemeinsam genannt wurden. Keine semantische Suche (Bedingung 3).

**Was festgelegt ist.**
- Kandidaten aus dem Geflecht der Marker — gleicher Absatz, Abschnitt, Nachbarabschnitt, Kapitel — und aus Suchschlüsseln als zweiter Quelle (1.7.4, Q-20).
- Kanten über Kapitelgrenzen entstehen nur in `relate`-Texten; deshalb ist die Frage nach einem solchen Text die folgenreichste Einzelheit der Erstanlage (1.7.4).
- Das Skript liefert Kandidaten mit Grund; die Instanz urteilt je Kandidat (1.7.4).
- Suchschlüssel wählt die Instanz beim Anlegen, sichtbar im Plan (Q-05).
- Abbruchwert einstellbar; die Weite wird gemessen, nicht gerechnet (1.7.4).
- `networkx` optional, nie Voraussetzung, bewusste Wahl des Entwicklers, drei Zustände (1.7.4, Q-25).
- Zitatmarker außerhalb `relate` optional; die Probe entscheidet (Q-06).
- **Die Rechtfertigung ist offen:** Findet die Probe keine Kandidaten, die eine Textsuche verfehlt hätte, entfällt das Geflecht und nur die Erwähnungssuche bleibt (1.7.4, 1.6.8 Schritt 8).

**Wo umgesetzt.** `impact.py` mit drei Kostenfunktionen (Kapitel 3.6.5); Kommandos `impact`, `mentions`; Skill-Parameter `impact_model`, `impact_cutoff`, `impact_lib`.

**Wo die Kette reißt.**

> **L-08 — Die Suchschlüssel haben keinen Weg vom Urteil zum Kommando.** Q-05: Die Instanz wählt die Schlüssel beim Anlegen. Kapitel 3.6.4: `plan-section` gibt „den Suchschlüsselblock für die neu angelegten IDs" aus, und `apply` schreibt die Schlüssel ins Register. Weder ist festgelegt, wie die von der Instanz gewählten Schlüssel in `plan-section` hineinkommen, noch gibt es zum Planzeitpunkt für neue Festlegungen schon IDs. Der Mechanismus hat zwei Enden und keine Mitte.

> **L-09 — Ein Drittel der Konfiguration hängt an einer unbewiesenen Leistung.** Drei der elf Skill-Parameter, ein eigenes Modul, drei Kostenfunktionen, eine optionale Bibliothek und ein Rechenmodell in Anhang B dienen Leistung 4, deren Bestand laut Kapitel 1.7.4 an einer einzigen Zahl der Probe hängt. Das ist keine Lücke in der Herleitung — jede dieser Festlegungen folgt aus 1.7.4 —, aber die Kette zeigt, wo das Vorhaben sein Risiko konzentriert hat: in der am weitesten ausgearbeiteten und am wenigsten belegten Leistung.

### F — Prüfung, Hooks, Wiederaufnahme

**Woraus es folgt.** Kapitel 1.3.5: Dass die Instanz Marker und Registerzeilen tatsächlich schreibt, sichern nicht Anweisungen, sondern ein Skript und Hooks — weil Anweisungen, die eine Haltung beschreiben, nicht zuverlässig feuern (1.2). Bedingung 4.

**Was festgelegt ist.**
- H1 Lint nach Doku-Edit, nur auf dem Diff, nur Meldung (1.3.5, Vorgabe 2.12).
- H2 Abgleich vor Commit; blockiert bei struktureller Inkonsistenz; aufhebbar nur durch Wort des Entwicklers; Aufhebung hinterlässt Notiz (Q-26, Vorgabe 2.8).
- Was eine strukturelle Inkonsistenz ist: sechs maschinell eindeutige Zustände (1.3.5).
- H3 Zustandsbericht am Sitzungsstart: einziger Hook mit Einrichtung je Projekt; **ob er gebaut wird, ist offen** (1.7.6).
- Hooks sind nur lesend (Vorgabe 2.8); Fingerabdruck wird erst nach dem Urteil geschrieben (1.7.6).
- Fingerabdruck je Definitionssatz; jede Abweichung wird gemeldet, nichts unterdrückt; billig durch Vorarbeit (Q-04).
- Dritte Säule Wiederaufnahme: Notiz im Commit, nur Faden, nie Kontext; fällig beim nächsten Kontakt, nicht am Sitzungsbeginn; mit Sitzungskennung (1.3.5, 2026-09-25).
- Absicherung kommt mit dem Skill, wirkt ohne Einrichtung je Projekt (1.3.5) — H3 ausgenommen.
- Abwahl gilt auch für Hooks; das leistet das Skript, nicht die Konfiguration (1.7.7, 2026-10-02).

**Wo umgesetzt.** Kapitel 3.7; Kommandos `lint`, `check`, `fp`, `notes`; Trailer-Grammatik in `rules-core.de.md` Abschnitt 19.

**Wo die Kette reißt.**

> **L-10 — H3 ist zugleich eingeplant und unentschieden.** Kapitel 1.7.6 lässt offen, ob H3 gebaut wird, und ob das jetzt oder nach der Probe entschieden wird. Fahrplanschritt 6 baut ihn. Das Entscheidungstor der Probe (3.8.5) sagt, über H3 werde vorher entschieden. Der Widerspruch ist in Kapitel 3.7 und im Fahrplan benannt und seit dem 2026-09-25 nicht aufgelöst.

### G — Skript

**Woraus es folgt.** Kapitel 1.3.6: Vier Arbeiten, bei denen eine Instanz Urteil vortäuschen würde, wo Mechanik gefragt ist — zählen, ableiten, einsammeln, abgleichen. Was eindeutig bestimmt ist, gehört in ein Programm.

**Was festgelegt ist.**
- Was das Skript nie tut: Prosa umschreiben, entscheiden ob ein Satz eine Festlegung ist, beurteilen ob ein Kandidat betroffen ist (1.3.6).
- Kommandos entlang der Anker, nicht entlang des Datenmodells; Listen statt Einzel-IDs; Entscheidungen im Bündel (1.3.6, Vorgabe 2.7).
- Drei Rückgabewege: inline, Datei mit Kurzfassung, Skript schreibt selbst (1.3.6).
- Jede Ausgabe ist eine Aussage: Kopfzeile vorn mit vier Ausgängen, darunter eine Zeile je Gegenstand (Vorgabe 2.5); die Form — Zeile oder JSON — ist offen und wird gemessen.
- Skripte entscheiden, was mechanisch entscheidbar ist; `DECIDE` nur für das Unkodierbare (Vorgabe 2.6).
- Kein Regelteil erzählt eine Mechanik nach, die ein Kommando ausführt; zweistufiger Maßstab (Vorgabe 2.6, 2026-10-03/04).
- Jede Voraussetzung hat einen Default, Fehlen wird exakt gemeldet, Script-Argument führt hin (Vorgabe 2.4).
- Was kostet, sind Entscheidungen und Edits der Instanz, nicht Rechenzeit (Vorgabe 2.7).
- Jedes Kommando liest zuerst die Parameterdatei und endet bei `mode: off` stumm (1.7.7).
- Skriptname folgt dem Skillnamen (Q-24); `impact` als Kommandoname (Q-22).

**Wo umgesetzt.** Kapitel 3.6 vollständig; Fahrplanschritte 4 und 5. Das Skript existiert nicht.

**Wo die Kette reißt.**

> **L-11 — Die Ausgabeform ist offen, und beide Formen werden gebaut.** Vorgabe 2.5 lässt offen, ob Zeile oder JSON der Standard ist, und verweist auf eine Messung. Kapitel 3.6.3 spezifiziert die Zeilenform vollständig und führt `--json` daneben. Das ist konsistent, aber die Entscheidung ist seit dem 2026-09-25 vertagt und blockiert laut Fahrplan Schritt 4.

### H — Ablauf an Ankern

**Woraus er folgt.** Die gemessene Eigenschaft aus 1.2: handlungsgebunden feuert, haltungsbeschreibend nicht. Also greift der Skill nicht kontinuierlich ein, sondern an benannten Handlungen (1.8).

**Was festgelegt ist.**
- Sechs Anker in Reihenfolge: Skillstart, Bereich öffnen, Lage bestimmen, Plan schreiben, Ausführen, Hooks (1.8).
- Der Trigger in der `CLAUDE.md` lädt den Skill; er bleibt unverändert, auch bei `mode: off` (Q-31).
- Der Ladebaum: Wurzel dünn, kein Zweig lädt einen anderen, Ladebedingung an benennbarem Anlass, Abbrüche in der Reihenfolge der Kosten (Vorgabe 2.15).
- Adressen im Zieltext: durchlaufende Abschnittsnummern, benannte Tabellen (Vorgabe 2.16).

**Wo umgesetzt.** `SKILL.de.md`; `CLAUDE-snippet.de.md`; `rules-core.de.md` Abschnitt 10.

**Wo die Kette reißt.**

> **L-12 — Kapitel 1.8 und Vorgabe 2.9 sagen noch, der Skillstart frage.** 1.8, Schritt 1: „Die Instanz liest die Skill-Parameterdatei oder erhebt aus dem Projekt, was sich ablesen lässt, und **fragt** nur, was sich nicht ablesen lässt." Vorgabe 2.9: „Der Skillstart **erfragt** nur, was sich aus dem Projekt nicht ablesen lässt." Beides widerspricht Q-15 vom 2026-10-02: Gefragt wird am ersten Anlass, nicht beim Laden. Der Prüfvermerk an 1.8 stammt vom 24. September, vor Q-15.

> **L-13 — Der Trigger wiederholt die Schwäche des Vorläufers wörtlich.** Anhang A.13 hält fest, der Trigger des Vorläufers sei „eigenschaftsförmig" gewesen — „sobald eine Software-Änderung über eine lokal begrenzte Korrektur hinausgeht" — und eine Abwahl damit realistisch. `CLAUDE-snippet.de.md` trägt denselben Wortlaut, nur mit dem neuen Skillnamen. Kapitel 3.11 sagt, der Wortlaut sei an eine Ankerhandlung gebunden; das trifft auf „bevor du zum ersten Mal einen Lösungsweg vorschlägst" zu, nicht auf die Bedingung dahinter, die ein Urteil verlangt. Weder Kapitel 1 noch 2 hat die eigene Beobachtung aus A.13 aufgegriffen.

### I — Konfiguration und Abwahl

**Woraus es folgt.** Leistung 7 und Vorgabe 2.13: Ein Projekt muss nie konfigurieren, um den Skill zu benutzen; eines, das ihn nicht braucht, zahlt nichts; der Entwickler füllt kein Formular.

**Was festgelegt ist.**
- Vor allem anderen: Wird hier Software entwickelt? Mechanisch, asymmetrisch, nur das klare Nein (1.7.7, 2026-10-02).
- Elf Skill-Parameter, jeder mit Standardwert, in `.claude/software-design-doc.json` (Vorgabe 2.9); Aufnahmetest: lohnt das Behalten, und setzen zwei Projekte es verschieden (2.9, 2026-10-03).
- `mode: off` ist eine gültige Betriebsart; fehlt er, wird nicht `on` angenommen, sondern am ersten Anlass gefragt (Q-16, Q-15).
- Eine Skill-Parameterdatei je Repository; ein Vorhaben weicht über `[register: pfad]` ab (Q-19).
- Das Absatzlayout ist kein Parameter (Q-17).
- Erstanlage: nur auf Auftrag, Vorschlag im Plan statt Fragebogen, drei Gliederungsformen, sechs Punkte, keine leeren Kapitelhüllen (1.7.1).
- Einmal je Sitzung sagt der Skill, wenn er abgewählt oder nicht zuständig ist (1.7.7).

**Wo umgesetzt.** `rules-startup.de.md`; `SKILL.de.md` Schritte 1–3 und 6; Kapitel 3.5.

**Wo die Kette reißt.**

> **L-14 — Kapitel 1.7.1 widerspricht sich selbst.** Es sagt: „Klärung im Gespräch, kein Formular … Sie arbeitet also keine Fragenliste ab." Vier Absätze später steht unter „Planungen und Arbeitsschritte" eine Liste von drei Fragen an den Entwickler — Fahrplan ja oder nein, Planung wo, Status wo. Der Entwickler hat diesen Widerspruch am 2026-09-18 benannt; der Abschnitt trägt dennoch den Prüfvermerk „Ok" und ist unverändert.

## Ebene 3 — Woher die Vorgaben in Kapitel 2 stammen

Kapitel 2 verlangt für jede Vorgabe, dass man auf eine Datei zeigen und sagen kann „das verletzt sie". Die folgende Tabelle fragt umgekehrt: Woraus folgt jede Vorgabe, und ist sie eine Vorgabe über den Skill oder eine über die Arbeit an ihm?

| Vorgabe | Folgt aus | Art |
|---|---|---|
| 2.1 Sprache und Namen | Leitidee 1: ein Schlüsselwort ist ein Name, kein Interpretationsspielraum; Englisch aus der Repositoryregel | Skill, teils äußere Regel |
| 2.2 Sieben Bedingungen | Größenschranke, Kapitel 1.10 | Skill |
| 2.3 Rollen statt Struktur | Leitidee 3, Bedingung 2 | Skill |
| 2.4 Default, Meldung, Script-Argument | 2.13 kein Zwang, 1.3.4 | Skill |
| 2.5 Jede Ausgabe ist eine Aussage | 1.3.6 Rückgabewege, 2.7 Kosten | Skill |
| 2.6 Skripte entscheiden | Leitidee 1, 1.3.6 | Skill |
| 2.6 Ergänzungen 2026-10-03/04 | aus Vorgabe 2.6 selbst, Anlass war die Entlastung | Arbeit am Skill |
| 2.7 Was kostet | 1.3.6 | Skill |
| 2.8 Hooks nur lesend | 1.3.5, Bedingung 6 | Skill |
| 2.9 Skill-Parameter | 2.13, Leistung 7 | Skill |
| 2.10 Felder | 1.3.2 | Skill, definitorisch |
| 2.11 Annahmen nie fixed | 1.3.4, Fehlbild Gesetz | Skill |
| 2.12 Lint nur auf Diff | Bedingung 4, 1.3.5 | Skill |
| 2.13 Kein Zwang | 1.3.4 | Skill |
| 2.14 Doku wendet Vorhaben nicht auf sich an | — | Arbeit am Skill |
| 2.15 Ladebaum | Fehlbild Intensität: der Vorläufer war immer geladen | Skill |
| 2.16 Adressierung im Zieltext | 2.15 „Laden und Verweisen sind zweierlei" | Arbeit am Skill |

Dreizehn der sechzehn Vorgaben folgen aus Ebene 0 oder 1. Drei — 2.14, 2.16 und die Ergänzungen zu 2.6 — regeln die Entwicklungsarbeit, nicht den Skill. Das ist nicht falsch, aber sie stehen in einem Kapitel, das sich als „Festlegungen für alles, was in diesem Vorhaben entsteht" versteht, und sie sind alle drei in den letzten drei Tagen entstanden oder gewachsen.

> **L-15 — Die Grenze zwischen Segment 1 und 2 wird nicht gehalten.** Kapitel 1 trägt mindestens zwanzig datierte Festlegungen, die den Aufnahmetest von Kapitel 2 bestehen würden — „Marker werden vorgeschlagen, nicht verfügt", „Gefragt wird, wenn die Antwort etwas bewirkt", „Jedes Kommando liest zuerst die Skill-Parameterdatei", „Was überholt ist, darf nicht unmarkiert dastehen", die gesamte Prüfliste R1–R7. Kapitel 2 trägt dagegen drei Vorgaben über die Arbeitsweise. Die Folge: Wer die Vorgaben sucht, findet die Hälfte in Kapitel 1 unter Begründungen; wer Kapitel 1 liest, um das Ziel zu verstehen, liest Vorgaben. Das ist der Zustand, den die Arbeitsanweisungen für Segment 1 und 2 ausschließen — und der erklärt, warum Befunde über Diskrepanzen zwischen Stellen entstehen, die beide normativ sind.

> **L-16 — Eine Vorgabe wird angewendet, die nirgends steht.** Kapitel 3.9.2 sagt, der Abschnitt „Zusammenspiel mit anderen Skills" verstoße „gegen die Vorgabe, dass kein Skill-Körper auf einen anderen Skill dieses Verzeichnisses verweist". Diese Vorgabe steht nicht in Kapitel 2. Sie wird in den Zieltexten mehrfach verletzt (`konzept-segmentierung`, `konsistenzpruefung`, `git-workbench.json`, `git-branch-model.json`), aber nirgends im Vorhaben festgehalten.

## Die Lücken gesammelt

| | Lücke | Art | Ebene |
|---|---|---|---|
| L-01 | Gründungsleistung 5 hat keine Vorgabe in Kapitel 2, nur drei Sätze und eine Messgröße | Leistung ohne Vorgabe | 1 |
| L-02 | `mode` trägt zwei Bedeutungen — Lage und Abwahl | Widerspruch zu 2.1 | A, I |
| L-03 | Lageabhängiger Abbruchwert versprochen, kein Weg zum Skript | Vorgabe ohne Mechanismus | A, E |
| L-04 | Wer Marker in die Prosa schreibt: drei Antworten | Widerspruch | B |
| L-05 | `[register: pfad]` ist weder Adresse nach 2.3 noch Feld nach 2.10 | Mechanismus ohne Vorgabe | B, I |
| L-06 | „Tabelle kostet nichts" als Begründung für siebzehn Rollen ist gemessen falsch | Begründung trägt nicht | C |
| L-07 | Planungsort-Regel folgt aus lokalem Anweisungskonflikt, nicht aus dem Ziel | Vorgabe ohne Herleitung | D |
| L-08 | Suchschlüssel: Instanz wählt, Skript gibt aus — keine Übergabe festgelegt | Mechanismus ohne Mitte | E |
| L-09 | Ein Drittel der Konfiguration hängt an einer Leistung, deren Bestand offen ist | Risikokonzentration | E |
| L-10 | H3 eingeplant und unentschieden zugleich | Widerspruch Fahrplan / Probe-Tor | F |
| L-11 | Ausgabeform offen, beide gebaut | vertagte Entscheidung | G |
| L-12 | 1.8 und 2.9 sagen „der Skillstart fragt" — gegen Q-15 | veraltet | H |
| L-13 | Trigger wiederholt die in A.13 benannte Schwäche des Vorläufers | unaufgegriffene eigene Beobachtung | H |
| L-14 | 1.7.1: „kein Formular" neben einer Fragenliste | Widerspruch im Abschnitt | I |
| L-15 | Segment-1/2-Grenze nicht gehalten: Vorgaben in Kapitel 1, Arbeitsregeln in Kapitel 2 | strukturell | 3 |
| L-16 | Vorgabe gegen Skill-Querverweise wird angewendet, steht aber nirgends | Vorgabe fehlt | 3 |

Was die Sammlung zeigt: Keine der sechzehn Lücken liegt in Ebene 0. Eine liegt in Ebene 1, dreizehn in den Mechanismen, zwei in der Struktur der Doku selbst. Von den dreizehn sind fünf Widersprüche zwischen Stellen, die beide festlegen wollen (L-02, L-04, L-10, L-12, L-14); L-15 benennt die Ursache dafür. Das stützt die Vermutung, mit der dieses Dokument begann: Die Diskrepanzen entstehen, weil dieselbe Sache an mehreren Orten festgelegt wird, nicht, weil zu wenig festgelegt wäre.

## Anhang — Fehlumsetzungen

Hier steht, was in Kapitel 3 oder in den Zieltexten steht und von keiner Vorgabe her erreicht wird. Es sind keine Fehler im Sinne von falsch — es sind Inhalte, deren Herkunft Interpretation oder Übereifer ist und die aus Sicht der Aufgabe nicht zu halten sind, solange ihnen keine Vorgabe vorausgeht. Jeder Eintrag nennt die Stelle und was dort steht; ob daraus eine Vorgabe werden soll oder der Inhalt entfällt, ist nicht hier zu entscheiden.

| | Stelle | Was dort steht | Warum ohne Vorgabe |
|---|---|---|---|
| F-01 | `SKILL.de.md`, Schritt 5 | `standard.de.md` wird geladen, „wenn eine Frage zur Methodik ansteht" | Vorgabe 2.15 nennt genau diese Formulierung als Beispiel einer unzulässig weichen Ladebedingung |
| F-02 | `rules-core.de.md`, Abschnitt 6 | Auswirkungsliste mit drei Bewertungen: Grund fällt mit der Idee, trägt weiter, nicht dokumentiert | Kapitel 1.7.5 kennt die Auswirkungsliste nicht; die drei Bewertungen stehen nirgends in Kapitel 1 oder 2 |
| F-03 | `rules-core.de.md`, Abschnitt 7 | „Nennt ein Plan mehr als etwa fünfzehn Festlegungen, ist der Schritt zu groß" | Die Zahl stammt aus Szene 8 in Kapitel 1.6 — einer Erzählung, keiner Vorgabe |
| F-04 | `rules-core.de.md`, Abschnitt 10 | Anker „Neue Einheit wird gegen eine Festlegung gebaut" | Kapitel 1.8 kennt sechs Anker; dieser ist keiner davon |
| F-05 | `rules-core.de.md`, Abschnitt 4 | Drei Antwortformen auf eine Frage: Antwort, „Später", „Lass uns das durchgehen" | Vorgabe 2.13 regelt, wie gefragt wird; ein Protokoll der Antworten steht nirgends |
| F-06 | Vorgabe 2.6, Ergänzung 2026-10-04 | „Die Markerformen schreibt zwar `apply` in die Prosa" | Widerspricht 3.6.2 und 1.3.4; eine Behauptung über die Umsetzung in einem Vorgabentext, siehe L-04 |
| F-07 | `rules-core.de.md` Abschnitte 17 und 20; `rules-startup.de.md` | Verweise auf `konzept-segmentierung`, `konsistenzpruefung`, `git-workbench.json`, `git-branch-model.json` | Verstoßen gegen eine Vorgabe, die angewendet, aber nirgends festgehalten wird, siehe L-16 |
| F-08 | Kapitel 3.6.4, `plan-section` | „darunter der Suchschlüsselblock für die neu angelegten IDs" | Neue Festlegungen haben zum Planzeitpunkt keine ID; B-03 legte den Block mit Wortlaut an, siehe L-08 |
| F-09 | Kapitel 3.6.4, `notes` | „läuft beim Öffnen eines Bereichs zusammen mit dem Abgleich" | Die Spezifikation von `open` nennt keine Notizen in ihrer Ausgabe |
| F-10 | `rules-startup.de.md`, Erkennung der Projektart | Listen von Manifesten und Dateiendungen im Regelteil | Fahrplanschritt 10 macht die Prüfung zu einem Kommando; nach Vorgabe 2.6 wären die Listen dann Spezifikation, nicht Regeltext |
| F-11 | Kapitel 3.9 | Migration und Installation | Das Kapitel benennt selbst, dass es „keine Quelle in Kapitel 1" hat und überwiegend Handlungen am System des Entwicklers beschreibt |
| F-12 | `rules-startup.de.md`, „Die Doku wächst" | „eine Festlegung aus Kapitel 1 oder 2" | Kapitelnummern dieser Doku im Zieltext; bekannt als B-09, verstößt gegen 2.3 |
| F-13 | `rules-core.de.md`, Abschnitt 2 | Zeile `mode` mit `execute`/`design` neben dem Skill-Parameter `mode` | siehe L-02 |

Dreizehn Einträge. Sechs davon (F-01, F-06, F-08, F-10, F-12, F-13) sind Verstöße gegen bestehende Vorgaben — Umsetzung, die eine Vorgabe kennt und ihr widerspricht. Die übrigen sieben sind Inhalte ohne Vorgabe darüber: Ausarbeitungen, die plausibel sind und vielleicht richtig, deren Herkunft aber die Umsetzung selbst ist.

## Was dieses Dokument nicht tut

Es schließt keine Lücke und schlägt für keine eine Lösung vor. Es ordnet nicht an, was aus einer Fehlumsetzung werden soll. Es bewertet nicht, ob das Vorhaben in seiner Größe richtig ist — die Zahlen dazu stehen in der Sitzung vom 2026-10-04: rund 10 000 Token Zieltext, rund 70 000 Token Entwicklungsdoku, 1 278 Token in dem Abschnitt der globalen Anweisungsdatei, den der Skill ersetzt. Was daraus folgt, ist eine Entscheidung des Entwicklers.
