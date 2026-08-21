# Fahrplan Chats-Export

Reine Aufgabenliste in sinnvoller Reihenfolge. **Keine inhaltlichen Details** — die Fakten je Aufgabe stehen in `implementation_doku.md`, auf die hier nur verwiesen wird. Erledigtes fliegt raus; die Nummern werden dabei **nicht** neu vergeben, damit ein Rückblick im Chat auf „Schritt n" eindeutig bleibt.

Die Prüfarten in Kurzfassung; normativ stehen sie in **Doku 4.1**, dort auch die dritte Art (**Beobachtung** — nicht prüfbar, nur bemerkbar, wenn sie kippt).

**kalt** heißt: mit dem prüfbar, was schon auf der Platte liegt — die heruntergeladenen Export-ZIPs unter `tests/test_results/`, ein Arbeitsordner unter `/tmp`, sonst nichts. Kein Netz, kein Konto, kein fremder Zustand; jederzeit und beliebig oft wiederholbar.

**warm** heißt: nur mit Zugriff auf ein echtes Projekt prüfbar — ein claude.ai-Projekt für `recent_chats`, `conversation_search`, Upload und Projektwissen, oder ein Claude-Code-Projekt als Zielort. Braucht Vorbereitung, ist nicht beliebig wiederholbar und hinterlässt Spuren an der Quelle.

## Als nächstes

