# Chrome-Bridge: welche Meldung welche Schicht betrifft

Diese Datei ist zu lesen, wenn die Anbindung nicht zustande kommt oder mitten im Lauf abreißt. Die Voraussetzungen selbst stehen in der `SKILL.md`; hier steht, was ein Fehlschlag bedeutet, wenn sie erfüllt sind und es trotzdem klemmt.

Der Zweck ist die Abgrenzung. Die teuerste Diagnose ist die, die den Nutzer zu einer Umstellung schickt, die mit der Ursache nichts zu tun hat — und genau daran ist die Untersuchung dieser Bridge selbst einmal einen Nachmittag hängengeblieben.

## Was ausdrücklich keine Ursache ist

**Verschiedene Konten in Chrome und in Claude Code sind kein Fehler.** Die Bridge folgt allein der claude.ai-Websitzung, die im Tab gerade aktiv ist — unabhängig davon, an welchem Konto diese Claude-Code-Sitzung hängt. Zweimal unabhängig reproduziert, einmal nach vollständigem Rechner-Neustart mit von Anfang an verschiedenen Konten. Schick den Nutzer also nicht zum Angleichen der Konten.

Dass dieser Irrtum wiederkehrt, hat einen Grund: **Anthropics eigene Fehlermeldung behauptet die Kontogleichheit** — „Please ensure the Claude browser extension is installed and running, and that you are logged into claude.ai with the same account as Claude Code.“ Eine Fehlermeldung zählt mögliche Ursachen auf; sie belegt keine Bedingung. Wer sie liest und den Testweg nicht kennt, schreibt die Pflicht erneut hin — in der Anwenderdokumentation dieses Skills ist genau das neun Tage lang passiert.

**Ein Kontowechsel im Tab bricht eine stehende Bridge nicht.** Ebenfalls zweimal reproduziert, das zweite Mal mit vertauschten Rollen. Nach dem Wechsel liefert der Tab prompt die neue Organisation, ohne dass sich die Bridge neu anmelden muss.

**Die Bridge ist nicht auf claude.ai beschränkt.** Navigation und Skriptausführung funktionieren auch auf fremden Domains. Ein Fehlschlag beim claude.ai-Aufruf ist deshalb noch kein Befund über die Anbindung.

## Vier Meldungen und ihre Schicht

**`Claude in Chrome is turned off in your settings`** — der Connector-Schalter. Eine der Voraussetzungen aus der `SKILL.md` ist nicht erfüllt, und der Nutzer stellt sie her. Der Schalter wirkt nicht rückwirkend auf schon offene Tabs.

**`Browser extension is not connected`** — zwei Ursachen, die zu unterscheiden sind. Beim **ersten** Aufruf: `@browser` fehlt an der Nachricht, oder eine Voraussetzung ist offen. **Mitten im Lauf** bei zuvor stehender Anbindung: das Flapping der Beta, siehe unten.

**`account_session_invalid`** — im Tab ist niemand bei claude.ai angemeldet. Die Bridge selbst steht dabei weiter: Navigation und Skriptausführung funktionieren, nur der claude.ai-API-Aufruf schlägt fehl. Betroffen ist die Websitzung, nicht die Anbindung.

**`API Error: Connection lost mid-response`** — die Modellverbindung dieser Claude-Code-Sitzung, nicht die Bridge. Beobachtet mitten im Großlauf über 171 Chats; der Ablauf lief danach ohne erneuten Zugriffsverlust weiter. Diese Meldung gehört nicht zu den Bridge-Befunden — sie sieht dem Flapping ähnlich, betrifft aber eine andere Schicht.

## Flapping der Beta

Verschwindet der MCP-Server `claude-in-chrome` ganz aus der Werkzeugliste, oder reißt die Anbindung mehrfach ohne erkennbaren Anlass ab und kommt wieder, ist das die Instabilität der Beta — keine Kontofrage und keine fehlende Voraussetzung. Über einen Nachmittag mehrfach beobachtet. Die richtige Antwort ist abwarten und erneut versuchen; eine Umstellung am Konto ist es nicht.

## Was du im Tab siehst

Du siehst ausschließlich deine eigenen Tabs, nie die des Nutzers. Ein `tabs_context_mcp` ohne `createIfEmpty` meldet in einer frischen Sitzung „No tab group exists for this session“ — das ist keine leere Liste, sondern das vollständige Fehlen jeder Sichtbarkeit auf vorhandene Tabs. Mit `createIfEmpty: true` entsteht ein **neuer, leerer** Tab, nicht der vom Nutzer geöffnete. Ein vorab geöffneter claude.ai-Tab ist deshalb weder nötig noch erreichbar.

## Woher diese Aussagen kommen

Aus dem systematischen Testweg zur Bridge, der im Repository dieses Skills unter `chrome-access.de.md` liegt — Stufen 0 bis 8, je Versuch mit Datum, Ausgangslage und Ergebnis, einschließlich der Versuche mit uneindeutigem Ausgang. Diese Datei gehört zur Entwicklung und ist im Installationspaket nicht enthalten. Wer eine Aussage hier anzweifelt oder nach einer Änderung an Anthropics Bridge neu messen muss, findet dort das Verfahren.
