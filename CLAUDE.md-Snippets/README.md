# CLAUDE.md-Snippets

*Stand: 2026-08-25*

*[English version](README.en.md)*

Fertig formulierte Textbausteine für die Anweisungen, die Claude dauerhaft mitbekommt — für die `CLAUDE.md` einer lokalen Claude-Code-Installation (`~/.claude/CLAUDE.md`), gegebenenfalls in Projekten, die mit Claude Code bearbeitet werden (`<projekt>/.claude/CLAUDE.md`) und für die Stellen, an denen claude.ai Anweisungen aufnimmt (Konto unter Allgemein sowie in Projekten). Jeder Baustein steht für sich: keine Reihenfolge, kein Gesamtdokument, kein Anspruch auf Vollständigkeit. Wer einen braucht, kopiert ihn heraus; der Rest bleibt liegen. Anweisungsbereiche in common-snippets.*.md können auch in den anderen beiden Files vorhanden sein: Hier sind die Anweisungen unter der entsprechenden Überschrift zu mixen.

## Nicht zu verwechseln mit `skills/`

Im Baustein [`skills/`](../skills/README.md) liegt in manchem Skill-Ordner eine Datei `CLAUDE-snippet.md`, die auf den ersten Blick dasselbe zu sein scheint. Sie ist etwas anderes: der **stille Trigger** eines bestimmten Skills — ein Verweis, der ohne diesen Skill wirkungslos ist und deshalb mit ihm zusammen in `CLAUDE.md` installiert wird.

Hier steht das Gegenteil davon: Anweisungen, die für sich wirken und keinen Skill hinter sich haben. Was zu einem Skill gehört, gehört nicht hierher — und umgekehrt.

## Die drei Dateien

Der Schnitt zwischen ihnen ist der **Wirkungsort**, nicht das Thema:


| Datei                                                                                                   | Gilt für                                        | Weil                                                          |
| ------------------------------------------------------------------------------------------------------- | ------------------------------------------------ | ------------------------------------------------------------- |
| [`common-snippets.de.md`](common-snippets.de.md) · [`.en.md`](common-snippets.en.md)                   | claude.ai **und** lokale Claude-Code-Installation | Der Baustein ist in beiden Umgebungen wortgleich brauchbar.   |
| [`claude.ai-snippets.de.md`](claude.ai-snippets.de.md) · [`.en.md`](claude.ai-snippets.en.md)          | nur claude.ai                                    | Der Baustein nennt Dinge, die es nur dort gibt.               |
| [`home-.claude-snippets.de.md`](home-.claude-snippets.de.md) · [`.en.md`](home-.claude-snippets.en.md) | nur lokal, `~/.claude/CLAUDE.md`                | Der Baustein nennt Ablageorte und Pfade des eigenen Rechners. |

Jede Datei liegt in zwei Sprachfassungen vor — `.de.md` deutsch, `.en.md` englisch. Beide sagen dasselbe; welche man nimmt, richtet sich nach der Sprache, in der üblicherweise der Nutzer arbeitet, damit Claude beim Antworten nicht in der Sprache durcheinander kommt.

**Ein Thema kann in mehreren Dateien vorkommen**, und das ist kein Versehen. Das Memory ist das Beispiel: In `common-snippets` steht die Frage, **ob** Wissen über den Nutzer überhaupt in den Speicher darf — die gilt überall gleich. In den beiden umgebungsspezifischen Dateien steht die Frage, **wohin** — und die möglichen Orte sind eben verschieden. Wer beides braucht, übernimmt beides.

## Verwendung

Nichts hier lädt sich von selbst. Ein Baustein wirkt erst, wenn sein Text an der Zielstelle steht.

**Einen Baustein übernimmt man immer: „Vorrang der Anweisungsebenen“ aus `common-snippets`.** Er klärt, welche Ebene gilt, wenn zwei Anweisungen einander widersprechen — und dieser Fall tritt früher ein, als man denkt. Ohne ihn wird sonst willkürlich eine der beiden Regeln gewählt, was sich als Rückfrage oder als überraschendes Verhalten zeigt. Er ist vier Zeilen lang, kostet kaum Kontext, und falsch machen kann man mit ihm nichts: Er ordnet nur, was ohnehin geregelt sein müsste.

1. **Sprachfassung wählen.** Eingefügt wird genau **eine**. Zwei wären eine Dublette, die beim nächsten Anpassen auseinanderdriftet.
2. **Baustein samt Überschrift herauskopieren.** Die Überschrift benennt an der Zielstelle das Thema und macht später wiederfindbar, worum es geht.
3. **Überschriftenebene anpassen.** Hier trägt jeder Baustein eine Überschrift erster Ordnung, weil die Datei ihm allein gehört. In einer gewachsenen `CLAUDE.md` gehört er auf die Ebene, die dort zur Gliederung passt.
4. **Gleiche Themen zusammenführen.** Übernimmt man zu einem Thema den gemeinsamen *und* den umgebungsspezifischen Baustein, gehören beide an der Zielstelle unter **eine** Überschrift — sonst steht dieselbe Überschrift dort zweimal.

## Stand

Der Inhalt der Dateien in diesem Ordner wächst immer mal wieder. Im Hauptbranch des Projekts sollten immer vollständige Anweisungen enthalten sein, sodass sie zur Nutzung immer freigegeben sind.

Der Nutzer entscheidet, was er davon übernimmt:

## Lizenz

Alle Bausteine in diesem Ordner stehen unter **[CC0 1.0 Universal](https://creativecommons.org/publicdomain/zero/1.0/)** — dem Verzicht auf alle Rechte, soweit gesetzlich möglich. Das bedeutet:

- **Nutzung ohne jede Bedingung** — privat, kommerziell, in geschlossenen wie in offenen Projekten.
- **Keine Namensnennung nötig.** Wer will, darf nennen; niemand muss.
- **Beliebig änderbar und weitergebbar**, auch in veränderter Form und unter anderem Namen.
- **Keine Pflicht, Änderungen offenzulegen** oder zurückzugeben.
- **Kein Lizenztext muss mitgegeben werden** — anders als bei MIT oder Apache-2.0, die beide Namensnennung und Mitgabe des Lizenztextes verlangen.
- **Keine Gewährleistung und keine Haftung.** Was diese Bausteine anrichten, verantwortet, wer sie einsetzt.

Dieselbe Wahl wie im Baustein [`skills/`](../skills/README.md) und aus demselben Grund: Ein Textbaustein, der in einer fremden `CLAUDE.md` landet, soll dort keine Lizenzpflichten hinterlassen.
