## 3.5 Skill-Parameter

Stand (2026-09-24): Das Prinzip „ablesen statt fragen, Doku wächst an Festlegungen, Abwahl je Projekt" ist entschieden. Am 2026-09-24 zusätzlich entschieden: der Standardwert von `mode` (vormals Q-16) und die Behandlung mehrerer Vorhaben je Repository (vormals Q-19) — siehe `status.md`. Der Ablauf, der bestimmt, ob und wie der Skill hier überhaupt startet, ist Teil der `SKILL.md` selbst (Kapitel 3.10), nicht dieses Regelteils; hier steht, was ein bereits laufender Skill über Skill-Parameter wissen muss.

### 3.5.1 Ablauf beim Skillstart

Dieser Ablauf ist Teil des dünnen Körpers der `SKILL.md`, nicht eines nachgeladenen Regelteils — er muss laufen, bevor feststeht, welche Regelteile überhaupt geladen werden. Zieltext und Einzelheiten stehen deshalb in Kapitel 3.10.2.

### 3.5.2 Die Skill-Parameterdatei

> Standardname `.claude/software-design-doc.json`; jeder Skill-Parameter hat einen Standardwert, und fehlt die Datei, gilt in allem der Standard (Vorgabe 2.9).
>
> | Skill-Parameter | Werte | Standard | Bedeutung |
> |---|---|---|---|
> | `mode` | `on`, `off` | erfragt (Kapitel 3.10.2) | Abwahl je Projekt |
> | `doc_dir` | Pfad | abgelesen | Ordner der Doku |
> | `register` | Pfad | `<doc_dir>/decisions.md` | Register (Kapitel 3.2) |
> | `planned_steps` | Liste von Pfaden | abgelesen | Dateien mit geplanten Schritten (Kapitel 3.4) |
> | `marking` | `define+relate`, `define`, `full` | `define+relate` | Pflicht der Zitatmarker |
> | `friction_threshold` | Zahl | 2 | Reibungsschwelle; Funktion `global` eine Stufe höher |
> | `assumptions_on_approval` | `accept`, `keep` | `accept` | Wirkung der Planfreigabe auf Annahmen (Kapitel 3.1) |
> | `impact_model` | `hops`, `weighted` | `hops` | Auswirkungsrechnung (Kapitel 3.6) |
> | `impact_lib` | `unknown`, `on`, `off` | `unknown` | ob die optionale Bibliothek `networkx` benutzt wird; der Entwickler wird einmal gefragt (Kapitel 1.7.4 und 3.6.1) |
> | `impact_cutoff` | Zahl | 1 bei `hops`, 0,40 bei `weighted` | Tiefe bzw. Abbruchschwelle |
> | `lint_signals` | Liste | eingebaute Liste DE/EN | Signalwörter des Lints (Kapitel 3.6) |
>
> Die Skill-Parameter wohnen bewusst in einer Datei mit dem Namen des Skills unter `.claude/`, wie `git-workbench.json` und `git-branch-model.json`: Projektwerte gehören ins Projekt, nicht in den Skilltext.

**Das Absatzlayout ist kein Skill-Parameter** (entschieden am 2026-09-25, vormals Q-17). Es wird aus der vorhandenen Doku abgelesen — hängen Sätze aneinander, bis ein Absatz endet, ist es die eine Variante; bricht der Text immer wieder nach einer festen Länge um, die andere, denn halbe Sätze sind kein Absatz. Nur wenn es keine Doku gibt oder der Befund wirklich uneindeutig bleibt, wird einmal gefragt (Kapitel 3.2.8).

**Wie der Abbruchwert der Auswirkungsrechnung kodiert wird, entscheidet sich bei der Umsetzung** (seit 2026-09-25 keine Entscheidungsgrundlage mehr, vormals Q-18). Das Funktionale ist längst entschieden: zwei grobe Griffe für das Projekt, keine einzelnen Gewichte (Kapitel 3.6.5). Offen ist allein die Kodierung, und sie trägt eine Fehlerquelle: Derselbe Wert bedeutet in den beiden Betriebsarten Verschiedenes — bei `hops` eine Tiefe, bei `weighted` eine Schwelle —, sodass ein Wechsel der Betriebsart ohne Nachziehen des Werts stillschweigend Unsinn ergibt. Zur Wahl stehen ein Feld mit modellabhängiger Bedeutung, zwei Felder, von denen immer eines wirkungslos ist, und ein zusammengesetzter Wert im Modellfeld. Entschieden wird beim Bauen, nicht vorher.

### 3.5.3 Die Doku wächst an Festlegungen, nicht an Pflichten

> Keine Struktur wird gefordert, die nichts zu halten hat. Die erste Festlegung, die den Code überdauert, braucht ein Zuhause — eine Datei, die der Skill vorschlägt; der erste Marker legt das Register an; der erste Text, der Festlegungen aus verschiedenen Orten in Beziehung setzt, bekommt die Rolle `relate` vorgeschlagen; der erste Fall von mehr als einem nächsten Schritt bekommt einen Ort für geplante Schritte vorgeschlagen. Die Ausbaustufe eines Projekts ist, was es hat — nicht, was ein Skill-Parameter sagt.
>
> Ebenso schrumpft sie wieder: Wird eine Festlegung aus Kapitel 1 oder 2 durch eine aktuelle Anwender- oder Programmdokumentation redundant und verliert dabei jede Funktion für die weitere Implementierung, darf sie entfallen — über den Lebenszyklus (`retired`), nie stillschweigend (Kapitel 1.3.7).

Die Dreiteilung des Vorläufers (Anhang A) bleibt die Empfehlung für Projekte, die groß werden (Kapitel 3.3).

### 3.5.4 Repositories mit mehreren Vorhaben

> Ein Repository kann mehrere Vorhaben mit eigener Doku tragen (Kapitel 1.5). Die Skill-Parameterdatei ist der Standard des Repositories. Ein Vorhaben mit eigener Doku weicht ab, indem seine Dateien Rollenmarker und eine `[register: pfad]`-Zeile tragen; der Skill folgt dann dem Vorhaben, in dem die berührten Dateien liegen — keine zweite Skill-Parameterdatei je Vorhaben, die Zeile im Dokument reicht.

Das entspricht der Regel dieses Repositories, dass jedes Vorhaben eigenständig aufgebaut ist — hier nur als Beleg dafür genannt, dass die Festlegung sich in der Praxis bewährt, nicht als Teil der Regel selbst.
