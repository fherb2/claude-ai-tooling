# web-code-editing — Code-Bearbeitung auf claude.ai

*Stand: 2026-08-29*

*[English version](README.en.md)*

**✅☑ Fertig und nutzbar.** Skilltext in beiden Sprachen, Frontmatter gesetzt; die Erprobung als hochgeladener Skill steht noch aus (siehe „Stand und Offenes").

**Der Skill regelt das Erstellen und Ändern von Code auf claude.ai für ein bestehendes Projekt** — mit drei Kernen: Quellen vollständig sichern, bevor geschrieben wird; geänderte Dateien mechanisch als Download zurückgeben statt sie aus dem Kontext neu zu diktieren; kleine Änderungen als Vorher/Ersetzen-Schema im Chat. Er ist **nur für claude.ai** (Zielwelt „nur web", `skill-dev-doc.md` Kapitel 9.4): In Claude Code schreibt das Edit-Werkzeug direkt in die Dateien, dort ist nichts davon nötig.

## Installation

Custom Skills kommen auf claude.ai als ZIP in die Skill-Einstellungen (Pro/Max/Team/Enterprise, Code-Ausführung eingeschaltet). Gewählt wird eine Sprachfassung — `SKILL.de.md` oder `SKILL.en.md` —, sie muss umbenannt nach `SKILL.md` ins ZIP gepackt werden. Das ZIP wird `web-code-editing.zip` benannt: claude.ai übernimmt den ZIP-Dateinamen als Skill-Namen. Weitere Dateien gehören nicht dazu; die READMEs werden im ZIP nicht benötigt.

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
