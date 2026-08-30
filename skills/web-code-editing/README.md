# web-code-editing — Code-Bearbeitung auf claude.ai

*Stand: 2026-08-30*

*[English version](README.en.md)*

**✅☑ Fertig und nutzbar.** Skilltext in beiden Sprachen, Frontmatter gesetzt; die Erprobung als hochgeladener Skill steht noch aus (siehe „Stand und Offenes"). — Benutzbar für Claude.ai / Claude Desktop (Chat + Cowork).

**Der Skill regelt das Erstellen und Ändern von Code auf claude.ai für ein bestehendes Projekt** — mit drei Kernen: Quellen vollständig sichern, bevor geschrieben wird; geänderte Dateien mechanisch als Download zurückgeben statt sie aus dem Kontext neu zu diktieren; kleine Änderungen als Vorher/Ersetzen-Schema im Chat. Er ist **nur für claude.ai** (Zielwelt „nur web", `skill-dev-doc.md` Kapitel 9.4): In Claude Code schreibt das Edit-Werkzeug direkt in die Dateien, dort ist nichts davon nötig.

## Installation

1. **Paket herunterladen.** `downloads/web-code-editing_de_web.zip`

2. **Hochladen.** Im dafür vorgesehenen Verwaltungsfeld für Skills der Anwendung das Archiv hochladen. Der Skill gilt danach für Dein Konto — nicht für Deine Organisation, und nicht gleichzeitig in Claude Code.

Ein stiller Trigger entfällt hier: Der Skill löst über seine `description` aus oder wird mit `/web-code-editing` aufgerufen. Ob die `description` allein zuverlässig genug auslöst, ist noch nicht erprobt — siehe „Stand und Offenes“.

## Details

**Der wichtigste Satz des Skills ist der über `/mnt/project/`, und er existiert wegen einer falschen Selbstauskunft.** Im Test vom 28. August 2026 verneinte die Instanz zunächst überzeugt und ausführlich begründet, auf Projektwissen-Dateien als Dateien zugreifen zu können — erst der konkrete Skript-Vorschlag des Entwicklers brachte die Korrektur: Die Dateien liegen unter `/mnt/project/` gemountet. Ohne die ausdrückliche Anweisung verneint die nächste Instanz das wieder. Der Skill ist die Gegenmaßnahme.

**Der mechanische Rückweg ist am echten Projekt belegt** (28. August 2026, Projektwissen mit 39.898 Zeilen gepackter Codebasis): eine 753-Zeilen-Datei anhand ihrer Markerzeilen exakt extrahiert, eine Zeile eingefügt, per `diff` nachgewiesen (`1a2`, Rest bitidentisch), als Download bereitgestellt und zugleich als Artefakt angezeigt. Damit gilt: Extrahieren, per Ersetzung ändern, Download plus Diff — nichts läuft durch die Antwort, nichts wird nachgedichtet.

**Die Form des Projektwissens setzt der Skill nicht voraus.** Einzeldateien, Archiv oder Sammeldatei mit beliebigem Markerschema — der Agent prüft zuerst, was vorliegt, erkennt ein Markerschema aus Kopf und Stichprobe der Datei selbst und fragt den Nutzer, wenn es nicht zweifelsfrei erkennbar ist. Das Werkzeug `pack-source-to-txt` dieses Repositories ist der Weg, den er dem Nutzer *vorschlägt*, wenn viele Dateien gebraucht werden — keine Voraussetzung.

**Die Pfade `/mnt/project/` und `/mnt/user-data/outputs` sind Beobachtung, keine Zusage.** Anthropic kann sie ändern; deshalb weist der Skill an, ihr Fehlen zu melden statt still auf die Suche auszuweichen.

**Die Artefakt-Regel ist bewusst zeitlos gefasst.** Die alte Fassung („Artefakte nicht mehr ändern") stammte aus Frontend-Fehlern von 2025, die Artefakte zerstören konnten. Der bleibende Grund ist ein anderer: Der Nutzer hat den Inhalt in der Regel längst in seinen Code übernommen — die gültige Fassung liegt bei ihm, ein geändertes Artefakt wäre eine zweite Wahrheit.

**Innerhalb eines Chats gilt die gemeinsame Codebasis als Normalfall** (Festlegung des Entwicklers vom 29. August 2026): Der Nutzer trägt erzeugten Code sofort in sein Projekt ein und lädt nicht jeden Zwischenstand neu hoch. Nachgefragt wird bei begründetem Zweifel — nicht routinemäßig.

**Herkunft:** Der Skill verarbeitet die Posten T8–T11 des Anweisungs-Inventars (Artefakt-Mechanik aus den claude.ai-Projektanweisungen 2025/26) — geprüft gegen den Frontend-Stand vom August 2026 statt übernommen: T11 (Teil-Artefakte) war schon in den Quellen überholt und ist ersatzlos entfallen, T9 ist zeitlos neu begründet, T10 (Vorher/Ersetzen-Schema) lebt als Chat-Schema weiter. T6/T7 (Ankündigen, Fragen vorher klären) stehen als „Bevor Du schreibst" am Anfang.

## Stand und Offenes

**Status:** Skilltext in beiden Sprachfassungen fertig und mit dem Entwickler abgestimmt (29. August 2026). Die tragenden Mechanik-Aussagen sind am laufenden System belegt (siehe Details).

**Offen:**

- **Erprobung als hochgeladener Skill** — der Text ist am echten Projekt entwickelt, aber noch nie als Custom Skill auf claude.ai gelaufen. Dabei klärt sich zugleich die Prüffrage aus `skill-dev-doc.md` 1.4 (zieht ein hochgeladener Skill gebündelte Dateien nach — hier nicht nötig, aber messbar).
- **Trigger-Absatz für das Anweisungsfeld** (global oder je Projekt) — ob die `description` allein zuverlässig auslöst, zeigt die Erprobung.
- **Prüffrage Chat-Anhänge:** Ob am Prompt angehängte Dateien zusätzlich als Datei in der Ausführungsumgebung liegen (und damit per Code exakt lesbar wären), ist nicht geprüft — der Skill behandelt sie bis dahin als Kontext-Quelle.

**Idee, noch nicht auf der Tagesordnung — Arbeitskopie im Arbeitsverzeichnis:** Die Dateien, an denen in einer Sitzung gearbeitet wird, einmal aus dem Projektwissen in Claudes eigenes Arbeitsverzeichnis kopieren und dort über die Sitzung mitziehen, statt jede Fassung erneut durch den Kontext zu tragen. Erhofft: Claude findet sich in zusammenhängendem Code besser zurecht als in über den Chat verstreuten Bruchstücken, und umfangreichere Probeläufe beim Planen werden möglich.

Ob das trägt, ist offen. Vor einem Angehen sind erst die tatsächlichen Gegebenheiten zu prüfen — bleibt das Arbeitsverzeichnis über eine ganze Sitzung stabil, wie verhält es sich zu `/mnt/project/` und `/mnt/user-data/outputs` — und der Vorbehalt zu klären, dass eine Arbeitskopie ein zweiter Stand desselben Codes ist und damit genau die Drift verschärft, vor der „Prüfe, ob Dein Stand aktuell ist“ warnt.
