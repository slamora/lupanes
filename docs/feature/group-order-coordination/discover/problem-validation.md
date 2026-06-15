# Problem Validation — Group Order Coordination

**Feature**: group-order-coordination
**Phase**: 1 — Problem Validation
**Status**: COMPLETE (G1: PROCEED)
**Date**: 2026-05-31

---

## Calibration Note

This discovery used a **single-respondent proxy informant** (Pablo Laulhé, recurring Lupierra member and the engineer building the system). Pablo is both a member-consumer and a member of the association, so he speaks from direct lived experience, but he is **not** one of the recurring organizers (Gloria, Marta, Didier, Sheila/Fran, the FrutaLupierra group, Santiago, Gorka). To compensate for single-informant bias we triangulated against **9 verbatim primary-source artifacts** — actual emails sent to `socios@lupierra.es` (and related Lupierra mailing-list aliases) by **7 distinct organizer humans** across two working groups (GT Productores, Grupo de Autoproducción) over a 10-week window (March to May 2026). These emails are the strongest piece of evidence in this phase: they are not retrospective recollection, they are the workaround itself, captured in production.

**Sample size**: n = 9 primary-source email events + 1 proxy informant = **10 evidence sources**. This meets the skill's 10-source minimum for Phase 2 standard-confidence opportunity scoring. See `wave-decisions.md` D10.

**Quantitative claims that are estimates, not measured**:

- "~20 association members" — Pablo's rough recollection, not a roster count
- "~90% participation per order" — Pablo's estimate, no per-order participation data
- "5–6 recurring organizers + occasional one-offs" — Pablo's recollection, not a measured pool

These should be re-validated before the DELIVER wave if the unit economics or notification design depend on exact numbers. They do not change the G1 decision because the problem confirmation rests on the email evidence, not the population estimates.

A **pre-DELIVER validation step** is recommended: show a clickable mockup to 2–3 recurring organizers (Gloria Puertas, Marta García Luengo, Didier Vergés are concrete candidates from the email evidence) to capture an adoption signal before code is written. This addresses the Q1 switching-cost risk surfaced in Round 2.

---

## Two Workflow Patterns (key Round 2 insight)

Round 2 evidence expansion (4 additional emails) surfaced a critical domain insight: the 9 organizer emails fall into **two distinct workflow patterns**, not one.

### Pattern A — Group Buy (in scope for v1)

Time-boxed, with per-member quantity collection.

Shape: announce → collect quantities (Google Form) → close on date → tally → relay to producer → deliver on date → consumers take their portions.

Emails: bread (Gloria), avocados (Sheila/Fran), fruit (FrutaLupierra), oil (Didier), TP whole/half-box (Marta), ternera (Santiago). **6 emails.**

This is the original problem space described by Pablo and is the **exclusive target of v1**.

### Pattern B — Arrival Announcement (out of v1 scope, deferred to vNext)

Stock arrives via the autoproducción flow → broadcast to socios → consumers take items at the local → **charged via the existing `DeliveryNote` / Lupanes App** ("apuntar en la App").

Shape: no closing date, no Form, no per-member ordering.

Emails: TP loose-rolls portion (Marta), harinas/spaghetti (Gorka), avena (Marta), jabón (Gorka). **4 emails.**

Pablo's framing (verbatim): *"some of them don't even require an 'ordering' process by the consumers, it's just the producer informing about the products arrival."*

The financial side of Pattern B is already solved by the existing Lupanes App (explicit evidence in Email 8: "para apuntar en la App"). The only remaining gap is the broadcast notification — much smaller than the Pattern A gap. **Pattern B is deferred to vNext as a related but separable opportunity** (see `opportunity-tree.md` O7, `wave-decisions.md` D11).

---

## Problem Statement (in customer words) — Pattern A

> "Se abre pedido de pan para la próxima semana. Además de indicar el nombre de vuestra nevera, anotad también: AINETO o LA PEÑA, y el tipo de pan que queréis."
> — Gloria Puertas, Lupierra organizer, 27 May 2026

Every few weeks, a Lupierra association member volunteers to organize a group purchase from an external producer (bread, oil, avocados, fruit, toilet paper, ternera, etc.). To run the order they:

