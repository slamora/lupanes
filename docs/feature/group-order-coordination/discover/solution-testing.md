# Solution Testing — Group Order Coordination

**Feature**: group-order-coordination
**Phase**: 3 — Solution Testing
**Status**: **DEFERRED** — no prototype built in DISCOVER wave
**Date**: 2026-05-31

---

## Scope

This document scopes solution testing to **Pattern A — Group Buy** only. Pattern B (arrival announcements) is out of v1 and is documented as opportunity O7 in `opportunity-tree.md`. See `wave-decisions.md` D11.

## Status: Phase 3 Testing Deferred — but Pre-DELIVER Mockup Review is a HARD GATE

No clickable prototype has been built and no usability tests have been run during the DISCOVER wave. Phase 3 success metrics (>80% task completion, value perception, comprehension) **cannot be evaluated today**.

This is a conscious choice for this project's scale: Lupierra is a 20-member association, the engineer is also a member, and the cost of a prototype-and-test cycle would be comparable to the cost of building the v1 itself. The substitute is a **clickable-mockup review with 2–3 recurring organizers** which has been **escalated to a non-negotiable hard gate** in `wave-decisions.md` D9 — see "Pre-DELIVER Validation Plan" below.

If the H6 mockup-review gate **FAILS** (< 2/3 organizers commit), the DISCUSS-wave product-owner activates pivot path (a) or (b) per `wave-decisions.md` **D12** — pre-committed before the review, so the failure path is concrete.

This document records the **hypotheses to test** so the DISCUSS and DELIVER waves have explicit, falsifiable success criteria carried forward.

---

## Hypotheses to Test in DELIVER (or pre-DELIVER mockup review)

Each hypothesis follows the Mom Test hypothesis template:
> We believe [doing X] for [user type] will achieve [outcome]. We will know this is TRUE when we see [signal]. FALSE when we see [counter-signal].

### H1 — Central order board solves discovery (covers O1)

> We believe **a single page listing all currently-open group orders** for **Lupierra members** will achieve **zero missed orders due to discovery failure**.
>
> TRUE when: after 3 real orders run on the new system, **0 members report "I didn't know the order was open"** when polled.
>
> FALSE when: members continue to rely exclusively on the Gmail blast and >1 member per order reports missing the window.

