# Software-begleitende Dokumentation

> **In Arbeit.** Dieser Text ist der Zieltext des Skills und noch nicht fertig: Verweise der Form „Kapitel 1.3.2" oder „Anhang A" zeigen auf die Entwicklungsdoku des Vorhabens und sind vor der Auslieferung durch die Zielstruktur zu ersetzen. Dieser Block entfällt beim Zusammensetzen (Fahrplanschritt 7).

## Zweck und Aufbau

Diese Datei ist dünn: Sie stellt fest, wie die Sitzung die Doku liest, und lädt die Regelteile nach, die dafür gebraucht werden. Die Regeln selbst — Härte, Register, Planung, Rollen, Methodik — stehen nicht hier, sondern in den nachgeladenen Dateien. Was diese Trennung leistet und warum ein dünner Einstiegspunkt besser ist als ein Regeltext, der alles auf einmal trägt, steht in Kapitel 1.5.

## Ablauf

Geladen wirst Du durch den geankerten Trigger aus der `CLAUDE.md` (Kapitel 3.11) oder durch ausdrücklichen Aufruf. Dann in dieser Reihenfolge:

1. **Prüfen, ob hier überhaupt Software entwickelt wird.** Rein mechanisch, ohne Rückfrage, nach Kapitel 3.5.5. Trägt das Vorhaben erkennbar keinen Quellcode, sondern etwas anderes — ein Buch, ein Paper, eine Dokumentsammlung —, endest Du hier, lädst keinen Regelteil und sagst einmal je Sitzung, warum. Ist es unentschieden, weil kaum Inhalt da ist, läufst Du weiter.
2. **Skill-Parameterdatei lesen.** `.claude/software-design-doc.json`. Steht dort `mode: off`, endest Du hier: Du forderst nichts, schlägst nichts vor, zitierst keine Regel; vorhandene Doku in fremder Form wird vor Änderungen gelesen und dort gepflegt, wo das Projekt sie selbst pflegt. Steht dort `mode: on`, weiter mit Schritt 4.
3. **Fehlt die Datei oder das Feld `mode`, wird jetzt nicht gefragt.** Trägt die Doku bereits Marker oder ein Register, gilt `mode: on` als abgelesen (Vorgabe 2.9). Sonst arbeitest Du zunächst still weiter: lesen, Lage bestimmen, Kollisionen parken — das ändert nichts und fordert nichts. Die Frage „Soll ich das hier führen?" stellst Du erst in dem Augenblick, in dem Du zum ersten Mal etwas vorschlagen oder schreiben würdest, einmal je Sitzung und mit dem Anlass in der Hand; bei Ablehnung bietest Du an, `mode: off` festzuhalten, damit sie nicht wiederkehrt (Kapitel 1.7 und 1.7.7).
4. **Lage bestimmen** — `execute` oder `design` — nach der Härteliste in Kapitel 3.1; lade dafür `rules-hardness.de.md`.
5. **Regelteile laden:** `rules-register.de.md` immer; `rules-planning.de.md`, wenn ein geplanter Schritt oder sein Umbauziel betroffen ist; `standard.de.md`, wenn eine Frage zur Methodik ansteht, die nicht die Härte- oder Registerregeln selbst betrifft.
6. **Ablesen, was ablesbar ist**, oder — fehlt die Skill-Parameterdatei ganz, oder braucht es die volle Erhebung — `rules-startup.de.md` zusätzlich laden: Doku-Ordner (Rollenmarker, eine `decisions.md`, die üblichen Ordnernamen), Register, Dateien mit geplanten Schritten (Rolle `plan`, `work-plan.md`, `fahrplan.md`, Abschnitt „Offen" einer README), Layout der Prosa, vorhandene Rollen. Die Einzelheiten der Erhebung und der vollständige Skill-Parameter stehen dort (Kapitel 3.5).

**Was hier überhaupt nicht gefragt wird:** nichts. Dieser Ablauf stellt keine Frage. Er liest, bestimmt die Lage und lädt, was gebraucht wird. Jede Frage an den Entwickler hat ihren Anlass später — dort, wo etwas vorzuschlagen oder zu schreiben ist (Kapitel 1.7).

## Was hier bewusst nicht steht

Kein Fragebogen, keine Inventur, keine Skill-Logik, die sich auch mechanisch aus den geladenen Regelteilen ergäbe. Diese Datei entscheidet nur, *was* geladen wird — nie, *wie* eine geladene Regel angewendet wird.
