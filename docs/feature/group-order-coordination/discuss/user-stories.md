<!-- markdownlint-disable MD024 -->
# User Stories — Group Order Coordination (v1, Pattern A)

**Feature**: group-order-coordination
**Wave**: DISCUSS
**Scope**: LOCKED by wave-decisions.md D1–D13. Do NOT expand.
**Acceptance criteria (Given/When/Then)**: see `acceptance-criteria.md`.
**Definition of Ready**: see `definition-of-ready.md`.

> Pragmatism note: this is an internal tool for a ~20-member Spanish association built by a single
> volunteer engineer. Stories are deliberately tiny, no enterprise ceremony. All UI copy is Spanish
> using association vocabulary (D8).

---

## System Constraints (cross-cutting — apply to all stories)

- **C-AUTH**: All views require an authenticated customer (member of the `neveras` group,
  `user.is_customer`). Auth piggybacks on the existing app (C3). No new signup flow.
- **C-ORGANIZER**: "Organizer" is NOT a new role. Organizer-only actions (create order, view tally,
  change status, set the albarán flag, edit/close) are gated by *"is this user the creator of this
  order?"* + authenticated customer — NOT by the `tienda` manager group.
- **C-FREEFORM (D4)**: An order's products are freeform line items (name + optional price + optional
  unit + optional notes). No catalog, no FK to the existing `Product` model.
- **C-PRODUCER (D7)**: Exactly one producer per order (freeform producer name string).
- **C-NOCHARGE (D13)**: v1 never owns charging and never writes a `DeliveryNote`. The albarán flow
  is only ever *referenced* via a read-only reminder.
- **C-LANG (D8)**: Spanish copy, association vocabulary. No generic e-commerce terms.
- **C-CONVENTION**: Django class-based views, ModelForms in `lupanes/forms.py`, templates extend
  `lupanes/base.html` (Bootstrap 5), URL names `lupanes:groworder-*`. Tests via `manage.py test`.

---

## Story Map (backbone + slicing)

Backbone (chronological activities across both personas):

| Open an order | Discover & join | Track my participation | Tally & conclude |
|---------------|-----------------|------------------------|------------------|
| US-01 create order | US-02 board lists open orders | US-04 "Mis pedidos" view | US-06 organizer tally |
| US-07 D3 email on open | US-03 submit quantities | US-05 albarán reminder (flag ON) | US-08 status lifecycle |

### Walking Skeleton (thinnest end-to-end slice)

**US-01 → US-02 → US-03 → US-06**: an organizer opens an order, members see it on the board,
members submit quantities, and the organizer reads the auto-tally. This is the minimum that
proves the core value (replace Gmail+Forms+manual CSV). Everything else enhances it.

### Release slices by outcome

- **Release 1 (Walking Skeleton)** — US-01, US-02, US-03, US-06. Outcome: organizers run a group
  buy and get an automatic tally instead of a manual CSV (moves O2 + O3, the two top organizer pains).
- **Release 2 (No missed orders, no lost track)** — US-07 (D3 email), US-04 ("Mis pedidos"),
  US-08 (status incl. `arrived`). Outcome: no member misses discovery/arrival or forgets what they
  ordered (moves O1, O4, O5).
- **Release 3 (Self-service charging nudge)** — US-05 albarán reminder behind the flag. Outcome:
  members who owe self-service charges are reminded to register their own albarán (D13).

> **Priority Rationale**: ordering is by outcome impact + dependency, not effort. The skeleton
> ships the highest-scored validated pains first (O2 tally = 15, O3 create = 13). US-07 (D3) is a
> HARD requirement (non-negotiable) so it leads Release 2; without it the tool competes with Gmail
> rather than replacing it (R2). US-04/US-08 finish the consumer confidence arc. US-05 is last
> because it depends on the flag (US-01) and on submissions (US-03) and is the least-validated of
> the locked scope.

### Scope Assessment: PASS — 8 stories, 1 bounded context (new group-order module in the existing `lupanes` app), estimated ~6–9 days total

