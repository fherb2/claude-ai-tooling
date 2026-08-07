# Fossil-Sync für `~/.claude`

**Hält den Arbeitszustand von Claude Desktop und Claude Code — Konfiguration, Sitzungsprotokolle, Projektgedächtnis — automatisch zwischen mehreren Rechnern synchron, damit derselbe Kontext überall zur Verfügung steht.**

Status: **In Codierung.** Das Konzept steht vollständig (`implementierungs_doku.md`); das Hauptskript wird gerade danach neu geschrieben (siehe `fahrplan.md`), bisher auf keinem Rechner automatisiert im Einsatz.

## Ziel

Wer an mehreren Rechnern mit Claude Code arbeitet, hat ohne dieses Werkzeug mehrere unabhängige Gedächtnisse: Was auf dem Laptop erarbeitet wurde, existiert auf dem Arbeitsplatzrechner nicht. Ein Hintergrunddienst gleicht `~/.claude` dazu regelmäßig über ein privat gehostetes Fossil-Repository ab — unbeaufsichtigt im Normalfall, mit geführter Eskalation an den Nutzer, sobald ein echter inhaltlicher Konflikt auftritt.

## Anwendung (grob)

- Läuft nach der Einrichtung als periodischer Hintergrunddienst (systemd `--user`-Timer) auf jedem beteiligten Rechner — kein manuelles Zutun im Alltag.
- Im Erfolgsfall: kurze, sich selbst schließende Meldung, sonst nichts zu tun.
- Bei einem Konflikt: ein Dialog fragt, ob jetzt gelöst werden soll; bei Zustimmung öffnet sich ein Terminal mit einer Claude-Code-Sitzung, die den Konflikt Datei für Datei gemeinsam mit dem Nutzer klärt und erst mit dessen ausdrücklicher Zustimmung einbucht.
- Ein neuer, bislang eigenständig gewachsener Rechner wird einmalig über ein eigenes Zusammenführungsverfahren angebunden, nicht durch einfaches Überschreiben.

## Weiterführendes

- `implementierungs_doku.md` — vollständiges Konzept (Zusammenhänge, Vorgaben, Einheiten)
- `fahrplan.md` — aktueller Stand und nächste Schritte
- `Fossil-Synology-Konfigurationsanleitung-allgemein.md` — Betrieb eines schmalen Fossil-Servers
