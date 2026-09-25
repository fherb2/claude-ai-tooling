# 2 Vorgaben

Projektweite Festlegungen für alles, was in diesem Vorhaben entsteht: Regelteile, Skript, Hooks, Dokumentation. Aufnahmetest: Auf eine Datei muss sich zeigen lassen „das verletzt diese Vorgabe". Was so nicht prüfbar ist, gehört als Begründung nach Kapitel 1 oder als Detail nach Kapitel 3.

## 2.1 Sprache und Namen

Schlüsselwörter, Feldnamen, Rollen, Kommandos, Script-Argumente, Skill-Parameter und Dateinamen sind **englisch**. Die Prosa der Regelteile ist deutsch und wird danach auch in englisch als separate Distribution (Zip-File) zur Verfügung gestellt. Diese Doku ist deutsch. Ein Schlüsselwort ist ein Name, keine Beschreibung: Wer `decided` schreibt, meint genau diesen Zustand, und niemand darf `fixed`, `decided` und ein drittes Wort als persönliche Ausdrucksformen desselben Zustands lesen. Jeder Wert eines Feldes ist im Regelteil aufgezählt; ein nicht aufgezählter Wert ist ein Fehler, den das Skript meldet.

## 2.2 Die sieben Bedingungen

Diese sieben Bedingungen halten das Vorhaben auf der Größe „ein Skill, ein Skript". Wird auch nur eine von ihnen fallen gelassen, würde es zurückwachsen: zu dem großen Softwareprojekt, das Kapitel 1.10 ausschließt — einer Editor-Erweiterung für maschinell unterstützte Softwareplanung. Jede Bedingung nennt deshalb, was ohne sie nötig würde.

1. **Marker pflichtig am Definitionsort und dort, wo Text Fakten aus verschiedenen Definitionsorten in Beziehung setzt** (Rolle mit Funktion `relate`, Kapitel 1.3.3); sonst optional — ohne diese Grenze müsste jede Erwähnung eines Fakts markiert und bei jeder Änderung nachgeführt werden, und das ist ohne Werkzeugunterstützung im Editor nicht zu leisten.
2. **Kapitel dürfen umnummeriert werden.** Nichts, was der Skill maschinell liest, hängt an einer Kapitelnummer oder einem Titel; IDs tragen kein Kapitel (Kapitel 3.2) — sonst zöge jedes Einfügen und Umsortieren eine Neuvergabe von Adressen über das ganze Dokument nach sich.
3. **Auswirkungskandidaten kommen aus dem Graphen** der Marker und aus Suchschlüsseln — Nähe im Text, Hops, Gewichte —, nie aus semantischer Suche (Kapitel 3.6) — sonst braucht das Vorhaben Einbettungen, ein Modell und einen Index, also eine eigene Infrastruktur je Projekt.
4. **Struktur wird durch Hook und Lint auf dem Diff erzwungen**, nicht durch Erinnerung der Instanz (Kapitel 3.7) — sonst hinge die Vollständigkeit des Registers an einer Eigenschaft, von der Kapitel 1.2 belegt, dass sie nicht trägt.
5. **Änderungen werden über Erwähnungslisten und Fingerabdruck propagiert**, nicht über Vollabdeckung jeder Erwähnung mit Markern — sonst gilt für jede Änderung, was Bedingung 1 für das Schreiben ausschließt.
6. **Kein automatisches Umschreiben von Prosa.** Das Skript listet, die Instanz schlägt im Plan vor, der Entwickler gibt frei — sonst bräuchte es eine verlässliche Texttransformation samt Vorschau und Rücknahme, und der Entwickler verlöre die Hoheit über seine Doku.
7. **Keine Oberfläche; keine Einbettung fremder Werkzeuge.** Ideen werden übernommen, Programme nicht — sonst entstehen eine Editor-Erweiterung mit eigenem Lebenszyklus und eine Laufzeitabhängigkeit in jedem Zielprojekt.

## 2.3 Rollen statt Struktur

