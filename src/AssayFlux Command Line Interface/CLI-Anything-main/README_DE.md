# AssayFlux CLI-Plattform

Die AssayFlux CLI soll der zentrale Einstiegspunkt zum Prüfen, Ausführen, Testen und Verwalten von AssayFlux-Projekten mit `.af`-Quelldateien werden. Der hier importierte CLI-Automatisierungscode wird noch geprüft und ist nicht vollständig integriert.

## Sprachzentrierte Regeln

- `.af`-Quelldateien müssen über den kanonischen AssayFlux-Sprachkern geparst, semantisch geprüft und ausgeführt werden.
- CLI-Dienste dürfen keine abweichende Grammatik definieren.
- Anwendungsspezifische Befehle gehören hinter modulare Service-Schnittstellen.
- Berechtigungen, Nebenwirkungen, Fehler und Ausgabeformate müssen eindeutig sein.

## Aktueller Status

**Importiert; native AssayFlux-Integration noch nicht verifiziert.** Der importierte Code bedeutet nicht, dass alle Befehle bereits native AssayFlux-Funktionen sind.

## Herkunft und Kompatibilität

Die ursprüngliche deutsche Dokumentation ist in [UPSTREAM_README_DE.md](UPSTREAM_README_DE.md) erhalten; die vollständige englische Referenz steht in [UPSTREAM_README.md](UPSTREAM_README.md). Upstream-Lizenzen, Copyright-Hinweise, Attribution, Anwendungsnamen und kompatibilitätsrelevante Kennungen bleiben erhalten.

## Nächste Schritte

- Befehle, Abhängigkeiten, unterstützte Anwendungen und Lizenzen inventarisieren.
- Einheitliche Befehlsregistrierung, strukturierte Ausgaben und Exit-Codes definieren.
- Nebenwirkungsreiche Aktionen mit Berechtigungen absichern und testen.
- Befehle erst nach bestandenen Integrations- und Packaging-Tests als unterstützt kennzeichnen.

Diese Seite verwendet AssayFlux-Branding für die Integrationsgrenze und behauptet nicht, dass der Upstream-Code ursprünglich von AssayFlux stammt.
