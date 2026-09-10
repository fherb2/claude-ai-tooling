# Fahrplan: Syncthing-Sync für `~/.claude`

Reine Abfolge der Arbeitsschritte, keine Inhalte. Details zu jedem Schritt stehen in `implementation-doc.md`.

Der Mechanismus ist fertig und im Betrieb. Offen ist allein die Portierung nach Windows.

## Schritte

6. **Windows-Pendant** entwickeln (Kap. 3.7). Die Zuordnung der plattformabhängigen Bausteine für die Kapselstelle steht dort bereits.

## Laufender Plan: Aufräumen der Implementierungsdoku (noch nicht ausgeführt)

Entscheidung des Entwicklers vom 10. September 2026: Die Implementierung ist abgeschlossen und beschreibt sich selbst. Aus den Kapiteln 1 bis 3 der Doku werden Fragen, Zwischenstände, Abwägungen und Detailerkenntnisse des Entstehungswegs vollständig entfernt. Übrig bleibt, was zum Bau der Anwenderdokumentation und zum Verständnis der Implementierung nötig ist.

**Schnittregel:** Die Festlegung bleibt, ihre Entstehungsgeschichte geht. Eine Folge („eine Dauerangabe wie `15m` wird mit 255 abgewiesen") bleibt, weil sie vor dem Wiedereinbau des Fehlers schützt; Datum, Messweg und Belegverweis dazu entfallen. Restlos entfallen: Datumsangaben und Messprotokolle, verworfene Alternativen, Vorher-nachher-Erzählungen, Verweise auf Befunde und Fragen.

**Erhalten bleibt Anhang B** (Code-Review vom 13. August 2026 samt Bearbeitung) — Nachweis und Wissensbasis künftiger Reviews. **Anhang A** (Fragenkatalog) entfällt: F3, F7 und F11 sind am 10. September 2026 als beantwortet geschlossen.

**Zwei Randbedingungen:** Keine Umnummerierung der Abschnitte, weil Wächter und beide Shell-Skripte im Klartext auf Kapitelnummern verweisen. Keine hängenden Verweise — die Stellen, die auf Anhang A oder F-Nummern zeigen, werden mitbereinigt.

**Etappen, jede mit Checkpoint-Commit:**

1. Anhang A entfernen, Vorbemerkung des Dokuments anpassen, die Verweise auf Anhang A und F-Nummern in den Kapiteln bereinigen.
2. Kapitel 3 kürzen (3.1 bis 3.9; größter Einzelposten ist 3.8, das auf den Umfang der Prüfskripte und die Grenze zur Handprobe zusammenschrumpft).
3. Kapitel 2 kürzen — Vorgabesatz und Verletzungstest bleiben je Abschnitt vollständig, die Herleitungen entfallen.
4. Kapitel 1 kürzen; 1.7 um das Prinzip erweitern, dass das Verfahren für beliebig viele Rechner trägt (jeder Rechner sieht nur den Vermittlungsknoten; Konflikte und Lösungen verteilt Syncthing als gewöhnliche Dateivorgänge) — ohne Rechnerzahl im Text. Die entwicklungszeitliche Schutzmarke am Kapitelanfang entfällt.
5. `status.md` löschen. Diesen Fahrplan auf Schritt 6 reduzieren. Im Kommentar von `claude_sync_watchd.py` den F7-Verweis auf die bleibenden Kapitel kürzen. In `offener_fall_chatprotokolle.md` den überholten Verweis auf den Fragenkatalog richtigstellen — die Datei selbst bleibt vollständig erhalten, weil der Fall künftig wieder Bedeutung bekommen kann.
6. Auf `infra`: in `.claude/CLAUDE.md` den Satz anpassen, der die `plansDirectory`-Frage als „offene Entscheidung im Fahrplan von `home-.claude-sharing`" führt — diese Frage ist mit dem Kürzen des Fahrplans entfallen.