Was ein Abschnitt für den Skill bedeutet, sagt eine Rolle am Abschnitt (Kapitel 1.3.3). Kein Regelteil, kein Skript und kein Hook darf eine Funktion an eine Kapitelnummer, einen Dateinamen, ein Nummernpräfix oder einen Titel binden. Das Dreiersschema des Vorläufers (Anhang A) ist eine Empfehlung, die als Rollensatz ausgedrückt wird.

Im Dokument des Entwicklers stehen vom Skill nur Adressen: Marker an Festlegungen und Rollen an Überschriften oder Absätzen. Keine Skill-Logik, kein Attribut, kein Zustand steht dort; was ein Marker oder eine Rolle bedeutet, steht ausschließlich im Register beziehungsweise im Skill. Prüfbar: Jede Zeile im Dokument, aus der ohne Register oder Skill eine Wirkung des Skills folgen würde, ist ein Verstoß.

**Eine Ausnahme steht zur Entscheidung.** Genau ein Gegenstand des Verfahrens möchte über einen Dateinamen adressieren: das Umbauziel eines geplanten Schritts, wenn es einen ganzen Bereich statt einzelner Festlegungen nennt (Kapitel 1.7.3). Damit steht diese Vorgabe an einer Gabelung. Bleibt sie ausnahmslos, muss das Bereichsziel ohne Dateinamen auskommen — über eine eigene stabile Kennung oder gar nicht. Trägt sie die Ausnahme benannt, bleibt sie prüfbar, ist aber nicht mehr ausnahmslos, und jede weitere Ausnahme wird sich an dieser messen. Was nicht geht, ist die stillschweigende Ausnahme: Sie liest sich für jeden späteren Review als Verstoß, und zwar zu Recht.

## 2.4 Default, Meldung, Script-Argument

Jede Voraussetzung eines Skripts — Registerort, Doku-Ordner, Dateien mit geplanten Schritten, Skill-Parameter — hat einen Default. Das Skript sucht den Default selbst. Findet es ihn nicht, meldet es exakt, wo es gesucht hat und mit welchem Script-Argument der Aufrufer es beim nächsten Mal hinführt; dann hilft die Instanz dem Skript nach und ruft es erneut auf. Der Entwickler wird zu keiner Ablage gezwungen; wer vom Default abweicht, zahlt einen Zwischenschritt der Instanz, sonst nichts.

## 2.5 Jede Ausgabe ist eine Aussage

Ein Skript endet immer mit einer von vier Aussageklassen, an den Exit-Codes festgemacht (Kapitel 3.6): `OK` mit einem Satz, auch wenn nichts zu berichten ist; `FINDINGS` mit einer Zeile je Gegenstand, jede mit Befund und Vorschlag; `DECIDE` mit einer Entscheidungsvorlage, die als solche gekennzeichnet ist; `FAILED` mit Schritt, Ursache, Zustand zu diesem Zeitpunkt und Abhilfe einschließlich des exakten Script-Arguments. Kein Fortschrittslog, kein Trace als Antwort, keine Zeile, die die Instanz interpretieren müsste, ohne dass eine Entscheidung daran hängt. Eine unbehandelte Ausnahme ist ein Defekt des Skripts; die Prüffälle enthalten absichtlich kaputte Eingaben, damit „keine Befunde" belegt ist und nicht behauptet.

**Begründung:** Ein Script ist rein logische Mechanik. Es kann nur definierte Zustände durchlaufen. Für jeden dieser Zustände ist eine Beschreibung nur einmalig beim Kodieren mit einem verständlichen Text als Zeichenkette zu versehen. Auf die Abarbeitung sind Computer spezialisiert und sie führen diese extrem effizient aus. Wird dabei ein Zustand nicht (nur dieses eine Mal beim Kodieren) mit einer aussagekräftigen Zeichenkette belegt, muss die Instanz eines LLM, die dieses Script startet und gezwungen ist, die Antwort des Scripts zu interpretieren, jedes Mal neu in mehreren Schritten die Situation analysieren, gegebenenfalls weitere Prüfungen ausführen, Informationen über das Script aus seinem Quellcode heraus holen und alles so vollständig analysieren, um klar zu entscheiden. Dieser Vorgang ist im Vergleich zu einem Script, indem vielleicht nur ein paar Byte für eine gut beschreibende Zeichenkette fehlen, ein unbeschreiblich (sinnloser) Ressourcenaufwand: kostet **extrem viel mehr** Zeit, Energie und damit auch Geld.