Oversized signals checked: 8 stories (≤10 ✓), 1 module (≤3 ✓), skeleton needs 1 real integration
point — the D3 email (≤5 ✓), est. <2 weeks ✓. Multiple user outcomes exist but they share one
surface and ship incrementally on it. **Right-sized. No split needed.**

---

## US-01: Organizer opens a group order

### Problem

Gloria Puertas wants to open a bread order for next week. Today she writes a 150–400 word email to
`socios@lupierra.es` from scratch and builds a Google Form by hand, one question per product. It is
the same chore every week and one-off organizers rebuild it from zero (O3). She finds it tedious to
recreate the infrastructure each time.

### Who

- Member-Organizer (Pattern A) | any authenticated nevera | motivated to coordinate a group buy
  with minimal setup. Includes one-off organizers who have never built a Form.

### Solution

A short guided form to open an order: title, producer name (freeform), one or more freeform product
line items (name + optional price + optional unit + optional notes), closing date, expected delivery
date, and a "El pago lo registra cada socio en albaranes" checkbox (default OFF). On save the order
exists with status `open` and the creator is recorded.

### Domain Examples

1. **Happy Path** — Gloria opens "Pan semana del 2 de junio", producer "Aineto", line items
   "Pan de espelta 1kg — 4,50€", "Galletas 250gr — 2€", closing 2026-06-01 20:00, delivery
   2026-06-03, flag OFF. Order saved, status `open`, Gloria recorded as creator.
2. **Edge Case** — Didier opens "Aceite primavera 2026", producer "ecoMatarranya", with 2 line
   items that have no price yet ("Aceite virgen extra 5L", "Aceite virgen extra 2L"). Prices are
   optional, so the order saves fine.
3. **Error/Boundary** — Marta tries to open "Papel higiénico" but leaves all line items blank.
   The form blocks her with a message that an order needs at least one product line item.

### Acceptance Criteria

- [ ] An organizer can create an order with title, freeform producer, ≥1 freeform line item,
      closing date, delivery date, and the albarán flag (default OFF).
- [ ] On save the order has status `open` and records the creating user as its organizer.
- [ ] An order cannot be created with zero line items.
- [ ] Prices/units/notes on line items are optional; only the line item name is required.

### Outcome KPIs

See `acceptance-criteria.md` is not where KPIs live; KPIs summarized here per story.

- **Who**: recurring + one-off organizers
- **Does what**: open a group order on the tool instead of building a Google Form
- **By how much**: ≥3 of the next ~5 monthly orders opened on the tool within 2 months of launch
- **Measured by**: count of orders created in the app vs. Gmail+Form orders (organizer self-report)
- **Baseline**: 0 (today 100% Gmail + Google Forms)

### Technical Notes

- New model in the `lupanes` app: group order + line items (freeform strings, no FK to `Product`, D4).
- Creator = `request.user`; gate creation on `is_customer` (C-AUTH).
- ModelForm in `lupanes/forms.py`; CBV `CreateView`; URL `lupanes:grouporder-new`.
- Depends on nothing. Walking-skeleton root.

---

## US-02: Members see the board of open orders

### Problem

Pablo gets the "Se abre pedido" email but it competes with all his other Gmail. Across the
association, at least one member misses the window in every order (O1). There is no single place
that answers "what group orders are open right now?".

### Who

- Member-Consumer | any authenticated nevera | wants to know at a glance which orders are open and
  when they close, without scrolling Gmail.

### Solution

A single board page listing all currently-open orders with title, producer, closing date, and
status. Each links to the order detail where the member can submit. Includes a helpful empty state
when no orders are open.

### Domain Examples

1. **Happy Path** — Two orders are open: Gloria's "Pan semana del 2 de junio" (closes 2026-06-01)
   and Didier's "Aceite primavera 2026" (closes 2026-06-05). Pablo opens the board and sees both
   with producer and closing date.
2. **Edge Case** — Marta's "Papel higiénico" order has passed its closing date and is `closed`.
   The board no longer lists it among open orders (board shows currently-open orders).
