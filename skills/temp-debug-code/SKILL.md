# Temorärer Debug-Code und zeitweises Auskommentieren

Alle Regeln gelten nur für temporären Debug-Code, der also nicht auf Dauer im Quellcode verbleiben soll. Für Debug-Code der dauerhaft im Quellcode verbleiben soll, der z.B. mittels Debug-Flags und ähnliche Methoden aktiviert werden soll, ist nicht nach diesen Regeln anzulegen.

Wenn Du temporären Debug-Code einfügst und gegebenenfalls derweil bestehenden Programmcode auskommentierst, 

- beachte folgende Regeln und 
- beachte das Leerzeichen am Ende und manchmal auch am Anfang der dazu im Folgenden definierten Token, die immer mit zum Token gehören. Begründung: Exakt definierte Token erleichtern das Auffinden und Entfernen temporär veränderten Codes (sogar effizient per Script). Halte Dich also exakt an die Vorgaben zwischen den "-Zeichen!

Wenn Du also temporären Debug-Code einfügst oder Programmcode tot legst:

- Prüfe, ob bereits erstellter Debug-Code wieder entfernt werden kann, weil er seinen Zweck erfüllt hat. Wenn:
  - es sich um Debug-Code handelt, der eben erst erstellt wurde und sein Dienst getan hat, kannst Du den selbständig entfernen und eventuell dabei auskommentierte Bereiche des Programmcodes wieder aktivieren.
  - Wenn es sich jedoch um früheren Debug-Code handelt, der mit dem aktuellen Vorgang nichts zu tun hat, lege dem Nutzern die Stelle vor und lasse ihn entscheiden. Entscheidet er sich gegen das Entfernen, dann schlage ihm diese Stelle erst dann wieder vor, wenn
    - ein neuer Tag oder ein neuer Chat begonnen hat oder
    - der Nutzer Dir den Auftrag gibt, Debugcode zu finden und zu entfernen.

- Wenn Du Debug-Code entfernst, prüfe sehr genau, ob dabei vorübergehend totgelegter Originalcode wieder zu aktivieren ist.

- Willst Code-Teile einer einzelnen Anweisungszeile zum Debugging temporär ändern, dann:
  - kopiere die betreffende Zeile zum Ändern unter die originale Zeile
  - kommentiere die originale Source-Code-Zeile aus und schreibe dabei zwischen den einleitenden Kommentar-Marker der jeweilgen Programmiersprache und der damit auskommentierten Source-Code-Zeile den Token " # DEBUG: ORIGINAL # "
  - behandle die Kopie darunter mit der Debug-Änderung so, wie jede andere Debug-Zeile, wie nachfolgend beschrieben ist (also Token " # DEBUG # " anhängen).

- fügst Du einzelne oder bis zu 4 Debug-Zeilen am Stück oder ganz dicht beieinander hinzu, dann
  - hänge an jede Zeile einen Kommentar an, der mit dem Token " # DEBUG # " hinter dem Kommentar-Marker beginnt.
  - Hinter dem Token kannst Du bei Bedarf zusätzlich die Zeile kommentieren.
  - Originale Codezeilen, die unmittelbar davor, danach oder zwischen den Debugzeilen stehen und auskommentiert werden müssen, bekommen zwischen dem vorn zugefügten Kommentar-Marker und dem Code den Token " # DEBUG: ORIGINAL # ".
  
- fügst Du 5 oder mehr Debug-Zeilen am Stück ein, 
  - verzichte auf die beschriebenen DEBUG-Token am Ende dieser Zeilen.
  - Lege statt dessen eine Debug-Einleitungszeile als Kommentar vor die erste Debug-Code-Zeile an, die nach dem Kommentar-Marker mit dem Token " # DEBUG:Start ------------ # " beginnt.
  - Lege nach der letzten Debug-Code-Zeile eine weitere Kommentarzeile an, die nach dem Kommentar-Marker mit dem Token " # DEBUG:End ------------ # " beginnt.

- Beachte bei allen Änderungen, die mit temporärem Debugging zu tun haben,

  - bei Code an Entscheidungsstellen (Verzweigungen, Case-Aufteilungen) und Loops auf die richtige Anwendung der Token, um den Originalzustand mit minimalem Aufwand und für den Nutzer transparent und einheitlich zu ermnöglichen.

  - die Einrückungen des Entwicklers bzw. der verwendeten Programmiersprache.

- Wenn Du zufällig Zeilen im Quellcode findest, die sich nicht exakt an diese Vorgaben halten, informiere den Entwickler und schlage ihm vor, das zu korrigieren. Zeige ihm dazu beispielhaft das Resultat der Korrektur im Chat, damit er leichter entscheiden kann, ob dieswe Korrektur ausgeführt werden kann. Keine solche Korrektur ohne vorherige Entwicklerzustimmung.