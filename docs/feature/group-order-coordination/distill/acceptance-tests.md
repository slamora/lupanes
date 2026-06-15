# DISTILL — Acceptance Tests — Group Order Coordination (v1, Pattern A)

**Feature**: group-order-coordination
**Wave**: DISTILL
**Designer**: Quinn (nw-acceptance-designer)
**Test module**: `lupanes/tests/test_grouporder_acceptance.py`
**Harness**: Django `TestCase`, run via `manage.py test` (Django 3.2). No pytest / no behave / no BDD libs.
**State on creation**: RED by design — production code (models, `lupanes:grouporder-*` URLs/views,
`GROUP_ORDER_NOTIFY_EMAIL` setting, announcement email template) does not exist yet. These tests are
the OUTER LOOP that drives Outside-In TDD in DELIVER.

> Run: `env/bin/python manage.py test lupanes.tests.test_grouporder_acceptance`
> Expected today: `ImportError: cannot import name 'GroupOrder' from 'lupanes.models'` — exactly the
> not-yet-implemented symbols. As DELIVER lands each slice, the matching class goes GREEN.

---

## Outside-In entry points (driving ports)

Every test enters the system through a **Django view exercised via `self.client` by URL name** — never
by calling a form/model/mixin directly. Assertions are on **observable outcomes**: HTTP status,
redirects, persisted `GroupOrder*` rows, view `context` objects, and `mail.outbox`. This satisfies
Mandate 1 (hexagonal boundary) and Mandate 7 (observable behaviour).

| Driving port (URL name) | View (architecture §10) | Stories driven |
|-------------------------|--------------------------|----------------|
| `lupanes:grouporder-new` | `GroupOrderCreateView` | US-01, US-07 (email on open), US-08 (sets `open`) |
| `lupanes:grouporder-list` | `GroupOrderListView` (board) | US-02 |
| `lupanes:grouporder-submit` | `GroupOrderSubmitView` | US-03, US-08 (submit gate) |
| `lupanes:grouporder-mine` | `GroupOrderMineView` | US-04, US-05 (reminder surface) |
| `lupanes:grouporder-detail` | `GroupOrderDetailView` | US-05 (reminder), US-06 (creator-only tally section) |
| `lupanes:grouporder-edit` | `GroupOrderUpdateView` (`GroupOrderOwnerMixin`) | US-08 (flag/edit, creator-only) |
| `lupanes:grouporder-status` | `GroupOrderStatusView` (`GroupOrderOwnerMixin`) | US-08 |

Existing port reused read-only by US-05: `lupanes:deliverynote-new` (`/albaran/new/`) — the reminder
is a deep link; the tool never writes a `DeliveryNote` (D13 / C-NOCHARGE).

**Test ARRANGE vs ACT**: preconditions (an order already exists, a member already submitted) are set
up directly via the model layer in `GroupOrderTestMixin.make_order` / `submit_line`. The *behaviour
under test* (create, submit, advance status, view) always goes through a view. This keeps fixtures as
PRECONDITIONS, never the expected output (No Fixture Theater).

---

## Personas & auth (mirrors `lupanes/tests/test_legacy.py`)

`Group.objects.create(name=CUSTOMERS_GROUP)` → `User.objects.create_user(...)` → `user.groups.add(...)`.
`CUSTOMERS_GROUP="neveras"`, `MANAGERS_GROUP="tienda"` imported from `lupanes.users`.

- **Gloria, Marta, Didier** — organizers (each is just `created_by` of their order; "organizer" is NOT
  a role).
- **Pablo** — consumer.
- **Santi** — `tienda` manager who created no order. Used to prove organizer actions are creator-gated,
  NOT manager-gated (C-ORGANIZER).

Authorization expectations (verified against the existing `ProductSummaryAccessTest` pattern + Django
`AccessMixin`): authenticated-but-unauthorized → **403**; anonymous → **302** redirect to login.

---

## Story → test method mapping

### US-01 — Organizer opens a group order — `GroupOrderCreateTests` (4)
| Scenario (acceptance-criteria.md) | Test method | Type |
|---|---|---|
| auth required | `test_anonymous_is_redirected_to_login` | sad |
| Opens bread order, status open, creator recorded | `test_organizer_opens_bread_order_with_priced_line_items` | happy / **walking skeleton** |
| Line items with no price | `test_organizer_opens_order_with_line_items_without_prices` | edge |
| Cannot open with zero products | `test_order_cannot_be_opened_with_no_products` | error |

