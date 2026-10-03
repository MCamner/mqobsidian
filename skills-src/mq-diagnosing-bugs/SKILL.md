---
name: mq-diagnosing-bugs
description: "Diagnostisera reproducerbara MQ-fel och prestandaregressioner med en verifierbar återkopplingsloop."
---

# MQ Felsökning

Fastställ berört repo från konfiguration eller stackverktyg. Läs AGENTS.md och aktuell task-pack. Använd CodeGraph först när repot är indexerat.

1. Beskriv användarens exakta symptom och bygg den minsta körbara kontroll som fångar det: befintligt test, CLI med fixture, HTTP-anrop eller återspelad redigerad logg. Kör kontrollen och visa relevant output och exitkod. För intermittenta fel: mät felfrekvens och håll indata och miljö kontrollerade.
2. Minimera reproduktionen en variabel i taget. Kontrollera att samma fel fortfarande uppstår.
3. Formulera rangordnade, falsifierbara hypoteser. Välj mätningar som skiljer dem åt; använd riktad instrumentering med ett unikt prefix.
4. Skriv ett regressionstest vid den gräns där felet faktiskt uppstår, när det är rimligt. Se det falla före en kirurgisk fix. Kör sedan testet och originalreproduktionen igen.
5. Ta bort tillfällig instrumentering. Redovisa bekräftad orsak, ändring och verifieringsbevis. Om korrekt testgräns saknas, dokumentera begränsningen.

MQ: mq-agent äger samlad stackstatus, mqlaunch är terminalingång och lokal doctor, mq-mcp analysverktyg, mq-hal operatörsbild, mqobsidian varaktigt minne. Kör bara relevanta läsande kontroller och kontrollera faktisk --help innan nya kommandon används. Minne ersätter inte aktuell runtime-sanning.

Om reproduktion saknas: redovisa vad som prövats och fortsätt med läsande insamling. Märk hypoteser som obekräftade; deklarera inte en orsak eller fix som verifierad. Använd mq-evidence-review om den finns för osäkra slutsatser. Visa endast maskerade loggar och håll hemligheter i miljövariabler. Produktionsinstrumentering, tjänsteändringar och destruktiva åtgärder behöver separat mandat.

## Ursprung

MQ-anpassning av Matt Pococks motsvarande skill, MIT, commit d81f3a183412e71a5b1e84ca21bc1a35eea03a60. Källa: [mattpocock/skills](https://github.com/mattpocock/skills). Licens: [LICENSE](LICENSE).
