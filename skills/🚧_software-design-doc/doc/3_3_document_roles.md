## 3.3 Dokumentrollen

Vorschlagsstand (2026-09-17). Entschieden ist das Prinzip: Rollen statt Struktur. Offen und am Ende benannt: der genaue Rollensatz, die Benennung der Funktionen und der Umgang mit der Rolle `decisions`.

### 3.3.1 Prinzip

Ein Abschnitt oder eine Datei kann eine Rolle tragen; die Rolle bestimmt, was der Skill dort tut. Der Marker steht am Ende der Überschrift, in eckigen Klammern mit dem Präfix `DS` (document structure) und einem englischen Schlüsselwort: `## Laufzeitsicht [DS:runtime]`. Nummern, Dateinamen und die Sprache der Überschriften sind frei; nichts, was der Skill liest, hängt an ihnen. Trägt nichts eine Rolle, ist alles `building-blocks`; der Skill schlägt beim ersten Kontakt vor, den Text mit den Zusammenhängen zu kennzeichnen — schlägt vor, verlangt nicht.

Zwei Schichten sind zu trennen, weil die eine für den Menschen und die andere für den Skill da ist: **Inhaltsrollen** benennen, worum es in einem Abschnitt geht. Die Instanz erkennt sie aus dem Inhalt, schlägt sie im Planabschnitt „Berührte Festlegungen" vor und schreibt den Marker mit der Ausführung des Plans — der Entwickler bestätigt oder korrigiert in Prosa, er setzt keinen Marker selbst. Deshalb müssen die Rollennamen ihm etwas sagen: Er liest sie im Plan und in seinen Überschriften. **Funktionen** benennen, was der Skill dort tut — sie folgen aus der Rolle über eine Tabelle im Regelteil, und der Entwickler muss sie nicht kennen. Der Grund für die Trennung: „Beziehungen" ist als Funktion richtig, aber als Beschreibung eines Kapitels für den Menschen unbrauchbar; er sieht dort Spezifikationen, Abläufe, Klassen und Methoden.

### 3.3.2 Inhaltsrollen

Die Inhaltsrollen folgen dem arc42-Schema, einem seit Jahren etablierten, frei lizenzierten (CC BY-SA 4.0) Gliederungsstandard für Architektur- und Designdokumentation, der in deutscher und englischer Fassung vorliegt. Seine zwölf Abschnitte decken genau das ab, was das Vorhaben „projektbegleitende Softwaredokumentation mit Ziel, Randbedingungen, Festlegungen bis zur Ausführung" nennt. Die englischen Abschnittsnamen sind an der Primärquelle belegt (arc42.org, 2026-09-17); die deutschen Entsprechungen in der Tabelle sind Modellwissen und bei der Umsetzung gegen die deutsche Vorlage zu prüfen.

| Rolle | arc42 | deutsch (zu prüfen) | Funktion für den Skill |
|---|---|---|---|
| `goals` | 1 Introduction and Goals | Einführung und Ziele | `define`, `relate` |
| `constraints` | 2 Constraints | Randbedingungen | `define`, `global` |
| `context` | 3 Context and Scope | Kontextabgrenzung | `relate` |
| `strategy` | 4 Solution Strategy | Lösungsstrategie | `relate` |
| `building-blocks` | 5 Building Block View | Bausteinsicht | `define` (Standard) |
| `runtime` | 6 Runtime View | Laufzeitsicht | `relate` |
| `deployment` | 7 Deployment View | Verteilungssicht | `define` |
| `crosscutting` | 8 Crosscutting Concepts | Querschnittliche Konzepte | `define`, `global` |
| `decisions` | 9 Architecture Decisions | Architekturentscheidungen | `define` |
| `quality` | 10 Quality Requirements | Qualitätsanforderungen | `define`, `relate` |
| `risks` | 11 Risks and Technical Debt | Risiken und technische Schulden | `nonbinding` |
| `glossary` | 12 Glossary | Glossar | `nonbinding` |

Dazu Rollen, die arc42 nicht kennt, weil es Architektur beschreibt und nicht Projektarbeit:

| Rolle | Inhalt | Funktion |
|---|---|---|
| `plan` | geplante Schritte, wo immer sie stehen | `plan` |
| `status` | erledigte Schritte | `nonbinding` |
| `concept` | Findungstext, ausdrücklich nicht bindend | `nonbinding` |
| `appendix` | Verlauf, Reviews, verworfene Wege | `nonbinding` |
| `register` | das Register selbst | `register` |

### 3.3.3 Funktionen

| Funktion | Was der Skill in einem Abschnitt mit dieser Funktion tut |
|---|---|
| `define` | Definitionsmarken; Standardfunktion für alles Unmarkierte |
| `relate` | Zitatmarken Pflicht; Quelle der Kanten für die Auswirkungsrechnung (Kapitel 3.6) |
| `global` | Festlegungen gelten projektweit: Reibungsschwelle eine Stufe höher; Kollisionen werden als projektweit gekennzeichnet |
| `nonbinding` | Lint und Auswirkungsrechnung überspringen den Abschnitt; Aussagen dort sind keine Festlegungen |
| `plan` | `target:`-Zeilen werden gelesen (Kapitel 3.4) |
| `register` | Registergrammatik gilt (Kapitel 3.2) |

