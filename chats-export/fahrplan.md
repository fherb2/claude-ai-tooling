# Fahrplan Chats-Export

Reine Aufgabenliste in sinnvoller Reihenfolge. **Keine inhaltlichen Details** — die Fakten je Aufgabe stehen in `implementation_doku.md`, auf die hier nur verwiesen wird. Erledigtes fliegt raus; die Nummern werden dabei **nicht** neu vergeben, damit ein Rückblick im Chat auf „Schritt n" eindeutig bleibt.

Die Prüfarten in Kurzfassung; normativ stehen sie in **Doku 4.1**, dort auch die dritte Art (**Beobachtung** — nicht prüfbar, nur bemerkbar, wenn sie kippt).

**kalt** heißt: mit dem prüfbar, was schon auf der Platte liegt — die heruntergeladenen Export-ZIPs unter `tests/test_results/`, ein Arbeitsordner unter `/tmp`, sonst nichts. Kein Netz, kein Konto, kein fremder Zustand; jederzeit und beliebig oft wiederholbar.

**warm** heißt: nur mit Zugriff auf ein echtes Projekt prüfbar — ein claude.ai-Projekt für `recent_chats`, `read_conversation`, Upload und Projektwissen, oder ein Claude-Code-Projekt als Zielort. Braucht Vorbereitung, ist nicht beliebig wiederholbar und hinterlässt Spuren an der Quelle.

## Als nächstes

*(derzeit nichts — die kalte Liste ist abgearbeitet, es fehlen nur noch warme Punkte.)*

## Danach

21. **Testprojekt bauen und den mehrstufigen Test fahren.** Fakten: Doku-Kopf (Ende der Entwicklungsphase), 1.5, 2.6, 3.2.3. Ein eigenes claude.ai-Projekt statt des FreeCAD-Projekts, dazu ein Zielrepo. Stufen: Erstlauf, aktives Weiterschreiben eines Chats zwischen zwei Läufen, Sitzungsübergabe, Fortsetzung eines früheren Chats. Beantwortet nebenbei die offene Frage aus 3.1.8. *Warm.*

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
