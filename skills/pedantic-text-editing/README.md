# pedantic-text-editing — Textbearbeitung mit Detailtreue

*Stand: 2026-08-25*

*[English version](README.en.md)*

**✅☑ Fertig und nutzbar.** Anweisungen vollständig, Frontmatter gesetzt, deutsche und englische Fassung vorhanden. Ein stiller Trigger fehlt noch (siehe „Offen“); bis dahin löst der Skill über seine `description` aus oder wird mit `/pedantic-text-editing` aufgerufen.

**Der Skill begrenzt den Eingriff in einen Text auf genau die Stellen, die der Nutzer freigegeben hat — und weist hinterher nach, dass sich nichts anderes geändert hat.** Er gilt für Texte, deren Wortlaut selbst das Produkt ist: Aufsätze, Anträge, Vorträge, Briefe, Buchkapitel, Gutachten. Der Schwerpunkt liegt nicht auf dem Finden von Fehlern — das kann Claude auch ohne Skill —, sondern auf der Begrenzung des Eingriffs: dass beim Korrigieren einer Kommastelle nicht nebenbei ein Halbsatz umgeschrieben, ein „vermutlich“ getilgt, zwei Sätze verschmolzen oder die Anführungszeichen im ganzen Text vereinheitlicht werden.

Dafür trennt er drei Arten von Fund — Regelverstoß, Sachfrage, Geschmack — und behandelt sie verschieden, legt jede Änderung einzeln zur Freigabe vor, hält die freigegebenen Befunde in einer Datei fest und prüft nach der Ausführung den Diff gegen diese Befunde. Was der Nutzer einmal entschieden hat, merkt sich eine zweite Datei dauerhaft, damit dieselbe Frage nicht in jeder Runde erneut kommt.

**Wofür er nicht gilt:** Quellcode und Texte, die einer Software folgen und sie dokumentieren. Dort greift er nur, wenn der Nutzer es ausdrücklich verlangt. Maßgeblich ist nicht das Thema des Textes und nicht der Ordner, in dem er liegt, sondern seine Rolle. Und er greift nie von selbst: Nach dem Laden fragt er einmal, ob er zur Anwendung kommen soll, und eine Absage gilt für die ganze Sitzung.

## Installation

1. **Zielort wählen.** Der Skill gilt entweder für alle Projekte des Nutzers oder nur für eines:

   | Ort         | Pfad                                        | Gilt für                  |
   | ----------- | ------------------------------------------- | ------------------------- |
   | Persönlich  | `~/.claude/skills/pedantic-text-editing/`   | alle Projekte des Nutzers |
   | Projekt     | `.claude/skills/pedantic-text-editing/`     | nur dieses Projekt        |

2. **Eine Sprachfassung kopieren.** Der Ordnername bleibt unverändert. Kopiert wird eine vollständige Sprachfassung:

   | Deutsch         | Englisch        |
   | --------------- | --------------- |
   | `SKILL.de.md`   | `SKILL.en.md`   |
   | `regeln.de.md`  | `regeln.en.md`  |
   | `README.md`     | `README.en.md`  |

   **Verpflichtend ist daran allein, dass die gewählte SKILL-Fassung am Zielort `SKILL.md` heißt** — Claude Code erkennt keinen anderen Namen. Ob dafür umbenannt oder zusätzlich abgelegt wird, ist gleichgültig. Die Regeldatei behält ihren Namen: Die `SKILL.md` verweist auf sie, und dieser Verweis ist der einzige Weg, auf dem die Regeln überhaupt geladen werden. Wer sie umbenennt, zieht den Verweis mit.

## Details

**Warum der Skill zweigeteilt ist.** Die `SKILL.md` trägt nur den Geltungsbereich, die Klärung und den Ladebefehl; die Regeln stehen in der Regeldatei. Der Grund ist der Kontexthaushalt: Ein geladener Skill bleibt für den Rest der Sitzung im Kontext, und dieser hier löst auf eine Lage aus, in der er oft doch nicht zum Zug kommt. Ohne die Teilung schleppte jede solche Sitzung den vollen Regeltext mit. Die Zusatzdatei kostet dagegen nichts, solange niemand auf sie verweist. Wer die beiden Dateien zusammenlegt, macht den Skill teuer, ohne ihn besser zu machen.

**Die drei Klassen sind der eigentliche Schutz vor Inhaltsdrift.** Ein Regelverstoß kommt als Korrektur in die Liste. Eine Sachfrage wird nie korrigiert, sondern gefragt, auch wenn sie offensichtlich falsch aussieht — und dabei noch einmal geteilt: Die Schreibweise einer Zahl oder eines Verweises gehört zum Auftrag, ein Widerspruch im Inhalt braucht dagegen erst die Zustimmung, dass er mitbearbeitet werden soll. Geschmacksänderungen kommen nur auf ausdrücklichen Auftrag. Wer diese Trennung aufweicht und „Ausdruck“ mit „Rechtschreibung“ in eine Liste wirft, hat den Skill entwertet: Der Nutzer gibt dann mit dem Komma auch den umgeschriebenen Halbsatz frei.

**Die Gegenprobe ist die Stelle, an der der Skill überhaupt wirkt.** Alles andere ist eine Bitte; erst der Diff gegen die freigegebenen Befunde macht daraus eine Prüfung. Deshalb zwei Commits je Runde: erst die freigegebenen Befunde bei noch unveränderter Textdatei, dann die ausgeführte Änderung. Die Differenz zwischen beiden ist genau das, was ausgeführt wurde, und lässt sich Zeile für Zeile gegen die Befunde halten. Ohne Git tritt eine Kopie des Ausgangsstands an die Stelle des ersten Commits — der Nachweis fehlt dann, die Gegenprobe nicht.

**Zwei Dateien mit verschiedener Lebensdauer.** `editing-findings_<datei>_<zeitstempel>.md` hält **eine Runde**: im Kopf den Auftrag samt dem, was ausdrücklich nicht untersucht wurde, darunter die Befunde. Sie darf später weg. `editing-data_<datei>.md` ist das **Gedächtnis** und bleibt: das Glossar der unantastbaren Stellen, die geklärten Sachfragen, die abgelehnten Vorschläge und je Runde eine Protokollzeile. Geschrieben wird sie am Ende jeder Runde und nicht erst beim Aufräumen — sonst löscht ein Aufräumen zur falschen Zeit Befunde, die nie ausgewertet wurden. Der Schlüssel ist überall der **Wortlaut**, nie die Zeilennummer und nie die ID; ändert sich die Passage, greift der Eintrag nicht mehr, und das ist richtig so.

**Deshalb bleiben die IDs rundenlokal.** Eine über die Sitzung hinweg eindeutige Nummerierung wäre für ein Sprachmodell fehleranfällig und bräuchte einen Zähler, der Tage und mehrere Sitzungen überdauert. Die Wiedervorlage-Sperre hängt stattdessen am Wortlaut in der Entscheidungsdatei — und gilt dadurch sogar länger als eine Sitzung.

**Der Prüflauf** ist kein eigener Modus, sondern eine gewöhnliche Runde über einen schon bearbeiteten Text. Sein Eigenwert liegt darin, dass er findet, was frühere Korrekturen erst hineingetragen haben. Vorgeschlagen wird er nach einer ausgeführten Änderung, wenn das Protokoll seit dem letzten mehrere Runden zeigt — nicht am „Ende einer Runde“, denn das ist kein beobachtbarer Moment, es ergibt sich erst, wenn der Nutzer fertig ist.

**Kopf und Protokoll sind kein Beiwerk.** Im Kopf steht, was **nicht** untersucht wurde. Das beantwortet später die Frage, warum eine Stelle damals nicht auffiel — ohne ihn ist das nicht mehr zu rekonstruieren.

