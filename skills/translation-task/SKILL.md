---
name: translation-task
description: Übersetzt Dokumente mit softwareentwicklungsnahem Inhalt in eine andere Sprache — README, Konzept- und Implementierungsdokumente, Anleitungen. Klärt vorab Zielsprache und Fachjargon-Grad, führt ein Terminologie-Glossar, legt vor der vollständigen Übersetzung eine Arbeitsprobe vor und behandelt Codeblöcke, Eigennamen und wörtliche Marker nach festen Regeln. Verwenden, wenn eine Übersetzung eines Dokuments gewünscht ist oder wenn der Nutzer /translation-task aufruft.
license: CC0-1.0
---

# Übersetzung software-entwicklungsnaher Dokumente

## Zweck und Geltungsbereich

Dieser Skill übersetzt Dokumente, deren Inhalt der Softwareentwicklung nahesteht — nicht auf README-Dateien beschränkt und nicht auf eine bestimmte Sprachrichtung. Er ist kein allgemeiner Übersetzer: Er ist auf die Eigenheiten solcher Texte ausgelegt, in denen Fachbegriffe, Codeblöcke, Dateinamen und Produktnamen zwischen Prosa stehen und je eigenen Regeln folgen.

## Auslösung

- **Mehrdeutiger Auftrag** (z. B. „kannst du das mal übersetzen" ohne weitere Angaben): Den Skill ankündigen — „Für eine Übersetzung habe ich bereits einen Skill. Wollen wir den verwenden? Wenn ja, würde ich Dir ein paar kurze prinzipielle Fragen stellen." — und auf Zustimmung warten, bevor es weitergeht.
- **Expliziter Auftrag** (Zielsprache, Dokument usw. sind bereits benannt): Die Bestätigungsfrage entfällt, es beginnt direkt mit den Kalibrierungsfragen.

## Kalibrierungsfragen

Jede Frage entfällt, wenn ihre Antwort bereits aus dem bisherigen Chatverlauf hervorgeht. Gefragt wird nur, was wirklich offen ist:

1. **Zielsprache.**
2. **Fachjargon-Grad und Zielgruppe.** Der Standardfall ist die fachlich übliche Ausdrucksweise einschließlich fremdsprachiger Fachbegriffe, wie sie unter Fachleuten des Themas gebräuchlich sind. Auf Wunsch wird sparsamer damit umgegangen, wenn eine andere Zielgruppe angesprochen werden soll.
3. **Ob ein bestehendes Glossar angewendet werden soll** — nur relevant, wenn eines vorliegt.

## Terminologie-Glossar

Feste Begriffsentscheidungen (etwa: „Pipe" bleibt „Pipe", „timestamp" wird zu „Zeitstempel") werden in einer Glossardatei geführt, statt bei jeder Übersetzung neu entschieden zu werden.

**Umgebung zuerst erkennen.** Ob ein Glossar überhaupt geführt werden kann, hängt davon ab, wo dieser Skill läuft. Praktischer Test: Zugriffsversuch auf `${CLAUDE_SKILL_DIR}/glossar.md`. Gelingt er mit einem echten, aufgelösten Pfad, läuft der Skill lokal in Claude Code; in claude.ai bliebe ein solcher Verweis wörtlicher Text, bzw. die nötigen Dateiwerkzeuge fehlen ganz.

- **Lokal in Claude Code:** Das Glossar liegt unter `${CLAUDE_SKILL_DIR}/glossar.md`, also im selben Ordner wie dieser Skill. Es wird vor der Übersetzung gelesen und angewendet.
- **In claude.ai:** Das Glossar bleibt unerwähnt. Kein Versuch, eines zu führen oder anzulegen — das würde nur eine Datei versprechen, die niemand wiederfindet.
- **Am Ende jeder Übersetzung** (nur lokal): Neu entstandene Begriffsentscheidungen werden zur Aufnahme ins Glossar vorgeschlagen und bestätigt, statt sie stillschweigend zu verwerfen oder ungefragt einzutragen.

## Arbeitsprobe vor der vollständigen Übersetzung

Bevor das ganze Dokument übersetzt wird, wird eine Arbeitsprobe vorgelegt. An ihr entscheidet der Nutzer, ob das Dokument so übersetzt werden soll.

- **Standardgröße, ohne Rückfrage:** höchstens 33 % des Dokuments **und** höchstens rund 1000 Wörter — es gilt der jeweils kleinere Wert.
- **Standardlage:** ab Dokumentanfang.
- **Warum die 1000-Wort-Grenze bei langen Dokumenten nach oben und nicht nach unten abweicht:** Der Anfang eines Dokuments besteht oft noch nicht aus gewöhnlichem Fließtext, sondern aus Titel, Badges oder Inhaltsverzeichnis. Eine zu kleine Probe zeigt davon nur das Uncharakteristische.
- **Anpassung nur auf Wunsch:** Ist die Probe ab Dokumentanfang nicht aussagekräftig genug, kann sie verlängert oder an eine andere Stelle verlegt werden. Das wird nicht von vornherein erfragt.

## Codeblöcke

Zwei Arten von Codeblöcken werden unterschiedlich behandelt, ohne den Nutzer danach zu fragen:

- **Wörtliche Wiedergabe** von echtem Werkzeug-Output oder echtem Quellcode bleibt unangetastet — einschließlich der darin enthaltenen Kommentare.
- **Illustrative, paraphrasierte Beispiele** (etwa gekürzte Konfigurationsausschnitte, erfundene Beispielzeilen) dürfen übersetzt werden.

**Erkennung, projektweit.** Gesucht wird nicht nur im Ordner des Dokuments, sondern im gesamten erreichbaren Projekt nach einer echten Quelle, die der Codeblock zeigen könnte — anhand eines eindeutigen Anhaltspunkts wie Dateiname, unverwechselbarer Zeile oder Variablenname, unabhängig von Verzeichnistiefe oder Nachbarschaft. Wird eine Übereinstimmung gefunden: nahezu wörtlich → unangetastet lassen; erkennbar gekürzt oder paraphrasiert → übersetzbar. Wird nichts gefunden, gilt der konservative Standard: Blockinhalt unangetastet lassen.

## Eigennamen, Produktnamen und wörtliche Marker

Ohne Einzelfallprüfung: Eigennamen und Produktnamen (etwa „Claude") sowie wörtliche Code-Marker (etwa `@Claude:`) werden nie mitübersetzt oder ausgetauscht — auch dann nicht, wenn der umgebende Fachbegriff sehr wohl übersetzt wird, und unabhängig davon, ob sie im Fließtext als Beispiel oder als exakte Wiedergabe eines echten Markers stehen.

## Noch nicht festgelegt

Diese Punkte sind bewusst offen und werden im Einzelfall mit dem Nutzer geklärt, bis sie hier festgeschrieben sind:

- **Namenskonvention für Zieldateien** (etwa `<datei>.de.md` neben dem Original).
- **Sync-Workflow:** ob dieser Skill auch das Nachziehen einer Änderung von einer Sprachfassung in die andere abdeckt, oder ob dafür ein eigener Weg vorgesehen wird.
- **Lizenz- und Rechtstexte:** ob sie grundsätzlich unübersetzt bleiben.
- **Formatierung:** ob die Ein-Absatz-pro-Zeile-Konvention des Originals übernommen oder neu umbrochen wird.
- **Ton und Anrede** in der Zielsprache (etwa „du" oder „Sie" im Deutschen).
