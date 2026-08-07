# Fahrplan: Fossil-Sync für `~/.claude`

Reine Abfolge der Arbeitsschritte, keine Inhalte. Details zu jedem Schritt stehen in `implementierungs_doku.md` (Kapitelverweise unten). Abgeschlossene Schritte werden aus dieser Liste vollständig entfernt, nicht nur markiert.

1. Reale Ausschlussregel einbuchen (`~/.claude/.fossil-settings/ignore-glob` ist korrigiert, aber noch nicht committet) und `fossil add . --dotfiles` im Hauptskript vorsehen (Kap. 1.3, 2.3, 3.1)
2. Offene Koordinationsfragen klären, bevor der Zyklus danach geschrieben wird: Verriegelung zwischen Timer-Zyklus und laufender Konfliktsitzung, Form des Abschlussberichts, Name/Ablageort der Arbeitsanweisungsdatei (Kap. 3.2, 3.4)
3. Haupt-Sync-Skript vollständig neu schreiben nach dem aktuellen Stand — der bisherige Entwurf spiegelt noch das verworfene Arbeitsstelle-Modell (Kap. 3.1): Trockenlauf plus Mengenschnitt, erweiterter Konfliktbegriff (Fossil-Konflikt vs. beidseitig berührte Nicht-Protokolldatei), Dialog-Wiederholschleife, Terminal-Abbruchverhalten, korrigiertes Transferzeilen-Format, `--dotfiles`
4. Arbeitsanweisung (und ggf. Hilfsskripte) für die Konfliktsitzung schreiben (Kap. 2.5, 3.4)
5. Erster echter Sync-Lauf gegen `claude-config` — vorher ausdrücklich Rücksprache halten; dabei auch beobachten, ob die Transferformate im Netzbetrieb den Dateipfad-Proben entsprechen (Kap. 2.2, 3.8)
6. systemd Service + Timer einrichten — Rechner A (Kap. 3.5)
7. Zweiten Rechner zusammenführen — erst wenn reale Zwei-Rechner-Tests nötig werden (Kap. 3.6)
8. systemd Service + Timer einrichten — Rechner B (Kap. 3.5)
9. Windows-Pendant entwickeln (Kap. 3.7)
