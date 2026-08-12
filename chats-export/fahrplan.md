# Fahrplan Chats-Export

Reine Aufgabenliste in sinnvoller Reihenfolge. **Keine inhaltlichen Details** — die Fakten je Aufgabe stehen in `implementation_doku.md`, auf die hier nur verwiesen wird. Erledigtes fliegt raus; die Nummern werden dabei **nicht** neu vergeben, damit ein Rückblick im Chat auf „Schritt n" eindeutig bleibt.

## Als nächstes

## Danach


7. **Forschung: Zuwachs nachladen statt ersetzen.** Fakten: Doku 3.2.5. Gültigkeitsdauer von `page_token` beobachten.

14. **`diff` um die Fenstergrenze ergänzen.** Fakten: Doku 2.4. `window_start()` liegt im ZIP-Weg schon vor und wird von `list` gemeldet; `diff` sollte es beim Nachschauen ohne neue Liste auch nennen.


10. **Entscheidung: `chat_crawl_store.py` behalten oder wegräumen?** Fakten: Doku 3.4. Erst nachdem sich 2 bis 5 bewährt haben. Enthält noch `predecessor`/`successor` in altem Zustand — bewusst nicht mitgezogen, solange die Entscheidung offen ist.

13. **README neu schreiben, sobald der Warnhinweis fällt.** Sie nennt den Lese-Weg noch „bevorzugt“ und hinkt der Richtungsentscheidung aus Doku 1.2 hinterher (der Export ist der reichere Weg). Solange der Nicht-benutzen-Hinweis darüber steht, ist das unschädlich — beim Freigeben wird sie aus Doku 1.1, 1.2 und 1.5 neu aufgebaut.

## Dauerhaft

- Kapitel 4 der Doku ist die Prüfliste gegen Anthropic-Änderungen; die Belege dazu tragen 1.6 und Kapitel 3. Ändert sich etwas: Zeile korrigieren, prüfen, was daran hing, gekippte Annahmen nach 1.7.
- Die README trägt den Warnhinweis, solange nichts benutzbar ist.
- Neues Feature mit eigenem Konzept (Feldname, Dateiendung, Funktion): die Begriffsliste in `tests/test_docstrings.py` nachziehen. Kommandos und `--Flags` prüft der Test von selbst, Begriffe nicht.
