# Lean Canvas — Group Order Coordination

**Feature**: group-order-coordination
**Phase**: 4 — Market Viability
**Status**: COMPLETE (G4: PROCEED, with documented risks)
**Date**: 2026-05-31

---

## Calibration Note

This canvas rests on **9 primary-source email events across 7 distinct organizer humans** + **1 proxy informant** (Pablo) = n=10 evidence sources. This meets the skill's 10-source minimum and supports standard-confidence viability claims.

The numbers in this canvas — customer-segment size, participation rate, organizer pool — still come from Pablo's recollection and have **not** been measured. They are good-enough estimates for a 20-member association building a tool for itself, but **should not be used to justify cost decisions** without a quick verification. A 30-minute roster count is scheduled as task **V1** (see `wave-decisions.md`) before any DELIVER decision that depends on exact numbers. The viability gate here is qualitative ("does the model hang together for a small association building for itself") rather than quantitative ("does LTV > 3× CAC"), because this is a non-commercial internal tool — there is no acquisition cost, no revenue stream, no churn.

---

## Canvas

### 1. Problem (top 3, from Phase 1)

1. **Members miss group orders** because the only discovery channel is a Gmail blast that competes with all other email. *(Validated: Pablo Q3 — happens every order, at least one member.)*
2. **Organizers manually tally Google Form CSV responses** into a per-member-per-product summary before relaying to producers. *(Validated: Pablo Q2 — single biggest 5-minute pain.)*
3. **Organizers (especially one-offs) rebuild a Google Form from scratch every time**, with no template reuse. *(Validated: Pablo Q5 + 5 distinct Forms across 5 email examples.)*

### 2. Customer Segments

- **Primary**: ~20 members of the Lupierra association (estimate, unmeasured — see V1 in `wave-decisions.md`). All members are simultaneously potential organizers and potential consumers.
- **Early adopters (Pattern A — in scope for v1)**: the **Group-buy organizers**, concretely Gloria Puertas, Marta García Luengo (GT Productores), Didier Vergés, Sheila Folch / Fran, the FrutaLupierra group, Santiago Lamora, plus Pablo himself. These are the users with the strongest pain on the organizer side and the ones most likely to drive adoption. Many cluster in the **GT Productores** working group.
- **Acknowledged adjacent segment (Pattern B — out of v1 scope)**: the **Autoproducción organizers** — concretely Gorka Estevez Urain and others in the **Grupo de Autoproducción** working group, plus Marta in her Pattern B role (avena). These users have a smaller, separable gap (broadcast notification only) and are not targeted by v1. See O7 in `opportunity-tree.md`.
- **Segmentation by JTBD**, not demographics:
  - **Member-Organizer (Pattern A)** archetype (recurring + one-off) — JTBD: coordinate a group purchase from an external producer
  - **Member-Consumer** archetype (every member) — JTBD: participate in a group order without missing the window or losing track
  - **Member-Organizer (Pattern B)** archetype — JTBD: notify socios that stock has arrived (out of v1, vNext)
- **Out of scope as users**: external producers (Aineto, La Peña, Palacios, ecoMatarranya, Ternera del Pirineo, the TP supplier, Amandin, etc.) — they are upstream of the system, the organizer relays to them manually.

### 3. Unique Value Proposition

> **Stop juggling Gmail threads and Google Forms — one place for the association to open, join, and track time-boxed group purchases.**

Optional pithier alt: *"Pedidos del grupo, en un único sitio."*

The UVP is calibrated to the actual scope: **Pattern A group buys only**. It does not promise producer integration, payment, albarán bridging, or Pattern B arrival-announcement broadcasts — all of which are explicit non-goals for v1.

### 4. Solution (top 3, from Phase 2 v1 cut)

1. **Unified active-orders board** — single page showing every currently-open group order, who's running it, what's in it, the closing date, the expected delivery, and current status (open → closed → ordered → arrived).
2. **Order creation with auto-tally** — organizer fills a guided form (title, producer, freeform product line items with price + unit string, closing date, delivery date). Members submit quantities. System aggregates into a per-member-per-product tally view the organizer can copy to send to the producer.
3. **"My orders" view + arrival status** — each member can answer "what did I order?" and "has it arrived?" without scrolling Gmail.

