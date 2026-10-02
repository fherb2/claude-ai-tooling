## 3.5 Skill-Parameter

Stand (2026-09-24): Das Prinzip „ablesen statt fragen, Doku wächst an Festlegungen, Abwahl je Projekt" ist entschieden. Am 2026-09-24 zusätzlich entschieden: der Standardwert von `mode` (vormals Q-16) und die Behandlung mehrerer Vorhaben je Repository (vormals Q-19) — siehe `status.md`. Der Ablauf, der bestimmt, ob und wie der Skill hier überhaupt startet, ist Teil der `SKILL.md` selbst (Kapitel 3.10), nicht dieses Regelteils; hier steht, was ein bereits laufender Skill über Skill-Parameter wissen muss.

### 3.5.1 Ablauf beim Skillstart

Dieser Ablauf ist Teil des dünnen Körpers der `SKILL.md`, nicht eines nachgeladenen Regelteils — er muss laufen, bevor feststeht, welche Regelteile überhaupt geladen werden. Zieltext und Einzelheiten stehen deshalb in Kapitel 3.10.2.

**Befund B-12 (2026-09-25): Hier ist eine Lücke entstanden, und zwar durch mich.** Ursprünglich beschrieb dieser Abschnitt zweierlei: den Ablauf des Skillstarts und die **Erhebung** — also was sich beim ersten Kontakt aus dem Projekt ablesen lässt, wenn die Skill-Parameterdatei fehlt oder ein Feld leer ist: der Doku-Ordner an seinem Namen oder an vorhandenen Markern, das Register, die Dateien mit geplanten Schritten, das Absatzlayout, die vorhandenen Rollen. Am 2026-09-24 habe ich den Ablauf nach Kapitel 3.10.2 verschoben, weil er laufen muss, bevor feststeht, welche Regelteile geladen werden — und die Erhebung dabei mitgenommen, statt sie hier zu lassen. Seither verweist 3.10.2 in seinem letzten Schritt für die Einzelheiten der Erhebung zurück auf Kapitel 3.5, wo nur noch dieser Stub steht. Der Inhalt selbst ist nicht verloren: Kapitel 1.7.1 beschreibt für die Erstanlage, was abgelesen und was gefragt wird. Zu tun: die Erhebung als eigener Zieltext hierher, und der Schritt in 3.10.2 auf einen Verweis gekürzt.

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

**Befund B-09 (2026-09-25): Der Zieltext oben nennt Kapitel, die es im fertigen Skill nicht gibt.** Der zweite Absatz spricht von einer Festlegung „aus Kapitel 1 oder 2" und meint damit die Struktur **dieser** Doku — Zusammenhänge und Vorgaben — im Gegensatz zu Kapitel 3, das ausgenommen bleiben soll. In der Doku eines beliebigen Projekts gibt es diese Nummerierung nicht, und die Vorgabe 2.3 verbietet ausdrücklich, eine Wirkung an eine Kapitelnummer zu binden; ausgedrückt wird so etwas über Rollen. Der Gedanke dahinter bleibt richtig und steht ausführlich in Kapitel 1.3.7: Eine Festlegung darf entfallen, wenn eine aktuelle Anwender- oder Programmdokumentation sie vollständig trägt und sie für die weitere Implementierung keine Funktion mehr hat — mit Ausnahme des Detailwissens, dessen Übernahme in eine Enddokumentation niemand garantieren kann. Zu entscheiden: welche Rollen die drei Fälle abbilden. Ein Vorschlag zum Prüfen — die Zusammenhänge sind die Rollen mit erzählender oder ordnender Funktion, die Vorgaben sind `crosscutting` und `constraints`, und ausgenommen bleiben `building-blocks` und `deployment`.

Die Dreiteilung des Vorläufers (Anhang A) bleibt die Empfehlung für Projekte, die groß werden (Kapitel 3.3).

### 3.5.4 Repositories mit mehreren Vorhaben

