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

**Die Vorgabe bleibt ausnahmslos** (entschieden am 2026-10-02). Der einzige Gegenstand, der über einen Dateinamen adressieren wollte, war das Umbauziel eines geplanten Schritts, wenn es einen ganzen Bereich nennt. Er tut es nicht mehr: Ein Bereich bekommt eine stabile Kennung in seinem Rollenmarker, und das Ziel nennt diese Kennung (Kapitel 1.7.3 und 3.3.2). Damit hängt nichts Maschinenlesbares mehr an Gliederung, Nummerierung oder Dateinamen — dieselbe Antwort wie beim verworfenen zweiten Ankermechanismus (Kapitel 1.3.3).

**Eine benannte Ausnahme gibt es doch, und sie steht hier, damit sie nicht stillschweigend bleibt:** Sind in einem Projekt mehrere Register im Spiel, trägt ein Umbauziel den Pfad des Registers als Qualifier (`rules-planning.de.md`). Das ist ein Dateiname. Er ist hinnehmbar, weil ein Register selten umbenannt wird, sein Pfad ohnehin in der Skill-Parameterdatei steht und ein Bruch nur die Zuordnung einer ID trifft, die das Skript dann exakt meldet — nicht die Identität einer Festlegung. Eine dritte Kennungsart dafür zu erfinden wäre teurer als der Fall wert ist.

## 2.4 Default, Meldung, Script-Argument

Jede Voraussetzung eines Skripts — Registerort, Doku-Ordner, Dateien mit geplanten Schritten, Skill-Parameter — hat einen Default. Das Skript sucht den Default selbst. Findet es ihn nicht, meldet es exakt, wo es gesucht hat und mit welchem Script-Argument der Aufrufer es beim nächsten Mal hinführt; dann hilft die Instanz dem Skript nach und ruft es erneut auf. Der Entwickler wird zu keiner Ablage gezwungen; wer vom Default abweicht, zahlt einen Zwischenschritt der Instanz, sonst nichts.

## 2.5 Jede Ausgabe ist eine Aussage

**Jede Ausgabe beginnt mit einer Kopfzeile, die den Ausgang des Laufs nennt und zählt, was folgt** (umgestellt am 2026-10-03). Vier Ausgänge gibt es: `OK`, wenn nichts zu tun ist — mit einem Satz, auch und gerade dann; `FINDINGS`, wenn Beanstandungen vorliegen; `DECIDE`, wenn ohne Beanstandung etwas zur Entscheidung vorgelegt wird; `FAILED` beim Abbruch, mit Schritt, Ursache, Zustand zu diesem Zeitpunkt und Abhilfe einschließlich des exakten Script-Arguments. Die drei ersten tragen die Zahlen mit: wie viele Gegenstände, wie viele Beanstandungen, wie viele Vorlagen folgen.

**Die Kopfzeile steht vorn, nicht hinten**, weil die Instanz nach der ersten Zeile wissen soll, ob und was sie weiterlesen muss. Das Skript rechnet umsonst, die Instanz nicht (2.7).

**Darunter folgen die Einzelheiten**, je Zeile ein Gegenstand: ein gelisteter Fakt, eine Beanstandung mit Vorschlag, eine Entscheidungsvorlage. Welche Zeilenarten es gibt und welche Felder sie tragen, steht in Kapitel 3.6.3. Der Plural gehört der Kopfzeile, der Singular der Einzelzeile — `FINDINGS` zählt, `FINDING` benennt. Kein Fortschrittslog, kein Trace als Antwort, keine Zeile, die die Instanz interpretieren müsste, ohne dass eine Entscheidung daran hängt. Eine unbehandelte Ausnahme ist ein Defekt des Skripts; die Prüffälle enthalten absichtlich kaputte Eingaben, damit „keine Befunde" belegt ist und nicht behauptet.

**Begründung:** Ein Script ist rein logische Mechanik. Es kann nur definierte Zustände durchlaufen. Für jeden dieser Zustände ist eine Beschreibung nur einmalig beim Kodieren mit einem verständlichen Text als Zeichenkette zu versehen. Auf die Abarbeitung sind Computer spezialisiert und sie führen diese extrem effizient aus. Wird dabei ein Zustand nicht (nur dieses eine Mal beim Kodieren) mit einer aussagekräftigen Zeichenkette belegt, muss die Instanz eines LLM, die dieses Script startet und gezwungen ist, die Antwort des Scripts zu interpretieren, jedes Mal neu in mehreren Schritten die Situation analysieren, gegebenenfalls weitere Prüfungen ausführen, Informationen über das Script aus seinem Quellcode heraus holen und alles so vollständig analysieren, um klar zu entscheiden. Dieser Vorgang ist im Vergleich zu einem Script, indem vielleicht nur ein paar Byte für eine gut beschreibende Zeichenkette fehlen, ein unbeschreiblich (sinnloser) Ressourcenaufwand: kostet **extrem viel mehr** Zeit, Energie und damit auch Geld.