27. **Ein Skill, der beide Wege anbietet, die Lage feststellt und den passenden vorschlägt.** *Warm für den Lauf, kalt für den Bau.* — **Plan, noch nicht ausgeführt.**

    **Der Zuschnitt.** Der Skill erklärt, stellt den Abgleich her, empfiehlt und führt aus, was ausführbar ist. Er **entscheidet nicht**: Die Wahl zwischen den Wegen bleibt beim Nutzer, wie sie es seit 1.2 ist. Und er **rechnet nicht selbst** — jeder Vergleich läuft durch ein Skript, das die JSON parst; die Instanz trägt nur vor. Das ist die Lehre aus den zehn statt neun Einträgen (1.4).

    **Name, Aufruf, Ablage — entschieden.** Der Skill heißt `chat-export`, Ordner und Frontmatter-`name` gleichlautend, Aufruf also `/chat-export`. Gepflegt wird er **ausschließlich in `chat-export/skills/chat-export/`** — nach der Regel aus `skills/skill_vorgaben.md` 1.1 trägt der Ordner hier genau die Struktur, die er am Zielort haben wird, weshalb der innere Ordnername dem Skillnamen gleicht. Das ist der Entwicklerordner und die Stelle, aus der der Nutzer sich seine Fassung holt. Am Zielort liegen `SKILL.md`, `README.md` und `chat_export_convert.py` **flach in einem Ordner**; das Skript spricht der Skill über `${CLAUDE_SKILL_DIR}` an, der in Claude Code aufgelöst wird und damit beide Ablageorte ohne Textänderung trägt. Ein stiller Trigger entfällt: Der Auslöser ist eine ausgesprochene Anfrage, also ereignisförmig — damit gibt es keine `CLAUDE-snippet.md` und in der README keinen Schritt dafür.

    **Zum Testen** wird eine Kopie in `.claude/skills/chat-export/` dieses Repos abgelegt und **nach dem Test wieder entfernt**. Sie ist Prüfaufbau, nicht Ablage. Im Projekt liegt der Ordner innerhalb der Wurzel, Lesen und Ausführen sind normale Handgriffe; erst die spätere Variante unter `~/.claude/skills/` liegt außerhalb des Arbeitsverzeichnisses und braucht die Freigabe als zusätzliches Verzeichnis — dieselbe Bedingung wie beim dritten Zielort (1.3).

    **Keine zweite gepflegte Fassung, also keine Drift-Sicherung.** `chat_export_convert.py` liegt genau einmal im Repo, und zwar **im Skill-Ordner** `chat-export/skills/chat-export/` — es ist das eine Skript, das der Skill mitbringt, und der Ordner trägt damit genau die Struktur, die er am Zielort haben wird. Der Nutzer kopiert diesen Ordner als Ganzes, nichts weiter. Die drei übrigen Skripte bleiben in `source/`, weil sie eigene Aufgaben haben und nicht zum Skill gehören: `inspect_export.py` als Diagnose des Export-ZIP, `chat_read_store.py` als zweite Umsetzung, an der Vorgabe 2.5 gemessen wird, `chat_crawl_store.py` bis zur Entscheidung in Punkt 10. Eine Prüfsumme oder ein Versionsabgleich wäre Maschinerie für ein Problem, das diese Anordnung nicht hat.

    **Die Arbeitsteilung, in einem Satz:** Die Instanz **deutet und ordnet zu**, das Skript **zählt und vergleicht**. Das Deuten ist die Stärke der Instanz — eine Aufzählung von Projektnamen mit Tippfehlern auf die echte Liste abbilden, oder auf „zeig mir einfach alle" sinnvoll reagieren; ein Skript kann das schlechter. Das Zählen ist ihre Schwäche, belegt mit zehn statt neun (1.4). Beides bleibt dort, wo es hingehört.

    **Genau zwei Haltepunkte, sonst keine.**

    - **Erster:** Der Skill erklärt kurz, was er tut, und fragt, ob er beginnen kann. Ein Ja ist die Zustimmung für alles Lesende — Kontoauskunft, Projektliste, Chatlisten, Abgleich.
    - **Dazwischen** nennt er das **Konto**, mit dem Chrome bei claude.ai angemeldet ist, und dass dort gesucht wird. Das ersetzt jede vorherige Anweisung, sich anzumelden: Der Nutzer kann sich besinnen, und ein fehlendes Login fällt an derselben Stelle auf. Nur wenn die Projektwahl unklar bleibt, fragt er hier nach — hat der Nutzer die Projekte schon genannt, fragt er nicht.
    - **Zweiter:** Nach der Statistik wählt der Nutzer je Projekt den Weg. Darauf folgt **ein** Hinweis, was nun geschieht — und der **nennt die Zahl der zu ersetzenden Chats und ihrer zu entfernenden Dateien**, denn das ist Löschen und darf nicht in einem allgemeinen Satz untergehen.

    Der Anweisungsblock für die `CLAUDE.md` des Zielprojekts wird deshalb **Schlussbemerkung, nicht Frage** — sonst entstünde ein dritter Haltepunkt.

    **Mehrere Quellprojekte in einem Lauf sind vorgesehen.** Der Nutzer zählt sie auf, oder er sagt nur, dass er aus dem Konto importieren will, und bekommt alle angezeigt — dann hat er eine Vorlage vor sich. Damit die Haltepunkte bei zwei bleiben, steht die Statistik als **eine** Tabelle mit einer Zeile je Projekt samt eigener Empfehlung, und der Nutzer antwortet **einmal** für alle.

    **Was am Code dazukommt** — bewusst wenig, weil die Struktur beider Quellen sich als gleich erwiesen hat (Nachrichten-UUIDs deckungsgleich, dieselben Felder `uuid`, `sender`, `content`, `parent_message_uuid`, `attachments`, `files`):

    - `chat_export_convert.py` bekommt eine **zweite Eingangsart**: `convert --bundle <datei>` neben `--zip`. Baumlauf, Blockauswahl, Nebendateien und Protokollführung bleiben unverändert — nur der Behälter ist ein anderer. Damit ist die Wegegleichheit hier **baulich** gegeben statt bloß geprüft.
    - `list` bekommt `--web <datei>` als Gegenstück zu `--map <dump>`: Protokoll anlegen oder ergänzen aus der Liste des Web-Wegs. Diese Liste trägt `created_at` und `project_uuid` je Chat — beides kannte der bisherige Weg nicht.
    - Zu prüfen, ob `diff` die UUIDs der zu holenden Chats schon nennt. Falls nicht, kommt eine Ausgabeform dazu, die der Skill an den Abruf weiterreicht.
    - Ob das flache Feld `text` im Web-Behälter fehlt, ist zu prüfen; der Konverter benutzt es nicht (3.1.3), aber die Annahme gehört bestätigt.

    **Was der Skill vom Nutzer braucht und in seiner README nennt:** angehängte Browser-Werkzeuge (in VS Code `@browser` je Nachricht, im CLI `claude --chrome`), und in Chrome ausgeschaltetes Nachfragen nach dem Speicherort — ein Dialog blockiert die Anbindung vollständig. **Nicht** dazu gehört die Anweisung, sich anzumelden: Das nennt der Skill zur Laufzeit.

    **Der erste kleine Handgriff, und er entscheidet über den ersten Haltepunkt:** Gibt claude.ai ohne Vorwissen Auskunft über das angemeldete Konto und seine Organisations-UUID? Gebraucht wird beides — der Kontoname für die Nennung, die UUID für jeden weiteren Aufruf. Die UUID steht ersatzweise im Dateinamen jedes Export-ZIP, der Kontoname dort nicht. Ein Endpunkt ohne Organisationsangabe müsste beides liefern; ungeprüft, eine Probe von Minuten.

    **Zwei Vereinfachungen, die dabei anfallen** und in die Doku gehören: Der Rückweg des Protokolls ins Projektwissen des Quellprojekts (1.4, 1.5 Schritt 4) wird **entbehrlich** — er trug den Lese-Weg, den es nicht mehr gibt; als Selbstauskunft des Quellprojekts bleibt er nützlich, als Pflicht entfällt er. Und der Wegwerfchat für die Chatliste samt der Regel, ihn zu löschen (1.5), entfällt vollständig: Der Web-Weg listet ohne Chat und übergeht nichts.

    **Das angestrebte Verhalten aus Nutzersicht** steht als Durchgang in `Zielvorlage.md` — Beurteilungsgrundlage und spätere Vorlage der Anwenderdokumentation, ausdrücklich kein zweiter Plan.

    **Nicht Teil dieses Punktes:** das Anfordern des Exports über das Formular. Das ist ein eigener, kleiner Schritt, sobald der Skill steht — und er endet ohnehin an der E-Mail.