3. **Error/Boundary** — No orders are open. Pablo sees an inviting empty state ("No hay pedidos
   abiertos ahora mismo") rather than a blank page.

### Acceptance Criteria

- [ ] The board lists every order whose status is `open`, showing title, producer, closing date,
      status.
- [ ] Orders not `open` are not listed on the board.
- [ ] Each listed order links to its detail/submit page.
- [ ] When no orders are open, an inviting empty-state message is shown.

### Outcome KPIs

- **Who**: members (consumers)
- **Does what**: discover an open order via the board instead of missing the Gmail blast
- **By how much**: missed-order count drops to 0 within the first 3 orders run on the tool
- **Measured by**: post-order poll "did you know this was open?" (organizer self-report)
- **Baseline**: ≥1 member misses the window every order today

### Technical Notes

- CBV `ListView` filtered to `status=open`; URL `lupanes:grouporder-list`. Gate on `is_customer`.
- Depends on US-01 (orders must exist).

---

## US-03: Member submits quantities against an open order

### Problem

When a member wants in on an order, today they fill the organizer's Google Form. The organizer then
has to export and tally those responses by hand (O2). Members also have no record tying their
submission to the order itself.

### Who

- Member-Consumer | any authenticated nevera | wants to put in their quantities for the products
  they want before the window closes.

### Solution

On an open order's detail page, the member enters a quantity for the line items they want and
submits. Their submission is stored against the order under their identity (nevera). Submission is
allowed only while the order is `open`.

### Domain Examples

1. **Happy Path** — Pablo opens Gloria's bread order and submits "Pan de espelta 1kg: 2" and
   "Galletas 250gr: 1". His line items are saved against the order under his nevera name.
2. **Edge Case** — Pablo realizes he wanted 3 loaves, returns before closing, and updates his
   submission. His latest quantities replace the previous ones (no duplicate double-counting).
3. **Error/Boundary** — Pablo tries to submit after the closing date has passed (order is `closed`).
   The system blocks the submission with a clear message that the order is closed.

### Acceptance Criteria

- [ ] While an order is `open`, a member can submit a quantity for one or more of its line items.
- [ ] A member's submission is stored against the order under their identity.
- [ ] A member can update their own quantities while the order is still `open`; the latest values
      replace the previous ones (no double counting).
- [ ] Submitting (or updating) is blocked once the order is no longer `open`.

### Outcome KPIs

- **Who**: members (consumers)
- **Does what**: submit quantities in-app, feeding an automatic tally instead of a Google Form CSV
- **By how much**: 100% of participating members of an in-app order submit in-app (no parallel Form)
- **Measured by**: submissions per order vs. participant count (organizer self-report)
- **Baseline**: 0 in-app today

### Technical Notes

- Submission model linked to order + line item + member; gate on `is_customer` and `order.status == open`.
- "Update replaces" implies one submission set per (member, order). CBV create/update; URL
  `lupanes:grouporder-submit`.
- Depends on US-01 and US-02.

---

## US-04: Member sees "Mis pedidos" — their own line items per active order

### Problem

Weeks after submitting, when the goods arrive, Pablo can't remember what he ordered (O4 — recall
failure every order). He scrolls Gmail or relies on personal notes.

### Who

- Member-Consumer | any authenticated nevera who has submitted to one or more active orders | wants
  to answer "what did I order?" without digging through email.

### Solution

A "Mis pedidos" view listing, per active order, the member's own submitted line items and
quantities, plus the order status. Active = currently open + most recent arrived (Open Q4 → active
+ most recent arrived; full history is vNext).

### Domain Examples

1. **Happy Path** — Pablo opens "Mis pedidos" and sees: Gloria's bread order — "Pan de espelta 1kg:
   3, Galletas 250gr: 1" — status `closed`; Didier's oil order — "Aceite 5L: 1" — status `open`.
2. **Edge Case** — Pablo has submitted to no orders. "Mis pedidos" shows an empty state inviting him
   to check the board.