**Offen ist die Form, nicht der Inhalt.** Diese Vorgabe regelt, *was* eine Ausgabe sagt; in welcher Schreibweise sie es sagt, ist damit nicht entschieden, und beide denkbaren erfüllen sie gleichermaßen. Eine Zeile mit Trennzeichen und benannten Feldern ist kürzer, und jede Ausgabe wird von einer Instanz gelesen, die für jedes Zeichen zahlt (2.7). Eine strukturierte Ausgabe ist dafür eindeutig und zerbricht an keinem Sonderzeichen im Text. Entschärft wird die Frage dadurch, dass beide Formen ohnehin gebraucht werden: Ein Hook kann seine Befunde nur strukturiert übergeben, weil die Engine sie so erwartet (Kapitel 3.7). Zu entscheiden bleibt allein, welche der beiden der Standard ist — und weil es dabei um Lesekosten geht, lässt sich das messen, statt es zu schätzen (Kapitel 1.9).
 
## 2.6 Skripte entscheiden, was mechanisch entscheidbar ist

Was sich aus den Feldern und Dateien mechanisch ableiten lässt — die Härte, die nächste freie ID, ein Abgleich, eine Zählung —, entscheidet das Skript und gibt das Ergebnis als Fakt aus. Nur was sich nicht kodieren lässt, geht als `DECIDE` an die Instanz, und die Ausgabe trennt sichtbar, was Fakt ist und was Entscheidungsvorlage. Eine Vorlage nennt den Gegenstand, die Frage, die Optionen und den Vorschlag des Skripts.

**Daraus folgt, was im Skilltext nicht stehen darf** (entschieden am 2026-10-03): **Kein Regelteil erzählt eine Mechanik nach, die ein Kommando ausführt.** Wo das Skript rechnet, liefert es den fertigen Satz, und der Regeltext sagt nur, was die Instanz mit der Antwort tut. Die Rechenvorschrift selbst gehört in die Doku — sie ist die Spezifikation des Kommandos und wird dort gebraucht, um es zu bauen und seine Richtigkeit zu prüfen, aber nicht zur Laufzeit.

Der Grund ist nicht nur der Kontext, den eine Nacherzählung kostet. Sie schafft **eine zweite Autorität für eine Frage, die bereits einen Zuständigen hat.** Rechnet das Skript nach der einen Fassung und liest die Instanz die andere, bekommt sie zwei Antworten auf dieselbe Frage und keine Regel, welcher sie glauben soll — sie wird eine wählen, stillschweigend, und niemand erfährt davon. Ein solcher Zustand entsteht nicht durch Nachlässigkeit, sondern durch jede Änderung, die nur eine der beiden Stellen erreicht.

Prüfbar: Auf jeden Abschnitt eines Regelteils, der eine Berechnung, eine Suchreihenfolge, eine Vergaberegel oder ein Dateiformat beschreibt, das ein Kommando erzeugt, lässt sich zeigen — das ist der Verstoß. Die Abgrenzung verläuft nicht am Thema, sondern an der Frage, wer rechnet: „Die erste zutreffende Prüfung bestimmt die Härte" ist Rechenvorschrift und gehört ins Skript; „fehlende Felder blockieren nie" ist eine Verhaltensregel für den Fall, dass das Skript nichts liefert, und bleibt im Regelteil.

## 2.7 Was kostet, sind Entscheidungen und Edits

Rechenzeit von Skripten und Hooks ist vernachlässigbar. Kosten entstehen, wenn die Instanz ein Skript starten und überwachen, eine Ausgabe zu einer Entscheidung verarbeiten, etwas formulieren oder eine Datei ändern muss — der Dateiedit ist der teuerste Vorgang. Daraus: ein Skriptaufruf je Anker, nicht mehrere; Ausgaben sind **entscheidungsfertig** — eine Zeile je Gegenstand mit der Stelle, an der die Instanz nur noch ja/nein oder einen Wert einträgt; das Gerüst des Planabschnitts liefert das Skript, nicht Rohdaten, aus denen die Instanz es baut.