Risk score: Impact 3 (solution fails) × 3 = 9 + Uncertainty 2 (mixed signals, Pablo says we don't know switching cost) × 2 = 4 + Ease 1 (board is easy to instrument) × 1 = 1 → **Total: 14 (Test first)**.

### H2 — Auto-tally eliminates the manual CSV pain (covers O2)

> We believe **a system-generated per-member-per-product tally** for **the organizer** will achieve **the organizer no longer needing to manually aggregate Google Form responses**.
>
> TRUE when: organizer of a real order completes the tally → producer relay in **under 5 minutes** (vs. current "tallying form responses" which Pablo named as the single biggest 5-minute pain).
>
> FALSE when: organizer still copy-pastes the tally into a spreadsheet or rewrites it before sending to the producer.

Risk score: Impact 3 × 3 = 9 + Uncertainty 1 (high confidence, the pain is concrete) × 2 = 2 + Ease 1 × 1 = 1 → **Total: 12 (Test first)**.

### H3 — Order-creation form replaces Google Form (covers O3)

> We believe **a guided order-creation form with freeform product line items and a closing date** for **occasional organizers (one-off, low-skill)** will achieve **a complete order published in under 5 minutes without consulting documentation**.
>
> TRUE when: in mockup review, Gloria / Marta / Didier or a one-off proxy creates an order matching one of the 5 email examples without help and without going back to Google Forms.
>
> FALSE when: organizer says "I'd still rather use the Form because [reason]" or fails to publish the order.

Risk score: Impact 3 × 3 = 9 + Uncertainty 3 (Q1 switching cost unanswered) × 2 = 6 + Ease 2 (need mockup + interview) × 1 = 2 → **Total: 17 (Test first — highest priority)**.

### H4 — "My orders" view solves recall (covers O4)

> We believe **a per-member view of their own line items across active orders** for **member-consumers** will achieve **members being able to answer "what did I order?" without scrolling Gmail**.
>
> TRUE when: in mockup review, members can locate their own pending lines for an arbitrary order in **under 10 seconds**.
>
> FALSE when: members say "I'd still note it down separately" or fail to find their own lines.

Risk score: Impact 2 (significant rework, not solution-killing) × 3 = 6 + Uncertainty 2 × 2 = 4 + Ease 1 × 1 = 1 → **Total: 11 (Test soon)**.

### H5 — Order status surface solves arrival (covers O5)

> We believe **a visible status field on each order (open → closed → ordered → arrived)** for **member-consumers** will achieve **members knowing when goods are available for pickup without depending on a follow-up email**.
>
> TRUE when: after 3 real orders, **>80% of members check the status page** (instrumentation: page-view per order) and arrival-related questions on the mailing list drop to ~0.
>
> FALSE when: members keep asking "did it arrive?" on the list, or never visit the status page.

Risk score: Impact 2 × 3 = 6 + Uncertainty 2 × 2 = 4 + Ease 1 × 1 = 1 → **Total: 11 (Test soon)**.

### H6 — Switching cost is low enough that organizers adopt (covers Q1 risk)

> We believe **recurring organizers (Gloria, Marta, Didier, Sheila, FrutaLupierra)** will **prefer the new tool over their existing Gmail+Forms muscle memory** within **2 orders** of trying it.
>
> TRUE when: after each organizer has used the new tool once, **all of them choose it again** for their next order without prompting.
>
> FALSE when: any of them reverts to Google Forms after one use, or never tries it.

Risk score: Impact 3 (no users = no product) × 3 = 9 + Uncertainty 3 (Q1 unanswered) × 2 = 6 + Ease 2 × 1 = 2 → **Total: 17 (Test first — tied with H3)**.

H6 is the **single most important hypothesis** in this discovery and it is the one that most needs the mockup-review check below.

---

## Pre-DELIVER Validation Plan (HARD GATE — `wave-decisions.md` D9)

This is **not optional**. It is a non-negotiable blocking gate between DISCUSS and DELIVER. No production code is written until the gate closes.

Calibrated to the project's scale:

1. **Build a clickable mockup** (Figma or HTML, not React) of the v1 board, order-creation form, my-orders view, and organizer tally view. Cost: ~half a day. Owner: DISCUSS-wave product-owner.
2. **Walk through it with 2–3 recurring Pattern A organizers** within ~1 week of DISCUSS kickoff:
   - Gloria Puertas (bread)
   - Marta García Luengo (toilet paper — the most complex case: pre-paid + half-box + loose-rolls)
   - Didier Vergés (oil — multi-variant, simplest pre-paid)
3. **Questions to ask each** (Mom Test compliant — past behavior, not future intent):
   - "Walk me through the last bread/oil/TP order. What did you do step by step?" *(job mapping)*
   - "What was the hardest part of running that order?" *(pain — captures customer pain in their words; R2 reviewer recommendation)*
   - "Where in this mockup would you have gotten stuck or had a question?" *(usability surface)*
   - "If this had existed for your last order, would you have used it or stuck with Gmail+Forms? Why?" *(adoption signal — H6)*
   - "What's missing here that you needed last time?" *(scope sanity check)*
   - *(Commitment test — the gate question)* **"Can we run your next order on this tool together?"**
4. **Capture verbatim pain quotes** from each organizer. These become primary-source evidence supplementing the email corpus (currently 9 emails — adding 2-3 organizer pain quotes lifts evidence further).
5. **Gate**: at least **2 of 3** organizers commit to running their next real order on the tool. If fewer, **DELIVER is paused** and pivot path (a) or (b) from D12 activates.

### Pivot Contingency (`wave-decisions.md` D12)

If H6 FALSE (fewer than 2/3 commit), the DISCUSS-wave product-owner has pre-committed to one of two pivot paths:

- **(a) Google Forms integration layer** — Lupanes hosts a "browse open orders" board mirroring Google Form metadata; collection stays on Forms. Solves O1, O4, O5; does NOT solve O2, O3.
- **(b) Auto-tally tool** — organizers paste a CSV; system produces tally email + per-member view. Solves O2, O4; does NOT solve O1, O3.

The path is selected **before** the mockup review, so the review can probe organizers about which pivot they would accept. See `wave-decisions.md` D12 for full rationale.

This pre-DELIVER mockup review is the **only** thing standing between the DISCOVER wave and DELIVER. It is small, cheap, and high-leverage.

---

## G3 Gate Evaluation

| Criterion | Target | Actual | Status |
|-----------|--------|--------|--------|
| Users tested | 5+ per iteration | 0 (no prototype built) | **DEFERRED** |
| Task completion | >80% | n/a | **DEFERRED** |
| Value perception | >70% would use | n/a | **DEFERRED** |
| Key assumptions validated | >80% proven | Hypotheses documented, untested | **DEFERRED** |

**G3 Decision: DEFERRED — with HARD GATE enforcement before DELIVER.** Phase 3 testing is replaced by a documented pre-DELIVER mockup-review **hard gate** (above). This is a conscious project-scale decision recorded in `wave-decisions.md` (D5) and enforced as non-negotiable in `wave-decisions.md` (D9).

The DISCOVER → DISCUSS handoff proceeds **with the explicit caveat** that Phase 3 success metrics have not been measured. The DISCUSS-wave `product-owner` **MUST**:

1. Schedule and execute the mockup review within ~1 week of DISCUSS kickoff (D9).
2. **BLOCK DELIVER from starting** until the gate closes (≥2/3 organizers commit).
3. Pre-select pivot path (a) or (b) from D12 before the review, so the failure path is concrete.

This is not a recommendation. It is the contract carried into DISCUSS.