3. **Error/Boundary** — An order Pablo ordered in moved to `arrived` and is the most recent arrived;
   it still appears in "Mis pedidos" so he knows what to pick up. An older arrived order does not.

### Acceptance Criteria

- [ ] "Mis pedidos" shows, per active order the member submitted to, their own line items,
      quantities, and the order status.
- [ ] It shows only the member's own submissions (never other members').
- [ ] Active orders = currently open + the member's most recent arrived order.
- [ ] When the member has no submissions, an inviting empty state is shown.

### Outcome KPIs

- **Who**: members (consumers)
- **Does what**: recall their own order from "Mis pedidos" instead of scrolling Gmail
- **By how much**: recall-failure incidents drop to 0 within the first 3 orders run on the tool
- **Measured by**: post-order poll "did you know what you ordered?" (organizer self-report)
- **Baseline**: ≥1 recall failure every order today

### Technical Notes

- CBV listing the member's submissions filtered to active orders; URL `lupanes:grouporder-mine`.
- Depends on US-03 (submissions) and US-08 (status, for the active/arrived filter).

---

## US-05: Member who ordered sees an albarán reminder when the order's flag is ON

### Problem

For self-service orders (e.g., toilet-paper loose rolls), members are charged on the honour system
by registering their own albarán — "los que cojáis así se apuntan en albarán" (D13, Mechanism B).
Members forget to register it. v1 must NOT charge for them; it must only remind.

### Who

- Member-Consumer who submitted to an order whose "paid in albaranes" flag is ON | any authenticated
  nevera | needs a nudge to register their own albarán via the existing flow.

### Solution

When a member who has ordered in an order with the flag ON views that order (on "Mis pedidos" / the
order detail), a read-only reminder appears: they must register their own albarán in the app
(self-service). The reminder links to the EXISTING albarán flow. The tool never creates the
`DeliveryNote` itself. When the flag is OFF, no reminder appears.

### Domain Examples

1. **Happy Path** — Marta's order has the flag ON. Pablo, who ordered loose rolls, sees a reminder
   on "Mis pedidos": "Recuerda apuntar lo que cojas en tu albarán" with a link to register an albarán.
2. **Edge Case** — Gloria's bread order has the flag OFF (she charges each nevera manually off-app).
   Pablo, who ordered bread, sees NO reminder.
3. **Error/Boundary** — Marta's order has the flag ON but Pablo did not order anything in it. Pablo
   sees no reminder (the reminder is conditional on having ordered).

### Acceptance Criteria

- [ ] When an order's "paid in albaranes" flag is ON and the viewing member submitted to it, a
      read-only reminder to register their own albarán is shown, linking to the existing albarán flow.
- [ ] When the flag is OFF, no reminder is shown to anyone.
- [ ] When the flag is ON but the member did not order, no reminder is shown.
- [ ] The tool never creates or writes a `DeliveryNote`; the reminder is informational only.

### Outcome KPIs

- **Who**: members who ordered in a flag-ON (self-service) order
- **Does what**: register their own albarán after being reminded, instead of forgetting
- **By how much**: self-service members who see the reminder follow through (qualitative, organizer
  self-report; not instrumented in v1)
- **Measured by**: organizer self-report of albarán completeness for flag-ON orders
- **Baseline**: members forget to self-register today (honour system, no nudge)

### Technical Notes

- Pure read-only conditional render: `order.paid_in_albaranes AND member_has_submission`.
- Link targets existing `lupanes:deliverynote-new`. NO writes (C-NOCHARGE / D13).
- Depends on US-01 (flag), US-03 (submission), US-04 (view surface).

---

## US-06: Organizer reads the per-member-per-product tally

### Problem

Marta's single biggest 5-minute chore is exporting the Google Form CSV and tallying it by hand into
a per-member-per-product summary to send to the producer (O2 — the top-scored organizer pain). It
is error-prone and repeated every order.

### Who

- Member-Organizer (the creator of that order) | wants a ready-to-send summary of who ordered how
  much of each product, without touching a spreadsheet.

### Solution