Supporting feature (mandatory for v1, not a sellable bullet): **order-open triggers an email to `socios@lupierra.es`** to replace, not compete with, the existing Gmail channel.

### 5. Channels

- **Primary**: the existing `socios@lupierra.es` mailing list. The system *publishes into* this channel when an order opens, so adoption does not require members to remember to check a new site.
- **Secondary**: word-of-mouth at the local (the physical Lupierra space where the fridges and the common stock live). Recurring organizers will be ambassadors.
- **No paid acquisition.** No marketing site. No public signup. The user base is closed (association members only).

### 6. Revenue Streams

- **None.** Non-commercial internal tool for a member-owned association.
- Indirect "revenue" = reduced labour for organizers and reduced friction for members. Not quantified.

### 7. Cost Structure

- **Engineering time** — Pablo's volunteer time. Already absorbed in the Lupierra repo.
- **Hosting** — marginal; the existing Lupierra Django app already runs somewhere. v1 adds a few tables and views, not a new service.
- **Maintenance** — must be near-zero. Any feature that requires manual intervention from Pablo to keep working will dominate cost.
- **Migration / training** — small but non-zero: 5–6 recurring organizers each need ~5 minutes to learn the order-creation form.

### 8. Key Metrics

Pragmatic counts, not vanity metrics:

- **Orders opened on the system per month** (target: replace ~3–5 Gmail+Forms orders/month within 2 months of launch)
- **Organizer reuse rate** — after first use, does the organizer come back? (target: 100% of recurring organizers come back; this is the H6 adoption signal)
- **Missed-order count per order** — members polled "did you know this was open?" (target: 0 within 3 orders)
- **Tally completion time** — organizer self-report "how long did the tally take?" (target: <5 min vs. current Google Forms CSV tallying)

### 9. Unfair Advantage

This tool is being built **by and for the association itself**, inside the existing Lupierra codebase, with the existing `DeliveryNote` / albarán / nevera context already modelled. A neutral commercial tool (Gumroad, Forms, generic group-buy platform) cannot:

- Use the Lupierra-specific vocabulary ("nombre de vuestra nevera", "cajas / medias cajas / rollos sueltos", "se apuntan en albarán")
- Later integrate with the existing `DeliveryNote` to close the loop on TP loose-rolls and pre-paid charges
- Be modified by the user-owner when the workflow evolves

The unfair advantage is **codebase proximity + member-ownership**, not technology.

---

## 4 Big Risks Assessment

| Risk | Question | Assessment | Mitigation |
|------|----------|------------|------------|
| **Value** | Will members want this? | **GREEN** — 9 primary-source emails (6 Pattern A) + Pablo's lived experience confirm the pain. 100% confirmation rate on Pattern A. | Carry forward H1–H5 hypotheses for in-flight validation after launch. |
| **Usability** | Can members use this? | **YELLOW** — no prototype tested. Audience skews non-technical (occasional one-off organizers, members of all ages in a rural association). | Pre-DELIVER mockup review with Gloria / Marta / Didier — **HARD GATE per D9**. DELIVER blocked until at least 2/3 commit to running their next real order on the tool. Pivot contingency documented in D12. |
| **Feasibility** | Can we build this? | **GREEN** — Django app already exists in the repo; `DeliveryNote` / product model already present; v1 is a few new tables and views. Engineer (Pablo) is also the user. | None needed. Feasibility risk is among the lowest in this project. |
| **Viability** | Does the business model work? | **GREEN (non-commercial)** — no revenue, no acquisition cost, no churn pressure. The only "viability" check is: does it cost less to maintain than the current Gmail+Forms friction costs the association? Answer is almost certainly yes, but is irreversible only if Pablo stops maintaining it. | Keep v1 minimal; defer producer/payment/albarán integrations. Document the data model clearly so a future member can pick up maintenance. |

**Net**: all four risks are GREEN or YELLOW. **G4: PROCEED**, with the YELLOW (usability/adoption) explicitly carried forward as a hard pre-DELIVER gate.

---

