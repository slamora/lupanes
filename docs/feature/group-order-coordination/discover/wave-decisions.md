# Wave Decisions — DISCOVER → DISCUSS

**Feature**: group-order-coordination
**Wave**: DISCOVER
**Date**: 2026-05-31
**Author**: Scout (nw-product-discoverer), proxy informant Pablo Laulhé

---

## Purpose

Decisions, constraints, validated assumptions, and invalidated assumptions from the DISCOVER wave. These are the contracts the DISCUSS wave (`product-owner`) must respect. Any reversal of a decision below requires explicit re-opening of the discovery artifact that anchors it.

---

## Decisions

### D1 — v1 scope is "unified active-orders board + auto-tally"

**Decision**: v1 ships exactly five capabilities, on a single page:
1. List all currently-open group orders.
2. Each member can submit quantities against any open order.
3. Each member can see their own line items per active order ("My orders").
4. Each order has a visible status (open → closed → ordered → arrived).
5. The organizer sees a per-member-per-product tally they can copy to send to the producer.

Plus one infrastructure requirement: order-open triggers an email to `socios@lupierra.es`.

**Anchor**: `opportunity-tree.md` v1 Solution Concept; Pablo Q4.
**Reversible**: only by re-opening Phase 2 with new evidence that this scope is wrong.

### D2 — Deferral list is non-negotiable in v1

**Decision**: the following are explicitly **out of v1**, even though each has a real-world driver in the 5 email evidence corpus:
- External producers as system users
- Pre-payment / common-account integration
- Bridge to existing `DeliveryNote` albarán
- Multi-producer orders (organizer opens two separate orders instead)
- Product variant catalogs (freeform line items only)
- Variable / fractional units (carried as freeform unit string)
- Closing-window reminder emails
- Co-organizer / working-group ownership ("GT Productores")
- Duplicate-previous-order templates

**Anchor**: `opportunity-tree.md` "Explicitly Out of v1" table; `lean-canvas.md` R3 (scope creep risk).
**Reversible**: each item individually, by product-owner in DISCUSS, but each reversal must justify the cost against R3. The default is to stay deferred.

### D3 — Order-open email notification is a hard v1 requirement

**Decision**: when an organizer publishes a new order, the system must send an email to `socios@lupierra.es` containing at minimum: order title, producer, line items, closing date, link to the order page.

**Anchor**: `lean-canvas.md` R2 (notification channel risk).
**Rationale**: without this, the new tool competes with the existing Gmail channel rather than replacing it. The result is worse than the status quo.
**Reversible**: NO. This is a non-negotiable for v1.

### D4 — Product-line items are freeform strings, not modelled entities

**Decision**: in v1, an order's "products" are a list of freeform strings (name + optional price + optional unit + optional notes). No product catalog, no producer-product join table, no variant modelling.

**Anchor**: `opportunity-tree.md` deferral table; 5/5 email evidence shows organizers write product lists from scratch each time, not picking from a catalog.
**Reversible**: vNext when a recurring producer-product pattern is observed in production usage.

### D5 — Phase 3 testing is deferred to a pre-DELIVER mockup review

**Decision**: no clickable prototype is built in the DISCOVER wave. Instead, a clickable mockup review with 2–3 recurring organizers (Gloria, Marta, Didier) is a **hard gate** before DELIVER begins coding. At least 2 of 3 must commit to running their next real order on the tool.

**Anchor**: `solution-testing.md` "Pre-DELIVER Validation Plan".
**Rationale**: project scale (20-member association) does not justify a full Phase 3 cycle. The mockup review is a calibrated substitute that addresses the highest-risk hypotheses (H3, H6) at low cost.
**Reversible**: by the DISCUSS wave if product-owner deems the gate inadequate; in that case, full Phase 3 with prototype + 5 testers must be added before DELIVER.

### D6 — Personas are Member-Organizer (recurring + one-off) and Member-Consumer

**Decision**: segment users by JTBD, not demographics. The two personas are:
- **Member-Organizer** — JTBD: coordinate a group purchase from an external producer. Covers both recurring (Gloria/Marta/Didier archetype) and one-off (random member) variants.
- **Member-Consumer** — JTBD: participate in group orders without missing the window or losing track. Every member, including organizers when they're not organizing.