Noch allgemeiner formuliert: Das, was sich mechanisch-logisch an Arbeit bündeln lässt und zwischen drinnen der Instanz für einen Entscheidungsprozess vorgelegt werden muss, um die mechanisch-logische Arbeit fortzusetzen, wird so in Scripts verpackt, dass die Aufrufhäufigkeit durch die Instanz minimiert wird. Lassen sich auf diese Weise Ergebnisse, die der Instanz vorgelegt werden sollen, bündeln, dann soll der Instanz dieses Bündel in geeigneter Form strukturiert nach einem Scriptablauf vorgelegt werden, anstatt von der Instanz für jedes Element dieses Bündels das Script erneut starten zu lassen.

## 2.8 Hooks sind nur lesend

Kein Hook ändert eine Datei des Projekts — nicht die Doku, nicht das Register, nicht den Code. Hooks prüfen, melden und blockieren; das Ändern bleibt bei der Instanz nach Freigabe. Was ein Hook außerhalb des Projekts für die Dauer der Sitzung notiert, um sich einen eigenen Lauf zu merken, fällt nicht darunter (Kapitel 3.6.2); es trägt keinen Inhalt und überlebt die Sitzung nicht. Die einzige Blockade ist der Commit bei struktureller Inkonsistenz von Prosa und Register.

**Die Blockade ist je Commit aufhebbar, und die Aufhebung hinterlässt eine Notiz** (entschieden am 2026-09-25). Aufheben kann sie nur der Entwickler durch eine ausdrückliche Äußerung; die Instanz setzt sie nie aus eigenem Antrieb, sondern legt dar, was gefunden wurde, und fragt. Der Commit trägt dann eine Notiz nach Kapitel 3.2.9, die benennt, was offenblieb. Prüfbar: Ein Commit, der eine strukturelle Inkonsistenz mitnimmt und keine Notiz trägt, ist ein Verstoß; ebenso eine Aufhebung, für die es keine Äußerung des Entwicklers gibt. Die Begründung — dass diese Blockade die Instanz diszipliniert und nicht den Entwickler — steht in Kapitel 1.3.5.

## 2.9 Skill-Parameter

Skill-Parameter sind die Parameter der Projektkonfiguration des Skills; sie stehen in der **Skill-Parameterdatei** (Standardname `.claude/software-design-doc.json`) und gelten je Projekt. Sie umfassen Festlegungen (`mode`, `marking`) ebenso wie Schwellen (`friction_threshold`).

Jeder Skill-Parameter hat einen Standardwert; fehlt die Datei, gilt in allem der Standard. **Ein Projekt muss nie konfigurieren, um den Skill zu benutzen.** Der Skillstart erfragt nur, was sich aus dem Projekt nicht ablesen lässt.

**B-05 erledigt (2026-10-03): Der Befund trug nicht, und zwar zweimal nicht.** Er hatte behauptet, `mode` habe keinen Standard**wert**, sondern ein Standard**verhalten**, und `doc_dir` und `planned_steps` trügen mit „abgelesen" eine Anweisung statt eines Werts. Beide Male war das ein Lesefehler: „Standardwert" wurde als „sinnvoller Betriebswert" gelesen, und deshalb nicht gesehen, dass `null` und die leere Liste Werte sind — und zwar genau die richtigen, weil sie eindeutig sagen „noch keiner vergeben". Ein Rückfallwert wird gebraucht, wenn am Ende der Ermittlung immer noch offen ist, was gilt; dass die Ermittlung danach einen echten Wert einträgt, macht den Rückfallwert nicht überflüssig, sondern ist genau sein Zweck. Damit hat jeder der elf Skill-Parameter einen Standardwert, und der erste Satz oben bleibt unverändert gültig. Auch der Zwischenvorschlag, einen Wert `auto` einzuführen, entfällt: Er hätte dem Nichtvorhandensein einen zweiten Namen gegeben, den `null` bereits trägt.

**Zwei Fehler hat die Prüfung dabei gefunden, nur andere als behauptet.** Der Tabelleneintrag von `mode` lautete „erfragt" und war seit dem 2026-10-02 überholt — seither wird nicht beim Laden gefragt, sondern am ersten Anlass (vormals Q-15). Die Standardspalte trägt jetzt `null`, `null` und `[]`. In Kapitel 1.7.7 und in `SKILL.de.md` war der Zeitpunkt bereits richtig beschrieben; dort kam nur hinzu, dass `null` als ausgeschriebener Wert dem fehlenden Feld gleichsteht — ohne das fiele ein Projekt, das ihn notiert hat, durch beide Prüfungen hindurch. Der zweite Fehler steckte im Aufnahmetest unten und ist dort behandelt.

