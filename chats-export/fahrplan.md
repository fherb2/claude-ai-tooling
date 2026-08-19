# Fahrplan Chats-Export

Reine Aufgabenliste in sinnvoller Reihenfolge. **Keine inhaltlichen Details** — die Fakten je Aufgabe stehen in `implementation_doku.md`, auf die hier nur verwiesen wird. Erledigtes fliegt raus; die Nummern werden dabei **nicht** neu vergeben, damit ein Rückblick im Chat auf „Schritt n" eindeutig bleibt.

Die Prüfarten in Kurzfassung; normativ stehen sie in **Doku 4.1**, dort auch die dritte Art (**Beobachtung** — nicht prüfbar, nur bemerkbar, wenn sie kippt).

**kalt** heißt: mit dem prüfbar, was schon auf der Platte liegt — die heruntergeladenen Export-ZIPs unter `tests/test_results/`, ein Arbeitsordner unter `/tmp`, sonst nichts. Kein Netz, kein Konto, kein fremder Zustand; jederzeit und beliebig oft wiederholbar.

**warm** heißt: nur mit Zugriff auf ein echtes Projekt prüfbar — ein claude.ai-Projekt für `recent_chats`, `conversation_search`, Upload und Projektwissen, oder ein Claude-Code-Projekt als Zielort. Braucht Vorbereitung, ist nicht beliebig wiederholbar und hinterlässt Spuren an der Quelle.

## Als nächstes

*(derzeit nichts — Punkt 26 ist ausgeführt und bestanden; die Bauentscheidung daraus ist noch nicht formuliert.)*

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

## Dauerhaft

- Kapitel 4 der Doku ist die Prüfliste gegen Anthropic-Änderungen; die Belege dazu tragen 1.6 und Kapitel 3. Ändert sich etwas: Zeile korrigieren, prüfen, was daran hing, gekippte Annahmen nach 1.7.
- Neue Prüfpunkte gehören nach Kapitel 4, jeder mit seiner Prüfart — kalt, warm oder Beobachtung, normativ in Doku 4.1.
- Der Entwicklungshinweis am Kopf der Doku gilt, solange die Phase läuft: halbfertige Passagen sind Normalzustand, Widersprüche zur README erlaubt, Widersprüche innerhalb der Doku und zwischen Doku und Code dagegen Defekte mit eigenem Fahrplanpunkt. Dort steht auch, woran die Phase endet.
- Dieses Vorhaben bekommt **keine** eigene `CLAUDE.md` und keine pfadgebundene Regel. Was dauerhaft gilt, steht hier oder in der Doku; die Begründung trägt die Repo-`CLAUDE.md`.
- Die README trägt den Warnhinweis, solange nichts benutzbar ist; Widersprüche zwischen ihr und der Doku sind bis dahin erlaubt (Doku-Kopf).
- Neues Feature mit eigenem Konzept (Feldname, Dateiendung, Funktion): die Begriffsliste in `tests/test_docstrings.py` nachziehen. Kommandos und `--Flags` prüft der Test von selbst, Begriffe nicht.
