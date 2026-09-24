# Definition of Ready — Group Order Coordination (v1, Pattern A)

**Feature**: group-order-coordination
**Wave**: DISCUSS
**Artifacts validated**: `user-stories.md`, `acceptance-criteria.md`, `journey.md`

> DoR is a hard gate. Each story must pass all 9 items with evidence before DESIGN/DELIVER.
> This is an internal tool for a ~20-member association built by a single volunteer engineer —
> stories are deliberately tiny; "right-sized" means hours-to-2-days each.

---

## DoR items

1. Problem statement clear, in domain language
2. User/persona with specific characteristics
3. 3+ domain examples with real data
4. UAT scenarios in Given/When/Then (3–7)
5. Acceptance criteria derived from UAT
6. Right-sized (≤ ~2 days, 3–7 scenarios)
7. Technical notes: constraints/dependencies
8. Dependencies resolved or tracked
9. Outcome KPIs defined with measurable targets

---

## Per-story validation

### US-01: Organizer opens a group order

| Item | Status | Evidence |
|------|--------|----------|
| 1 Problem clear | PASS | Gloria rebuilds the email + Google Form from scratch each week (O3) |
| 2 Persona | PASS | Member-Organizer (recurring + one-off), authenticated nevera |
| 3 Examples | PASS | Gloria bread / Didier oil / Marta empty-items |
| 4 UAT (3–7) | PASS | 3 scenarios in `acceptance-criteria.md` |
| 5 AC from UAT | PASS | 4 AC, each maps to a scenario |
| 6 Right-sized | PASS | New model + ModelForm + CreateView; 3 scenarios |
| 7 Technical notes | PASS | Freeform line items (D4), creator=request.user, URL named |
| 8 Dependencies | PASS | None; skeleton root |
| 9 Outcome KPIs | PASS | ≥3 of next ~5 orders opened in-app within 2 months; baseline 0 |

### US-02: Members see the board of open orders

| Item | Status | Evidence |
|------|--------|----------|
| 1 Problem clear | PASS | Discovery failure every order (O1); email lost in Gmail |
| 2 Persona | PASS | Member-Consumer, authenticated nevera |
| 3 Examples | PASS | Two open orders / closed hidden / empty state |
| 4 UAT (3–7) | PASS | 3 scenarios |
| 5 AC from UAT | PASS | 4 AC mapped |
| 6 Right-sized | PASS | ListView filtered to open + empty state |
| 7 Technical notes | PASS | ListView, is_customer gate, URL named |
| 8 Dependencies | PASS | US-01 (tracked) |
| 9 Outcome KPIs | PASS | Missed-order count → 0 within 3 orders; baseline ≥1/order |

### US-03: Member submits quantities

| Item | Status | Evidence |
|------|--------|----------|
| 1 Problem clear | PASS | Feeds the manual-tally pain (O2); no record tied to order |
| 2 Persona | PASS | Member-Consumer, authenticated nevera |
| 3 Examples | PASS | Submit / update-before-close / submit-after-close |
| 4 UAT (3–7) | PASS | 3 scenarios |
| 5 AC from UAT | PASS | 4 AC mapped |
| 6 Right-sized | PASS | One submission set per (member, order); create/update view |
| 7 Technical notes | PASS | Gated on status==open; "update replaces" semantics |
| 8 Dependencies | PASS | US-01, US-02 (tracked) |
| 9 Outcome KPIs | PASS | 100% in-app submissions per in-app order; baseline 0 |

### US-04: "Mis pedidos"

| Item | Status | Evidence |
|------|--------|----------|
| 1 Problem clear | PASS | Recall failure every order (O4) |
| 2 Persona | PASS | Member-Consumer who has submitted |
| 3 Examples | PASS | Multi-order recall / own-only / arrived-most-recent / empty |
| 4 UAT (3–7) | PASS | 4 scenarios |
| 5 AC from UAT | PASS | 4 AC mapped |
| 6 Right-sized | PASS | Listing of own submissions filtered to active orders |
| 7 Technical notes | PASS | Active = open + most-recent arrived (Open Q4 resolved) |
| 8 Dependencies | PASS | US-03, US-08 (tracked) |
| 9 Outcome KPIs | PASS | Recall failures → 0 within 3 orders; baseline ≥1/order |

### US-05: Albarán reminder (flag ON)

| Item | Status | Evidence |
|------|--------|----------|
| 1 Problem clear | PASS | Self-service members forget to self-register (D13, Mechanism B) |
| 2 Persona | PASS | Consumer who ordered in a flag-ON order |
| 3 Examples | PASS | Flag ON+ordered / flag OFF / flag ON not-ordered |
| 4 UAT (3–7) | PASS | 4 scenarios (incl. "never auto-charges") |
| 5 AC from UAT | PASS | 4 AC mapped |
| 6 Right-sized | PASS | Read-only conditional render + link; no writes |
| 7 Technical notes | PASS | Links to existing `deliverynote-new`; NO writes (C-NOCHARGE/D13) |
| 8 Dependencies | PASS | US-01, US-03, US-04 (tracked) |
| 9 Outcome KPIs | PASS | Qualitative follow-through (not instrumented in v1) — explicitly noted |

### US-06: Organizer tally

