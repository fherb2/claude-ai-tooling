---
name: pedantic-text-editing
description: Bearbeitet Texte, deren Wortlaut selbst das Produkt ist — Aufsätze, Anträge, Vorträge, Briefe, Buchkapitel: Korrekturlesen, Lektorat, Rechtschreibung, Grammatik, Zeichensetzung, Formulierung. Legt jede Änderung einzeln zur Freigabe vor, ändert außerhalb der freigegebenen Stellen kein Zeichen und hält die Freigaben versioniert fest. Gilt nicht für Quellcode und nicht für Texte, die Software dokumentieren. Verwenden, bevor in einer Sitzung zum ersten Mal ein solcher Text geändert wird, oder wenn der Nutzer /pedantic-text-editing aufruft.
license: CC0-1.0
---

# Pedantische Textbearbeitung

## Wofür dieser Skill gilt

Für Texte, deren **Wortlaut selbst das Produkt ist** — Aufsätze, Anträge, Vorträge, Briefe, Buchkapitel, Gutachten. Nicht für Quellcode und nicht für Texte, die einer Software folgen und sie dokumentieren; dort gilt der Skill nur, wenn der Nutzer es ausdrücklich verlangt. Maßgeblich ist nicht das Thema des Textes und nicht der Ordner, in dem er liegt, sondern seine Rolle.

## Zuerst klären, ob er angewendet wird

- **Ruft der Nutzer `/pedantic-text-editing` auf**, ist das die Zustimmung. Dann nicht fragen, sondern weiter beim letzten Abschnitt.
- **Sonst frage einmal**, ob der anstehende Text nach diesem Skill bearbeitet werden soll. Bis zur Antwort änderst Du an ihm nichts.
- **Eine Absage gilt für die ganze Sitzung.** Frage nicht erneut, erwähne den Skill nicht erneut, lies keine weitere Datei dieses Skills. Damit ist er für diese Sitzung erledigt.
- Ist erkennbar keine solche Textbearbeitung im Gang — Softwarearbeit, Quellcode, softwarebegleitende Dokumentation —, frage gar nicht erst.

## Gilt er, dann die Regeln laden

**Lies `${CLAUDE_SKILL_DIR}/regeln.de.md` vollständig und arbeite ab dann danach.** Liegt dort keine Datei dieses Namens, sieh im Skill-Ordner nach, welche Regeldatei es gibt — beim Installieren kann umbenannt worden sein. Die Regeln stehen dort, nicht hier. Bevor Du sie gelesen hast, ändere an dem Text nichts — auch keine Kleinigkeit.

Diese Teilung ist Absicht und wird nicht zusammengelegt: Der Skill wird häufig geladen, ohne zur Anwendung zu kommen, und was er dann kostet, ist genau diese Seite. Der Regeltext bleibt in solchen Sitzungen draußen.
