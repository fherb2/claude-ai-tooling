# Fahrplan Chats-Export

Reine Aufgabenliste in sinnvoller Reihenfolge. **Keine inhaltlichen Details** — die Fakten je Aufgabe stehen in `implementation_doku.md`, auf die hier nur verwiesen wird. Erledigtes fliegt raus; die Nummern werden dabei **nicht** neu vergeben, damit ein Rückblick im Chat auf „Schritt n" eindeutig bleibt.

Die Prüfarten in Kurzfassung; normativ stehen sie in **Doku 4.1**, dort auch die dritte Art (**Beobachtung** — nicht prüfbar, nur bemerkbar, wenn sie kippt).

**kalt** heißt: mit dem prüfbar, was schon auf der Platte liegt — die heruntergeladenen Export-ZIPs unter `tests/test_results/`, ein Arbeitsordner unter `/tmp`, sonst nichts. Kein Netz, kein Konto, kein fremder Zustand; jederzeit und beliebig oft wiederholbar.

**warm** heißt: nur mit Zugriff auf ein echtes Projekt prüfbar — ein claude.ai-Projekt für `recent_chats`, `read_conversation`, Upload und Projektwissen, oder ein Claude-Code-Projekt als Zielort. Braucht Vorbereitung, ist nicht beliebig wiederholbar und hinterlässt Spuren an der Quelle.

## Als nächstes

*(derzeit nichts — die kalte Liste ist abgearbeitet, es fehlen nur noch warme Punkte.)*

## Danach

21. **Testprojekt bauen und den mehrstufigen Test fahren.** Fakten: Doku-Kopf (Ende der Entwicklungsphase), 1.5, 2.6, 3.2.3. Ein eigenes claude.ai-Projekt statt des FreeCAD-Projekts, dazu ein Zielrepo. Stufen: Erstlauf, aktives Weiterschreiben eines Chats zwischen zwei Läufen, Sitzungsübergabe, Fortsetzung eines früheren Chats. Beantwortet nebenbei die offene Frage aus 3.1.8. *Warm.*

    **Zwei Dinge geben den Takt vor.** Der Kontoexport hat Vorlaufzeit — Antrag, E-Mail, Download, Link 24 Stunden gültig; jeder Export ist eine Wartezeit, also muss der Inhalt, den er einfangen soll, vorher vollständig da sein. Und der Zeitraumfilter arbeitet auf Tagesebene: Damit „alter Chat, letzte Woche weitergelaufen" überhaupt prüfbar wird, müssen zwischen Anlegen und Fortschreiben **Tage** liegen. Das ist der einzige Schritt mit echter Vorlaufzeit und deshalb der, der zuerst passieren muss, während wir anderes tun.

    **Block A — sofort, weil die Uhr läuft**

    - **21.1 Prüfplan festschreiben** *(Claude Code, kalt)* — je Stufe: was sie beweisen soll, woran man es erkennt, was ein Fehlschlag bedeutet. Ohne das läuft man in Exporte und merkt hinterher, dass ein Merkmal fehlte. Dazu gehört, das **Profil des Testprojekts** in Doku 4.1 festzuschreiben — welche strukturellen Merkmale es tragen muss und warum; es ist das dort benannte fehlende warme Prüfwerkzeug und wird nach jeder Anthropic-Änderung wieder gebraucht.
    - **21.2 Testprojekt anlegen und nach Profil füllen** *(Nutzer, claude.ai)* — der Schritt mit Vorlaufzeit. Anlegedatum notieren: Es ist der **Sollwert** für den Sondierungsexport.
    - **21.3 Sondierungsexport anfordern** *(Nutzer)* — **parallel zu 21.2**, denn er braucht die Chats gar nicht: Ein Zeitraum von einem Tag, der vor dem Projekt liegt, liefert trotzdem alle Projektdateien. Genau das ist die Behauptung, die geprüft wird, und es ist der billigste Export überhaupt.
    - **21.4 Sondierung auswerten** *(Claude Code, kalt)* — `inspect_export.py`; das gefundene Projektdatum muss dem notierten aus 21.2 entsprechen.

    **Block B — Erstlauf über den Export**

    - **21.5 Chatliste holen** *(Nutzer im Quellprojekt)* — mit `MAPPING_PROMPT` wörtlich; prüft ihn an einer frischen Instanz.
    - **21.6 Protokoll anlegen** *(Claude Code)* — `list --project-created`; die gemeldete Fenstergrenze muss auf das Projektdatum zeigen.
    - **21.7 Export anfordern und umwandeln** *(Nutzer, dann Claude Code)* — `convert`, dann `diff`, `report`, `analyse` gegeneinander halten. Erwartet: alle vier Dateiarten, jedes Profilmerkmal wiedergefunden.
    - **21.8 Rückweg** *(Nutzer)* — Protokoll ins Projektwissen des Quellprojekts, Anweisungsblock in die `CLAUDE.md` des Zielprojekts. Diese Übergabestelle ist noch nie gelaufen.

    **Block C — Fortschreiben, frühestens einige Tage nach 21.2**

    - **21.9 Bewegung erzeugen** *(Nutzer)* — einen alten Chat fortsetzen, einen neuen anlegen, einen löschen.
    - **21.10 Zweiter Abgleich** *(Nutzer holt die Liste, Claude Code `list`/`diff`)* — erwartet: `stale`, `listed`, ein gesetztes `created_after`, und der gelöschte wird gemeldet, aber nicht entfernt. Die neue Fenstergrenze ist das eigentliche Ergebnis.
    - **21.11 Zweiter Export über genau dieses Fenster** *(Nutzer, dann Claude Code)* — der Kern der ganzen Konstruktion: Reicht das errechnete Fenster wirklich weit genug zurück, um den fortgeschriebenen Altchat zu erfassen? Dazu Ersetzen samt Aufräumen der alten Nebendateien.

    **Block D — Lese-Weg und der Härtetest**

    - **21.12 Lese-Weg im Quellprojekt** *(Nutzer lädt Skript und Protokoll hoch, die Instanz arbeitet)* — `plan`, `map`, `ingest`, `export`, dazu die Sitzungsübergabe am langen Chat. Prüft die Betriebsanleitung im Docstring an einer Instanz, die nichts von uns weiß.
    - **21.13 Wegegleichheit an echten Daten** *(Claude Code, kalt)* — denselben Chat aus beiden Wegen vergleichen; genau fünf Metadatenfelder dürfen abweichen. Das ist der schärfste Test, den dieses Vorhaben kennt, und er lief bisher nur gegen synthetische Daten.

    **Danach die Auswertung:** gekippte Annahmen nach 1.7, Kapitel 4 nachziehen, die offene Frage aus 3.1.8 entscheiden, Punkt 10 entscheiden. Erst dann 22 und der Wegfall des Entwicklungshinweises.

    **Was das an Exporten kostet:** drei — die Sondierung (winzig), der Erstlauf, der Nachpflegelauf. Weniger geht nicht, ohne eine der drei Behauptungen ungeprüft zu lassen. Alles, was Claude Code kalt tun kann, liegt bewusst zwischen den Wartezeiten.