| Item | Status | Evidence |
|------|--------|----------|
| 1 Problem clear | PASS | Manual CSV tally = single biggest pain (O2, VA3) |
| 2 Persona | PASS | Member-Organizer (creator of that order) |
| 3 Examples | PASS | Multi-member tally / single participant / non-creator blocked |
| 4 UAT (3–7) | PASS | 3 scenarios |
| 5 AC from UAT | PASS | 4 AC mapped |
| 6 Right-sized | PASS | Aggregate submissions, creator-only render |
| 7 Technical notes | PASS | Same page as order, creator-only (Open Q2 resolved) |
| 8 Dependencies | PASS | US-01, US-03 (tracked) |
| 9 Outcome KPIs | PASS | Tally time <5 min; baseline = biggest 5-min pain |

### US-07: D3 socios email (HARD requirement)

| Item | Status | Evidence |
|------|--------|----------|
| 1 Problem clear | PASS | Without it the tool competes with Gmail (R2); D3 non-negotiable |
| 2 Persona | PASS | All members on the socios list |
| 3 Examples | PASS | Happy send / items-without-price / send-fails-order-survives |
| 4 UAT (3–7) | PASS | 3 scenarios |
| 5 AC from UAT | PASS | 3 AC mapped |
| 6 Right-sized | PASS | Reuse existing send_mail pattern; one email template |
| 7 Technical notes | PASS | Existing list (Open Q1 resolved); failure must not roll back order |
| 8 Dependencies | PASS | US-01 (tracked) |
| 9 Outcome KPIs | PASS | 100% of in-app orders trigger the email; baseline manual |

### US-08: Status lifecycle

| Item | Status | Evidence |
|------|--------|----------|
| 1 Problem clear | PASS | Arrival miss every order (O5); no controlled status surface |
| 2 Persona | PASS | Organizer advances; consumer reads |
| 3 Examples | PASS | Full lifecycle / early close / non-creator blocked / no-backward |
| 4 UAT (3–7) | PASS | 4 scenarios |
| 5 AC from UAT | PASS | 5 AC mapped |
| 6 Right-sized | PASS | Status field + forward-only guard + creator-only change view |
| 7 Technical notes | PASS | Auto-close on date OK; arrived = v1 arrival signal (no email, D2) |
| 8 Dependencies | PASS | US-01; consumed by US-02/03/04 (tracked) |
| 9 Outcome KPIs | PASS | Arrival misses → 0 within 3 orders; baseline ≥1/order |

---

## Completeness & quality checks

- **Error/sad paths present** (anti-happy-path-bias): every story has an error/boundary example and
  a corresponding Gherkin scenario (empty items, submit-after-close, non-creator blocked, mail-send
  failure, flag-OFF/no-reminder, no-backward-status).
- **Solution-neutral**: scenario titles describe outcomes, not implementation; technical choices
  (Django CBV, models) are confined to "Technical Notes", not the AC.
- **Real data**: real personas (Gloria, Marta, Didier, Pablo, Santiago) and real products/dates
  throughout; no `user123`.
- **Scope discipline**: all 8 stories trace to locked D1+D13 capabilities; out-of-scope list (D2)
  restated in `user-stories.md`. No story expands scope.
- **Vocabulary (D8)**: Spanish association terms used in copy-facing AC ("Se abre pedido", "nevera",
  "cerrar pedido", "se apuntan en albaranes", "Mis pedidos").

---

## DoR Status: PASSED — all 8 stories pass all 9 items

---

## Outstanding gates before PRODUCTION rollout (not blocking code now)

- **D9 — Pre-DELIVER mockup review (HARD GATE, human)**: a clickable mockup (or the running feature
  itself) must be walked through with Gloria Puertas, Marta García Luengo, and Didier Vergés; ≥2 of
  3 must commit to running their next real order on the tool (Mom-Test-compliant: past behaviour, not
  future intent). This gate is a **human step that CANNOT run in this autonomous session**. It
  remains **OUTSTANDING**. Per the task brief, it does **not** block writing code now — the running
  feature will serve as the mockup for the review. The review must close (≥2/3 commit) **before
  production rollout**. If <2/3 commit, evaluate the D12 pivot contingency (the DISCUSS-wave owner
  must pick path (a) Google Forms integration layer or (b) auto-tally-only **before** running the
  review).

- **V1 — Population roster validation (~30 min)**: replace the unmeasured "~20 members / ~90%
  participation / 5–6 organizers" estimates with measured values before any DELIVER decision that
  scales notification volume, batching, or pagination. Low risk for v1 (the socios email is a single
  list send, not per-member), but flagged so estimates are not treated as measurements.

## Resolved open questions (carried from wave-decisions.md)

- **Q1** → socios email uses the **existing** `socios@lupierra.es` list (US-07).
- **Q2** → the tally lives on the **same page** as the order, visible only to that order's creator (US-06).
- **Q3** → auth **piggybacks on the existing app**; gate on `is_customer` (System Constraints).
- **Q4** → "Mis pedidos" shows **active + most recent arrived**; full history is vNext (US-04).
- **Q6** → **RESOLVED by D13**: Mechanism B only, behind the per-order flag; no charging UI, no
  `DeliveryNote` writes (US-05).
