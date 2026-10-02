# 3 Einheiten

**Was in dieses Segment gehört.** Kapitel 1 sagt, was der Skill funktional leisten soll — es ist die Quelle jeder Tätigkeit bei der Implementierung. Kapitel 2 legt die allgemein gültigen Vorgaben fest, mit denen das zu erfüllen ist. Kapitel 3 trägt allein die Detaillierung, die zum Implementieren nötig ist oder sich aus ihr ergibt: Regeltexte im Wortlaut, Grammatiken, Kommandos, Tabellen, Schnittstellen.

Daraus folgen drei Prüfungen für jeden Absatz hier: Steht hier eine **Absicht** oder **Begründung**, die nicht schon in Kapitel 1 steht, gehört sie dorthin. Steht hier eine **prüfbare Regel**, die über eine Einheit hinaus gilt, gehört sie nach Kapitel 2. Steht hier **Beurteilungsmaterial** — Recherchen, verworfene Wege, Messungen —, gehört es in die Anhänge.

**Der Text des Skills steht nicht mehr hier** (Festlegung des Entwicklers vom 2026-10-02). Bis dahin trugen sechs Kapitel dieses Segments den ausformulierten Skilltext als Zitat, umgeben von Entwicklungstext. Das war ein Behelf aus der Zeit, als beides noch gemeinsam wuchs, und es weichte eine Regel auf, die sonst überall gilt: Eine Implementierungsdoku enthält nicht die Implementierung. Für dieses Vorhaben **ist** der Skilltext die Implementierung — er ist das, was in einem gewöhnlichen Projekt der Quellcode wäre.

Seither liegen die Zieltexte als eigene Dateien im Ordner des Skills, eine Ebene über dieser Doku: `SKILL.de.md`, `rules-hardness.de.md`, `rules-register.de.md`, `rules-planning.de.md`, `rules-startup.de.md`, `CLAUDE-snippet.de.md`. Hinzu kommen später `standard.de.md` aus dem bisherigen Standard und, falls so entschieden, eine Datei für die Rollenzuordnung. Beim Installieren entstehen daraus die Dateien ohne Sprachkürzel; die englischen Fassungen werden am Schluss hergestellt.

**Was damit in Segment 3 bleibt**, ist dasjenige Wissen über die Skilltexte, das aus ihnen selbst nicht hervorgeht: warum eine Formulierung so und nicht anders gewählt wurde, welcher Weg verworfen wurde und woran er scheiterte, welche Messung eine Festlegung stützt, wo die Entscheidung in Kapitel 1 oder 2 steht, auf der ein Textstück beruht. Was der Text schon sagt, wird hier nicht wiederholt. Ein Kapitel, das danach dünn aussieht, ist nicht unfertig, sondern ehrlich: Dann gab es zu diesem Textstück nichts hinzuzufügen.

**Die Verweisrichtung ist festgelegt und gilt in eine Richtung.** Jedes Kapitel dieses Segments nennt oben die Zieldatei, die es begleitet. Die Zieldateien verweisen **nie** auf diese Doku — sie sollen am Ende ohne sie lesbar sein, denn beim Nutzer existiert sie nicht.

**Für die übrigen Kapitel dieses Segments (3.3, 3.6 bis 3.9) ändert sich nichts.** Sie tragen keinen Zieltext, sondern spezifizieren Code, Konfiguration oder einen Vorgang — das Skript, die Hooks, die Probe, die Migration. Für sie gelten die drei Prüfungen oben unverändert.

## 3.1 Härte einer Festlegung — Ableitung und Wirkung

Finaler Stand von Arbeitspunkt 1 (2026-09-17), mit zwei nachträglichen Anpassungen aus Arbeitspunkt 2: Die Ereigniszeile „bestätigt" des Vorläufers (Anhang A) heißt `upheld` statt `confirmed`, weil `confirmed` zugleich ein Statuswert ist (Kapitel 3.2) — vom Entwickler am 2026-09-24 bestätigt (vormals Q-02); und „Segment 2" ist ersetzt durch „Abschnitte mit der Funktion `global`" (Kapitel 1.3.3). Adressat des Regelteils ist die Instanz („Du"), der Mensch heißt „der Entwickler".

**Dieses Kapitel begleitet `rules-hardness.de.md`.** Dort steht der Text selbst; hier steht, was bei seiner Ausarbeitung angefallen ist und nicht aus ihm hervorgeht. Der Zieltext verweist nie hierher zurück.

### 3.1.6 Der Planabschnitt „Berührte Festlegungen"

**Befund B-03 (2026-09-25): Die Suchschlüssel sollen hier sichtbar sein, stehen aber nicht in der Aufzählung.** Suchschlüssel sind zwei bis vier markante Begriffe je Festlegung; sie finden Erwähnungen im Text, die keinen Marker tragen, und sind damit die zweite Quelle der Auswirkungsrechnung neben dem Graphen (Kapitel 1.7.4). Am 2026-09-24 wurde entschieden, dass die Instanz sie beim Anlegen selbst wählt und der Entwickler sie **im Planabschnitt** sieht — ausdrücklich deshalb, damit er sie korrigieren kann, ohne dass sie eine eigene Rückfrage kosten. Genau dieser Planabschnitt wird oben beschrieben, und die Suchschlüssel fehlen in der Aufzählung; ebenso in der Ausgabe des Kommandos, das den Abschnitt erzeugt (Kapitel 3.6.4, `plan-section`). Ohne sie gäbe es die beschlossene Korrekturgelegenheit nicht. Zu entscheiden ist nur die Form: eine eigene Spalte beziehungsweise ein eigenes Feld je Eintrag, oder eine angehängte Aufzählung hinter dem Grund.

### 3.1.10 Bewusst nicht Teil dieses Regelteils

Die Begründung, warum vier naheliegende Eingänge — Alter der Entscheidung, Umbaukosten, Gewichtung, neues Wissen — fehlen, steht in Kapitel 1.3.1 und gehört nicht hierher. Die Konsistenzprüfung, die der Regelteil am Ende als nicht zu ihm gehörig nennt, leistet in diesem Repository der Skill `konsistenzpruefung`; im Zieltext wird er nicht genannt, weil kein Skill-Körper auf einen anderen Skill verweist (`skill-dev-doc.md`, 2.3).