### US-02 — Members see the board of open orders — `GroupOrderBoardTests` (5)
| Scenario | Test method | Type |
|---|---|---|
| auth required | `test_anonymous_is_redirected_to_login` | sad |
| Board lists all open orders w/ producer + closing | `test_board_lists_all_currently_open_orders` | happy / **walking skeleton** |
| Closed orders excluded | `test_closed_orders_do_not_clutter_the_board` | edge |
| Past-closing (lazy-derived) excluded | `test_orders_past_closing_date_drop_off_the_board` | edge |
| Inviting empty state | `test_inviting_empty_state_when_nothing_is_open` | error/boundary |

### US-03 — Member submits quantities — `GroupOrderSubmitTests` (5)
| Scenario | Test method | Type |
|---|---|---|
| auth required | `test_anonymous_is_redirected_to_login` | sad |
| Submit quantities (saved under nevera) | `test_member_submits_quantities` | happy / **walking skeleton** |
| Update replaces (no double count, unique_together) | `test_member_update_replaces_previous_quantities` | edge |
| Blocked when closed | `test_submission_blocked_once_order_is_closed` | error |
| Blocked when closing date passed (lazy close) | `test_submission_blocked_when_closing_date_passed` | error/boundary |

### US-04 — "Mis pedidos" — `GroupOrderMineTests` (5)
| Scenario | Test method | Type |
|---|---|---|
| auth required | `test_anonymous_is_redirected_to_login` | sad |
| Recall lines across active orders w/ status | `test_member_recalls_their_lines_across_active_orders` | happy |
| Only own submissions | `test_member_only_sees_their_own_submissions` | edge |
| Most-recent arrived shown, older hidden | `test_most_recent_arrived_order_appears_older_arrived_hidden` | error/boundary |
| Inviting empty state | `test_inviting_empty_state_when_member_has_not_ordered` | error/boundary |

### US-05 — Albarán reminder (flag ON/OFF, D13) — `GroupOrderReminderTests` (4)
| Scenario | Test method | Type |
|---|---|---|
| Flag ON + member ordered → reminder + albarán link | `test_reminder_shown_when_flag_on_and_member_ordered` | happy |
| Flag OFF → no reminder | `test_no_reminder_when_flag_off` | edge |
| Flag ON but did not order → no reminder | `test_no_reminder_for_member_who_did_not_order` | error/boundary |
| Never writes a DeliveryNote (count invariant) | `test_viewing_reminder_never_creates_a_delivery_note` | hard guarantee |

### US-06 — Organizer tally (creator-only) — `GroupOrderTallyTests` (4)
| Scenario | Test method | Type |
|---|---|---|
| Per-member-per-product table + per-product totals | `test_creator_reads_per_member_per_product_tally_with_totals` | happy / **walking skeleton** |
| Single participant | `test_tally_works_with_a_single_participant` | edge |
| Non-creator sees no tally (not in context) | `test_non_creator_does_not_see_the_tally_section` | error/boundary |
| Manager (non-creator) sees no tally | `test_manager_who_is_not_creator_does_not_see_the_tally` | @property |

### US-07 — Order-open email to socios (D3) — `GroupOrderEmailTests` (3)
> Class-decorated `@override_settings(EMAIL_BACKEND="...locmem.EmailBackend")` because the app default
> is `post_office.EmailBackend` (enqueues, does NOT populate `mail.outbox`).
| Scenario | Test method | Type |
|---|---|---|
| Announce to `GROUP_ORDER_NOTIFY_EMAIL` w/ title/producer/items | `test_opening_an_order_announces_it_to_the_socios_list` | happy |
| Items without price still listed | `test_email_lists_items_even_when_some_have_no_price` | edge |
| Failed send keeps order open + logs ERROR + warns | `test_failed_announcement_does_not_lose_the_order` | error/boundary |

### US-08 — Status lifecycle — `GroupOrderStatusTests` (5)
| Scenario | Test method | Type |
|---|---|---|
| Advance open→closed→ordered→arrived (+arrived_at) | `test_organizer_advances_order_through_lifecycle` | happy |
| Close early; submissions then blocked | `test_organizer_closes_an_order_early` | edge |
| Non-creator cannot change status (403) | `test_non_creator_cannot_change_status` | error |
| Manager (non-creator) cannot change status (403) | `test_manager_who_is_not_creator_cannot_change_status` | @property |
| Status only moves forward (no rollback) | `test_status_only_moves_forward` | error/boundary |