**Offen ist die Form, nicht der Inhalt.** Diese Vorgabe regelt, *was* eine Ausgabe sagt; in welcher Schreibweise sie es sagt, ist damit nicht entschieden, und beide denkbaren erfüllen sie gleichermaßen. Eine Zeile mit Trennzeichen und benannten Feldern ist kürzer, und jede Ausgabe wird von einer Instanz gelesen, die für jedes Zeichen zahlt (2.7). Eine strukturierte Ausgabe ist dafür eindeutig und zerbricht an keinem Sonderzeichen im Text. Entschärft wird die Frage dadurch, dass beide Formen ohnehin gebraucht werden: Ein Hook kann seine Befunde nur strukturiert übergeben, weil die Engine sie so erwartet (Kapitel 3.7). Zu entscheiden bleibt allein, welche der beiden der Standard ist — und weil es dabei um Lesekosten geht, lässt sich das messen, statt es zu schätzen (Kapitel 1.9).
 
## 2.6 Skripte entscheiden, was mechanisch entscheidbar ist

Was sich aus den Feldern und Dateien mechanisch ableiten lässt — die Härte, die nächste freie ID, ein Abgleich, eine Zählung —, entscheidet das Skript und gibt das Ergebnis als Fakt aus. Nur was sich nicht kodieren lässt, geht als `DECIDE` an die Instanz, und die Ausgabe trennt sichtbar, was Fakt ist und was Entscheidungsvorlage. Eine Vorlage nennt den Gegenstand, die Frage, die Optionen und den Vorschlag des Skripts.

## 2.7 Was kostet, sind Entscheidungen und Edits

Rechenzeit von Skripten und Hooks ist vernachlässigbar. Kosten entstehen, wenn die Instanz ein Skript starten und überwachen, eine Ausgabe zu einer Entscheidung verarbeiten, etwas formulieren oder eine Datei ändern muss — der Dateiedit ist der teuerste Vorgang. Daraus: ein Skriptaufruf je Anker, nicht mehrere; Ausgaben sind **entscheidungsfertig** — eine Zeile je Gegenstand mit der Stelle, an der die Instanz nur noch ja/nein oder einen Wert einträgt; das Gerüst des Planabschnitts liefert das Skript, nicht Rohdaten, aus denen die Instanz es baut.

Noch allgemeiner formuliert: Das, was sich mechanisch-logisch an Arbeit bündeln lässt und zwischen drinnen der Instanz für einen Entscheidungsprozess vorgelegt werden muss, um die mechanisch-logische Arbeit fortzusetzen, wird so in Scripts verpackt, dass die Aufrufhäufigkeit durch die Instanz minimiert wird. Lassen sich auf diese Weise Ergebnisse, die der Instanz vorgelegt werden sollen, bündeln, dann soll der Instanz dieses Bündel in geeigneter Form strukturiert nach einem Scriptablauf vorgelegt werden, anstatt von der Instanz für jedes Element dieses Bündels das Script erneut starten zu lassen.

## 2.8 Hooks sind nur lesend

Kein Hook ändert eine Datei. Hooks prüfen, melden und blockieren; das Ändern bleibt bei der Instanz nach Freigabe. Die einzige Blockade ist der Commit bei struktureller Inkonsistenz von Prosa und Register.

## 2.9 Skill-Parameter

Skill-Parameter sind die Parameter der Projektkonfiguration des Skills; sie stehen in der **Skill-Parameterdatei** (Standardname `.claude/software-design-doc.json`) und gelten je Projekt. Sie umfassen Festlegungen (`mode`, `marking`) ebenso wie Schwellen (`friction_threshold`).

