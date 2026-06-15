# UX Journey — Group Order Coordination (v1, Pattern A)

**Feature**: group-order-coordination
**Wave**: DISCUSS
**Platform**: Web (Django + Bootstrap 5, inside the existing Lupierra app)
**Scope**: LOCKED by wave-decisions.md D1–D13. Two personas: Member-Organizer (Pattern A) + Member-Consumer.

> All UI copy is Spanish, using association vocabulary (D8): "Se abre pedido", "nevera",
> "cerrar pedido", "se apuntan en albarán". This journey describes WHAT users experience,
> not HOW it is built (that is DESIGN's job).

---

## Personas (from D6)

- **Member-Organizer** — any nevera who created a given order. Not a new role; the organizer
  is simply the creator of that order. Examples: Gloria Puertas (bread), Marta García Luengo
  (toilet paper), Didier Vergés (oil).
- **Member-Consumer** — any nevera participating in an order. Every member is a consumer; an
  organizer is also a consumer in orders they did not create. Example: Pablo wants 2 loaves of
  Aineto bread from Gloria's order.

---

## Organizer Journey — "Se abre pedido"

Emotional arc: **Problem Relief** (frustrated by Gmail+Forms rebuild → hopeful → relieved the tally is automatic).

```
[Trigger]            [Step 1]              [Step 2]            [Step 3]            [Goal]
Producer ready   →   Open the order    →   Watch it fill  →   Read the tally  →   Relay to producer
to take a batch      (title, producer,     up on the board    + close + mark      & mark arrived
                     line items, dates,    as members          status
                     "paid in albaranes"   submit
                     flag)
 Feels: "ugh,        Feels: guided,        Feels: in          Feels: relieved —   Feels: done,
 not the Form        the form is short     control, no        no manual CSV       low effort
 again"              and reuses my words   chasing            tallying

 Artifact:           Artifact: Order       Artifact:          Artifact: tally     Artifact: status
 producer + prices   (status=open) +       member line        view (per-member-   = ordered/arrived
 in organizer's      email to              items accumulate   per-product)
 head                socios@lupierra.es
```

### Step-by-step

1. **Open the order.** Organizer fills a short guided form: title, producer name (freeform),
   product line items (freeform name + optional price/unit/notes), closing date, expected
   delivery date, and a "El pago lo registra cada socio en albaranes" checkbox (default OFF).
   On save the order is `open` and an email goes to `socios@lupierra.es` with title, producer,
   line items, closing date, and a link (D3 — hard requirement).
   - *Confidence lever*: the form mirrors the words organizers already write in their emails
     (D8), so it feels familiar, not like learning a new tool.
2. **Watch it fill.** The order appears on the active-orders board with status `open`. The
   organizer sees submissions accumulate. No chasing, no CSV.
3. **Close + read the tally.** When the closing date passes (or the organizer closes manually),
   status becomes `closed`. The organizer opens the tally — a per-member-per-product table they
   copy and send to the producer. This replaces the manual CSV tally (O2, the single biggest pain).
4. **Advance status.** Organizer marks `ordered` (relayed to producer) and later `arrived`.
   Only the creator of that order can change its status or see its tally.

### Organizer emotional checkpoints

| Phase | Target emotion | Lever |
|-------|---------------|-------|
| Opening | Guided, not burdened | Short form, association vocabulary, sensible defaults |
| Collecting | In control | Live board status; no manual chasing |
| Tallying | Relieved | Auto-aggregated tally replaces CSV |
| Concluding | Done | One-click status advance |

---

## Consumer Journey — "Me apunto al pedido"

Emotional arc: **Confidence Building** (anxious "did I miss it / what did I order?" → engaged → confident).

```
[Trigger]              [Step 1]            [Step 2]           [Step 3]           [Goal]
Email "Se abre     →   See the board   →   Submit my      →   Check "Mis     →   Pick up what
pedido" arrives        of open orders      quantities         pedidos" later     I ordered
in socios list                             against the        + see status

 Feels: "oh, an       Feels: "good, I     Feels: "done,      Feels: confident   Feels: nothing
 order — don't        can see it's open    it's recorded"     — I can recall     missed
 want to miss it"     and when it closes"                     what I asked for

 Artifact: email      Artifact: board      Artifact: my       Artifact: "Mis     Artifact: status
 from D3 with link    (open orders +       line items         pedidos" view +    = arrived (+
                      closing dates)                          albarán reminder   reminder if flag ON)
                                                              if flag ON
```

### Step-by-step

1. **See the board.** The consumer follows the email link (or opens the app) and sees the board
   of currently-open orders: title, producer, closing date, status. Solves the discovery problem (O1).
2. **Submit quantities.** Against an open order, the consumer enters a quantity for the line items
   they want. Submissions are blocked once the order is no longer `open` (past closing date / closed).
3. **Recall via "Mis pedidos".** At any time the consumer sees their own line items per active
   order — answering "what did I order?" without scrolling Gmail (O4). If the order's "paid in
   albaranes" flag is ON, a reminder is shown nudging them to register their own albarán via the
   EXISTING flow (D13 — read-only nudge, the tool never writes the albarán). If the flag is OFF,
   no reminder appears.
4. **Track arrival.** The consumer sees order status advance to `arrived` on the board / "Mis
   pedidos", so they know when to pick up (O5).

### Consumer emotional checkpoints

| Phase | Target emotion | Lever |
|-------|---------------|-------|
| Discovery | Reassured "I won't miss it" | Email (D3) + always-visible board |
| Submitting | Confident it's recorded | Clear confirmation, own quantities visible |
| Recall | Confident, not embarrassed | "Mis pedidos" shows exactly what they asked for |
| Albarán (flag ON) | Reminded, not nagged | Empathetic one-line nudge to existing albarán flow |
| Arrival | Informed | Visible status change |

---

## Shared artifacts across steps

| Artifact | Source of truth | Appears in | Integration risk |
|----------|-----------------|-----------|------------------|
| Order (title, producer, line items, dates) | The Order record | Board, email (D3), submit form, tally, "Mis pedidos" | HIGH — email content must match the order; line items must be the same set the consumer submits against |
| Order status (open→closed→ordered→arrived) | The Order record | Board, "Mis pedidos", organizer controls | HIGH — submissions gated on `open`; consumer arrival signal reads this |
| Member line items (a member's quantities) | The submission record | Submit form, "Mis pedidos", tally | HIGH — "Mis pedidos" and the organizer tally must reflect the same submitted data |
| "Paid in albaranes" flag | The Order record (set by creator) | Order create/edit form, consumer "Mis pedidos" reminder | MEDIUM — reminder shows iff flag ON and member ordered |
| "Is this user the creator?" | Order.creator vs request.user | Tally visibility, status controls, edit | HIGH — organizer-only actions gated on creator identity, NOT the manager group |
| `socios@lupierra.es` list | Existing mailing list | D3 email recipient | MEDIUM — must use existing list, not a new sender (Open Q1 → existing list) |

---

## Error / edge paths surfaced for DESIGN & DISTILL

- Consumer tries to submit after closing date / on a non-open order → blocked with a clear message.
- Non-creator tries to view tally or change status → not permitted (creator-only).
- Order opened with empty line items → prevented at creation (an order needs at least one line item).
- D3 email send fails → order still created; failure logged; organizer is informed the order is
  open but notification may not have gone out (does not silently lose the order).
- Flag ON but member ordered nothing → no albarán reminder (reminder is conditional on having ordered).
