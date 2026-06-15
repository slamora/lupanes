# Acceptance Criteria — Group Order Coordination (v1, Pattern A)

**Feature**: group-order-coordination
**Wave**: DISCUSS
**Format**: Gherkin (Given/When/Then). One section per story in `user-stories.md`.

> Scenario titles describe business outcomes, not implementation. Real data throughout (D8 Spanish
> vocabulary, real personas: Gloria, Marta, Didier, Pablo, Santiago). Scenarios are solution-neutral
> — they describe WHAT the member observes, not HOW Django renders it.
>
> Shared preconditions for every scenario: the actor is an authenticated member of the `neveras`
> group (`is_customer`). Organizer-only behaviour is gated on "is this user the creator of this
> order", not the manager group.

---

## US-01: Organizer opens a group order

```gherkin
Scenario: Organizer opens a bread order for the association
  Given Gloria is an authenticated member
  When she opens an order titled "Pan semana del 2 de junio" for producer "Aineto"
    with line items "Pan de espelta 1kg — 4,50€" and "Galletas 250gr — 2€"
    closing on 2026-06-01 20:00 and delivering on 2026-06-03
    and leaves "El pago lo registra cada socio en albaranes" unchecked
  Then the order is created with status "open"
  And Gloria is recorded as the organizer of the order

Scenario: Organizer opens an order with line items that have no price yet
  Given Didier is an authenticated member
  When he opens an order titled "Aceite primavera 2026" for producer "ecoMatarranya"
    with line items "Aceite virgen extra 5L" and "Aceite virgen extra 2L" and no prices
  Then the order is created with status "open"
  And the line items are saved without prices

Scenario: An order cannot be opened with no products
  Given Marta is an authenticated member
  When she tries to open an order "Papel higiénico" with no line items
  Then the order is not created
  And she is told that an order needs at least one product line item
```

---

## US-02: Members see the board of open orders

```gherkin
Scenario: Member sees all currently-open orders on one board
  Given Gloria's order "Pan semana del 2 de junio" is open and closes 2026-06-01
  And Didier's order "Aceite primavera 2026" is open and closes 2026-06-05
  When Pablo opens the orders board
  Then he sees both orders with their producer, closing date, and status
  And each order links to its detail page where he can submit

Scenario: Closed orders do not clutter the board
  Given Marta's order "Papel higiénico" has passed its closing date and is closed
  When Pablo opens the orders board
  Then "Papel higiénico" is not listed among the open orders

Scenario: Inviting empty state when nothing is open
  Given there are no open orders
  When Pablo opens the orders board
  Then he sees a message that no orders are open right now
  And the page is not blank
```

---

## US-03: Member submits quantities against an open order

```gherkin
Scenario: Member submits the quantities they want
  Given Gloria's bread order is open with line items "Pan de espelta 1kg" and "Galletas 250gr"
  When Pablo submits "Pan de espelta 1kg: 2" and "Galletas 250gr: 1"
  Then his quantities are saved against the order under his nevera
  And he sees a confirmation that his order was recorded

Scenario: Member updates their quantities before the window closes
  Given Pablo has already submitted "Pan de espelta 1kg: 2" to Gloria's open order
  When he updates his submission to "Pan de espelta 1kg: 3"
  Then his recorded quantity for "Pan de espelta 1kg" is 3
  And he is not counted twice

Scenario: Submission is blocked once the order is closed
  Given Gloria's bread order has passed its closing date and is closed
  When Pablo tries to submit "Pan de espelta 1kg: 2"
  Then his submission is not accepted
  And he is told the order is closed
```

---

## US-04: Member sees "Mis pedidos"

```gherkin
Scenario: Member recalls what they ordered across active orders
  Given Pablo submitted "Pan de espelta 1kg: 3, Galletas 250gr: 1" to Gloria's closed bread order
  And Pablo submitted "Aceite virgen extra 5L: 1" to Didier's open oil order
  When Pablo opens "Mis pedidos"
  Then he sees his bread line items with status "closed"
  And he sees his oil line items with status "open"

Scenario: Member only sees their own submissions
  Given Marta also submitted to Gloria's bread order
  When Pablo opens "Mis pedidos"
  Then he sees only his own line items
  And he does not see Marta's line items

Scenario: Most recent arrived order still appears so the member can pick up
  Given Didier's oil order has moved to status "arrived" and is the most recent arrived order Pablo ordered in
  And an older bread order Pablo ordered in also has status "arrived"
  When Pablo opens "Mis pedidos"
  Then the arrived oil order is shown so he knows what to pick up
  And the older arrived bread order is not shown

Scenario: Inviting empty state when the member has not ordered anything
  Given Pablo has not submitted to any order
  When Pablo opens "Mis pedidos"
  Then he sees a message inviting him to check the orders board
```