Jeder Skill-Parameter hat einen Standardwert; fehlt die Datei, gilt in allem der Standard. **Ein Projekt muss nie konfigurieren, um den Skill zu benutzen.** Der Skillstart erfragt nur, was sich aus dem Projekt nicht ablesen lässt.

**Aufnahmetest für einen neuen Skill-Parameter:** Er ist nur berechtigt, wenn beides gilt — der Wert lässt sich aus dem Projekt nicht ablesen, **und** es lassen sich zumindest theoretisch zwei Projekte, Projekt-Ausprägungen nennen, die ihn verschieden setzen würden. Trifft eines von beiden nicht zu, ist es keiner: Was ablesbar ist, wird abgelesen; was überall gleich wäre, wird entschieden und steht im Regelteil oder als Konstante im Skript.

Jeder Skill-Parameter kostet dreifach: eine Entscheidung des Entwicklers, eine Zeile Kontext bei jedem Skillstart, einen Verzweigungspfad im Skript. Wächst die Liste über etwa ein Dutzend, ist das kein Verstoß, aber ein Anlass zur Durchsicht — ein Zeichen, dass Entscheidungen als Parameter ausgelagert wurden, statt getroffen zu werden.

## 2.10 Felder: was der Skill liest

**Ein Feld ist ein Bereich, der ausgefüllt wird — und zwar nicht vom Schreibenden selbst, sondern vom Werkzeug.** In diesem Sinn kennt der Skill vier Sorten, und jede wird beim Namen genannt, wo sie vorkommt:

| Sorte | Was darin steht | Wo |
|---|---|---|
| **Marker-Feld**, kurz **Marker** | eine Adresse: `[D-0042]`, `[>D-0042]`, `[DS:runtime]` | Prosa des Entwicklers (3.2, 3.3) |
| **Registerfeld** | `kind`, `reason`, `source`, `instead`, `status`, `pinned`, `keys`, `fp` sowie die Ereigniszeilen | Register (3.2.5) |
| **Skill-Parameter** | Projektkonfiguration | Skill-Parameterdatei (2.9) |
| **Ausgabefeld** | `subject`, `issue`, `proposal`, … | Ausgabe des Skripts (3.6.3) |

Dazu das **Umbauziel** `target:` als Feld eines geplanten Schritts (3.4.2).

**Fehlende Felder blockieren nie.** Ein fehlendes Feld macht die Prüfung stumm, die es bräuchte; die Härteliste endet dann beim Auffangwert. Eine Doku ohne Marker ist kein Fehlerzustand, sondern der Anfangszustand jedes Projekts.

## 2.11 Annahmen machen nie `fixed`

Eine Festlegung wird nur dann unantastbar, wenn der Entwickler ihre Attribute bestätigt oder in einem freigegebenen Plan mitgetragen hat. Die Lesart der Instanz allein reicht dafür nie. Grund: Irrtümlich weich kostet einen Vorschlag; irrtümlich hart bringt das Fehlbild zurück, das dieses Vorhaben abschafft.

## 2.12 Lint nur auf dem Diff

Der Lint prüft geänderte Zeilen, nicht Dateien. Ein Fehlalarm erscheint genau einmal — beim Schreiben — und braucht keine Unterdrückungsliste.

## 2.13 Kein Zwang für den Entwickler

Alles, was der Entwickler über das Schreiben von Prosa, das Lesen von Plänen und das Antworten in Prosa hinaus tun müsste, ist ein Verstoß gegen dieses Vorhaben. Er muss weder die Grammatik der Marker noch die des Registers noch die Namen der Härtewerte kennen. Fragen an ihn tragen Anlass und Wortlaut der Festlegung und vermeiden das Vokabular des Skills.

## 2.14 Diese Doku wendet das Vorhaben nicht auf sich an

Bis zum Abschluss der Probe trägt diese Doku keine Marker, kein Register und keine Rollen; sie folgt dem bisherigen Schema. Wird das Vorhaben danach auf sich selbst angewendet, geschieht das als eigener Fahrplanschritt.