**Anchor**: `problem-validation.md` Jobs-to-be-Done section; `lean-canvas.md` Customer Segments.
**Reversible**: only if new user types emerge (e.g., external producers, which today are explicitly out of scope).

### D7 — Single-producer-per-order rule

**Decision**: each order has exactly one producer. The Gloria bread case (Aineto + La Peña in one email) is handled in v1 by the organizer opening **two separate orders**.

**Anchor**: `opportunity-tree.md` deferral table.
**Rationale**: simpler data model, cleaner tally, no UI complexity. Cost: organizer has to repeat closing date / delivery date. Acceptable.
**Reversible**: vNext if two-orders-per-batch friction becomes a pain in production.

### D8 — Customer language is preserved in the UI

**Decision**: UI copy uses the actual association vocabulary captured in the email evidence — "Se abre pedido", "nombre de vuestra nevera", "cerrar pedido", "cajas / medias cajas / rollos sueltos", "se apuntan en albarán" (when albarán bridge ships). No translation to generic e-commerce terms.

**Anchor**: `problem-validation.md` Customer Language Inventory.
**Reversible**: only if usability testing shows the vocabulary confuses one-off members. Unlikely.

### D9 — Pre-DELIVER Mockup Review is a Hard Gate

**Decision**: The pre-DELIVER mockup review with Gloria Puertas, Marta García Luengo, and Didier Vergés is a **non-negotiable blocking gate** for the DISCUSS → DELIVER transition. No production code is written until:

1. A clickable mockup (or paper prototype) of the v1 group-order board is complete.
2. At least **2 of 3** named organizers have walked through it and answered the commitment question: *"Can we run your next order on this tool together?"*
3. Both answers are **YES**, OR one is **NO with specific actionable feedback** (in which case the mockup is revised and re-tested before DELIVER).

If fewer than 2/3 commit, **DELIVER is paused**. Pivot contingencies (see D12) are evaluated.

**Why**: the switching-cost risk (R1, H6) is unmitigated and based on speculation. Pablo's Q1 response ("they might be used to that and not consider another option") is future-intent speculation, not evidence. This gate converts the risk from a post-launch hypothesis into a pre-build commitment test.

**How to apply**: the DISCUSS-wave `product-owner` MUST schedule and execute this review **within ~1 week of DISCUSS kickoff**. The `product-owner` BLOCKS DELIVER from starting until the gate closes. The mockup-review script in `solution-testing.md` "Pre-DELIVER Validation Plan" remains the source of truth for question wording (Mom-Test compliant: past behaviour, not future intent).

**Anchor**: `solution-testing.md` H3, H6, "Pre-DELIVER Validation Plan"; `lean-canvas.md` R1.
**Reversible**: NO. This is a non-negotiable hard gate.

### D10 — Phase 2 Sample Size: Resolved via Additional Evidence

**Decision**: Phase 2 OST is now grounded in **9 distinct primary-source email events** across **7 distinct organizer humans** (Gloria, Sheila/Fran, FrutaLupierra, Didier, Marta, Santiago, Gorka), plus **1 proxy informant** (Pablo). Combined n=10 — meets the skill's 10-source minimum for Phase 2 standard-confidence opportunity scoring.

**Why**: Round 2 evidence expansion (after peer review B1) surfaced 4 additional emails Pablo already had on hand:
- Email 6 — Ternera del Pirineo (Santiago Lamora) — Pattern A
- Email 7 — Harinas y Spaghetti (Gorka, Grupo de Autoproducción) — Pattern B
- Email 8 — Bebida de avena (Marta, GT Productores) — Pattern B with multi-alias addressing
- Email 9 — Jabón de lavadora (Gorka, Grupo de Autoproducción) — Pattern B

These revealed the **two-pattern domain insight** (see D11) and two distinct working groups (GT Productores, Grupo de Autoproducción).

**How to apply**: opportunity scores in `opportunity-tree.md` are now standard-confidence (not YELLOW or provisional). Downstream waves can rely on them as input to story-mapping and prioritisation. Reviewer blocker B1 is **CLOSED**.

