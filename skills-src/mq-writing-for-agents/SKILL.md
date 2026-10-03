---
name: mq-writing-for-agents
description: "Skapa eller förbättra MQ-skills och agentinstruktioner med precisa triggers, källhänvisningar och verifierbara slutkriterier."
---

# MQ Agentinstruktioner

Läs faktisk instruktion, dess referenser och tillämplig AGENTS.md. Identifiera målverktyg och den observerade brist som ändringen ska lösa.

- Beskriv kapabilitet och konkreta aktiveringsvillkor i skillens name/description. Avgränsa från närliggande MQ-skills där felaktig aktivering är sannolik.
- Håll alltid laddade instruktioner korta. Hänvisa till faktiska källor med villkor för när de ska läsas; lagra större modespecifika detaljer separat bara när det hjälper.
- Varje arbetssteg ska ha ett observerbart slutkriterium. Ange vad som räknas som bevis och vad som återstår när verifiering inte kan ske.
- Använd befintliga MQ-kommandon, ansvar och dokumentvägar. Kontrollera verktygens tillgänglighet och syntax; skriv inte in gissade API:er eller duplicerade kommandokataloger.
- Behåll en källa per regel. Skilj runtime-data, repo-kontrakt och beständigt minne. Instruktionen får inte ge nytt mandat för externa skrivningar, commit, produktion eller destruktiva åtgärder.
- Använd plattformsneutrala instruktioner för delade Codex/Claude-skills. Lägg produktspecifik UI-metadata i agents/openai.yaml när relevant.

Validera YAML-frontmatter, namn, relativa referenser och eventuella scripts. Granska minst ett realistiskt aktiveringsfall och ett närliggande fall där skillen inte ska användas. Redovisa filändringar och vad valideringen faktiskt täcker. Föreslå inte ny agentorkestrering om uppgiften bara gäller text.

## Ursprung

MQ-anpassning av Matt Pococks motsvarande skill, MIT, commit d81f3a183412e71a5b1e84ca21bc1a35eea03a60. Källa: [mattpocock/skills](https://github.com/mattpocock/skills). Licens: [LICENSE](LICENSE).
