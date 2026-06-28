# Workflow Observations

## Problem eller system

När mq-agent kör ett workflow (Phase 8: `bridget --workflow` →
`mq-agent workflow run`) uppstår körningsdata: vilken tool-sekvens som kördes,
om den lyckades, var den föll, hur lång tid den tog och hur många godkännanden
den krävde. Den datan är inte minnesbevis (`memory-observation.v1`) — den är
*run-metrics*. Phase 9 ger den ett eget kontrakt och en egen lokal vy-yta i
mqobsidian.

mqobsidian äger vokabulären men **kör ingenting**. Det enda systemet gör är att
visa vilka sekvenser som återkommer. Se [[command-learning-system]] för det
parallella kommando-mönsterbiblioteket som denna yta speglar.

---

## Synligt utfall

Workflow-ytan ska över tid kunna svara på:

- vilka workflow-sekvenser återkommer?
- vilka lyckas / misslyckas?
- var bryts de (vilket steg faller oftast)?
- hur lång tid tar de i snitt?
- hur många godkännanden kostar de?
- vilka sekvenser är kandidater att återanvända?

---

## Kontrakt

`schemas/workflow-observation.v1.json` (publik, tracked) är kontraktet mq-agent
emitterar mot. En post är **en workflow-körning**. Obligatoriska fält:
`schema`, `id`, `timestamp`, `producer`, `repository`, `workflow_id`,
`template`, `task_type`, `tool_sequence`, `outcome`
(`completed` | `failed` | `cancelled`). Valfria: `failed_step`, `duration_ms`,
`approval_count`, `tags`, `metadata`.

`memory-observation.v1` lämnas orört — de två kontrakten får inte blandas.

### Sanering (hård regel)

Endast **sanerade** tool-namn och resultat lagras. Aldrig:

- fullständiga prompts
- rå stdout
- hemligheter / tokens
- absoluta privata sökvägar

Posterna landar i en **lokal-only, gitignored** yta:
`memory/workflows/inbox/workflow-observations.jsonl`.

---

## Vyer

`memory/workflows/build_workflow_views.py` läser inbox och renderar fyra
lokala vyer i `memory/workflows/views/`:

- `workflow-top-reusable.md` — sekvenser rankade på frekvens × success
- `workflow-failure-points.md` — vanligaste `failed_step`
- `workflow-by-repo.md` — grupperat per `repository`
- `workflow-proposals.md` — kandidater till återanvändning (**endast förslag**)

Builder + schema + denna doc är tracked. Inbox, genererade vyer och tester är
lokal-only, precis som `memory/commands` (ownership boundary: lokala renderare
ligger medvetet inte i `scripts/`).

---

## Gräns

- mqobsidian **visar** vilka sekvenser som återkommer — den kan inte köra dem.
- Frekvens befordrar aldrig något automatiskt (ADR-007, ADR-008). `*-proposals`
  är förslag; befordran avgörs av scoring-motorn + människa, inte av denna yta.
- Buildern skriver inget under `memory/local/`, emitterar inga promotion-events
  och har ingen exekveringsväg.