**Anchor**: `interview-log.md` "Pattern Recognition" section + appendix Emails 6–9; `problem-validation.md` Calibration Note and Evidence Quality section.
**Reversible**: only if downstream evidence contradicts the pattern (e.g., a 10th organizer reveals a third workflow).

### D11 — Pattern A vs Pattern B Scoping (v1 targets Pattern A only)

**Decision**: Discovery surfaced two workflow patterns. **v1 targets Pattern A exclusively. Pattern B is acknowledged and deferred to vNext.**

- **Pattern A — Group Buy** (in scope): time-boxed group buys with closing/delivery dates and per-member quantity collection. 6/9 emails (bread, avocados, fruit, oil, TP, ternera).
- **Pattern B — Arrival Announcement** (out of v1 scope): stock-arrival announcements where consumers take items at the local via the existing albarán/Lupanes App, with no per-member ordering. 3/9 standalone emails (harinas, avena, jabón) + the TP loose-rolls portion.

**Why**: Pattern B's primary gap is a broadcast notification — which the existing `socios@lupierra.es` mailing list **largely already solves**. The financial/pickup side is **explicitly handled by the existing Lupanes App** (Email 8 verbatim: *"para apuntar en la App"*). Pattern A has multiple compounding gaps (discovery + collection + tally + arrival) that justify a dedicated tool. Building both at once would dilute v1 and slow the highest-value delivery.

**How to apply**: 
- `opportunity-tree.md` lists Pattern B as O7 (score 9, vNext).
- `lean-canvas.md` Customer Segments splits early adopters into "Group-buy organizers" (in scope) and "Autoproducción organizers" (acknowledged, vNext).
- DISCUSS-wave user stories MUST scope to Pattern A. Pattern B remains a documented future opportunity.
- A vNext epic ("Pattern B arrival broadcast") should be queued in the product-owner backlog.

**Anchor**: `problem-validation.md` "Two Workflow Patterns" section; `interview-log.md` "Pattern Recognition" section.
**Reversible**: only if Pattern A delivery is so successful that the team has capacity for Pattern B before any other vNext item — and only after a Pattern-B-specific opportunity validation (would benefit from interviewing Gorka directly).

### D12 — Pivot Contingency if H6 Fails

**Decision**: If the pre-DELIVER mockup review (D9) reveals that organizers overwhelmingly prefer Google Forms (H6 FALSE), the team will choose between two pre-prepared pivot paths:

**Path (a) — Google Forms integration layer**:
- Lupanes app exposes a "browse open orders" page that mirrors Google Form metadata (title, closing date, delivery date) created/edited by organizers in a lightweight admin UI.
- Form responses still flow to Google.
- Consumer-side discovery + arrival notifications are solved. Collection stays on Google Forms.
- **Pros**: minimal switching cost (organizers keep their existing tool). Solves O1, O4, O5.
- **Cons**: does not solve O2 (manual tally) or O3 (rebuild from scratch).

**Path (b) — Auto-tally tool only**:
- Organizers paste a Google Form CSV export into a Lupanes admin tool.
- The system produces (i) a per-product, per-member tally email ready to forward to the producer and (ii) per-member "what you ordered" pages.
- **Pros**: solves O2 (the single biggest 5-minute pain) and O4 (recall) without forcing any organizer behaviour change.
- **Cons**: does not solve O1 (discovery) — Gmail blast remains the only channel.

**Why**: pre-prepared contingency avoids ad-hoc reactions if H6 fails. Forces honest reckoning with the most likely failure mode (switching cost). Either path preserves at least some of the v1 value while respecting organizer muscle memory.

**How to apply**: the DISCUSS-wave `product-owner` picks (a) vs (b) **BEFORE running the mockup review**, so the failure path is concrete and the review can probe which pivot organizers would accept. The chosen path is recorded as an amendment to D1 (v1 scope).

**Anchor**: `solution-testing.md` H6; `lean-canvas.md` R1.
**Reversible**: this is itself a contingency plan; it activates only if D9's hard gate fails.