**Aufnahmetest für einen neuen Skill-Parameter:** Er ist nur berechtigt, wenn beides gilt — es lohnt sich, den Wert zu **behalten**, statt ihn bei jedem Skillstart neu zu beschaffen, **und** es lassen sich zumindest theoretisch zwei Projekte, Projekt-Ausprägungen nennen, die ihn verschieden setzen würden. Trifft eines von beiden nicht zu, ist es keiner: Was überall gleich wäre, wird entschieden und steht im Regelteil oder als Konstante im Skript.

**Dass ein Wert sich ablesen lässt, schließt ihn nicht aus** (bis zum 2026-10-03 lautete die erste Bedingung genau umgekehrt, was den Doku-Ordner ausgeschlossen hätte — einen Parameter, der seit jeher zu Recht in der Liste steht). Zu behalten lohnt sich ein Wert aus zwei Gründen: weil seine Beschaffung teuer ist, oder weil sie mehrdeutig ausgehen und eine Entscheidung des Entwicklers verlangen kann, die nicht bei jedem Start erneut fällig werden darf. Beides trifft auf `doc_dir` zu: Ein Dateibaum ist zu durchsuchen, und zwei Ordner mit Rollenmarkern lassen sich nicht mechanisch auflösen. Auf das Absatzlayout der Prosa trifft keines von beiden zu, obwohl zwei Projekte es durchaus verschieden halten — man sieht es beim Lesen der Doku ohnehin. Deshalb ist es kein Skill-Parameter (vormals Q-17, entschieden am 2026-09-25); die zweite Bedingung allein hätte das nicht hergegeben.

Jeder Skill-Parameter kostet dreifach: eine Entscheidung des Entwicklers, eine Zeile Kontext bei jedem Skillstart, einen Verzweigungspfad im Skript. Wächst die Liste über etwa ein Dutzend, ist das kein Verstoß, aber ein Anlass zur Durchsicht — ein Zeichen, dass Entscheidungen als Parameter ausgelagert wurden, statt getroffen zu werden.

## 2.10 Felder: was der Skill liest

**Ein Feld ist ein Bereich, der ausgefüllt wird — und zwar nicht vom Schreibenden selbst, sondern vom Werkzeug.** In diesem Sinn kennt der Skill vier Sorten, und jede wird beim Namen genannt, wo sie vorkommt:

| Sorte | Was darin steht | Wo |
|---|---|---|
| **Marker-Feld**, kurz **Marker** | eine Adresse: `[D-0042]`, `[>D-0042]`, `[DS:runtime]` | Prosa des Entwicklers (3.2, 3.3) |
| **Registerfeld** | `kind`, `reason`, `source`, `instead`, `status`, `pinned`, `keys`, `fp` sowie die Ereigniszeilen | Register (3.2.5) |
| **Skill-Parameter** | Projektkonfiguration | Skill-Parameterdatei (2.9) |
| **Ausgabefeld** | `subject`, `issue`, `proposal`, … | Ausgabe des Skripts (3.6.3) |

Dazu das **Umbauziel** `target:` als Feld eines geplanten Schritts (`rules-planning.de.md`).

**Fehlende Felder blockieren nie.** Ein fehlendes Feld macht die Prüfung stumm, die es bräuchte; die Härteliste endet dann beim Auffangwert. Eine Doku ohne Marker ist kein Fehlerzustand, sondern der Anfangszustand jedes Projekts.

## 2.11 Annahmen machen nie `fixed`

Eine Festlegung wird nur dann unantastbar, wenn der Entwickler ihre Attribute bestätigt oder in einem freigegebenen Plan mitgetragen hat. Die Lesart der Instanz allein reicht dafür nie. Grund: Irrtümlich weich kostet einen Vorschlag; irrtümlich hart bringt das Fehlbild zurück, das dieses Vorhaben abschafft.

## 2.12 Lint nur auf dem Diff

Der Lint prüft geänderte Zeilen, nicht Dateien. Ein Fehlalarm erscheint genau einmal — beim Schreiben — und braucht keine Unterdrückungsliste.

## 2.13 Kein Zwang für den Entwickler