## Danach

21. **Testprojekt bauen und den mehrstufigen Test fahren.** Fakten: Doku-Kopf (Ende der Entwicklungsphase), 1.5, 2.6, 3.2. Ein eigenes claude.ai-Projekt statt des FreeCAD-Projekts, dazu ein Zielrepo. Stufen: Erstlauf, aktives Weiterschreiben eines Chats zwischen zwei Läufen, Sitzungsübergabe, Fortsetzung eines früheren Chats. Beantwortet nebenbei die offene Frage aus 3.1.8. *Warm.*

    **Der laufende Stand steht in `testlauf.md`** — was angelegt, was beobachtet, was noch offen ist. Die Datei endet mit diesem Punkt; ihr Kopf sagt, wohin ihr Inhalt dann wandert.

    **Den Takt gibt der Export vor.** Antrag, E-Mail, Download, Link 24 Stunden gültig — jeder Export ist eine Wartezeit, also muss der Inhalt, den er einfangen soll, vorher vollständig da sein. Die zweite Bedingung ist inzwischen erfüllt: Der Zeitraumfilter arbeitet auf Tagesebene, zwischen Anlegen und Fortschreiben mussten **Tage** liegen, und der Tageswechsel ist seit dem 18. August da. Alles Kalte gehört deshalb in die Wartezeit zwischen Anforderung und Eintreffen.

    **Block A — Fortschreiben, ab jetzt**

    - **21.9 Bewegung erzeugen** *(Nutzer)* — den wachsenden Chat fortsetzen, einen neuen anlegen, einen löschen. **Im selben Zug** die beiden Merkmale nacherzeugen, die im ersten Lauf ausblieben: Denkschritte und Erzeugnis, nach den korrigierten Rezepten in Doku 4.1. Das dritte, die Sendewiederholung, bleibt außen vor — für sie ist kein Rezept bekannt.
    - **21.10 Zweiter Abgleich** *(Nutzer holt die Liste, Claude Code `list`/`diff`)* — erwartet: `stale`, `listed`, ein gesetztes `created_after`, und der gelöschte wird gemeldet, aber nicht entfernt. Die neue Fenstergrenze ist das eigentliche Ergebnis.
    - **21.11 Zweiter Export über genau dieses Fenster** *(Nutzer, dann Claude Code)* — der Kern der ganzen Konstruktion: Reicht das errechnete Fenster wirklich weit genug zurück, um den fortgeschriebenen Altchat zu erfassen? Dazu Ersetzen samt Aufräumen der alten Nebendateien. **Sofort nach 21.10 anfordern** — es ist das Einzige mit Wartezeit.

    **Block B — Rückweg, Lese-Weg und der Härtetest**

    - **21.8 Rückweg** *(Nutzer)* — Protokoll ins Projektwissen des Quellprojekts, Anweisungsblock in die `CLAUDE.md` des Zielprojekts. Diese Übergabestelle ist noch nie gelaufen. **Nach 21.11**, weil das Protokoll sich in Block A ohnehin ändert und ein zweiter Upload nichts Neues zeigte — aber **vor 21.12**, das ohne das Protokoll im Projektwissen nicht arbeiten kann. Offen ist das Zielprojekt: Es gibt keines, und die zweite Hälfte des Schrittes verlangt eines. Vorgesehen ist ein Wegwerf-Ordner außerhalb dieser Projektwurzel; die Abgrenzung zu Punkt 22 ist dabei zu ziehen.
    - **21.12 Lese-Weg im Quellprojekt** *(Nutzer lädt Skript und Protokoll hoch, die Instanz arbeitet)* — `plan`, `map`, `ingest`, `export`, dazu die Sitzungsübergabe am langen Chat. Prüft die Betriebsanleitung im Docstring an einer Instanz, die nichts von uns weiß.
    - **21.13 Wegegleichheit an echten Daten** *(Claude Code, kalt)* — denselben Chat aus beiden Wegen vergleichen; genau fünf Metadatenfelder dürfen abweichen. **Nicht** am wachsenden Chat, der ein bewegtes Ziel wäre; vorgesehen sind ein schlichter Grundfall und Chat 1 als Härtefall (Gabelung und Sendewiederholung sieht der Lese-Weg nicht).

    **Der Prüfplan.** Je Schritt, was er beweisen soll und was ein Fehlschlag bedeutet. 21.9 fehlt: Er erzeugt nur Material.

    - **21.10** — *Erwartung:* der fortgesetzte Chat `stale`, der neue `listed` mit einem `created_after` auf dem Zeitpunkt des ersten Abgleichs, der gelöschte gemeldet und **nicht** entfernt; daraus eine neue Fenstergrenze. *Fehlschlag:* `updated_at` trägt die Veraltungserkennung nicht — dann fällt die Grundlage von Vorgabe 2.4 und 2.6.
    - **21.11** — *Erwartung:* Der zweite Export über genau das errechnete Fenster enthält den fortgeschriebenen Altchat; `convert` ersetzt ihn und **nennt** die entfernten Vorgängerdateien; der Waisen-Scan meldet nichts. Dazu die nacherzeugten Merkmale: eine Denkdatei und eine Erzeugnisdatei, die im ersten Lauf beide fehlten. *Fehlschlag:* stiller Inhaltsverlust — der gefährlichste Fall überhaupt, weil ein zu knappes Fenster nichts meldet, sondern einfach weniger liefert.
    - **21.8** — *Erwartung:* `protokoll.json` wird als Projektdatei angenommen und ist im nächsten Chat des Quellprojekts lesbar; und die **Zielinstanz sieht von selbst im Archiv nach**, wenn man sie nach etwas fragt, das nur in den Testchats vorkam. *Fehlschlag:* Der Rückweg aus 1.4/1.5 trägt nicht, oder der Anweisungsblock wirkt nicht — Letzteres ist nur so prüfbar, alles andere wäre die bloße Behauptung, er wirke.
    - **21.12** — *Erwartung:* Eine Instanz, die nichts von diesem Vorhaben weiß, arbeitet allein aus dem Docstring; `plan` legt die Lage richtig vor; `export` behauptet Vollständigkeit nur gegen `total_turns`; die Sitzungsübergabe am langen Chat gelingt. *Fehlschlag:* Die Betriebsanleitung ist unvollständig — 3.2 nachziehen, und zwar dort, wo die Instanz gestockt hat.
    - **21.13** — *Erwartung:* genau fünf abweichende Metadatenfelder, und nach Abzug der Referenzfelder zwei identische Transkripte. *Fehlschlag:* Vorgabe 2.5 ist an echten Daten verletzt — der schwerste denkbare Befund dieses Vorhabens, weil dann „habe ich diesen Chat?" unscharf wird.

    Für jeden Fehlschlag gilt, was unter „Dauerhaft" steht: gekippte Annahme nach Doku 1.7, geänderte Umgebungstatsache nach Kapitel 4.

    **Danach die Auswertung:** gekippte Annahmen nach 1.7, Kapitel 4 nachziehen, die offene Frage aus 3.1.8 entscheiden, Punkt 10 entscheiden. Erst dann 22 und der Wegfall des Entwicklungshinweises.

    **Was das an Exporten kostet:** drei — die Sondierung (winzig), der Erstlauf, der Nachpflegelauf. Weniger geht nicht, ohne eine der drei Behauptungen ungeprüft zu lassen. Alles, was Claude Code kalt tun kann, liegt bewusst zwischen den Wartezeiten.