> Ein Repository kann mehrere Vorhaben mit eigener Doku tragen (Kapitel 1.5). Die Skill-Parameterdatei ist der Standard des Repositories. Ein Vorhaben mit eigener Doku weicht ab, indem seine Dateien Rollenmarker und eine `[register: pfad]`-Zeile tragen; der Skill folgt dann dem Vorhaben, in dem die berührten Dateien liegen — keine zweite Skill-Parameterdatei je Vorhaben, die Zeile im Dokument reicht.

Das entspricht der Regel dieses Repositories, dass jedes Vorhaben eigenständig aufgebaut ist — hier nur als Beleg dafür genannt, dass die Festlegung sich in der Praxis bewährt, nicht als Teil der Regel selbst.

### 3.5.5 Erkennung der Projektart

Warum der Skill zuerst klärt, ob hier überhaupt Software entsteht, und warum die Prüfung nur das klare Nein erkennen muss, steht in Kapitel 1.7.7. Hier steht, woran sie es erkennt.

> Geprüft wird rein mechanisch, ohne Rückfrage, an zwei Signalen. Ein **Projektmanifest** im Baum: `pyproject.toml`, `setup.py`, `package.json`, `Cargo.toml`, `go.mod`, `pom.xml`, `build.gradle`, `CMakeLists.txt`, `Makefile`, `composer.json`, `Gemfile`, `pubspec.yaml`, `mix.exs`, eine `*.csproj`, `Dockerfile`, `docker-compose.yml`. Oder **Quelldateien** an ihrer Endung: `.py` `.js` `.ts` `.tsx` `.jsx` `.c` `.h` `.cpp` `.hpp` `.cs` `.java` `.kt` `.rs` `.go` `.rb` `.php` `.swift` `.scala` `.ex` `.lua` `.sh` `.ps1` `.sql` `.vue` `.dart` `.cu` `.f90` `.jl` `.r`. Übersprungen werden die üblichen Werkzeug- und Fremdordner (`.git`, `.venv`, `node_modules`, `__pycache__`, Editor- und Werkzeugordner).
>
> | Befund | Folge |
> |---|---|
> | Manifest oder Quelldateien vorhanden | Softwareentwicklung; der Ablauf geht weiter |
> | weder noch, aber substantieller anderer Inhalt | kein Softwareprojekt; Du endest hier und sagst es einmal je Sitzung |
> | weder noch, und kaum Inhalt | unentschieden; Du läufst still weiter, bis es etwas vorzuschlagen gibt |
>
> Das Ergebnis wird nicht festgehalten: Ein Vorhaben ohne Code heute kann morgen welchen haben, und die Prüfung ist billiger als die Folgen einer veralteten Antwort.

**Die Listen altern — das ist ihr eingebauter Mangel**, und deshalb stehen sie hier im Regelteil und nicht als Konstante im Skript: So lassen sie sich erweitern, ohne Code anzufassen. Trifft die Erkennung daneben, ist die Folge mild. Im einen Fall läuft der Skill still mit, obwohl er nicht gebraucht wird; im anderen schweigt er, und der Entwickler ruft ihn bei Bedarf ausdrücklich auf.

**Zur Schwelle zwischen „substantieller Inhalt" und „kaum Inhalt"** steht hier bewusst keine Zahl. Gemeint ist: mehr als eine Handvoll inhaltlicher Dateien, die erkennbar ein anderes Vorhaben tragen — Texte, Abbildungen, Daten. Der genaue Wert wird in der Probe kalibriert (Kapitel 3.8), wie die Normalisierung des Fingerabdrucks auch.

**Gemessen am 2026-10-02** an sechs konstruierten Vorhaben und an diesem Repository: Ein Python-Projekt mit Manifest, ein Infrastruktur-Repository und ein Paper mit einem Auswertungsskript wurden als Software erkannt; ein reines Doku-Repository, ein LaTeX-Paper und ein neues Projekt mit nur einer README blieben unentschieden. Der vollständige Durchlauf dieses Repositories mit rund fünfhundert Dateien dauerte 24 Millisekunden, die konstruierten Fälle jeweils unter einer.
