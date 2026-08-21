# Fahrplan Chats-Export

Reine Aufgabenliste in sinnvoller Reihenfolge. Die Fakten je Aufgabe stehen in `implementation_doku.md`, auf die hier nur verwiesen wird — **ausgenommen der jeweils anstehende Schritt**: Der trägt seinen Plan hier ausdetailliert, weil eine neue Sitzung ihn von selbst finden muss (Repo-`CLAUDE.md`, „Wo ein Plan steht"). Höchstens einer gleichzeitig, und nach der Ausführung wird er ersetzt, nicht ergänzt. Erledigtes fliegt raus und wandert nach `status.md`; die Nummern werden dabei **nicht** neu vergeben, damit ein Rückblick im Chat auf „Schritt n" eindeutig bleibt.

Die Prüfarten in Kurzfassung; normativ stehen sie in **Doku 4.1**, dort auch die dritte Art (**Beobachtung** — nicht prüfbar, nur bemerkbar, wenn sie kippt).

**kalt** heißt: mit dem prüfbar, was schon auf der Platte liegt — die heruntergeladenen Export-ZIPs unter `tests/test_results/`, ein Arbeitsordner unter `/tmp`, sonst nichts. Kein Netz, kein Konto, kein fremder Zustand; jederzeit und beliebig oft wiederholbar. Eine Einschränkung, die leicht übersehen wird: Das Prüfmaterial ist **rechnergebunden**, weil `test_results/` gitignoriert ist und nicht mitwandert. Dieselbe kalte Prüfung ist auf dem einen Rechner lauffähig und auf dem anderen nicht.

**warm** heißt: nur mit Zugriff auf ein echtes Konto prüfbar. Zwei Sorten: über die **Browser-Anbindung** (Web-Endpunkte, der Regelfall — Voraussetzungen in `chrome-zugriff.md`) oder über eine **claude.ai-Instanz** (`recent_chats`, `conversation_search`, Upload, Projektwissen). Braucht Vorbereitung, ist nicht beliebig wiederholbar und hinterlässt Spuren an der Quelle.

## Als nächstes

27. **Den Skill fertigstellen.** *Kalt.* — **Plan, noch nicht ausgeführt.**

    Gebaut, erprobt und in `status.md` verbucht ist alles außer der README: die zweite Eingangsart, die Ablage in `skills/chat-export/`, die `SKILL.md`, der echte Lauf über eine zweite, unabhängige Sitzung mit zwei Team-Projekten (Testlauf, Abschnitt „27c"), und die Bestätigung, dass `diff` die UUIDs der zu holenden Chats schon nennt.

    **Offen ist allein die `README.md` des Skills.** Aufbau nach `skills/skill_vorgaben.md` 6.1, in dieser Reihenfolge: Überschrift mit Halbsatz zum Zweck; Statushinweis ohne eigene Zwischenüberschrift; Überblick in Prosa mit der Kernaussage fett im ersten Satz und der Abgrenzung, wofür der Skill **nicht** gilt; Kapitel „Installation" mit echten Pfaden statt Platzhaltern — der Schritt für einen stillen Trigger wird **ersatzlos weggelassen**, nicht als „entfällt hier" aufgeführt; Kapitel „Details"; Kapitel „Stand und Offenes". Hinein gehören die Voraussetzungen aus `chrome-zugriff.md` — `@browser` je Nachricht, Connector-Schalter auf claude.ai, angemeldete Erweiterung, ausgeschaltetes Nachfragen nach dem Speicherort — und der Anweisungsblock für die `CLAUDE.md` des Zielprojekts, auf den die `SKILL.md` verweist.

    **Ein Nebenbefund aus dem Lauf, vor dem nächsten Commit zu klären:** `.claude/imported_chats/` ist bislang nicht in der `.gitignore` dieses Repos ausgeschlossen — nur die Wegwerf-Testkopie des Skripts selbst ist es. Ein Testlauf, der (wie am 21. August) dieses Repo statt eines externen Wegwerfordners als Ziel nimmt, legt damit echten Chat-Inhalt ungeschützt in den Arbeitsbaum. Zu entscheiden: `.gitignore`-Eintrag ergänzen, oder künftige Läufe grundsätzlich außerhalb des Repos.

## Danach

22. **Erster Durchlauf in ein echtes Zielprojekt.** Fakten: Doku 1.5, Vorgabe 2.10. Zielprojekt steht bewusst noch nicht fest — das ist nicht mehr Entwicklung. Mit 27 und 22 fällt der Entwicklungshinweis am Dokumentkopf. *Warm.*

24. **Gegenprobe am FreeCAD-Altbestand — fast erledigt.** Fakten: Doku 1.6, 1.7. Der Befund steht schon: Der Listen-Endpunkt zeigt **23** Chats, das Protokoll führt **22**. Damit ist die stille Lücke aus der Auslassung des laufenden Chats an echten Daten bestätigt. Offen ist allein, **welcher** Chat fehlt — ein lokaler Vergleich der Chatliste gegen `freecad/protokoll.json`, ohne Netz. *Kalt, sobald eine frische Liste vorliegt.*

10. **Entscheidung: `chat_crawl_store.py` behalten oder wegräumen?** Fakten: Doku 3.4. **Die Faktenlage ist inzwischen vollständig** — der Satz, der es außer Dienst stellte, ist gegenstandslos, und `conversation_search` liefert bei längeren Chats eine Zusammenfassung statt Schnipsel, was Vorgabe 2.8 verletzt. Es fehlt nur die Entscheidung. 2.664 Zeilen, die von nichts als ihrem Test angefasst werden.

13. **README des Vorhabens neu schreiben und die Anwenderdokumentation daraus aufbauen, sobald der Warnhinweis fällt.** Fakten: Doku 1.1, 1.2, 1.5. Einschließlich der Nutzerpflicht, die Aufbewahrungsdauer hochzusetzen, bevor nach `~/.claude/projects/` abgelegt wird (1.3).

    **Die Wegewahl gehört hinein**, in der Fassung aus Doku 1.2: Der Kontoexport ist der Anker und die Wahl für Erstmigration und große Mengen; der Web-Weg ist die Wahl für kleine Nachträge und für Team- und Enterprise-Konten der **einzige** Weg. Dazu die Voraussetzungen der Browser-Anbindung aus `chrome-zugriff.md`.

    Zwei Dateien werden dabei aufgelöst, weil ihr Inhalt dorthin wandert: `Zielvorlage.md` (der Nutzerdurchgang) und `chrome-zugriff.md` (die Mechanik). `testlauf.md` ist mit Punkt 21 abgeschlossen und kann fallen, sobald geprüft ist, dass alles Bleibende in der Doku steht.

## Dauerhaft

- Kapitel 4 der Doku ist die Prüfliste gegen Anthropic-Änderungen; die Belege dazu tragen 1.6 und Kapitel 3. Ändert sich etwas: Zeile korrigieren, prüfen, was daran hing, gekippte Annahmen nach 1.7.
- Neue Prüfpunkte gehören nach Kapitel 4, jeder mit seiner Prüfart — kalt, warm oder Beobachtung, normativ in Doku 4.1.
- **Der Web-Weg ist die empfindlichste Stelle des Entwurfs:** undokumentierte Endpunkte, von Dritten rückentwickelt, ohne Ankündigung änderbar. Bricht einer weg, trägt nur noch der Kontoexport — und in Team-Konten nichts mehr. Deshalb steht er in der Prüfliste (4.3) und nicht bloß in der Beschreibung.
- **Was der Nutzer kopiert, ist `skills/chat-export/` — nichts sonst.** Alles andere in diesem Ordner gehört zur Entwicklung. Wer dem Skill ein Werkzeug hinzufügt, muss es dorthin legen, sonst fehlt es beim Nutzer.
- Der Entwicklungshinweis am Kopf der Doku gilt, solange die Phase läuft: halbfertige Passagen sind Normalzustand, Widersprüche zur README erlaubt, Widersprüche innerhalb der Doku und zwischen Doku und Code dagegen Defekte mit eigenem Fahrplanpunkt. Dort steht auch, woran die Phase endet.
- Dieses Vorhaben bekommt **keine** eigene `CLAUDE.md` und keine pfadgebundene Regel. Was dauerhaft gilt, steht hier oder in der Doku; die Begründung trägt die Repo-`CLAUDE.md`.
- Die README trägt den Warnhinweis, solange nichts benutzbar ist; Widersprüche zwischen ihr und der Doku sind bis dahin erlaubt (Doku-Kopf).
- Neues Feature mit eigenem Konzept (Feldname, Dateiendung, Funktion): die Begriffsliste in `tests/test_docstrings.py` nachziehen. Kommandos und `--Flags` prüft der Test von selbst, Begriffe nicht. Zieht ein Skript um, gehört die Zuordnung Skript → Verzeichnis in derselben Datei nachgezogen.