22. **Erster Durchlauf in ein echtes Zielprojekt.** Fakten: Doku 1.5, Vorgabe 2.10. Zielprojekt steht bewusst noch nicht fest — das ist nicht mehr Entwicklung. Mit 21 und 22 fällt der Entwicklungshinweis am Dokumentkopf. *Warm.*

23. **Probe: Arbeitet der Lese-Weg in einem Team-Projekt?** Fakten: Doku 1.2, 1.6, 3.2. Für Chats, die in einem Team-Konto liegen, ist er der einzige Weg — ob `read_conversation` dort ebenso greift wie im Pro-Konto, ist unbelegt. Ein Chat, ein `ingest`, mehr nicht; das vorhandene Testprojekt im Team-Konto bleibt dafür stehen. *Warm.*

24. **Gegenprobe am FreeCAD-Altbestand.** Fakten: Doku 1.6, 1.7. Die heutige Chatliste des Projekts gegen das Protokoll halten: Fehlt dort ein Chat, der älter ist als der damalige Export, ist die Auslassung des laufenden Chats an echten Daten bestätigt und die stille Lücke einmal vorgeführt. Kostet eine Abfrage. *Warm.*

7. **Forschung: Zuwachs nachladen statt ersetzen.** Fakten: Doku 3.2. **Derzeit nicht ausführbar** — die Frage galt der Gültigkeitsdauer eines `page_token`, und das Werkzeug, das sie ausgibt, gibt es nicht mehr. Ob der Punkt bleibt, entscheidet sich mit dem Fahrplan-Durchgang. *Warm.*