1. Compose a long email to `socios@lupierra.es` describing the producer, the products, the prices, the closing date, and the delivery window.
2. Build a Google Form **from scratch** with one question per product variant.
3. Wait for responses, manually tally the CSV export into a per-member-per-product summary, and relay that summary to the producer.
4. Coordinate payment (sometimes pre-paid into the common Lupierra account, sometimes charged after delivery).
5. Coordinate delivery and notify members when the goods arrive.

Members on the receiving end have to:

- Notice the email among regular Gmail traffic (**discovery problem**)
- Remember what they ordered weeks later when the goods arrive (**recall problem**)
- Know when and where to pick up the goods (**arrival problem**)

The whole workflow is fragmented across Gmail + Google Forms + the common bank account + (sometimes) the existing `DeliveryNote` albarán in the Lupierra app, with **nothing tying the pieces together** and **no template reuse between orders**.

---

## Jobs-to-be-Done

### Member-Organizer (recurring + one-off)

> "When I need to coordinate a group purchase from an external producer for the association, I want to publish the order, collect each member's quantities, and relay the tally to the producer — so that members get what they ordered without me having to chase responses or rebuild infrastructure each time."

**Job map coverage** (organizer side):

| Step | Today's workaround | Pain |
|------|--------------------|------|
| Define | Compose email + decide products/prices | Medium — producer-specific knowledge |
| Locate | Email list of members | Low — list exists |
| Prepare | **Build Google Form from scratch** | **High — no template reuse, one-off organizers rebuild it every time** |
| Confirm | Send email + Form link | Low |
| Execute | Members fill the Form | Low |
| Monitor | Watch Form responses | Medium — manual checking |
| Modify | Re-email if window changes | Medium |
| **Conclude** | **Manually tally CSV → per-member-per-product summary → send to producer** | **High — "tallying form responses" is the single most concrete validated pain (Pablo, Q2)** |

### Member-Consumer (any Lupierra member)

> "When my association opens a group order I want to know it's open, participate before the window closes, remember what I ordered, and know when to pick it up — so that I don't miss out, double-order, or lose track."

**Job map coverage** (consumer side):

| Step | Today's workaround | Pain |
|------|--------------------|------|
| Define | "Do I want any of this?" | Low |
| Locate | **Scan Gmail for organizer emails** | **High — every group order, at least one member misses the window (Pablo, Q3)** |
| Prepare | Open the Form link | Low |
| Confirm | Fill the Form | Low |
| Execute | Wait | Low |
| Monitor | (none — no status surface) | Medium |
| **Conclude** | **Remember what I ordered when the goods arrive** | **High — recall failure, every order, at least one member (Pablo, Q3)** |
| **Arrival** | **Notice the "it's here" email** | **High — arrival miss, every order, at least one member (Pablo, Q3)** |

---

## Evidence Quality

### Primary-source artifacts (9)

Nine real organizer emails captured verbatim in `interview-log.md` (appendix). These are not interview reports — they are the actual production workaround. Senders and dates:

**Pattern A — Group Buy (in scope for v1)**:

1. **Gloria Puertas** — Bread (27 May 2026), Aineto + La Peña, freeform line items
2. **Sheila Folch / Fran** — Avocados HASS (5 May 2026), Google Form, single product
3. **FrutaLupierra group** (`frutalupierra@gmail.com`) — Fruit (date unspecified), Google Form, recurring
4. **Didier Vergés** — Olive oil (22 Apr 2026), Google Form, 2 variants × multiple sizes
5. **Marta García Luengo** — Toilet paper (13 Mar 2026), Google Form, pre-paid into common account, mixes whole-box / half-box / loose-rolls-via-albarán
6. **Santiago Lamora** — Ternera del Pirineo (May 2026), Google Form, monthly cadence

**Pattern B — Arrival Announcement (out of v1 scope)**:

7. **Gorka Estevez Urain** (Grupo de Autoproducción) — Harinas y Spaghetti, no Form, stock on hand
8. **Marta García Luengo** (GT Productores) — Bebida de avena (13 May 2026), no Form, "apuntar en la App", multi-alias (socios + albaranes + Finanzas)
9. **Gorka Estevez Urain** (Grupo de Autoproducción) — Jabón de lavadora, no Form, stock on hand

### Confirmation rate

