---
name: mq-tdd
description: "Implementera MQ-features och bugfixar testdrivet vid publika CLI-, MCP- och Python-kontrakt när meningsfulla regressionstester är rimliga."
---

# MQ TDD

Läs repo-instruktioner, befintliga tester och faktisk check-konfiguration. Definiera önskat beteende och testgräns från uppgiften och etablerade kontrakt. Bekräftelse behövs bara om beteende eller publikt kontrakt är oklart, inte för ett redan etablerat gränssnitt.

Arbeta en vertikal beteendeskiva i taget:

1. Skriv ett test med oberoende förväntat resultat: specificerad JSON, känd fixture, exitkod eller dokumenterat kontrakt.
2. Kör det och kontrollera att det faller av rätt anledning, inte bara på trasig setup.
3. Gör minsta ändring som uppfyller beteendet och kör testet igen.
4. Kör relevanta befintliga kontroller. Håll eventuell lokal förenkling inom uppgiften och behåll gröna tester.

För CLI: kontrollera exitkod och relevanta stdout/stderr-kontrakt. För MCP: testa schema, felrespons och faktiskt anrop vid gränsen. För Python: testa publikt beteende, inte privata hjälpmetoder. Följ repoets testverktyg; anta inte pytest eller en viss MCP-klient.

Mocka externa gränser när miljön kräver det, men redovisa vad mockningen lämnar overifierat. Isolera tid, filesystem och nätverk. Tester får inte anropa produktion eller använda riktiga hemligheter.

Undvik tester som speglar implementationen, tautologiska förväntningar och stora mängder tester för hypotetiska beteenden. För enkla dokumentationsändringar räcker lätt validering. Klart när rätt fel har observerats före fix, relevant test är grönt och kvarvarande risker är redovisade. Commit och publicering följer separat uppgiftsmandat.

## Ursprung

MQ-anpassning av Matt Pococks motsvarande skill, MIT, commit d81f3a183412e71a5b1e84ca21bc1a35eea03a60. Källa: [mattpocock/skills](https://github.com/mattpocock/skills). Licens: [LICENSE](LICENSE).
