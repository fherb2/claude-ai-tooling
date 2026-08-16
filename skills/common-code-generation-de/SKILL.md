---
name: common-code-generation-de
description: Regeln für das Erzeugen und Ändern von Code — englische Benennungen, kein ungefragt erweiterter Funktionsumfang, sparsamer Umgang mit Rechenzeit und Speicher; Benennungen und Optimierungen werden vorgeschlagen, nicht entschieden. Verwenden, bevor in einer Sitzung zum ersten Mal Code entsteht oder geändert wird oder eine Optimierung vorgeschlagen wird, oder wenn der Nutzer /common-code-generation-de aufruft.
license: CC0-1.0
---

# Allgemeine Regeln für das Erzeugen von Code

## Geltung und Abgrenzung

Diese Regeln gelten, sobald in einer Sitzung Code entsteht oder geändert wird — und von da an durchgehend, nicht nur für den Schritt, der sie ausgelöst hat.

Nicht Gegenstand dieser Regeln:

- Die Pflicht, vor einer Dateiänderung einen Plan vorzulegen und die Zustimmung abzuwarten. Sie gehört in die `CLAUDE.md` des Projekts und bleibt dort: Ein Skill wird nur wahrscheinlich geladen, eine Schutzregel muss sicher greifen.
- Der Aufbau von Konzept- und Implementierungsdokumentation sowie der Umgang mit temporärem Debug-Code. Dafür gibt es eigene Skills.

## Sprache und Benennungen im Quelltext

Alles, was im Quelltext steht — Bezeichner, Kommentare und Docstrings —, schreibst Du auf Englisch.

Wenn Du Codebestandteile selbst benennst, dann:

- schlage sie dem Nutzer zur Entscheidung in übersichtlicher Form vor
- kurze, inhaltlich treffende Begriffe sind besser als lange Begriffe
- baue "sprechenden Code", soweit das die Styling-Vorgaben erlauben
- beachte immer die jeweiligen Code-Styling-Vorgaben als primär geltend und mache den Nutzer darauf aufmerksam, wenn er das durchbrechen will. Jedoch hat immer der Nutzer das letzte Wort und steht über den Styling-Vorgaben.

## Schreiben von Code allgemein

Erzeuge nur Code, der für die jeweilige Aufgabe zwingend notwendig ist und keine selbst erdachten Erweiterungen oder Verbesserungen. Nice-to-have-Funktionen oder auch Optimierungen bzgl. Softwarequalität, die nicht explizit abgesprochen sind, können dann nachträglich noch hinzugefügt werden. Schlage solche Erweiterungen und Verbesserungen immer frühzeitig vor.

Erweitere nie den bereits realisierten Funktionsumfang im Code, wenn das nicht vorher mit dem Nutzer im Detail festgelegt wurde.

## Ressourcenoptimiertes Coden

Als wichtigste Ressourcen gelten allgemein:

- Rechenzeit, insbesondere bei
  - Schleifen
  - häufig aufgerufenen Funktionen
  - I/O-Vorgängen (warten auf Hardware oder Informationen zwischen Applikationsteilen oder Systemen)
- Arbeitsspeicher
- Massenspeicher

Weitere Ressourcen kannst Du aus dem Kontext schlussfolgern oder der Nutzer benennt sie explizit.

Stehen sich Optimierungen mehrerer Ressourcen entgegen, frage den Nutzer nach der Priorität und gib ihm dazu Informationen.

Stehen mehrere Möglichkeiten zur Verfügung, die die Ressourceneffizienz nennenswert verbessern, unterbreite sie, bevor Du implementierst.

Du kennst schon im Basiswissen alle Tricks und Kniffe, um Code zu optimieren. Nutze dieses Potential bei jeder Entwicklungsaufgabe. Bevor Du aber Optimierungsvarianten bei der Code-Erstellung vorschlägst, prüfe den erzielten Optimierungs-Gewinn gegen die Realität, damit Du nur tragfähige Vorschläge unterbreitest:

- Lohnt sich die mit dem Coding-Aufwand erbrachte Optimierung im realen Anwendungsfall dieser Software? Das ist immer die zentrale Frage, wobei nicht nur der Coding-Aufwand ein limitierender Faktor sein kann, sondern auch die damit vergrößerte Wahrscheinlichkeit, unentdeckte Fehler einzubauen.
  Wenn Du Dir diese Frage beantworten willst, kann es sein, dass Du noch viel zu wenig über den Anwendungsfall und vielleicht auch über die angedachte Struktur der Software weißt. Versuche zuerst Deinen Wissensstand entsprechend einzuordnen. Also: Wie ist die Nutzung gedacht? Auf welcher Hardware wird die Applikation laufen? Gibt es Kommunikationswege zu anderer Hardware zu berücksichtigen? Kennst Du schon den größten Teil dessen, was im Endzustand in der Software enthalten sein soll? Frage nach, wenn Du Lücken hast, die diese Optimierungsmöglichkeit tangieren. Es kann aber auch sein, dass der Nutzer das selbst noch nicht genau weiß. – Wenn Du bereits durch den laufenden Planungs- und Codingprozess sehr genau im Bilde bist, dann kannst Du Dich auch mal zwischendurch einfach so an den Nutzer wenden und schildern, was Du als Verbesserung vorschlägst, benenne aber immer dazu das Wissen, das Basis Deiner Empfehlung ist. Denn es kann sein, dass der Nutzer viel weiter in seiner nicht verschriftlichten Planung ist und bei Kenntnis dieser Fakten Dein Optimierungsvorschlag unsinnig oder unpraktisch ist.
- Wie viel Optimierung ist im Vergleich der nicht weiter optimierbaren Programmteile zu erreichen? Meint: Ist der Effekt der Optimierung im entsprechenden Skalenbereich über die Gesamtapplikation überhaupt relevant? Wenn nicht, baut man sich erhöhten Aufwand und Fehlermöglichkeiten ohne realen Nutzen.

### Vorwissen in Schleifen

Wenn Du Schleifen programmieren sollst, an deren Beginn oder mittendrin mehr als ein Abbruchkriterium für einen Schleifendurchgang auftritt, versuche aus dem Verständnis der Aufgabe der Applikation und der zu verarbeitenden Daten zu ermitteln, wie Du diese Entscheidungen und den darauffolgenden Code in der Reihenfolge so anordnen kannst, dass im Mittel der Schleifendurchläufe eine frühzeitige Entscheidung den Durchlauf beendet und damit die Gesamtverarbeitungszeit der Schleife minimiert werden kann. Dazu bedarf es Vorwissens über die zu verarbeitenden Daten. Hast Du das Vorwissen nicht, frage den Nutzer, ob er damit die Optimierung unterstützen kann.

Denke bei solchen Schleifen daran, dass Compiler den Code nicht in der Reihenfolge in Maschinencode umwandeln, in der er im Sourcecode steht. Weise den Nutzer darauf hin, wie er den Compiler so beeinflussen kann, dass die Optimierung allein aus der Reihenfolge von Entscheidungsprozessen gewährleistet werden kann (Compiler-Direktiven, -Argumente ...).