Erweiterbar, indem der Regelteil eine neue Rolle mit ihrer Funktion definiert. Die Funktion `nonbinding` für `concept` löst ein Problem, das der bisherige Standard nicht adressierte: Findungstexte neben der bindenden Doku, die die Instanz genauso als Gesetz las.

### 3.3.4 Das Dreiersschema des Vorläufers als Rollensatz

Das Schema ist in Anhang A beschrieben. Segment 1 „Zusammenhänge" entspricht `goals`, `constraints`, `context`, `strategy`, `runtime` und `quality`; Segment 2 „Vorgaben" entspricht `crosscutting` und `constraints`; Segment 3 „Einheiten" entspricht `building-blocks` und `deployment`. Wer das Dreiersschema weiterführt, kennzeichnet seine drei Dateien mit den passenden Rollen; die Verkettungsregel („Dateireihenfolge ergibt ein gültiges Dokument") bleibt als Empfehlung.

### 3.3.5 Recherche zu Standards

Geprüft am 2026-09-17: arc42 (belegt: zwölf Abschnitte, Lizenz, deutsche Fassung vorhanden; keine Vorgabe von Identifikatoren je Aussage). Google-Design-Docs (unbestätigt, aus Sekundärquellen: Kontext und Umfang, Ziele und Nicht-Ziele, Entwurf, erwogene Alternativen, Querschnittsbelange; bewusst informell). IEEE 1016 Software Design Description (unbestätigt: Sichten context, composition, logical, dependency, information, patterns use, interface). ISO/IEC/IEEE 42010 (unbestätigt: Begriffe viewpoint, view, concern; schreibt keine Sichten vor). Die Diátaxis-Gliederung betrifft Anwenderdokumentation und ist hier nicht einschlägig. Ergebnis: arc42 ist die einzige der Quellen mit einem festen, benannten Abschnittssatz in beiden Sprachen und ohne Lizenzhürde — deshalb die Wahl.

### 3.3.6 Entscheidungsgrundlagen

> **[Q-08] Entscheidungsgrundlage — Umfang des Rollensatzes**
> Kontext: arc42 hat zwölf Abschnitte. Alle als Rollen anzubieten ist vollständig, aber für kleine Projekte viel; ein Kern deckt die drei alten Segmente ab und lässt den Rest als Erweiterung.
> Optionen: (a) alle zwölf plus die fünf Projektrollen; (b) ein Kern — `goals`, `constraints`, `context`, `strategy`, `building-blocks`, `runtime`, `crosscutting` — plus Projektrollen, der Rest wird bei Bedarf ergänzt; (c) nur die drei alten Segmente als Rollen (`relations`, `rules`, `units`) und die arc42-Namen als Empfehlung im Regeltext.
> Vorschlag: (a) — die Tabelle kostet nichts, und ein Projekt benutzt, was es braucht; die Funktion jeder Rolle ist ohnehin einer von sechs Werten.
> Gewicht: groß · Blockiert: Fahrplanschritt 1
> Antwort:

> **[Q-09] Entscheidungsgrundlage — Rolle `decisions` neben dem Register**
> Kontext: arc42 sieht in Abschnitt 9 Architekturentscheidungen vor, typisch als Architecture Decision Records. Unser Register hält die Attribute jeder Festlegung; die Prosa hält Grund und Alternative. Eine eigene Rolle `decisions` könnte doppeln.
> Optionen: (a) Rolle behalten: sie hält die Begründungen großer, kapitelübergreifender Entscheidungen in Prosa, das Register die Attribute; (b) Rolle streichen — Begründungen stehen beim Kapitel, das die Festlegung definiert.
> Vorschlag: (a) — für Entscheidungen, die kein einzelnes Kapitel „besitzt".
> Gewicht: mittel · Blockiert: Fahrplanschritt 1
> Antwort:

> **[Q-10] Entscheidungsgrundlage — Namen der Funktionen**
> Kontext: `define`, `relate`, `global`, `nonbinding`, `plan`, `register` sind Skill-intern; der Entwickler sieht sie nicht, außer er liest den Regelteil.
> Optionen: (a) so lassen; (b) andere Wörter — welche?
> Vorschlag: (a).
> Gewicht: klein · Blockiert: Fahrplanschritt 1
> Antwort:

> **[Q-11] Entscheidungsgrundlage — Position des Rollenmarkers**
> Kontext: `[DS:runtime]` am Ende der Überschrift wird beim Rendern Teil der Überschrift (sichtbar, `grep`-bar); als erste Zeile unter der Überschrift stört es die Überschrift nicht, ist aber leichter zu übersehen und beim Umsortieren von Abschnitten leichter zu trennen.
> Optionen: (a) am Ende der Überschrift; (b) erste Zeile unter der Überschrift; (c) beides erlaubt.
> Vorschlag: (a).
> Gewicht: klein · Blockiert: Fahrplanschritt 1
> Antwort:
