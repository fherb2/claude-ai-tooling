

# Sprachen und Benennungen in Source Code Files

Wenn Du Codebestandteile sowie Kommentare und Docstring selbst benennen sollst, dann:

- wähle englisch Begriffe

Wenn Du Codebestandteile benennst, dann:

- kurze, inhaltlich treffende Begriffe sind besser als lange Begriffe
- baue "sprechenden Code", soweit das die Styling-Vorgaben erlauben
- beachte immer die jeweiligen Code-Styling-Vorgaben als primär geltend

# Temorärer Debug-Code und Auskommentieren

Wenn Du temporären Debug-Code einfügst bzw. derweil bestehenden Code auskommentierst, beachte folgende Regeln:

- prüfe, ob bereits erstellter Debug-Code wieder entfernt werden sollte, weil er seinen Zweck erfüllt hat. Sage das vor dem Entfernen dem Benutzer, statt es heimlich zu entfernen.

- fügst Du einzelne oder bis zu 4 Debug-Zeilen fortlaufend (am Stück) hinzu, dann hänge an jede Zeile einen Kommentar an, der mit dem Token " # DEBUG #" 

 indem Du für jede Zeile immer einen Kommentar ans Ende der Zeile hängst und diesen hinter dem Kommentar-"Operator" mit "# DEBUG # " einleitest. Auch, wenn sonst kein weiterer Kommentar darauf folgt.

- Bei Code-Änderungen in der Zeile:
  - kommentiere die Source-Code-Zeile aus
  - schreibe zwischen den einleitenden Kommentar-"Operator" und der damit auskommentierten Source-Code-Zeile den Token #ORIGINAL#



Wenn Du zu temporärem Debug-Code beschreibende Kommentare anlegst, dann: 

- wähle Deutsch als Sprache. Begründung: Erhöht den Wiedererkennungswert von später vom gleichen Entwickler wieder zu entfernenden Debug-Code.







# Schreiben von Code allgemein

Erzeuge nur Code, der für die jeweilige Aufgabe zwingend notwendig ist und keine selbst erdachten Erweiterungen oder Verbesserungen. Nice-to-have-Funktionen oder auch Optimierungen bzgl. Softwarequalität, die nicht explizit abgesprochen sind, können dann nachträglich noch zugefügt werden. Schlage solche Erweiterungen, Verbesserungen immer zuerst dem Nutzer vor.

Erweitere nie den bereits realisierten Funktionsumfang im Code, wenn das mit dem Nutzer nicht vorher einzeln festgelegt wurde.

# Ressourcenoptimiertes Coden

Als wichtigste Ressourcen gelten allgemein:

- Rechenzeit
- Arbeitsspeicher
- Massenspeicher

Weitere Ressource kannst Du aus dem Kontext schlussfolgern oder der Nutzer benennt sie explizit.

Stehen sich Optimierungen zwischen mehrere Ressource einader entgegen, frage den Nutzer nach der Priorität, bevor Du eine optimale Entscheidung triffst.

Stehen bei der Implementierung mehrere Möglichkeiten zur Verfügung, die die Ausführungszeit nennenswert verbessern oder den Speicherverbrauch reduzieren, schlage solche Möglichkeiten dem Nutzer vor der Implementierung vor. 

Bevor Du Optimierungsvarianten bei der Coderstellung vorschlägst: Prüfe den erzielten Gewinn gegen die Realität an der entsprechenden Codestelle:

- Lohnt sich die mit dem Coding-Aufwand eingesparten Ressourcemenge (meist eit)

# Debugging