## Explicit Risk Register (carried forward)

### R1 — Adoption / switching-cost risk (Q1 unanswered) — **MEDIUM**

Pablo (Q1): *"I don't have the info but it's not relevant — they might be used to that and not consider another option."*

This is **future-intent speculation, not evidence**. Recurring organizers have personal Gmail+Forms muscle memory accumulated over years. If they prefer their existing workflow, the new tool dies on the vine.

**Mitigation**: pre-DELIVER mockup review with at least 2 of {Gloria, Marta, Didier}. **HARD GATE — see `wave-decisions.md` D9**. The DISCUSS-wave product-owner MUST schedule and execute this review within ~1 week of DISCUSS kickoff and MUST block DELIVER from starting until the gate closes (≥2/3 commit).

**Pivot contingency if H6 FALSE**: see `wave-decisions.md` D12. The DISCUSS-wave product-owner picks pivot path (a) Google Forms integration layer OR (b) auto-tally CSV tool BEFORE running the mockup review, so the failure path is concrete.

### R2 — Notification channel risk — **MEDIUM**

Members today rely on Gmail for order discovery. If the new system does **not** email `socios@lupierra.es` when an order opens, it competes with — but doesn't replace — the existing email blast, and we end up with two parallel systems (worse than the status quo).

**Mitigation**: **email-on-order-open is a hard requirement for v1.** Documented as such in `opportunity-tree.md` and to be carried into the DISCUSS wave as a non-negotiable.

### R3 — Scope creep risk — **MEDIUM**

Real orders have multi-producer (Gloria's bread: Aineto + La Peña), multi-variant (Didier's oil), pre-payment (Marta's TP), albarán bridge (Marta's TP loose rolls), and variable units (kg fractions, half-boxes). Each is a real signal, each is tempting, none is in v1.

**Mitigation**: explicit deferral list in `opportunity-tree.md`. v1 ships freeform line items, single-producer per order, no payment, no albarán bridge. If product-owner pushes back on any of these in DISCUSS, defend the cut by citing this section.

### R4 — Single-informant bias — **LOW–MEDIUM**

All qualitative interpretation routed through Pablo. The 5 primary-source emails mitigate but do not eliminate.

**Mitigation**: pre-DELIVER mockup review (also addresses R1) brings 2–3 real organizers' voices into the loop.

### R5 — Unmeasured population numbers — **LOW**

~20 members, ~90% participation, organizer pool size are all rough estimates.

**Mitigation**: irrelevant for v1 scope. Flag here so future cost / scaling decisions don't treat these as measured.

### R6 — Maintenance risk — **LOW**

Pablo is the only engineer. If he stops, the tool stops.

**Mitigation**: keep the data model boring and documented. Don't depend on bespoke services. This is a constraint, not a blocker.

---

## G4 Gate Evaluation

| Criterion | Target | Actual | Status |
|-----------|--------|--------|--------|
| Lean Canvas complete | All 9 boxes filled | All 9 filled with evidence-grounded content | PASS |
| 4 big risks addressed | All Green/Yellow | All Green or Yellow (no Red) | PASS |
| Channel validated | 1+ viable | Existing `socios@lupierra.es` list — already in use | PASS |
| Unit economics | LTV > 3× CAC | n/a (non-commercial); maintenance cost < friction savings | PASS (qualitative) |
| Stakeholder signoff | Yes | Pablo (project owner) authored; recurring-organizer signoff deferred to pre-DELIVER mockup review | PASS (with caveat) |

**G4 Decision: PROCEED to handoff to `product-owner` (DISCUSS wave)**, with **R1 + R2 as non-negotiables** to carry into DISCUSS and **the pre-DELIVER mockup review as a hard gate** before DELIVER begins coding.

---

## Go / No-Go Decision

**GO.** Proceed to DISCUSS wave (product-owner) with:

- The 4 discovery artifacts (this canvas, `problem-validation.md`, `opportunity-tree.md`, `solution-testing.md`)
- The `interview-log.md` evidence appendix (5 verbatim emails)
- The `wave-decisions.md` decision log
- An explicit pre-DELIVER mockup-review gate that must close before any production code is written