### D13 — Two payment mechanisms; v1 does NOT own charging

**Context discovered**: socios pay for group-order items via one of two mechanisms. Both already map cleanly onto the **existing** `DeliveryNote` (albarán) model — the model's `customer` (who is charged) vs `created_by` (who registered the note) distinction is exactly what separates them:

- **Mechanism A — Organizer-driven charging**: the organizer (or a manager) records how much each nevera owes and creates the charge on their behalf. App mapping: `DeliveryNote` with `customer` = nevera, `created_by` = organizer. Evidence: TP email — *"a los que piden por cajas/medias cajas se les carga directamente en su cuenta."*
- **Mechanism B — Self-service charging**: each member registers in the albaranes app what they take, on the honour system that they pick only what they ordered. App mapping: `DeliveryNote` with `customer` = `created_by` = self. Evidence: TP email — *"los que cojáis así se apuntan en albarán"*; avena email — *"para apuntar en la App."*

A third, out-of-band mechanism exists — **pre-payment** by bank transfer / donation to the Lupierra common account (TP email: *"hacer un donativo… se paga por adelantado"*). It happens entirely outside the app and is not a charging mode the tool can own. **Out of scope** (already covered by D2 "Pre-payment / common-account integration").

**Decision (RATIFIED by Pablo, 2026-06-01)**: v1 implements **Mechanism B only**, gated behind a per-order flag the creator sets. The tool itself **never owns charging and never writes a `DeliveryNote`** — it only reminds.

- The group-order creator configures each order with a boolean — **"paid by the socio in albaranes"** (e.g. *"El pago lo registra cada socio en albaranes"*).
- **Flag ON**: when a socio who has ordered views the order, they see a **reminder** that they must register their own albarán in the app (self-service, Mechanism B). Read-only nudge — the tool does not create the `DeliveryNote` for them.
- **Flag OFF** (default): the socio sees **no payment warning**. The creator charges each nevera **manually, outside the tool, exactly as today** (the manual form of Mechanism A). v1 provides no assistance for this path.

**This amends D1 (v1 scope)**: add (6) a per-order "paid in albaranes" flag set by the creator, and (7) a conditional self-service albarán reminder on the consumer's order view when that flag is ON.

v1 builds **no organizer charging UI and no auto-charge**. Organizer-side charging (Mechanism A, whether manual-assisted or automatic) is **entirely vNext**.

**Tension with D4 (only relevant once Mechanism A is built, vNext)**: auto-charging would require the ordered item to be a catalog `Product` with a dated `ProductPrice` — because `DeliveryNote.product` is a FK and `amount()` reads `product.get_price_on(date)` (`lupanes/models.py:21-22`). D4 makes v1 order line-items freeform strings, so the two are incompatible. v1 sidesteps this entirely by never writing charges. The tension becomes the first design question of the vNext Mechanism-A epic.

**Why**: keeps v1 shippable by a single volunteer engineer (C1) and reuses the working albarán flow (C2) instead of building a charging engine. The per-order flag respects that orders are paid differently (TP boxes charged by the organizer vs loose rolls self-service) without the tool modelling charging at all. The tally (D1.5) still serves the organizer's producer-reconciliation need (Santiago's MUST #1) regardless of the flag.

**How to apply**:
- DISCUSS user stories: (a) creator sets the "paid in albaranes" flag at order creation/edit; (b) consumer order view conditionally renders the self-service albarán reminder when the flag is ON.
- The "Bridge to existing `DeliveryNote` albarán" item in D2's deferral list is **partially re-opened**: a *read-only reminder* enters v1; any *write integration* (auto-create albarán, auto-charge) stays deferred.
- A vNext epic "Organizer charging assist / auto-charge (Mechanism A)" is queued, with the D4-vs-catalog tension as its first design question.
- **Open Question 6 is RESOLVED by this decision.**

**Anchor**: existing `lupanes/models.py` `DeliveryNote`; TP + avena email evidence (`interview-log.md` appendix Emails 5, 8); Santiago Lamora comment + Pablo ratification on the Notion issue (2026-06-01).
**Reversible**: low likelihood — this is a deliberate, product-owner-ratified scope cut.

