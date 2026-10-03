---
name: mq-domain-modeling
description: "Förtydliga MQ-begrepp, komponentansvar och arkitekturbeslut när terminologi eller systemgränser diskuteras."
---

# MQ Domänmodellering

Läs befintlig ordlista, arkitekturdokumentation och relevanta ADR:er före nya dokument. Kontrollera påståenden mot kod och aktuella kontrakt; skilj önskat beteende från observerat.

Utgå från MQ:s ansvar: mq-agent orkestrering och stackstatus; macos-scripts/mqlaunch terminalingång och lokal doctor; mq-mcp analysverktyg; mq-hal operatörssummering; mqobsidian varaktigt minne; repo-signal kvalitetsbedömning. Flagga avvikelser som måste verifieras, inte som automatiska namnbyten.

När ett ord har flera betydelser, föreslå ett precist begrepp och pröva det med ett konkret scenario. Fråga endast när valet påverkar kontrakt eller beteende och kontexten inte avgör det.

Vid auktoriserad dokumentationsändring: uppdatera befintlig ordlista på dess etablerade plats. Skapa GLOSSARY.md först när en faktisk definition finns och ingen motsvarande källa finns. Ange term, kort definition, ansvar och viktiga skillnader. Implementation hör hemma i kodreferenser eller arkitekturdokument, inte i definitionen.

Skapa ADR endast för ett betydande, dyrt att reversera val med verkliga alternativ: kontext, beslut, alternativ och konsekvenser. Bevara etablerade dokumentvägar och en enda auktoritativ definition. Klart när de berörda termerna är konsekventa och kvarvarande osäkerhet är uttrycklig. Att diskutera modellen ger inte mandat att refaktorera kod.

## Ursprung

MQ-anpassning av Matt Pococks motsvarande skill, MIT, commit d81f3a183412e71a5b1e84ca21bc1a35eea03a60. Källa: [mattpocock/skills](https://github.com/mattpocock/skills). Licens: [LICENSE](LICENSE).
