# Fahrplan Version 2 — Hauptaufgaben und Ziele

**Was diese Datei ist.** Der Umriss der nächsten Ausbaustufe: die Komplexe, ihre Ziele und was sie berühren. **Noch keine Schritte** — die entstehen, wenn wir mit einem Komplex anfangen, und werden dann hier ausdetailliert (Arbeitsanweisungen §2.6, Repo-`CLAUDE.md` „Wo ein Plan steht"). Schrittnummern gibt es deshalb noch keine; sie beginnen bei 1, sobald der erste Komplex aufgeschlagen wird.

**Wo Version 1 steht.** Produktiv und unangetastet. Was sie leistet, sagt `implementation-doc.md`; was sie **nicht** leistet, deren Kapitel 1.8. Dieser Fahrplan setzt dort an und wiederholt es nicht.

**Die Reihenfolge ist nicht frei.** Komplex A trägt Komplex B: Ohne den Projektbezug in der Chatdatei kann ein Claude-Code-Projekt nicht neben einem claude.ai-Projekt im selben Verzeichnis stehen.

---

## Komplex A — Das Protokoll trägt mehrere Projekte

**Ziel:** Ein Verzeichnis darf Chats mehrerer Quellprojekte halten, und jede Chatdatei nennt das Projekt, aus dem sie kommt.

Ein Ziel, drei Grenzen aus 1.8 fallen damit zusammen:

- Der **gemischte Ordner** rechnet richtig, weil jedes Projekt seine eigene Fenstergrenze bekommt. Kein Verbot, die Mechanik trägt es.
- Eine **einzeln weitergegebene Chatdatei** ist selbsterklärend — der Widerspruch zur Begründung in 1.4 ist aufgelöst.
- Im **Projektwissen-Ziel** bleibt die Zuordnung erhalten, obwohl das Protokoll nicht mit hinaufwandert.

**Was das berührt.** Das Protokoll führt Name, Anlegedatum und Listenstand **je Projekt** statt je Datei; jeder Chateintrag nennt sein Projekt. Damit ändern sich `window_start()`, `window_lines()` und `project_start_warnings()` von „das Projekt" auf „je Projekt", `list --project` wählt den gemeinten Eintrag statt ihn zu überschreiben, und `diff` wie `report` gliedern ihre Ausgabe nach Projekt. Die Chatdatei bekommt ein Metadatenfeld; das rührt an Vorgabe 2.2 und ist der erste Anlass, `protocol_version` auf 2 zu heben — die Warnung dafür steht seit Version 1 bereit.

**Zwei Festlegungen, die vorab getroffen sind**, damit sie nicht in der Umsetzung neu diskutiert werden:

Das neue Feld ist **kein sechstes abweichendes** im Sinne von Vorgabe 2.5. Beide Wege können es füllen — der Web-Weg aus den Daten, der Export-Weg über das Protokoll — und schreiben denselben Wert. Es ist ein sechstes *gleiches* Feld.

Das Feld heißt **nicht nach claude.ai**. Ein Projekt ist mal ein claude.ai-Projekt, mal ein Arbeitsverzeichnis; welches, sagt `source`. Ein Name wie `claude_ai_project` wäre nach Komplex B falsch.

**Rückwärtsverträglichkeit ist Teil des Ziels, nicht ein Zusatz.** Ein Protokoll heutiger Form liest sich als genau ein Projekteintrag; ein bestehendes Archiv bleibt lesbar und fortschreibbar. Chatdateien ohne das neue Feld bleiben gültig — sie sagen dann eben nichts über ihr Projekt, wie heute alle.

---

## Komplex B — Claude-Code-Sitzungen als Quelle

**Ziel:** Eigene Claude-Code-Sitzungen ins Projektarchiv retten, bevor die Aufbewahrungsfrist sie wegräumt.

**Warum das jetzt anders bewertet wird als in 1.7.** Dort ist Claude Code als Quelle verworfen worden, und für den damaligen Fall zu Recht: Für die Migration claude.ai → Claude Code gab es eine dokumentierte, stabile Quelle, also war ein internes, versionsabhängiges Format der schlechtere Weg. Für die Rettung eigener Sitzungen gibt es **keine Alternative**. Die Wahl ist nicht „instabiles Format gegen stabiles", sondern „instabiles Format gegen nichts". Damit wird das Risiko nicht kleiner — es wird von einem Ausschlussgrund zu einem Grund für eine Schemawache, wie `inspect_export.py` sie für das Export-ZIP schon ist.

**Es wird ein eigenes Werkzeug, keine Variante des Konverters.** Drei Dinge passen nicht: Die Quelle ist eine Ereignis-`jsonl`, nicht `conversations.json`. Es gibt keine Chatliste und keinen Fremdstand, gegen den sich `stale` bestimmen ließe — die lokale Datei **ist** die Quelle. Und eine Sitzung gehört zu einem Arbeitsverzeichnis, nicht zu einem claude.ai-Projekt.

**Gleich bleibt das Zielformat.** Dieselbe Chatdatei, dasselbe Protokoll, damit ein Grep beides gleich findet. Das ist der Wiederverwendungspunkt und der einzige.

**Die Auswahl trifft der Mensch.** „Nur die Chats mit Kontext" ist eine inhaltliche Entscheidung, und Vorgabe 2.7 verbietet die im Code. Auflösung: Der Nutzer benennt die Sitzungen, oder das Werkzeug filtert **strukturell** vor — Länge, Alter, Arbeitsverzeichnis, Zahl der Dateiänderungen — und legt die Auswahl zur Entscheidung vor. Ein Werkzeug, das „wertvolle" Chats erkennt, wird es nicht geben.

**Was heute schon zu tun ist und auf kein Werkzeug wartet:** `cleanupPeriodDays` hochsetzen. Nach Ablauf der Frist ist jede Rettung wirkungslos, und man weiß nie rechtzeitig, welchen Chat man später braucht. Der Hinweis steht deshalb bereits in den Skill-READMEs, obwohl der Skill diese Quelle nicht anbietet.

---

## Was für beide Komplexe bindend bleibt

- **Vorgabe 2.5** — beide Wege schreiben dieselbe Datei, und der Maßstab unter `tests/` darf nichts aus dem Konverter importieren. Jede Formatänderung ist damit zweimal zu machen; das ist der Preis und keine Nachlässigkeit.
- **Vorgabe 2.7** — Auswahl strukturell, nie inhaltlich. Über Inhalt entscheidet der Mensch.
- **Vorgabe 2.8** — kein Chattext durch den Kontext einer Instanz.
- **Der Maßstab aus 1.8** — einmal geschriebene Chatdateien bleiben durchsuchbar, auch wenn eine künftige Fassung das Format ändert. Verlieren können sie die **Fortschreibbarkeit**, nicht den Inhalt. Deshalb ist Ablegen nie zu früh, und die Frage nach der perfekten Struktur ist kein Grund zu warten.

## Was ausdrücklich kein Ziel ist

- **Chats fortsetzen.** War es nie; das Archiv dient dem Wiederfinden (1.1).
- **Cowork.** Über keinen Weg erreichbar (1.7); eine Lücke, keine Aufgabe.
- **Die Compliance-API.** Kann genau das, was hier nachgebaut wird, steht aber nur Enterprise offen (1.7).
- **Ein Werkzeug, das Chats nach Wichtigkeit bewertet.** Siehe Vorgabe 2.7.
