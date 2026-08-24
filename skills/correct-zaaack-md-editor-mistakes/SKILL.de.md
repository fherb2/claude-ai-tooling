---
name: correct-zaaack-md-editor-mistakes
description: Findet und behebt beschädigten Leerraum in Markdown-Tabellen — gefressene Leerzeichen vor Inline-Code oder Fettdruck und geschützte Leerzeichen (U+00A0), die jede Suche über den Wortlaut brechen, ohne im Text sichtbar zu sein. Manche WYSIWYG-Markdown-Editoren richten das beim Speichern an. Verwenden, sobald in einer Sitzung zum ersten Mal eine Markdown-Datei gelesen oder geändert wird, und vor jedem Commit, der Markdown-Dateien einschließt, oder wenn der Nutzer /correct-zaaack-md-editor-mistakes aufruft.
license: CC0-1.0
---

# Artefakte des zaaack-Markdown-Editors in Tabellen

Im Ordner dieses Skills liegt eine `README.md`. Sie erklärt den Editor, den Aufbau der Werkzeuge, die Hook-Einrichtung und die Grenzen im Einzelnen. Lies sie, wenn Du eines davon brauchst — nicht vorsorglich.

## Wofür das gilt

Diese Regeln gelten für **jede** Markdown-Datei. Sie sind nicht auf Softwareprojekte beschränkt und setzen keine Codearbeit voraus.

Beschädigt werden nur Tabellenzeilen, auf zwei Arten: ein gefressenes Leerzeichen vor Inline-Code oder Fettdruck, und ein geschütztes Leerzeichen (U+00A0) anstelle eines gewöhnlichen. Das zweite ist unsichtbar und bricht jede Suche über den Wortlaut — deshalb ist es nicht erlaubt, auch wo es inhaltlich harmlos wäre. Welche Datei betroffen ist, stellst Du nicht selbst fest; das tun die Werkzeuge.

## Der Ablauf

Ist noch nicht geklärt, ob dieses Projekt betroffen ist, dann prüfe bei der ersten Gelegenheit: sobald Du in einer Sitzung eine Markdown-Datei liest oder änderst.

**Findest Du Artefakte:** Korrigiere sie im ganzen Projekt, nicht nur in der Datei, die Dir aufgefallen ist. Melde dem Nutzer die Zahl der Dateien und Zeilen — nicht die einzelnen Stellen — und dass Du das von jetzt an selbständig tust, bei jedem Fund und vor jedem Commit. Halte die Feststellung anschließend fest.

**Findest Du keine:** Frage den Nutzer, ob er diesen Editor grundsätzlich benutzt und ob Du künftig ungefragt prüfen und korrigieren sollst. Halte seine Antwort fest — **auch die Absage**. Ohne das fragst Du beim nächsten Mal wieder.

**Ist kein Hook eingerichtet** — nachzusehen in `.claude/settings.json` —, sage das beim ersten Melden und beschreibe dem Nutzer die Einrichtung. Der Abschnitt „Verlässlichkeit: der Hook" der `README.md` in diesem Ordner trägt sie samt fertigem Eintrag. Nur ein Hook macht die Prüfung vor jedem Commit verlässlich; dieser Skill allein wird bloß wahrscheinlich geladen.

## Dauerfreigabe

Sobald der Nutzer zugestimmt hat oder Du Artefakte gefunden und die Korrektur gemeldet hast, brauchst Du für diese Korrektur keine erneute Zustimmung — auch dann nicht, wenn Du sonst vor jeder Dateiänderung einen Plan vorlegst. Melde sie, statt sie zur Entscheidung vorzulegen.

Die Freigabe deckt ausschließlich **Leerraum innerhalb von Tabellenzeilen**. Kein Wort, keine Zeichensetzung, keine Umformulierung. Wer mehr anfasst, handelt ohne Freigabe.

Zwei Grenzen setzen die Werkzeuge selbst durch. Die dritte fängt niemand für Dich ab: **einfaches `*kursiv*` wird nicht erkannt.** Fällt Dir so eine Stelle auf, lege sie dem Nutzer vor, statt sie selbst zu ändern.

## Die Werkzeuge

Drei Python-Dateien im Ordner dieses Skills. `md_table_artifacts.py` trägt die Regeln und wird nur importiert; die beiden anderen sind die Kommandos. Benutze sie, statt selbst zu suchen.

Immer dieselbe Abfolge, drei getrennte Aufrufe. Einzige Variable ist der Projektpfad — gib ihn **absolut** an, dann ist das Arbeitsverzeichnis gleichgültig:

```bash
# 1 Befund
python3 "${CLAUDE_SKILL_DIR}/scan_md_tables.py" PFAD

# 2 korrigieren
python3 "${CLAUDE_SKILL_DIR}/scan_md_tables.py" PFAD | python3 "${CLAUDE_SKILL_DIR}/fix_md_tables.py"

# 3 Leerprobe
python3 "${CLAUDE_SKILL_DIR}/scan_md_tables.py" PFAD
```

Der Prüfer steigt von `PFAD` aus selbst bis in jeden Unterordner — ein Aufruf, nicht einer je Ordner.

Seine Ausgabe hat zwei Listen. **`files`** ist die Arbeitsliste und bestimmt allein den Rückgabewert: 1 solange etwas zu tun ist, 0 wenn nicht. **`notes`** trägt, was gemeldet aber absichtlich nie korrigiert wird, und ist **keine** offene Arbeit. Sieh die Notizen an und lege dem Nutzer vor, was darunter falsch aussieht.

**Schritt 3 muss `"files": []` und Rückgabewert 0 ergeben.** Tut er das nicht, ist der Korrektor kaputt: nicht wiederholen, sondern dem Nutzer melden.

Passt `SKIP` in `md_table_artifacts.py` nicht zu diesem Projekt, sage es. Erkennen die Werkzeuge etwas nicht als Artefakt, das eines ist, melde es und ändere es nicht selbst.

## Was Du Dir merkst

Halte im Projektgedächtnis fest, ob dieses Projekt betroffen und die Korrektur freigegeben ist — oder dass der Nutzer den Editor nicht benutzt und keine Automatik will. Formuliere es als Feststellung über das Projekt, nicht als Behauptung über den Nutzer.

Das Gedächtnis gilt nur für dieses Projekt. Benutzt der Nutzer den Editor überall, schlage ihm vor, die Feststellung in seine `~/.claude/CLAUDE.md` aufzunehmen. Selbst hineinschreiben darfst Du sie nicht.