---

## Constraints (carried into DISCUSS / DELIVER)

### C1 — Single engineer, volunteer time

Pablo is the only engineer. Designs that require ongoing manual intervention (e.g., approving each order, manually emailing notifications, manually closing windows) will dominate maintenance cost and must be avoided.

### C2 — Existing Django app, existing data model

The v1 ships into the existing Lupierra repo. New tables must coexist cleanly with the existing `DeliveryNote`, product, and nevera models. v1 does not have to integrate with them, but it must not block future integration.

### C3 — Closed user base, no acquisition channel

Users are association members only. There is no signup flow, no public landing page, no SEO, no paid acquisition. Auth piggybacks on whatever the existing app already does.

### C4 — Non-commercial, no revenue stream

There is no monetization. Decisions that trade developer time for "growth" or "conversion" have no payoff. Decisions that trade developer time for **reduced organizer chore time** do have payoff.

### C5 — Email must remain the discovery channel

See D3. Members today rely on `socios@lupierra.es`. v1 publishes into that channel, does not replace it with a notification system that requires checking the app.

---

## Validated Assumptions

| # | Assumption | Evidence |
|---|-----------|----------|
| VA1 | Group orders are a recurring, multi-organizer workflow in Lupierra | 5 distinct organizers × 5 product categories over 10 weeks (`interview-log.md` appendix) |
| VA2 | Every group order today uses Gmail + Google Form + manual tally | 5/5 emails follow this pattern (4 with explicit Form link; 1 inline freeform) |
| VA3 | Tallying Google Form CSV responses is the single biggest organizer pain | Pablo Q2 (named explicitly as the top 5-minute chore) |
| VA4 | Three member-side failure modes — discovery, recall, arrival — happen in every order | Pablo Q3 |
| VA5 | Occasional one-off organizers rebuild the Google Form from scratch | Pablo Q5 |
| VA6 | Real orders include multi-producer, multi-variant, pre-payment, albarán bridge, variable units | 5/5 emails surface at least one of these complexities; Marta TP email surfaces 4 of them |
| VA7 | The existing `socios@lupierra.es` channel works for order announcements today | 5/5 emails delivered through this channel; Pablo confirms it's the current discovery channel |
| VA8 | The Lupierra-specific vocabulary ("nevera", "albarán", "cajas / medias cajas / rollos sueltos") is shared and understood by members | Used across 5/5 emails by 5 different organizers without explanation |

## Invalidated Assumptions

