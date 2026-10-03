---
name: mq-retro
description: "Granska en genomförd MQ-arbetssession och prioritera konkreta förbättringar i kontroller, navigation och agentmiljö."
---

# MQ Retro

Utgå från den session användaren anger, annars aktuell session. Läs tillgängliga diffar, kommandoutfall och fel; uppfinn inte historik.

Identifiera högst tre förbättringar med belagd effekt:
- Navigation: saknade referenser, föråldrat index eller otydliga ansvar som fördröjde arbetet.
- Kontroller: befintliga tester, lint eller doctor som inte kördes eller vars signal missades. Läs faktisk CI och checks före förslag om nya.
- Instruktioner: motsägelser, dubblerade regler eller otydliga triggers som gav ett observerat fel.
- Verktygsekonomi: upprepade dyra anrop eller rapporter som saknade beslutssignal.

Mekaniska fel bör i första hand få en billig deterministisk kontroll i befintlig verktygskedja. Bedömningsfrågor hör hemma i relevant standard eller skill. Lägg inte fler globala regler för ett engångsfel utan stöd.

Rapportera fynd, sessionsbevis, konsekvens och minsta konkreta förbättring i prioritetsordning. Detta är en granskning; ändra miljö, filer eller minne endast om användarens uppgift också omfattar det. Koppla eventuell minnesinspelning till befintligt auktoriserat MQ-flöde. Klart när rekommendationerna går att genomföra och varje förslag har ett faktiskt underlag.

## Ursprung

MQ-anpassning av Matt Pococks motsvarande skill, MIT, commit d81f3a183412e71a5b1e84ca21bc1a35eea03a60. Källa: https://github.com/mattpocock/skills. Licens: [LICENSE](LICENSE).