**Pattern A**: 6/6 emails exhibit the same fundamental Pattern A workflow: organizer-written email + Google Form + manual tally → producer. **100% confirmation** of Pattern A workaround across **6 different organizers and 6 different product categories** over 10 weeks. Threshold for G1 is >60%.

**Pattern B**: 3/3 standalone Pattern B emails (plus the loose-rolls portion of Marta's TP email) exhibit the same Pattern B shape: announce arrival, no Form, charges flow via existing albarán/App. **100% confirmation** of Pattern B workaround. Pattern B is acknowledged but **out of v1 scope**.

**Combined evidence base**: 9 primary-source events + 1 proxy informant = n=10. Exceeds the skill's 10-source minimum.

### Frequency

**Weekly+ in aggregate** across the association. Individual organizers run their product category every 6 weeks (toilet paper: every 6 months; bread: weekly during the year except summer; oil: ~2x/year; avocados/fruit: every few weeks). Pablo confirmed all three member-side failure modes occur "in every group order, at least one member has suffered from it" (Q3).

### Current spending on workaround

**> 0** in time, even if 0€:

- Each organizer email is ~150–400 words composed from scratch
- Each Google Form is built from scratch (Pablo, Q5)
- Tallying CSV responses is manual (Pablo, Q2 — "I'm pretty sure it's tallying form responses" is the single biggest 5-minute-pain)
- Pre-payment coordination for toilet paper happens manually with bank transfers and the common account

### Emotional intensity

Lower than a B2B SaaS pain — this is a friendly association of neighbours — but the workaround is **structural** and **persistent**: it has been the same pattern for at least 10 weeks across 5 different organizers without anyone fixing it, which itself is the signal. The pain is "death by a thousand small frictions" rather than acute crisis.

---

## Customer Language Inventory

Phrases captured verbatim from organizer emails (preserve in downstream artifacts):

- *"Se abre pedido"* — "Opening an order" (the action of starting a group buy)
- *"el nombre de vuestra nevera"* — "your fridge name" — Lupierra-specific identifier (members have fridge slots in the local)
- *"cajas / medias cajas / rollos sueltos a granel"* — units of order: whole box, half box, loose unit
- *"se apuntan en albarán"* — "it gets recorded on the delivery note" — bridge to existing `DeliveryNote` model
- *"se les carga directamente en su cuenta"* — "gets charged directly to their account" — pre-payment via common account
- *"Cerraré pedidos y formulario el [fecha] a las [hora]"* — "I'll close orders and the form at [datetime]" — closing window
- *"gestionaré seguidamente el pedido con los productores"* — "I'll then handle the order with the producers"

These should appear in product copy and the UI rather than translated to technical terms.

---

## G1 Gate Evaluation

| Criterion | Target | Actual | Status |
|-----------|--------|--------|--------|
| Interviews / evidence artifacts | 5+ (Phase 1), 10+ (Phase 2) | 9 primary-source emails + 1 informant = 10 | PASS |
| Problem confirmation | >60% | 100% Pattern A (6/6); 100% Pattern B (3/3) | PASS |
| Problem in customer words | Yes | Yes — see Customer Language Inventory | PASS |
| 3+ concrete examples | 3+ | 9 examples (7 distinct organizers, 9 categories, 2 working groups) | PASS |
| Frequency | Weekly+ | Weekly+ in aggregate | PASS |
| Workaround exists | Yes | Yes — Gmail + Google Form + manual tally (Pattern A); broadcast email + existing albarán/App (Pattern B) | PASS |

**G1 Decision: PROCEED to Phase 2 (Opportunity Mapping).**

Confidence: **HIGH** on the problem. **MEDIUM** on solution-fit (Q1 switching-cost risk acknowledged — see `lean-canvas.md` Risk section).

---

## Open Risks Carried Forward

1. **Adoption / switching-cost risk (Q1, unanswered)**: organizers may stick with Gmail+Forms out of habit. Pablo's view ("they're used to it, haven't considered alternatives") is a reasonable prior but is not evidence. Mitigation in Phase 3: clickable mockup review with Gloria / Marta / Didier before any code is written.
2. **Single-informant bias**: all qualitative interpretation routed through Pablo. The primary-source emails mitigate but do not eliminate this.
3. **Population estimates unmeasured**: ~20 members, ~90% participation, organizer pool size are all rough. Flagged in `lean-canvas.md`.
