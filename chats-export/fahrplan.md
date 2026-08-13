# Fahrplan Chats-Export

Reine Aufgabenliste in sinnvoller Reihenfolge. **Keine inhaltlichen Details** — die Fakten je Aufgabe stehen in `implementation_doku.md`, auf die hier nur verwiesen wird. Erledigtes fliegt raus; die Nummern werden dabei **nicht** neu vergeben, damit ein Rückblick im Chat auf „Schritt n" eindeutig bleibt.

**kalt** heißt: mit dem prüfbar, was schon auf der Platte liegt — die heruntergeladenen Export-ZIPs unter `tests/test_results/`, ein Arbeitsordner unter `/tmp`, sonst nichts. Kein Netz, kein Konto, kein fremder Zustand; jederzeit und beliebig oft wiederholbar.

**warm** heißt: nur mit Zugriff auf ein echtes Projekt prüfbar — ein claude.ai-Projekt für `recent_chats`, `read_conversation`, Upload und Projektwissen, oder ein Claude-Code-Projekt als Zielort. Braucht Vorbereitung, ist nicht beliebig wiederholbar und hinterlässt Spuren an der Quelle.

## Als nächstes

15. **Prüfpunkte an einem Ort zusammenfassen und vervollständigen.** Fakten: Doku Kapitel 4, besonders 4.1. Die verstreuten Punkte aus 1.6, 3.2.5 und 1.3 werden in Kapitel 4 als Liste geführt; normativ bleiben sie, wo sie stehen, Kapitel 4 verweist. 4.1 bekommt das Verfahren und je Punkt den Kalt/Warm-Vermerk. *Kalt.*

16. **Projekteigene `CLAUDE.md` anlegen, beschränkt auf den Baum unter `chats-export/`.** Fakten: Arbeitsanweisungen §1.2 und Abschnitt 2, Doku-Kopf. Nur Abweichendes und Zusätzliches. *Kalt.*

17. **Docstring von `chat_export_convert.py` mit dem Code in Übereinstimmung bringen.** Fakten: Doku 3.1.3, 3.1.8, Vorgabe 2.9. Prüfung: `tests/test_docstrings.py` plus Sichtprüfung — der Wächter prüft Vorkommen, nicht Richtigkeit. *Kalt.*

18. **`INSTRUCTION_BLOCK` auf die drei Zielorte und alle vier Dateiarten bringen.** Fakten: Doku 1.3, Vorgaben 2.2 und 2.10. Prüfung: Begriffsliste in `tests/test_docstrings.py` nachziehen. *Kalt geschrieben, Wirkung erst warm prüfbar.*

19. **`analyse` um die Erzeugnisse ergänzen.** Fakten: Doku 3.1.6, 3.1.1. Prüfung: Lauf gegen die vorhandenen ZIPs, Summe gegen `report`. *Kalt.*

14. **`diff` um die Fenstergrenze ergänzen.** Fakten: Doku 2.4. `window_start()` liegt im ZIP-Weg schon vor und wird von `list` gemeldet; `diff` sollte es beim Nachschauen ohne neue Liste auch nennen. Prüfung: Fall in `tests/test_export_convert.py`. *Kalt.*

20. **Doku-Durchgang Zahlen und Kleinstellen.** Fakten: Doku 3.1, 3.2, 3.1.4, 3.1.7, 1.1 sowie `Statusueberblick.md`. Testzahlen, Dateizahlen des Echtlaufs, „bis zu drei Dateien", und der Statusüberblick als Ganzes. *Kalt.*

## Danach

21. **Testprojekt bauen und den mehrstufigen Test fahren.** Fakten: Doku-Kopf (Ende der Entwicklungsphase), 1.5, 2.6, 3.2.3. Ein eigenes claude.ai-Projekt statt des FreeCAD-Projekts, dazu ein Zielrepo. Stufen: Erstlauf, aktives Weiterschreiben eines Chats zwischen zwei Läufen, Sitzungsübergabe, Fortsetzung eines früheren Chats. Beantwortet nebenbei die offene Frage aus 3.1.8. *Warm.*

22. **Erster Durchlauf in ein echtes Zielprojekt.** Fakten: Doku 1.5, Vorgabe 2.10. Zielprojekt steht bewusst noch nicht fest — das ist nicht mehr Entwicklung. Mit 21 und 22 fällt der Entwicklungshinweis am Dokumentkopf. *Warm.*

7. **Forschung: Zuwachs nachladen statt ersetzen.** Fakten: Doku 3.2.5. Gültigkeitsdauer von `page_token` beobachten. *Warm, über mehrere Tage.*

10. **Entscheidung: `chat_crawl_store.py` behalten oder wegräumen?** Fakten: Doku 3.4. Erst nachdem sich 3.1 und 3.2 bewährt haben; das Verhältnis zum übrigen Bestand ist derzeit nicht beurteilbar.

13. **README neu schreiben und die Anwenderdokumentation daraus aufbauen, sobald der Warnhinweis fällt.** Fakten: Doku 1.1, 1.2, 1.5. Einschließlich der Nutzerpflicht, die Aufbewahrungsdauer hochzusetzen, bevor nach `~/.claude/projects/` abgelegt wird (1.3).

## Dauerhaft

- Kapitel 4 der Doku ist die Prüfliste gegen Anthropic-Änderungen; die Belege dazu tragen 1.6 und Kapitel 3. Ändert sich etwas: Zeile korrigieren, prüfen, was daran hing, gekippte Annahmen nach 1.7.
- Neue Prüfpunkte gehören nach Kapitel 4, jeder mit Kalt/Warm-Vermerk.
- Die README trägt den Warnhinweis, solange nichts benutzbar ist; Widersprüche zwischen ihr und der Doku sind bis dahin erlaubt (Doku-Kopf).
- Neues Feature mit eigenem Konzept (Feldname, Dateiendung, Funktion): die Begriffsliste in `tests/test_docstrings.py` nachziehen. Kommandos und `--Flags` prüft der Test von selbst, Begriffe nicht.
