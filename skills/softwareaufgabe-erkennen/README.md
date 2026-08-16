# softwareaufgabe-erkennen — Idee, noch kein Skill

Erkennen, dass die Anfrage des Nutzers auf eine zu schreibende oder zu ändernde Software hinausläuft — auch wenn sie das nicht mit Wörtern wie „Code", „programmieren" oder „Software" ausdrückt — und daraufhin die einschlägigen Entwicklungsregeln nachladen.

**Status:** Nur diese README, keine `SKILL.md`. Die Idee ist festgehalten samt dem, was die Testreihe darüber ergeben hat.

**Messergebnis** (Testreihe vom 14. August 2026, siehe Kapitel 3 der Vorgaben): Erprobt wurde eine eigenschaftsförmige Trigger-Fassung („behalte im Blick, ob die Anfrage auf zu schreibende oder zu ändernde Software hinausläuft", mit Beispielen für Anzeichen). Sie feuerte auf Sonnet in keiner von drei Eskalationsstufen — von der reinen Verständnisfrage zu einem vorhandenen Skript über die Schilderung eines Fehlverhaltens bis zur konkreten Vermutung über eine Programmierlücke. Dieselbe Fassung feuerte sofort, als statt einer knappen Frage ein Quelltextausschnitt mit einem vagen Unmut geschickt wurde. Auf Opus und Fable genügte bereits die mittlere Stufe.

**Teilweise überholt.** `common-code-generation` trägt inzwischen einen Teil dessen, was hier als Idee steht: Er wird ausgelöst, wenn Code entsteht, auch ohne dass die Anfrage von Code spricht.

**Offen:**

- Entscheiden, ob daraus ein eigenständiger Skill wird, ob er die Vorstufe von `software-dev-doc-fh` ist — oder ob er sich mit `common-code-generation` erledigt hat. Erst danach lohnt Arbeit am Inhalt.
- Fällt die Entscheidung für einen eigenen Skill: den Trigger nach Kapitel 2 der Vorgaben geankert neu formulieren, nicht als Hintergrund-Beobachtung.