On the order, the creator sees a tally: a per-member-per-product table aggregating all submissions,
with per-product totals. It is laid out so the organizer can copy it to send to the producer. Only
the creator of that order can see its tally.

### Domain Examples

1. **Happy Path** — Gloria opens her bread order's tally and sees: Pablo — Pan 3, Galletas 1; Marta
   — Pan 2; per-product totals Pan 5, Galletas 1. She copies it into an email to Aineto.
2. **Edge Case** — Didier's oil order has only one participant (himself). The tally shows a single
   row and matching totals — still valid.
3. **Error/Boundary** — Pablo (not the creator) opens Gloria's order; he does not see the tally
   section at all (creator-only, C-ORGANIZER).

### Acceptance Criteria

- [ ] The order's creator sees a per-member-per-product tally aggregating all submissions, with
      per-product totals.
- [ ] The tally is visible only to the creator of that order (not other members, not by manager group).
- [ ] The tally reflects the same submitted data shown to members in "Mis pedidos" (single source).
- [ ] The tally is presented so it can be copied to send to the producer.

### Outcome KPIs

- **Who**: organizers
- **Does what**: produce the producer tally by reading it instead of manually tallying a CSV
- **By how much**: tally time drops to <5 minutes (from manual CSV tallying today)
- **Measured by**: organizer self-report "how long did the tally take?"
- **Baseline**: manual CSV tally is the single biggest 5-minute pain today (VA3)

### Technical Notes

- Aggregation over submissions grouped by member × line item; creator-only via C-ORGANIZER gate.
- Same page as the order (Open Q2 → tally section visible only to that order's organizer).
- Depends on US-01 and US-03. Walking-skeleton leaf.

---

## US-07: Order-open sends an email to the socios list (HARD requirement, D3)

### Problem

Members rely on `socios@lupierra.es` for discovery. If opening an order does not email that list,
the tool competes with Gmail instead of replacing it — two parallel systems, worse than the status
quo (R2). D3 makes this non-negotiable.

### Who

- Member-Consumer (all members on the socios list) | needs the order announcement to arrive in
  their existing mail channel so they discover it without checking a new site.

### Solution

When an organizer opens an order, the system sends an email to `socios@lupierra.es` containing at
minimum: order title, producer, line items, closing date, and a link to the order page. The email
uses the existing list (Open Q1 → existing list), so members' existing mail rules still work.

### Domain Examples

1. **Happy Path** — Gloria opens her bread order. An email to `socios@lupierra.es` goes out with
   subject referencing the order, body listing producer "Aineto", line items, closing date
   2026-06-01 20:00, and a link to the order page.
2. **Edge Case** — Didier's oil order has line items without prices. The email still lists the
   items (prices omitted where absent).
3. **Error/Boundary** — The mail send fails (SMTP error). The order is still created and `open`; the
   failure is logged and the organizer is told the order is open but the notification may not have
   been sent. The order is never silently lost.

### Acceptance Criteria

- [ ] Opening an order sends an email to `socios@lupierra.es` with title, producer, line items,
      closing date, and a link to the order page.
- [ ] The email is sent via the existing socios list (not a separate per-member transactional send).
- [ ] If the email send fails, the order is still created as `open`, the failure is logged, and the
      organizer is informed the notification may not have gone out.

### Outcome KPIs

- **Who**: members (consumers)
- **Does what**: receive the order announcement in their existing mail channel (replacing the manual
  Gmail blast)
- **By how much**: 100% of orders opened on the tool trigger the socios email automatically
- **Measured by**: email-send log / mail-server delivery confirmation
- **Baseline**: today the organizer composes and sends this email by hand

### Technical Notes

- Reuse Django `send_mail`/templated email as in existing `customer.py`; recipient is the configured
  socios list address (config value, not hardcoded per-member). Email template under `emails/`.
- Triggered on order create (US-01). Send failure must not roll back order creation.
- Depends on US-01.

---

## US-08: Order status lifecycle (open → closed → ordered → arrived)

### Problem

Members don't know when an order has been closed, sent to the producer, or arrived (O5 — arrival
miss every order). The organizer has no controlled way to advance the order through its stages, and
submissions need to be cut off at the right point.

