# Opportunity Solution Tree — Group Order Coordination

**Feature**: group-order-coordination
**Phase**: 2 — Opportunity Mapping
**Status**: COMPLETE (G2: PROCEED)
**Date**: 2026-05-31

---

## Sample Size Note

Phase 2 opportunity scoring is grounded in **9 primary-source email events** across **7 distinct organizer humans** + **1 proxy informant** (Pablo). Combined n=10, meeting the skill's 10-source minimum for standard-confidence opportunity scoring. Resolved via Round 2 evidence expansion (4 additional emails surfaced after peer review). See `wave-decisions.md` D10.

## Scope Note — v1 targets Pattern A only

Discovery surfaced **two workflow patterns** (see `problem-validation.md` "Two Workflow Patterns" section and `interview-log.md` "Pattern Recognition" section):

- **Pattern A — Group Buy**: time-boxed, per-member quantity collection, Google Form, manual tally. 6/9 emails.
- **Pattern B — Arrival Announcement**: stock on hand, broadcast notification only, charges via existing albarán/App. 3/9 standalone emails (+ partial overlap on Marta's TP).

**v1 explicitly targets Pattern A.** Pattern B is documented as opportunity O7 below and deferred to vNext. Anchored in `wave-decisions.md` D11.

---

## Desired Outcome

> **Lupierra members can run group purchases (Pattern A) from external producers with less friction than the current Gmail + Google Forms workaround, without any member missing an order they wanted, and without organizers having to rebuild infrastructure each time.**

Anchored in the validated Jobs-to-be-Done from `problem-validation.md`:

- **Member-Organizer JTBD**: "Coordinate a group purchase from an external producer for the association." (Pattern A)
- **Member-Consumer JTBD**: "Participate in group orders for products I want without missing the window or losing track." (Pattern A)

---

## Opportunity Solution Tree

```
Desired Outcome:
  Lupierra members run group purchases with less friction,
  no missed orders, no rebuilt infrastructure.
    |
    +-- O1: Members can't reliably DISCOVER that an order is open  [score: 16]
    |     +-- S1.A: Central "active orders" board (one page lists all open orders)  *** v1 ***
    |     +-- S1.B: Email notification on order-open (keep Gmail channel)            *** v1 ***
    |     +-- S1.C: Push / digest notification (vNext)
    |
    +-- O2: Organizers tally Google Form CSVs by hand              [score: 15]
    |     +-- S2.A: System auto-aggregates responses into per-member-per-product tally  *** v1 ***
    |     +-- S2.B: One-click export of tally to send to producer  (vNext)
    |     +-- S2.C: Producer-side ingestion API  (out of scope)
    |
    +-- O3: Organizers rebuild a Google Form from scratch every time [score: 13]
    |     +-- S3.A: Organizer creates an order with freeform product line items + closing date  *** v1 ***
    |     +-- S3.B: Duplicate-previous-order template  (vNext)
    |     +-- S3.C: Per-producer product catalog with variants  (vNext, scope risk)
    |
    +-- O4: Members can't RECALL what they ordered weeks later     [score: 12]
    |     +-- S4.A: "My orders" view — each member sees their own line items per active order  *** v1 ***
    |     +-- S4.B: Order-arrival summary email with each member's lines  (vNext)
    |
    +-- O5: Members don't know when orders ARRIVE                  [score: 11]
    |     +-- S5.A: Order has a status (open → closed → ordered → arrived) visible on the board  *** v1 ***
    |     +-- S5.B: Email notification on arrival  (vNext)
    |     +-- S5.C: Bridge to existing DeliveryNote/albarán (vNext — TP loose-rolls case)
    |
    +-- O6: Payment coordination is manual & off-system            [score: 8]
    |     +-- S6.A: Mark order as "pre-paid required" + members self-declare payment  (vNext)
    |     +-- S6.B: Charge member accounts via DeliveryNote bridge  (vNext)
    |     +-- S6.C: Bank/transfer integration  (out of scope)
    |
    +-- O7: Pattern B arrivals (autoproducción stock) lack a discoverable broadcast surface  [score: 9 — vNext]
          +-- S7.A: "New stock available" notification surface integrated with existing DeliveryNote  (vNext)
          +-- S7.B: Stock-arrivals broadcast page (read-only, no per-member ordering)  (vNext)
          +-- S7.C: Multi-alias notification routing (socios + albaranes + Finanzas)  (out of v1 scope)
```

Legend: `*** v1 ***` = in the v1 cut. Other items are explicitly deferred to vNext or out of scope.

---

## Opportunity Scoring

**Formula**: Score = Importance + Max(0, Importance − Satisfaction). Each 1–10. Max 20.

Scores are calibrated against the **9 primary-source emails** and Pablo's Round 1+2 answers. With n=10 evidence sources (9 emails + 1 informant) scores are now **standard-confidence**, not provisional. Pattern A scoring is reinforced by Email 6 (Santiago Lamora — confirms the workflow extends to monthly meat orders). Pattern B is introduced as O7.

| ID | Opportunity | Importance | Satisfaction | Score | Reasoning |
|----|-------------|------------|--------------|-------|-----------|
| **O1** | Members can't reliably discover an order is open (Pattern A) | 9 | 2 | **16** | Pablo Q3: discovery failure happens "in every group order, at least one member." Today's only channel is a Gmail blast competing with all other mail. Reinforced by 6 Pattern A emails. |
| **O2** | Organizers tally CSV responses by hand (Pattern A) | 9 | 3 | **15** | Pablo Q2: explicitly named as the single biggest 5-minute pain. Affects every organizer, every order. 6/6 Pattern A emails use Google Form CSV aggregation manually. |
| **O3** | Organizers rebuild Forms from scratch (Pattern A) | 8 | 3 | **13** | Pablo Q5: one-off organizers start from scratch, no template reuse. Recurring organizers have personal muscle memory but no shared template. Higher importance for one-off organizers, who are also the lowest-skill users. |
| **O4** | Members can't recall what they ordered (Pattern A) | 7 | 2 | **12** | Pablo Q3: recall failure happens every order. Members rely on personal notes / scrolling Gmail. Lower importance than O1 because consequence is smaller (mild embarrassment vs. missing the order entirely). |
| **O5** | Members don't know when orders arrive (Pattern A) | 7 | 3 | **11** | Pablo Q3: arrival miss every order. Today's signal is a follow-up email from the organizer (when sent). Satisfaction nonzero because some organizers do email on arrival. |
| **O7** | Pattern B arrivals lack a discoverable broadcast surface | 6 | 3 | **9** | 3 standalone Pattern B emails + TP loose-rolls. Charges already handled by existing Lupanes App ("apuntar en la App", Email 8); only gap is the broadcast notification. Lower importance than Pattern A because financial workflow is already solved. **Deferred to vNext.** |
| **O6** | Payment coordination is manual | 6 | 4 | **8** | Only relevant for pre-paid orders (toilet paper, oil sometimes). Most orders settle post-delivery on member accounts. Lower frequency, partially served by existing common-account convention. |

**Top opportunities (score > 8)**: O1, O2, O3, O4, O5, O7 — six opportunities exceeding the G2 threshold. **v1 targets only the Pattern A subset (O1–O5)**; O7 is documented and deferred.

**v1 anchor opportunities** (the three the v1 cut must address): **O1, O2, O3**. These are the highest-scoring and the most concretely validated.

**v1 also addresses (lower cost, same surface)**: O4 and O5 — because once we have a "central board" and an "order" entity, "My orders view" and "order status" are nearly-free additions on the same screen.

---

## v1 Solution Concept

The five `*** v1 ***` items collapse into a single coherent product surface:

> **A unified group-order board** — one page in the existing Lupierra app where:
>
> 1. **Members see all currently-open group orders** (solves O1)
> 2. **Members see what they themselves have ordered in each** (solves O4)
> 3. **Members see arrival status of each order** (solves O5)
> 4. **Organizers create an order** — title, producer name, freeform product line items, closing date, expected delivery date (solves O3)
> 5. **The system aggregates submitted lines** into a per-member-per-product tally that the organizer can view / copy / send to the producer (solves O2)
> 6. **Order-open triggers an email to `socios@lupierra.es`** so the new system *replaces* rather than *competes with* the current Gmail blast (channel risk mitigation, see `lean-canvas.md`)

UVP draft (proposed for the canvas): *"Stop juggling Gmail threads and Google Forms — one place for the association to open, join, and track group orders."*

---

## Explicitly Out of v1 (Deferred to vNext or Out of Scope)

Pushed out to keep first delivery shippable. Each item below has been considered, has a real-world driver in the email evidence, and is **intentionally** not in v1.

| Deferred capability | Driver in evidence | Reason for deferral |
|---------------------|--------------------|---------------------|
| **Pattern B — arrival-announcement broadcast (O7)** | Emails 7, 8, 9 + TP loose-rolls: stock arrives, no per-member ordering, charged via existing App | Financial side already solved by existing Lupanes App + albarán; only gap is broadcast notification. Smaller and separable from Pattern A. Deferred to vNext. |
| External producer as a system user | All 9 emails: organizers relay to producer manually | Producers are not Lupierra members; account model would 3x the user-management scope |
| Pre-payment / common-account integration | Marta TP email: "se les carga directamente en su cuenta" / "haced un donativo equivalente" | Touches finance; would require an audit trail and reconciliation that v1 can't justify |
| Bridge to existing `DeliveryNote` albarán | Marta TP email: "los que cojáis así se apuntan en albarán" (loose rolls) | Existing model; integration scope unknown. v1 can mark an order as "arrived" without bookkeeping the albarán. |
| Multi-producer orders | Gloria bread email: Aineto + La Peña in one form | v1: organizer opens two separate orders, one per producer. Cleaner data model, only marginal UX cost. |
| Product variant catalog | Didier oil email: 2 oils × multiple sizes; Marta TP: whole/half-box/loose | v1: organizer types freeform line items (string + price). No variant modeling, no producer catalog. |
| Variable units (kg fractions, half-boxes) | Aineto bread: galletas "en fracciones de 250gr"; TP: half-box | v1: line items carry unit as freeform string; member enters integer quantity. Good enough for the 5 email cases. |
| Closing-window automation | All emails have a closing datetime | v1: closing date is a display field; member submissions blocked after it. No reminder emails (those are vNext). |

---

## Team Alignment Note

This OST has not yet been reviewed in a synchronous cross-functional session (PM + Design + Eng). Because the engineer (Pablo) and the proxy informant are the same person, and there is no separate Design or PM in this association project, team-alignment as a formal step is partially satisfied by Pablo's authorship and partially deferred to the DISCUSS wave, where `product-owner` will challenge the v1 cut against requirements. The Phase 3 mockup-review with Gloria/Marta/Didier (see `solution-testing.md`) is the substantive alignment check before any code lands.

---

## G2 Gate Evaluation

| Criterion | Target | Actual | Status |
|-----------|--------|--------|--------|
| Interviews / evidence | 10+ cumulative | 9 emails + 1 informant = 10 | PASS |
| Opportunities identified | 5+ distinct | 7 (O1–O7) | PASS |
| Top opportunities score | > 8 | O1=16, O2=15, O3=13, O4=12, O5=11, O7=9 (six above) | PASS |
| Job step coverage | 80%+ | Organizer job: 8/8 steps mapped. Consumer job: 8/8 steps mapped. | PASS |
| Strategic alignment | Stakeholder confirmed | Pablo confirmed v1 direction (Q4); deferred items consciously cut; Pattern A vs B scope explicit (D11) | PASS (with formal cross-functional check deferred to DISCUSS wave) |

**G2 Decision: PROCEED to Phase 3 (Solution Testing).**