10. **Entscheidung: `chat_crawl_store.py` behalten oder wegräumen?** Fakten: Doku 3.4. Erst nachdem sich 3.1 und 3.2 bewährt haben; das Verhältnis zum übrigen Bestand ist derzeit nicht beurteilbar.

13. **README neu schreiben und die Anwenderdokumentation daraus aufbauen, sobald der Warnhinweis fällt.** Fakten: Doku 1.1, 1.2, 1.5. Einschließlich der Nutzerpflicht, die Aufbewahrungsdauer hochzusetzen, bevor nach `~/.claude/projects/` abgelegt wird (1.3).

    **Zwei Sätze zur Wegewahl gehören hinein**, Wortlaut und Begründung stehen in `testlauf.md`: Der Web-Weg ist der Weg für kleine Nach-Exporte; sonst bereitet er nur die Protokolldatei vor, und die Inhalte kommen als Kontoexport-ZIP. Dazu die Nutzerpflicht, in Chrome das Nachfragen nach dem Speicherort abzuschalten.

## Dauerhaft

- Kapitel 4 der Doku ist die Prüfliste gegen Anthropic-Änderungen; die Belege dazu tragen 1.6 und Kapitel 3. Ändert sich etwas: Zeile korrigieren, prüfen, was daran hing, gekippte Annahmen nach 1.7.
- Neue Prüfpunkte gehören nach Kapitel 4, jeder mit seiner Prüfart — kalt, warm oder Beobachtung, normativ in Doku 4.1.
- Der Entwicklungshinweis am Kopf der Doku gilt, solange die Phase läuft: halbfertige Passagen sind Normalzustand, Widersprüche zur README erlaubt, Widersprüche innerhalb der Doku und zwischen Doku und Code dagegen Defekte mit eigenem Fahrplanpunkt. Dort steht auch, woran die Phase endet.
- Dieses Vorhaben bekommt **keine** eigene `CLAUDE.md` und keine pfadgebundene Regel. Was dauerhaft gilt, steht hier oder in der Doku; die Begründung trägt die Repo-`CLAUDE.md`.
- Die README trägt den Warnhinweis, solange nichts benutzbar ist; Widersprüche zwischen ihr und der Doku sind bis dahin erlaubt (Doku-Kopf).
- Neues Feature mit eigenem Konzept (Feldname, Dateiendung, Funktion): die Begriffsliste in `tests/test_docstrings.py` nachziehen. Kommandos und `--Flags` prüft der Test von selbst, Begriffe nicht.