### Who

- Member-Organizer (creator) advances the status; Member-Consumer reads it on the board / "Mis
  pedidos" to know when to pick up.

### Solution

Each order has a status that moves forward through `open → closed → ordered → arrived`. The creator
advances it (manual control; auto-close when the closing date passes is acceptable too). Status is
visible to all members on the board and in "Mis pedidos". Submissions are allowed only while `open`.

### Domain Examples

1. **Happy Path** — Gloria's bread order: opens `open`; at the closing date it becomes `closed`;
   after she relays to Aineto she marks it `ordered`; when the bread arrives she marks it `arrived`.
   Pablo sees `arrived` on "Mis pedidos" and goes to pick up.
2. **Edge Case** — Didier closes his oil order early (before the closing date) because everyone has
   submitted; status goes `open → closed` and submissions are now blocked.
3. **Error/Boundary** — Pablo (not the creator) tries to change the status of Gloria's order; he is
   not permitted (creator-only, C-ORGANIZER). Status only moves forward, never backward.

### Acceptance Criteria

- [ ] An order has a status that progresses forward through open → closed → ordered → arrived.
- [ ] Only the order's creator can change its status (creator-only, not manager group).
- [ ] Status is visible to all members on the board and in "Mis pedidos".
- [ ] Member submissions are accepted only while status is `open`.
- [ ] Status cannot move backward.

### Outcome KPIs

- **Who**: members (consumers)
- **Does what**: learn an order has arrived from the visible status instead of waiting for an ad-hoc email
- **By how much**: arrival-miss incidents drop to 0 within the first 3 orders run on the tool
- **Measured by**: post-order poll "did you know when it arrived?" (organizer self-report)
- **Baseline**: ≥1 arrival miss every order today

### Technical Notes

- Status field with forward-only transition guard; creator-only status-change view (C-ORGANIZER).
- Auto-close when `closing_date` passes is acceptable; manual close also allowed (Edge Case 2).
- `arrived` is the v1 arrival signal (no arrival email in v1 — that is vNext per D2).
- Depends on US-01; consumed by US-02 (board filter), US-03 (submission gate), US-04 (active filter).

---

## Dependency summary

| Story | Depends on | Release |
|-------|-----------|---------|
| US-01 create order | — | R1 (skeleton) |
| US-02 board | US-01 | R1 (skeleton) |
| US-03 submit | US-01, US-02 | R1 (skeleton) |
| US-06 tally | US-01, US-03 | R1 (skeleton) |
| US-07 D3 email | US-01 | R2 |
| US-08 status lifecycle | US-01 | R2 |
| US-04 "Mis pedidos" | US-03, US-08 | R2 |
| US-05 albarán reminder | US-01, US-03, US-04 | R3 |

## Risks carried into DESIGN/DELIVER

- **R1 adoption (MEDIUM)**: recurring organizers may stick with Gmail+Forms. Mitigation: D9
  pre-DELIVER mockup review — a HARD GATE before production rollout (see DoR). Not blocking writing
  code now (the running feature serves as the mockup).
- **R2 notification channel (MEDIUM)**: addressed by US-07 (D3 hard requirement).
- **R3 scope creep (MEDIUM)**: deferral list locked by D2; defend the cut against any expansion.
- **D13 tension (LOW, vNext)**: auto-charging would need catalog products vs. D4 freeform strings.
  v1 sidesteps it entirely (no charging). Documented as the first design question of the vNext
  Mechanism-A epic.

## Explicitly out of v1 (do NOT build — D2)

External producer accounts · pre-payment/common-account integration · DeliveryNote write
integration/auto-charge · multi-producer orders · product variant catalogs · fractional-unit
modelling · closing-window reminder emails · arrival broadcast emails · co-organizer ownership ·
duplicate-previous-order templates · Pattern B arrival broadcast · full order history in "Mis pedidos".