---

## US-05: Member sees the albarán reminder when the order flag is ON

```gherkin
Scenario: Self-service order reminds the member to register their own albarán
  Given Marta's order has "El pago lo registra cada socio en albaranes" turned ON
  And Pablo submitted loose rolls to that order
  When Pablo views the order in "Mis pedidos"
  Then he sees a read-only reminder that he must register his own albarán
  And the reminder links to the existing albarán registration flow

Scenario: No reminder when the order is charged by the organizer
  Given Gloria's bread order has the albarán flag OFF
  And Pablo submitted bread to that order
  When Pablo views the order in "Mis pedidos"
  Then he sees no albarán reminder

Scenario: No reminder for a member who did not order
  Given Marta's order has the albarán flag ON
  And Pablo did not submit anything to that order
  When Pablo views the order
  Then he sees no albarán reminder

Scenario: The tool never charges on the member's behalf
  Given Marta's order has the albarán flag ON
  And Pablo submitted to that order
  When Pablo views the albarán reminder
  Then no delivery note is created automatically for him
  And he must register his albarán himself via the existing flow
```

---

## US-06: Organizer reads the per-member-per-product tally

```gherkin
Scenario: Organizer reads a ready-to-send producer tally
  Given Pablo submitted "Pan de espelta 1kg: 3, Galletas 250gr: 1" to Gloria's order
  And Marta submitted "Pan de espelta 1kg: 2" to Gloria's order
  When Gloria opens the tally for her order
  Then she sees a per-member-per-product table:
    | Member | Pan de espelta 1kg | Galletas 250gr |
    | Pablo  | 3                  | 1              |
    | Marta  | 2                  | 0              |
  And she sees per-product totals: Pan de espelta 1kg = 5, Galletas 250gr = 1
  And the tally is laid out so she can copy it to send to Aineto

Scenario: Tally works with a single participant
  Given Didier is the only member who submitted to his oil order ("Aceite 5L: 1")
  When Didier opens the tally
  Then he sees one row and matching per-product totals

Scenario: Only the organizer of the order can see its tally
  Given Pablo is not the creator of Gloria's bread order
  When Pablo opens Gloria's order
  Then he does not see the tally section
```

---

## US-07: Order-open sends an email to the socios list (D3, HARD requirement)

```gherkin
Scenario: Opening an order announces it to the socios list
  Given Gloria opens her bread order "Pan semana del 2 de junio" for producer "Aineto"
    closing 2026-06-01 20:00
  When the order is created
  Then an email is sent to the socios@lupierra.es list
  And the email contains the title, producer, line items, closing date, and a link to the order page

Scenario: Email lists items even when some have no price
  Given Didier opens his oil order with line items that have no price
  When the order is created
  Then the announcement email lists the items with prices omitted where absent

Scenario: A failed announcement does not lose the order
  Given the mail server is temporarily unavailable
  When Gloria opens her bread order
  Then the order is still created with status "open"
  And the failure is logged
  And Gloria is informed the order is open but the announcement may not have been sent
```

---

## US-08: Order status lifecycle (open → closed → ordered → arrived)

```gherkin
Scenario: Organizer advances an order through its lifecycle
  Given Gloria's bread order is open
  When the closing date passes and the order becomes closed
  And Gloria marks it as ordered after relaying to Aineto
  And Gloria marks it as arrived when the bread arrives
  Then members see the status "arrived" on the board and in "Mis pedidos"

Scenario: Organizer closes an order early
  Given Didier's oil order is open and everyone has already submitted
  When Didier closes the order before its closing date
  Then the order status is closed
  And further submissions are blocked

Scenario: Only the organizer can change status
  Given Pablo is not the creator of Gloria's order
  When Pablo tries to change the order status
  Then the status is not changed
  And he is not permitted to perform the action

Scenario: Status only moves forward
  Given Gloria's order has status "ordered"
  When an attempt is made to set it back to "open"
  Then the status remains "ordered"
```

---

## Cross-cutting properties

```gherkin
@property
Scenario: "Mis pedidos" and the organizer tally always reflect the same submitted data
  Given members have submitted quantities to an order
  Then every quantity a member sees in "Mis pedidos" for that order
    equals the corresponding cell in the organizer's tally
  And neither view shows a quantity the member did not submit

@property
Scenario: Organizer-only actions are never available to non-creators
  Given an order created by Gloria
  Then for any member who is not Gloria
    the tally, the status controls, the albarán-flag setting, and order editing are unavailable
  And this holds regardless of whether that member is in the manager group
```