### Cross-cutting @property — `GroupOrderConsistencyTests` (2)
| Scenario | Test method |
|---|---|
| Mis-pedidos quantities == tally cells (single source) | `test_mis_pedidos_quantities_match_the_tally` |
| Organizer-only actions never reach any non-creator (incl. manager) | `test_organizer_only_actions_never_available_to_non_creators` |

---

## Coverage summary

- **37 test methods**, 9 test classes (1 per story area + cross-cutting), 1 shared `GroupOrderTestMixin`.
- **Story coverage**: US-01..US-08 + both cross-cutting `@property` scenarios — **8/8 stories**.
- **Error/edge ratio**: 18 sad/error/boundary of 37 ≈ **49%** (target ≥ 40%). Every story area has at
  least one sad/edge path.
- **Walking skeletons** (US-01 → US-02 → US-03 → US-06, the validated thinnest slice): the
  organizer-opens → board-lists → member-submits → creator-reads-tally journey is covered by the four
  happy-path methods marked **walking skeleton** above. Each is framed as a user goal with observable
  outcomes (order confirmed, board shows it, quantities recorded, tally readable).
- **Creator-vs-non-creator** proven on every organizer action (tally, status, edit) both as the creator
  (allowed) and as another customer AND a manager (forbidden / no tally in context).

## DELIVER build order (one-at-a-time enablement)

Follow the release slices (user-stories.md §Story Map). Recommended Outside-In sequence — enable one
test, make it GREEN, commit, repeat:

1. **R1 (skeleton)**: `GroupOrderCreateTests` → `GroupOrderBoardTests` → `GroupOrderSubmitTests` →
   `GroupOrderTallyTests`. Lands the three models, the create/board/submit/detail views, and the
   computed `tally()`.
2. **R2**: `GroupOrderEmailTests` (add `GROUP_ORDER_NOTIFY_EMAIL` + `emails/group_order_opened.txt`) →
   `GroupOrderStatusTests` (forward-only guard + `arrived_at`) → `GroupOrderMineTests` (active +
   most-recent-arrived).
3. **R3**: `GroupOrderReminderTests` (flag-conditional read-only reminder).
4. **Cross-cutting**: `GroupOrderConsistencyTests` should pass once R1–R3 land; keep as regression
   guards for the single-source-of-truth and creator-only invariants.

## Assumed contracts left to DELIVER (mechanism-neutral where possible)

The load-bearing assertions are on DB state, status codes, redirects, context objects, and
`mail.outbox` — these are mechanism-neutral and survive DELIVER's internal choices. Two places make a
concrete-but-changeable assumption to be able to POST at all; DELIVER may adjust the *form field
names* and the tests' POST payloads must then match (the assertions themselves stay):

- **Order create** uses an inline formset prefixed `products-*` for `GroupOrderProduct`
  (architecture §6 `inlineformset_factory(..., min_num=1, validate_min=True)`).
- **Submission** posts one field per product named `product_<pk>` (architecture §6 "dynamic per-product
  form"). If DELIVER names them differently, update the POST keys in `GroupOrderSubmitTests` /
  `GroupOrderStatusTests.test_organizer_closes_an_order_early`; the assertions on persisted
  `GroupOrderLineItem` rows are unchanged.
- **Status advance** posts `status=<target>` to `grouporder-status`.

## Mandate compliance evidence (for handoff)

- **CM-A (hexagonal boundary)**: every test enters via `reverse("lupanes:grouporder-*")` + `self.client`.
  Imports are limited to the three models (`GroupOrder`, `GroupOrderProduct`, `GroupOrderLineItem`),
  `DeliveryNote` (for the D13 count-invariant), and group constants — zero internal validator/form/mixin
  imports.
- **CM-B (business language)**: Gherkin in `acceptance-criteria.md` and test/method names use domain
  terms (order, board, submit, tally, albarán, socios). No HTTP/JSON/REST jargon in scenario language.
- **CM-C (user-journey completeness)**: walking skeletons trace the full open→discover→submit→tally
  value journey with observable outcomes.
- **CM-D (pure-function/adapter)**: N/A at this scale — the one external boundary (socios email) is
  isolated in `form_valid` and asserted via the locmem backend (no fixture-matrix parametrization
  warranted; architecture §8).