**In der Datei stehen Blöcke, keine Tabellenzeilen.** Die Textstücke müssen zeichengenau sein, und manche Editoren richten Markdown-Tabellenzeilen beim Speichern neu aus und fressen dabei Leerraum. Im Chat wird tabellarisch vorgelegt, weil sich das leichter überblicken lässt — dort bekommt ein Fund so viele Tabellenzeilen, wie er braucht, die Folgezeilen lassen ID und Zeilennummer leer, und die Beschriftung (`Vorh`, `Nach`, `Begr`) steht in einer eigenen schmalen Spalte, damit der Text darunter überall an derselben Stelle beginnt. Ein `<br>` in der Zelle wäre der naheliegende Weg, wird aber nicht überall umgesetzt: Im Frontend von Claude Code erscheint es als sichtbarer Text (beobachtet am 25. August 2026, beim ersten Einsatz des Skills).

**Angezeigter und gespeicherter Ausschnitt sind zwei Dinge.** Der angezeigte richtet sich nach der Entscheidung: Der Nutzer muss die Stelle finden und über sie befinden können, ohne den Kontext selbst zusammenzusuchen. Der gespeicherte richtet sich nach der Eindeutigkeit in der Datei, denn er ist die Vorlage für eine exakte Ersetzung. Beide dürfen sich in der Länge unterscheiden; wer das zusammenzieht, bekommt entweder unklare Vorlagen oder verrutschende Ersetzungen.

**Dateinamen und Commit-Marken sind sprachunabhängig.** `editing-findings_`, `editing-data_`, `Findings:` und `Text correction:` stehen wörtlich so in beiden Fassungen. Würden sie mit der Sprache wechseln, fände eine später installierte Fassung die Runden der früheren nicht mehr wieder. Frei in der Sprache sind nur die Beschriftungen innerhalb der Dateien.

## Stand und Offenes

**Status:** Beide Sprachfassungen von `SKILL` und Regeldatei sind fertig, ebenso beide READMEs. Der Regeltext ist mit dem Entwickler durchgesprochen und freigegeben (25. August 2026). Die Erprobung im Betrieb läuft; die ersten Betriebsbefunde (Tabellenformat der Vorlage, Sollzahl zurückgestellter Funde) sind in den Regeltext eingearbeitet (25. August 2026).

**Offen:**

- **Stiller Trigger.** Es fehlen `CLAUDE-snippet.de.md` und `CLAUDE-snippet.en.md`. Der Anker liegt am frühestmöglichen Moment — bevor in einer Sitzung zum ersten Mal ein Text geändert wird, dessen Wortlaut selbst das Produkt ist —, nicht erst beim Vorschlagen einer Korrektur: Der Skillkörper wird nach dem Laden nicht neu gelesen.
- **Nacharbeit aus dem Betrieb.** Ob Rundengröße, Ausschnittlängen und die Form der Vorlage in der Praxis tragen, zeigt erst die Arbeit an einem echten Text.

**Bewusst offen gelassene Entscheidungen:**

- **Rechtschreibregelwerk und Varietät** legt der Skill nicht fest, sondern klärt sie je Text mit dem Nutzer. Sie gehören zum Text, nicht zum Werkzeug, und dürfen bei mehreren Texten verschieden sein.
- **Das Trackingverfahren** ist nur für Git ausformuliert. Nennt der Nutzer ein anderes, prüft der Skill, ob er es bedienen kann. Das im Zielprojekt zu entscheiden ist Absicht.
- **Die Rundengröße von 30 Änderungsstellen** ist ein Vorgabewert, den der Nutzer überschreiben darf — keine Eigenschaft des Verfahrens.
- **Der Zuschnitt der Entscheidungsdateien.** Herangezogen werden alle `editing-data_*` eines Ordners, weil von außen nicht sicher zu erkennen ist, ob zwei Dateien zu einem Text gehören oder nur nebeneinanderliegen. Ein engerer Zuschnitt ließe das Glossar zerfallen. Der Nutzer erfährt, welche Dateien benutzt werden, und kann einzelne ein- oder ausschließen.
- **Ein Prüfskript für die Gegenprobe** ist bewusst nicht dabei. Eine Zusatzdatei im Skill-Ordner kostet keinen Kontext, aber ein Skript müsste das Format der Befunddatei parsen, und das ist noch nicht erprobt. Zeigt sich der Zahlenvergleich per Auge als zu weich, kommt es dazu.
