# 2 Vorgaben

Projektweite Festlegungen für alles, was in diesem Vorhaben entsteht: Regelteile, Skript, Hooks, Dokumentation. Aufnahmetest: Auf eine Datei muss sich zeigen lassen „das verletzt diese Vorgabe". Was so nicht prüfbar ist, gehört als Begründung nach Kapitel 1 oder als Detail nach Kapitel 3.

## 2.1 Sprache und Namen

Schlüsselwörter, Feldnamen, Rollen, Kommandos, Parameter und Dateinamen sind **englisch**. Die Prosa der Regelteile und dieser Doku ist deutsch. Ein Schlüsselwort ist ein Name, keine Beschreibung: Wer `decided` schreibt, meint genau diesen Zustand, und niemand darf `fixed`, `decided` und ein drittes Wort als persönliche Ausdrucksformen desselben Zustands lesen. Jeder Wert eines Feldes ist im Regelteil aufgezählt; ein nicht aufgezählter Wert ist ein Fehler, den das Skript meldet.

## 2.2 Die sieben Bedingungen

Jede einzeln fallen gelassen, holt das Softwareprojekt zurück, das dieses Vorhaben nicht sein will:

1. **Marke pflichtig am Definitionsort und dort, wo Text Fakten aus verschiedenen Definitionsorten in Beziehung setzt** (Rolle mit Funktion `relate`, Kapitel 3.3); sonst optional.
2. **Kapitel dürfen umnummeriert werden.** Nichts, was der Skill maschinell liest, hängt an einer Kapitelnummer oder einem Titel; IDs tragen kein Kapitel (Kapitel 3.2).
3. **Auswirkungskandidaten kommen aus dem Graphen** der Marken und aus Suchschlüsseln — Nähe im Text, Hops, Gewichte —, nie aus semantischer Suche (Kapitel 3.6).
4. **Struktur wird durch Hook und Lint auf dem Diff erzwungen**, nicht durch Erinnerung der Instanz (Kapitel 3.7).
5. **Änderungen werden über Erwähnungslisten und Fingerabdruck propagiert**, nicht über Vollabdeckung jeder Erwähnung mit Marken.
6. **Kein automatisches Umschreiben von Prosa.** Das Skript listet, die Instanz schlägt im Plan vor, der Entwickler gibt frei.
7. **Keine Oberfläche; keine Einbettung fremder Werkzeuge.** Ideen werden übernommen, Programme nicht.

## 2.3 Rollen statt Struktur

Was ein Abschnitt für den Skill bedeutet, sagt eine Rolle am Abschnitt (Kapitel 3.3). Kein Regelteil, kein Skript und kein Hook darf eine Funktion an eine Kapitelnummer, einen Dateinamen, ein Nummernpräfix oder einen Titel binden. Das alte Dreiersschema ist eine Empfehlung, die als Rollensatz ausgedrückt wird.

Im Dokument des Entwicklers stehen vom Skill nur Adressen: Marken an Festlegungen und Rollen an Überschriften. Keine Skill-Logik, kein Attribut, kein Zustand steht dort; was eine Marke oder eine Rolle bedeutet, steht ausschließlich im Register beziehungsweise im Skill. Prüfbar: Jede Zeile im Dokument, aus der ohne Register oder Skill eine Wirkung des Skills folgen würde, ist ein Verstoß.

## 2.4 Default, Meldung, Argument

Jede Voraussetzung eines Skripts — Registerort, Doku-Ordner, Dateien mit geplanten Schritten, Parameter — hat einen Default. Das Skript sucht den Default selbst. Findet es ihn nicht, meldet es exakt, wo es gesucht hat und mit welchem Argument der Aufrufer es beim nächsten Mal hinführt; dann hilft die Instanz dem Skript nach und ruft es erneut auf. Der Entwickler wird zu keiner Ablage gezwungen; wer vom Default abweicht, zahlt einen Zwischenschritt der Instanz, sonst nichts.

## 2.5 Jede Ausgabe ist eine Aussage

Ein Skript endet immer mit einer von vier Aussageklassen, an den Exit-Codes festgemacht (Kapitel 3.6): `OK` mit einem Satz, auch wenn nichts zu berichten ist; `FINDINGS` mit einer Zeile je Gegenstand, jede mit Befund und Vorschlag; `DECIDE` mit einer Entscheidungsvorlage, die als solche gekennzeichnet ist; `FAILED` mit Schritt, Ursache, Zustand zu diesem Zeitpunkt und Abhilfe einschließlich des exakten Arguments. Kein Fortschrittslog, kein Trace als Antwort, keine Zeile, die die Instanz interpretieren müsste, ohne dass eine Entscheidung daran hängt. Eine unbehandelte Ausnahme ist ein Defekt des Skripts; die Prüffälle enthalten absichtlich kaputte Eingaben, damit „keine Befunde" belegt ist und nicht behauptet.

## 2.6 Skripte entscheiden, was mechanisch entscheidbar ist

Was sich aus den Feldern und Dateien mechanisch ableiten lässt — die Härte, die nächste freie ID, ein Abgleich, eine Zählung —, entscheidet das Skript und gibt das Ergebnis als Fakt aus. Nur was sich nicht kodieren lässt, geht als `DECIDE` an die Instanz, und die Ausgabe trennt sichtbar, was Fakt ist und was Entscheidungsvorlage. Eine Vorlage nennt den Gegenstand, die Frage, die Optionen und den Vorschlag des Skripts.

## 2.7 Was kostet, sind Entscheidungen und Edits

Rechenzeit von Skripten und Hooks ist vernachlässigbar. Kosten entstehen, wenn die Instanz ein Skript starten und überwachen, eine Ausgabe zu einer Entscheidung verarbeiten, etwas formulieren oder eine Datei ändern muss — der Dateiedit ist der teuerste Vorgang. Daraus: ein Skriptaufruf je Anker, nicht mehrere; Ausgaben sind **entscheidungsfertig** — eine Zeile je Gegenstand mit der Stelle, an der die Instanz nur noch ja/nein oder einen Wert einträgt; das Gerüst des Planabschnitts liefert das Skript, nicht Rohdaten, aus denen die Instanz es baut.

> **[Q-01] Entscheidungsgrundlage — Wortlaut der Vorgaben 2.5 bis 2.7**
> Kontext: Die drei Vorgaben (Ausgabevertrag, mechanisch entscheiden, Kostenmodell) sind aus Deinen Hinweisen der letzten Runde formuliert und von Dir im Wortlaut nicht gesehen. Sie binden Kapitel 3.6 und 3.7.
> Optionen: (a) Wortlaut bestätigen; (b) einzelne Sätze ändern — welche?
> Vorschlag: (a).
> Gewicht: mittel · Blockiert: Fahrplanschritt 4
> Antwort:

## 2.8 Hooks sind nur lesend

Kein Hook ändert eine Datei. Hooks prüfen, melden und blockieren; das Ändern bleibt bei der Instanz nach Freigabe. Die einzige Blockade ist der Commit bei struktureller Inkonsistenz von Prosa und Register.

## 2.9 Parameter

Höchstens zwölf Parameter, jeder mit Standardwert. Fehlt die Parameterdatei, gilt in allem der Standard. Der Skillstart erfragt nur, was sich aus dem Projekt nicht ablesen lässt.

## 2.10 Fehlende Felder blockieren nie

Ein fehlendes Feld macht die Prüfung stumm, die es bräuchte; die Härteliste endet dann beim Auffangwert. Eine unmarkierte Doku ist kein Fehlerzustand, sondern der Anfangszustand jedes Projekts.

## 2.11 Annahmen machen nie `fixed`

Eine Festlegung wird nur dann unantastbar, wenn der Entwickler ihre Attribute bestätigt oder in einem freigegebenen Plan mitgetragen hat. Die Lesart der Instanz allein reicht dafür nie. Grund: Irrtümlich weich kostet einen Vorschlag; irrtümlich hart bringt das Fehlbild zurück, das dieses Vorhaben abschafft.

## 2.12 Lint nur auf dem Diff

Der Lint prüft geänderte Zeilen, nicht Dateien. Ein Fehlalarm erscheint genau einmal — beim Schreiben — und braucht keine Unterdrückungsliste.

## 2.13 Kein Zwang für den Entwickler

Alles, was der Entwickler über das Schreiben von Prosa, das Lesen von Plänen und das Antworten in Prosa hinaus tun müsste, ist ein Verstoß gegen dieses Vorhaben. Er muss weder die Grammatik der Marken noch die des Registers noch die Namen der Härtewerte kennen. Fragen an ihn tragen Anlass und Wortlaut der Festlegung und vermeiden das Vokabular des Skills.

## 2.14 Diese Doku wendet das Vorhaben nicht auf sich an

Bis zum Abschluss der Probe trägt diese Doku keine Marken, kein Register und keine Rollen; sie folgt dem bisherigen Schema. Wird das Vorhaben danach auf sich selbst angewendet, geschieht das als eigener Fahrplanschritt.