22. **Erster Durchlauf in ein echtes Zielprojekt.** Fakten: Doku 1.5, Vorgabe 2.10. Zielprojekt steht bewusst noch nicht fest — das ist nicht mehr Entwicklung. Mit 21 und 22 fällt der Entwicklungshinweis am Dokumentkopf. *Warm.*

7. **Forschung: Zuwachs nachladen statt ersetzen.** Fakten: Doku 3.2.5. Gültigkeitsdauer von `page_token` beobachten. *Warm, über mehrere Tage.*

10. **Entscheidung: `chat_crawl_store.py` behalten oder wegräumen?** Fakten: Doku 3.4. Erst nachdem sich 3.1 und 3.2 bewährt haben; das Verhältnis zum übrigen Bestand ist derzeit nicht beurteilbar.

13. **README neu schreiben und die Anwenderdokumentation daraus aufbauen, sobald der Warnhinweis fällt.** Fakten: Doku 1.1, 1.2, 1.5. Einschließlich der Nutzerpflicht, die Aufbewahrungsdauer hochzusetzen, bevor nach `~/.claude/projects/` abgelegt wird (1.3).

## Dauerhaft

- Kapitel 4 der Doku ist die Prüfliste gegen Anthropic-Änderungen; die Belege dazu tragen 1.6 und Kapitel 3. Ändert sich etwas: Zeile korrigieren, prüfen, was daran hing, gekippte Annahmen nach 1.7.
- Neue Prüfpunkte gehören nach Kapitel 4, jeder mit seiner Prüfart — kalt, warm oder Beobachtung, normativ in Doku 4.1.
- Der Entwicklungshinweis am Kopf der Doku gilt, solange die Phase läuft: halbfertige Passagen sind Normalzustand, Widersprüche zur README erlaubt, Widersprüche innerhalb der Doku und zwischen Doku und Code dagegen Defekte mit eigenem Fahrplanpunkt. Dort steht auch, woran die Phase endet.
- Dieses Vorhaben bekommt **keine** eigene `CLAUDE.md` und keine pfadgebundene Regel. Was dauerhaft gilt, steht hier oder in der Doku; die Begründung trägt die Repo-`CLAUDE.md`.
- Die README trägt den Warnhinweis, solange nichts benutzbar ist; Widersprüche zwischen ihr und der Doku sind bis dahin erlaubt (Doku-Kopf).
- Neues Feature mit eigenem Konzept (Feldname, Dateiendung, Funktion): die Begriffsliste in `tests/test_docstrings.py` nachziehen. Kommandos und `--Flags` prüft der Test von selbst, Begriffe nicht.