| # | Original assumption | Status | Evidence that invalidated |
|---|---------------------|--------|----------------------------|
| IA1 | "Organizers are a fixed pool of 5–6 people; we can optimize for power users" | **INVALIDATED** | Pablo Q5: occasional one-off organizers exist and rebuild from scratch. Tool must work for low-skill / first-time organizers. |
| IA2 | "Discovery failures happen rarely; recall is the main member-side pain" *(initial hunch from Pablo's narrative)* | **INVALIDATED** | Pablo Q3: all three failure modes happen in every order. Discovery is NOT secondary to recall. |
| IA3 | "We can ignore the existing Gmail channel — members will check the new app" *(potential design shortcut)* | **INVALIDATED** | Captured as R2 (notification channel risk) and locked down by D3 (email-on-open is mandatory). |
| IA4 | "v1 should model producers as system users so they can pull their own tallies" *(potential scope expansion)* | **INVALIDATED** | All 5 emails show the organizer relaying manually. Producers are not Lupierra members and have no reason to log in. |

## Unmitigated / Acknowledged Risks (carried into DISCUSS)

| # | Risk | Status |
|---|------|--------|
| UR1 | Switching cost (Q1 unanswered) — will recurring organizers actually adopt? | **MITIGATION SCHEDULED**. Pre-DELIVER mockup review is now a **HARD GATE** per D9. Pivot contingency per D12. |
| UR2 | Single-informant bias — all qualitative routing through Pablo | **MITIGATED to acceptable level** by 9 primary-source emails across 7 organizers (D10); remainder addressed by mockup review (D9). |
| UR3 | Unmeasured population numbers (~20 members, ~90% participation, organizer pool size) | **MITIGATION SCHEDULED**. Validation task V1 (below) — 30-minute roster count before any cost/scaling decision in DELIVER. |

---

## Pre-DELIVER Validation Tasks

### V1 — Validate Population Estimates (R1 reviewer recommendation)

**Task**: Before any cost / scaling / notification-volume decision in DISCUSS or DELIVER, validate the population numbers used in `lean-canvas.md` Key Metrics and `problem-validation.md` Calibration Note.

**How**:
1. Pull the Lupierra member roster from the existing app.
2. Count unique members who submitted quantities in the last 3 group orders (e.g., Marta TP, Didier oil, FrutaLupierra fruit).
3. Compute actual unique-organizer count over the last 6 months (anchored in the email evidence).

**Replace**: the "~20 members", "~90% participation", "5–6 recurring organizers" estimates with measured values.

**Effort**: ~30 minutes. Owner: DISCUSS-wave product-owner (with Pablo's read access to the Lupierra app).

**Why**: any DELIVER-wave decision that scales notification volume, batching, or pagination depends on knowing the actual size. Estimates are not measurements.

**Anchor**: `problem-validation.md` Calibration Note ("Quantitative claims that are estimates, not measured").

---

## Open Questions for DISCUSS Wave

1. Does the email-on-order-open notification go through the existing `socios@lupierra.es` list (so members get it via their existing mail rules) or through a new transactional sender? **Recommendation**: existing list.
2. Where does the "tally view" for the organizer live — same page as the order, or a separate organizer-only view? **Recommendation**: same page, with the tally section visible only to the organizer of that order.
3. What is the auth posture? Does the existing Lupierra app already authenticate all members, or does v1 need a sign-in flow? **Recommendation**: piggyback on existing auth; if none, defer auth scope to DISCUSS.
4. Should the "My orders" view include closed-and-arrived historical orders, or only currently-active ones? **Recommendation**: v1 shows currently-active + most recent arrived; full history is vNext.
5. Who runs the pre-DELIVER mockup review session — Pablo, or a separate facilitator? **Recommendation**: Pablo runs it; documented script in `solution-testing.md` keeps it Mom-Test-compliant.
6. ~~**Charging posture for v1**~~ — **RESOLVED 2026-06-01 (see D13)**: v1 = Mechanism B only, behind a per-order "paid in albaranes" creator flag that conditionally shows a self-service reminder to socios who ordered. Flag OFF = no warning, creator charges manually off-app as today. No charging UI / no auto-charge / no `DeliveryNote` writes in v1. Mechanism A is vNext.

---

## Handoff Package to `product-owner`

Artifacts in `docs/feature/group-order-coordination/discover/`:

- `problem-validation.md` — Phase 1 validated problem + calibration note + two-pattern insight
- `opportunity-tree.md` — Phase 2 OST + v1 cut + deferral list + Pattern B (O7) as vNext
- `solution-testing.md` — Phase 3 hypotheses + pre-DELIVER mockup review plan (testing deferred, D9 hard gate)
- `lean-canvas.md` — Phase 4 viability + risk register + segment split (Pattern A vs Pattern B)
- `interview-log.md` — Single-informant session notes + 9 verbatim primary-source emails + Pattern Recognition section
- `wave-decisions.md` — This file: **13 decisions**, 5 constraints, 8 validated + 4 invalidated assumptions, 3 carried-forward risks (now with active mitigations), 1 pre-DELIVER validation task (V1), 6 open questions

**Decision: GO to DISCUSS**, with:
- D9 pre-DELIVER mockup review locked as a **non-negotiable hard gate** before DELIVER begins
- D11 Pattern A scope explicitly locked; Pattern B documented as O7 vNext
- D12 pivot contingency pre-committed for H6 failure path
- V1 population-roster validation scheduled before any DELIVER cost/scaling decision

All 3 reviewer blockers addressed: **B1 (sample size)** by D10; **B2 (mockup review as hard gate)** by D9; **B3 (G3 deferral + pivot contingency)** by D9 + D12.
