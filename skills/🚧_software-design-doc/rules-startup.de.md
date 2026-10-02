# Skill-Parameter und Erhebung

> **In Arbeit.** Dieser Text ist der Zieltext des Skills und noch nicht fertig: Verweise der Form „Kapitel 1.3.2" oder „Anhang A" zeigen auf die Entwicklungsdoku des Vorhabens und sind vor der Auslieferung durch die Zielstruktur zu ersetzen. Dieser Block entfällt beim Zusammensetzen (Fahrplanschritt 7).

## Die Skill-Parameterdatei

Standardname `.claude/software-design-doc.json`; jeder Skill-Parameter hat einen Standardwert, und fehlt die Datei, gilt in allem der Standard (Vorgabe 2.9).

| Skill-Parameter | Werte | Standard | Bedeutung |
|---|---|---|---|
| `mode` | `on`, `off` | erfragt (Kapitel 3.10.2) | Abwahl je Projekt |
| `doc_dir` | Pfad | abgelesen | Ordner der Doku |
| `register` | Pfad | `<doc_dir>/decisions.md` | Register (Kapitel 3.2) |
| `planned_steps` | Liste von Pfaden | abgelesen | Dateien mit geplanten Schritten (Kapitel 3.4) |
| `marking` | `define+relate`, `define`, `full` | `define+relate` | Pflicht der Zitatmarker |
| `friction_threshold` | Zahl | 2 | Reibungsschwelle; Funktion `global` eine Stufe höher |
| `assumptions_on_approval` | `accept`, `keep` | `accept` | Wirkung der Planfreigabe auf Annahmen (Kapitel 3.1) |
| `impact_model` | `hops`, `weighted` | `hops` | Auswirkungsrechnung (Kapitel 3.6) |
| `impact_lib` | `unknown`, `on`, `off` | `unknown` | ob die optionale Bibliothek `networkx` benutzt wird; der Entwickler wird einmal gefragt (Kapitel 1.7.4 und 3.6.1) |
| `impact_cutoff` | Zahl | 1 bei `hops`, 0,40 bei `weighted` | Tiefe bzw. Abbruchschwelle |
| `lint_signals` | Liste | eingebaute Liste DE/EN | Signalwörter des Lints (Kapitel 3.6) |

Die Skill-Parameter wohnen bewusst in einer Datei mit dem Namen des Skills unter `.claude/`, wie `git-workbench.json` und `git-branch-model.json`: Projektwerte gehören ins Projekt, nicht in den Skilltext.

## Die Doku wächst an Festlegungen, nicht an Pflichten

Keine Struktur wird gefordert, die nichts zu halten hat. Die erste Festlegung, die den Code überdauert, braucht ein Zuhause — eine Datei, die der Skill vorschlägt; der erste Marker legt das Register an; der erste Text, der Festlegungen aus verschiedenen Orten in Beziehung setzt, bekommt die Rolle `relate` vorgeschlagen; der erste Fall von mehr als einem nächsten Schritt bekommt einen Ort für geplante Schritte vorgeschlagen. Die Ausbaustufe eines Projekts ist, was es hat — nicht, was ein Skill-Parameter sagt.

Ebenso schrumpft sie wieder: Wird eine Festlegung aus Kapitel 1 oder 2 durch eine aktuelle Anwender- oder Programmdokumentation redundant und verliert dabei jede Funktion für die weitere Implementierung, darf sie entfallen — über den Lebenszyklus (`retired`), nie stillschweigend (Kapitel 1.3.7).

## Repositories mit mehreren Vorhaben

Ein Repository kann mehrere Vorhaben mit eigener Doku tragen (Kapitel 1.5). Die Skill-Parameterdatei ist der Standard des Repositories. Ein Vorhaben mit eigener Doku weicht ab, indem seine Dateien Rollenmarker und eine `[register: pfad]`-Zeile tragen; der Skill folgt dann dem Vorhaben, in dem die berührten Dateien liegen — keine zweite Skill-Parameterdatei je Vorhaben, die Zeile im Dokument reicht.

## Erkennung der Projektart

Geprüft wird rein mechanisch, ohne Rückfrage, an zwei Signalen. Ein **Projektmanifest** im Baum: `pyproject.toml`, `setup.py`, `package.json`, `Cargo.toml`, `go.mod`, `pom.xml`, `build.gradle`, `CMakeLists.txt`, `Makefile`, `composer.json`, `Gemfile`, `pubspec.yaml`, `mix.exs`, eine `*.csproj`, `Dockerfile`, `docker-compose.yml`. Oder **Quelldateien** an ihrer Endung: `.py` `.js` `.ts` `.tsx` `.jsx` `.c` `.h` `.cpp` `.hpp` `.cs` `.java` `.kt` `.rs` `.go` `.rb` `.php` `.swift` `.scala` `.ex` `.lua` `.sh` `.ps1` `.sql` `.vue` `.dart` `.cu` `.f90` `.jl` `.r`. Übersprungen werden die üblichen Werkzeug- und Fremdordner (`.git`, `.venv`, `node_modules`, `__pycache__`, Editor- und Werkzeugordner).

| Befund | Folge |
|---|---|
| Manifest oder Quelldateien vorhanden | Softwareentwicklung; der Ablauf geht weiter |
| weder noch, aber substantieller anderer Inhalt | kein Softwareprojekt; Du endest hier und sagst es einmal je Sitzung |
| weder noch, und kaum Inhalt | unentschieden; Du läufst still weiter, bis es etwas vorzuschlagen gibt |

Das Ergebnis wird nicht festgehalten: Ein Vorhaben ohne Code heute kann morgen welchen haben, und die Prüfung ist billiger als die Folgen einer veralteten Antwort.