Alles, was der Entwickler über das Schreiben von Prosa, das Lesen von Plänen und das Antworten in Prosa hinaus tun müsste, ist ein Verstoß gegen dieses Vorhaben. Er muss weder die Grammatik der Marker noch die des Registers noch die Namen der Härtewerte kennen. Fragen an ihn tragen Anlass und Wortlaut der Festlegung und vermeiden das Vokabular des Skills.

## 2.14 Diese Doku wendet das Vorhaben nicht auf sich an

Bis zum Abschluss der Probe trägt diese Doku keine Marker, kein Register und keine Rollen; sie folgt dem bisherigen Schema. Wird das Vorhaben danach auf sich selbst angewendet, geschieht das als eigener Fahrplanschritt.

## 2.15 Der Ladebaum des Skills

Der Skilltext liegt in mehreren Dateien, und der einzige Grund dafür ist der Kontext: Was in einer Sitzung nicht gebraucht wird, soll ihn nicht kosten und nicht stören. Daraus folgen vier Festlegungen (2026-10-03).

**Der Baum verzweigt von der Wurzel.** Die `SKILL`-Datei lädt die Zweige; **kein Zweig lädt einen anderen**. Quer über die Dateien zu laden macht unvorhersehbar, was im Kontext steht, und erzeugt denselben Inhalt mehrfach.

**Die Wurzel bleibt dünn, weil jedes Projekt sie zahlt** — auch das, in dem der Skill nach dem ersten Satz endet, und auch das, in dem gar keine Software entsteht. Was dort steht, ist der Ablauf und sonst nichts; jede Regel, jede Liste, jede Tabelle gehört in einen Zweig. Die Entscheidungen des Ablaufs selbst, soweit sie mechanisch sind, trifft ein Kommando und nicht ein beschriebenes Prüfverfahren.

**Die Reihenfolge der Abbrüche ist die der Kosten.** Was ohne Rückfrage entschieden werden kann, wird zuerst entschieden; alles, wofür der Entwickler gefragt werden muss, kommt danach. So endet ein Projekt, das den Skill nicht braucht, bevor irgendjemand etwas beantworten muss.

**Ein Zweig lohnt sich nur, wenn seine Ladebedingung an einem benennbaren Anlass hängt**, nicht an einer Einschätzung. Eine weiche Bedingung — „wenn eine Frage zur Methodik ansteht" — führt dazu, dass im Zweifel geladen wird und die Ersparnis entfällt, oder dass nicht geladen wird und eine Regel fehlt. Trennscharf sind Anlässe wie „die Parameterdatei fehlt" oder „ein freigegebener Plan wird ausgeführt".

**Laden und Verweisen sind zweierlei.** Ein Ladebefehl steht nur an der Stelle, die ihn auslöst, und er lädt nur, was noch nicht geladen ist. Jede weitere Regel, die denselben Inhalt braucht, **verweist** darauf, statt ihn erneut zu holen — sonst steht dieselbe Tabelle mehrfach im Kontext, teurer als gar keine Aufteilung und für die Instanz verwirrend, weil sie zwei Fundstellen sieht und nicht weiß, ob sie übereinstimmen.

Prüfbar: Auf jeden Zweig, der einen anderen lädt, auf jede Regel in der Wurzel, auf jede Ladebedingung, die ein Urteil statt eines Anlasses nennt, und auf jeden zweiten Ladebefehl für denselben Inhalt lässt sich zeigen — das sind die Verstöße.

## 2.16 Adressierung im Zieltext

Damit eine Regel auf eine andere Stelle des Skilltextes zeigen kann, braucht diese Stelle eine Adresse (2026-10-03).

**Abschnitte des Zieltextes tragen durchlaufende Nummern.** Eine nummerierte Überschrift ist die robusteste Adresse, die Markdown hergibt: Sie bezeichnet nicht nur den Anfang, sondern auch das Ende — die nächste Überschrift gleicher oder höherer Ordnung —, sie ist für Mensch und Maschine gleich lesbar, und sie wandert beim Verschieben mit ihrem Text.

**Eine Tabelle, auf die verwiesen wird, trägt eine eigene Überschriftszeile mit Namen**, weil die Abschnittsüberschrift sie nicht genau genug trifft, wenn im Abschnitt auch anderes steht.

Diese Nummerierung gehört dem Zieltext und ist von der Nummerierung dieser Doku unabhängig; die beiden werden nie gegeneinander verwiesen. Ein Verweis aus einem Zieltext auf diese Doku ist ohnehin ausgeschlossen — beim Nutzer existiert sie nicht.
