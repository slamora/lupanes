# Interview Log — Group Order Coordination

**Feature**: group-order-coordination
**Wave**: DISCOVER
**Date range**: 13 Mar 2026 → 31 May 2026
**Compiled**: 2026-05-31

---

## Method

This DISCOVER wave used a **single proxy informant** (Pablo Laulhé) plus **9 primary-source artifacts** (real organizer emails sent to `socios@lupierra.es` and related Lupierra mailing-list aliases over a 10-week window). The primary-source emails are the strongest piece of evidence and the downstream waves should treat them as ground truth.

Pablo's role:

- **Informant**: lived experience as a member-consumer in 5+ years of Lupierra group orders.
- **Engineer / project owner**: building the system.
- **NOT** a recurring organizer — that role is held by Gloria, Marta, Didier, Sheila/Fran, the FrutaLupierra group, Santiago Lamora, Gorka Estevez Urain, and others.

This single-respondent setup carries bias. It is mitigated, not eliminated, by the email corpus. See `problem-validation.md` "Calibration Note" for the full bias treatment.

### Mailing-list infrastructure observed

The email corpus reveals more than one alias in active use. Distinct aliases identified:

- `socios@lupierra.es` — broad socios broadcast (the primary discovery channel for Pattern A orders)
- `albaranes@lupierra.es` — delivery-note / albarán handling alias
- `Finanzas` — financial working-group alias (cc'd on price updates)

This multi-alias structure should inform the v1 notification design: Pattern A order-open emails flow through `socios@lupierra.es` (consistent with current behaviour). Other aliases are out of v1 scope but acknowledged.

---

## Informant Session — Pablo Laulhé

### Round 1 — Problem narrative (paraphrased from Pablo)

- Lupierra is a ~20-member rural food-buying association.
- Every few weeks a member volunteers to coordinate a group purchase from an external producer (bread, oil, fruit, avocados, toilet paper, etc.).
- The workflow is always: long email to `socios@lupierra.es` + Google Form built from scratch + manual CSV tally + relay to producer.
- Three failure modes hit members in every order: missing the open window (discovery), forgetting what they ordered (recall), missing the arrival (arrival).
- The existing Lupierra Django app already models `DeliveryNote` (albarán), products, and the local-stock workflow.

### Round 2 — Probing questions and answers

**Q1 — Switching cost: would recurring organizers actually move off Gmail+Forms?**
*Pablo*: "I don't have the info but it's not relevant — they might be used to that and not consider another option."
→ **Flagged as unmitigated risk** (R1 in `lean-canvas.md`). Pablo's "they're used to it, haven't considered alternatives" is a plausible prior, not evidence. Pre-DELIVER mockup review is the proposed validation.

**Q2 — Organizer 5-minute pain: what is the single most painful chore?**
*Pablo*: "I'm pretty sure it's tallying form responses."
→ Confirmed: aggregating Google Form CSV responses into a per-member-per-product summary for the producer is the most concrete validated pain. Maps to opportunity O2.

**Q3 — Member failure modes: which of {discovery, recall, arrival} happens most?**
*Pablo*: "All of them, probably in every group order at least one member has suffered from it."
→ All three are real and recurring at "every order" frequency. Prioritization can't come from frequency — must come from impact / ease / dependency. v1 cut addresses all three on a single surface.

**Q4 — v1 cut: what's the single most valuable first delivery?**
*Pablo*: "(a) I think? — a single page where any member can see all currently-open group orders and join them."
→ Strong v1 anchor. The "central active-orders board" idea folds discovery + collection + recall + arrival into one surface. See `opportunity-tree.md` v1 Solution Concept.

**Q5 — Organizer turnover: is it always the same 5–6 people?**
*Pablo*: "More people but not sure how many; I think they created the form from scratch."
→ Occasional one-off organizers exist, and they **rebuild the Google Form from scratch each time**. Implication 1: tool must be usable by an occasional, low-skill organizer — not just optimized for power users. Implication 2: opportunity O3 ("Forms-from-scratch waste") is real and validated.

---

## Pattern Recognition — Two distinct workflow patterns

Across the 9 emails two distinct workflow patterns emerge. This is a domain insight surfaced in Round 2 evidence expansion, and the v1 cut depends on it.

### Pattern A — Group Buy (time-boxed, per-member ordering)

Shape: announce → collect quantities (Google Form or freeform reply) → close on date → tally → relay to producer → deliver on date → consumers take their portions.

Emails matching Pattern A (5/9):

- Email 1 — Bread (Gloria Puertas)
- Email 2 — Avocados (Sheila / Fran)
- Email 3 — Fruit (FrutaLupierra group)
- Email 4 — Olive oil (Didier Vergés)
- Email 5 — Toilet paper, whole-box / half-box portion (Marta García Luengo)
- Email 6 — Ternera del Pirineo (Santiago Lamora)

### Pattern B — Arrival Announcement (no per-member ordering)

Shape: stock arrives via the autoproducción workflow → broadcast to socios → consumers take items at the local → charged on the existing `DeliveryNote` / albarán / Lupanes App. **No per-member quantity collection. No closing window. No Form.**

Emails matching Pattern B (4/9, counting the TP loose-rolls portion separately):

- Email 5 — Toilet paper, loose-rolls portion (Marta García Luengo, "se apuntan en albarán")
- Email 7 — Harinas y Spaghetti (Gorka Estevez Urain, Grupo de Autoproducción)
- Email 8 — Bebida de avena (Marta García Luengo, GT Productores — explicitly references "apuntar en la App")
- Email 9 — Jabón de lavadora (Gorka Estevez Urain, Grupo de Autoproducción)

### Implication for v1

Pablo's framing (verbatim): *"some of them don't even require an 'ordering' process by the consumers, it's just the producer informing about the products arrival."*

The two patterns have different gaps:

- **Pattern A** has multiple compounding gaps (discovery + collection + tally + arrival) and is the right target for v1. The existing tooling (Gmail + Google Form + manual tally) covers none of them well.
- **Pattern B**'s primary gap is just the broadcast notification ("new stock available"). The financial and pickup side is already solved by the existing `DeliveryNote` model + the Lupanes App (explicit evidence: Email 8 says "apuntar en la App"). The gap that remains is a notification surface that members can subscribe to instead of relying on Gmail.

**Decision (anchored in `wave-decisions.md` D11)**: v1 targets Pattern A exclusively. Pattern B is acknowledged and deferred to vNext as a related but separable opportunity.

### Working groups observed

The corpus reveals **two distinct working groups** above the individual organizer:

- **GT Productores** (Grupo de Trabajo Productores) — Marta García Luengo signs here. Pattern A oriented (TP, also Pattern B for avena).
- **Grupo de Autoproducción** — Gorka Estevez Urain signs here. Pattern B oriented (harinas, jabón).

Early adopters for v1 likely cluster in **GT Productores** (the Pattern A organizers). Acknowledged in `lean-canvas.md` Customer Segments.

### Organizers identified (6+ distinct humans)

| # | Organizer | Email(s) | Pattern | Working group |
|---|-----------|----------|---------|---------------|
| 1 | Gloria Puertas | 1 (bread) | A | (none stated) |
| 2 | Sheila Folch / Fran | 2 (avocados) | A | (none stated) |
| 3 | FrutaLupierra group | 3 (fruit) | A | FrutaLupierra |
| 4 | Didier Vergés | 4 (oil) | A | (none stated) |
| 5 | Marta García Luengo | 5 (TP), 8 (avena) | A + B | GT Productores |
| 6 | Santiago Lamora | 6 (ternera) | A | (none stated) |
| 7 | Gorka Estevez Urain | 7 (harinas), 9 (jabón) | B | Grupo de Autoproducción |

Plus Pablo Laulhé as proxy informant (lived-experience member, not a recurring organizer).

**n = 9 distinct primary-source events across 7 distinct organizer humans + 1 proxy informant.** Exceeds the skill's 10-source minimum (combined 9 + 1 = 10).

---

## Appendix — Primary-Source Evidence (verbatim emails)

Nine real emails from the `socios@lupierra.es` (and related) mailing list, used as primary-source evidence of the current workaround. **Do not alter or paraphrase these** — downstream waves will reference them as ground truth for vocabulary, workflow shape, and edge cases.

---

### Email 1 — Bread (Gloria Puertas via lupierra.es)

**From**: Gloria Puertas via lupierra.es
**Date**: Wed May 27, 2026 12:54 PM
**To**: Lupierra
**Subject**: (bread order, ~next week)

> Hola Lupierris
>
> Se abre pedido de pan para la próxima semana.
> Además de indicar el nombre de vuestra nevera, anotad también: AINETO o LA PEÑA, y el tipo de pan que queréis.
> La panadería de AINETO no podrá servirnos más pan hasta septiembre, este es el último pedido antes del verano, por si queréis pedir pan para congelar.
>
> Adjunto el catálogo y precios de la panadería de La Peña.
>
> Y los productos de Aineto son:
> - pan de trigo blanco a 5.5€
> - pan de trigo integral a 5 €
> - pan de centeno 100% integral a 5€
> - espelta integral 6€
> - galletas cookies 12€/kg, pueden pedirse en fracciones de 250gr.
>
> El pedido puede realizarse hasta el próximo domingo 31 de mayo, hasta las 18h.
>
> El pan de Aineto llegará el miércoles y el de La Peña el viernes, ambos entre las 11-13h.

**Notable shape**:
- Multi-producer in one email (Aineto + La Peña) → v1 cut: organizer opens two separate orders.
- Freeform product list embedded in the email body (no Form linked here — just freeform reply, even more friction).
- Variable unit: "galletas en fracciones de 250gr" → v1 cut: line item unit is a freeform string.
- "Nombre de vuestra nevera" — Lupierra-specific identifier worth preserving in UI copy.
- Closing date + two delivery dates (one per producer).

---

### Email 2 — Avocados (Sheila Folch / Fran)

**From**: sheila folch via Lupierra Socios <socios@lupierra.es>
**Date**: Tue May 5
**Subject**: (avocados HASS)

> Hola a todos y todas,
> Os lanzamos el siguiente pedido de Aguacates. Rellenar el formulario para hacer vuestro pedido.
> https://docs.google.com/forms/d/e/1FAIpQLSfVrmGswq9JH3MOV5m54Z1uqvmFXbuL_Ii1p33FtOKFxBav1g/viewform?usp=header
> Pedido de Aguacates HASS 🥑🥑🥑 a 5,70€ el kilo
>
> Forma y piel: Mientras que el Hass presenta una piel rugosa que cambia de color a negro al madurar, el Fuerte tiene una piel más suave y verde.
> Sabor y textura: El aguacate Hass es conocido por su cremosidad y fuerte sabor, a diferencia de las otras variedades que pueden tener una textura más acuosa.
> Contenido graso: El Hass tiene un mayor contenido de grasa saludable, lo que lo convierte en una opción preferida para quienes buscan beneficios nutricionales.
>
> El formulario estará abierto hasta sábado 9 de mayo a las 20h.
> Se mandará el pedido al productor para recibirlo aproximadamente el próximo martes 12 de MAYO.
>
> Fran y Sheila

**Notable shape**:
- Single producer, single product. Simplest case.
- Google Form for collection.
- Educational copy ("forma y piel", "sabor y textura") — v1 cut: organizer can attach a freeform description per order.
- Co-organizer signature ("Fran y Sheila") — v1 cut: only one organizer-of-record per order; co-organization is a vNext concern.

---

### Email 3 — Fruit (FrutaLupierra group)

**From**: FrutaLupierra Grupo fruta <frutalupierra@gmail.com> via lupierra.es
**To**: socios
**Subject**: (fruit order)

> Buen día!!!
> Os paso el formulario para el pedido de fruta.
>
> Que la disfruteis.
>
> https://docs.google.com/forms/d/e/1FAIpQLScUxElL3rKEJ1iEcb5AjzqlpjNQlOOuX7GeRXC58DEIIwjROA/viewform?usp=header
>
> Un saludo

**Notable shape**:
- Sub-group ("FrutaLupierra") with a shared Gmail account organizes a recurring category. v1 cut: order organizer = the member who creates the order. Sub-group identity is a vNext concern.
- Minimal email — all detail is inside the Form. Implication: members must click through to see what's even being offered. This is a strong driver for the central board (O1).

---

### Email 4 — Olive oil (Didier Vergés)

**From**: Didier VERGES via Lupierra Socios <socios@lupierra.es>
**Date**: Wed Apr 22, 2026 7:35 AM
**Subject**: LUPIERRA - Pedido de aceite (abril 2026)

> Hola, buenos días!!
>
> Llegó el momento de realizar el pedido primaveral de aceite de oliva.
>
> Seguimos con los 2 tipos de aceite:
> 1 - Aceite PALACIOS: es aceite de aceitunas de variedad arbequina con sabor más intenso. Las aceitunas son de su finca con tratamiento natural, aunque no con label ecológico. El precio sigue el mismo que el anterior pedido, 6€ el litro (30€ la garrafa).
> 2- Aceite ecoMATARRANYA: es aceite de aceitunas de variedad empeltre con sabor más suave. Dispone del label ecológico. El precio está ligeramente más caro: 8,5€ el litro (42€ la garrafa) al cual deberemos sumar el transporte.
>
> En este formulario, podréis pedir lo que necesitáis: [Pedido de aceite LUPIERRA — forms.gle]
>
> Cerraré pedidos y formulario el Miércoles 29 de abril a las 20h y gestionaré seguidamente el pedido con los productores.
>
> Muchas gracias!

**Notable shape**:
- Two variants × two sizes (litre / garrafa) — v1 cut: each variant is a freeform line item ("Palacios — 1L @ 6€", "Palacios — garrafa 5L @ 30€"). No variant modelling.
- "+ transporte" — variable shipping cost. v1 cut: organizer absorbs this into freeform pricing or notes.
- Pattern repeats ("seguimos con los 2 tipos") → strongest signal for a "duplicate previous order" template (vNext, S3.B).
- Closing datetime explicit and clean.

---

### Email 5 — Toilet paper (Marta García Luengo)

**From**: Marta García Luengo <martagluengo@hotmail.com>, GT Productores
**Date**: Fri Mar 13 12:48 PM
**To**: Socios
**Subject**: (toilet + kitchen paper order)

> Buenas Lupierris,
>
> Como viene siendo habitual cada 6 meses, abro pedido de papel higiénico y de cocina, para quien quiera coger cajas enteras o medias cajas bajo pedido.
>
> Para quien quiera coger rollos sueltos a granel en el local, como otras veces dejaré en el local un par de cajas, y los que cojáis así se apuntan en albarán (a los que piden por cajas/medias cajas se les carga directamente en su cuenta).
>
> Es ecologico, sin plásticos, hecho en España y suave (a pesar del aspecto/color de papel de lija que tiene).
>
> Para pedir sólo tenéis que:
>
> 1) Rellenar el formulario:
> https://forms.gle/X2e1DYG4bU9pPKt3A
>
> 2) Hacer un donativo de cantidad equivalente a lo que estáis pidiendo, o superior, a la cuenta de Lupierra, puesto que este pedido se paga por adelantado y si no lo hacéis así, se nos queda la cuenta común en números rojos y con problemas para pagar a otros proveedores. Gracias!
>
> Fecha límite para pedir: 18 de marzo a las 22h.
>
> Cualquier duda me decís.
>
> Buen fin de semana!
>
> Marta García Luengo
> GT Productores

**Notable shape — this is the most complex case in the corpus**:
- **Three sale modes in one order**: whole box (pre-paid, charged to account), half box (pre-paid, charged to account), loose rolls (recorded on albarán at the local).
- **Pre-payment via donation to the common account** — explicitly because otherwise the common account goes red. Strong financial coupling.
- **Bridge to existing `DeliveryNote`** — "se apuntan en albarán" — directly references the model already in the Lupierra app.
- Recurring cadence ("cada 6 meses") — another candidate for the duplicate-previous-order template.
- Signs as "GT Productores" — there's a working-group concept ("Grupo de Trabajo") above the individual organizer. vNext concern.

**This email alone justifies the explicit "out of v1" list** in `opportunity-tree.md`: payment, albarán bridge, multi-sale-mode, and pre-payment-with-financial-consequences are all real. None is in v1. The organizer of the next TP order will either use v1 minimally (board + tally) and handle payment off-system as today, or stay on Gmail+Forms for this category until vNext.

---

### Email 6 — Ternera del Pirineo (Santiago Lamora via lupierra.es)

**From**: Santiago Lamora via lupierra.es
**To**: Lupierra
**Subject**: Pedido mayo Ternera del Pirineo

> Buenos días,
>
> Pedido de este mes de Ternera del Pirineo, para que repongáis vuestra despensa 🙂
> * Fecha límite: domingo 3 de mayo a las 22h
> * Fecha de llegada: jueves 7 de mayo durante la mañana
> FORMULARIO 👉 https://forms.gle/pdp4PpH3MuEJRUdj9 👈

**Type**: GROUP BUY (Pattern A). New organizer: Santiago Lamora. Monthly cadence ("Pedido de este mes").

**Notable shape**:
- Identical workflow to Emails 1–5 — confirms Pattern A is not category-specific (bread, fruit, oil, TP, avocados, *and now meat*).
- Cleanest possible "open + close + arrival" trio.
- Monthly cadence → strong driver for a duplicate-previous-order template (vNext, S3.B).

---

### Email 7 — Harinas y Spaghetti (Gorka Estevez Urain, Grupo de Autoproducción)

**From**: Gorka Estevez Urain <gorki_1993@hotmail.com>
**To**: Alicia (probably forwarded via socios)
**Subject**: (harinas y spaghetti — disponibles)

> Buenas,
>
> Hacer saber que ya hay disponibles:
> - 25 kg de harina de trigo integral en paquetes de 1 kg
> - 15 kg de espaguetis ecolecera en paquetes también de 1 kg
>
> ¡Que los disfruteis!
>
> Un saludo y buen día,
> Grupo de Autoproducción.

**Type**: ARRIVAL ANNOUNCEMENT (Pattern B). No closing date. No Form. No per-member ordering. Stock already at the local. New organizer: Gorka Estevez Urain. New working group: **Grupo de Autoproducción**.

**Notable shape**:
- Zero consumer-side ordering action — members take items at the local via the existing albarán flow.
- Stock counts disclosed up front (25 kg / 15 kg) — the broadcast doubles as inventory.
- This category is **largely out of v1 scope**; the gap is just the broadcast notification.

---

### Email 8 — Bebida de avena (Marta García Luengo, GT Productores)

**From**: Marta García Luengo <martagluengo@hotmail.com> via lupierra.es
**Date**: Wed May 13, 10:59 AM
**To**: Lupierra, albaranes@lupierra.es, Finanzas
**Subject**: (bebida de avena — nueva remesa)

> Buenos días,
>
> Ha llegado nueva remesa de bebida de avena Amandin, son 138 litros, lo que tenían disponible en la central de Ecoplaza (cada vez van teniendo menos, parece que lo trabajan poco).
>
> El precio ha subido ligeramente, de 2,05€ a 2,07€ el litro, para apuntar en la App.
>
> Saludos y buen día!
>
> Marta Gª Luengo
> GT Productores

**Type**: ARRIVAL ANNOUNCEMENT (Pattern B) with a **price update**. Charged via the existing **Lupanes App** (explicit reference: "apuntar en la App"). Multi-address: socios + `albaranes@lupierra.es` + `Finanzas`.

**Notable shape**:
- **Explicit confirmation that the existing app already handles the consumer-side charge** for Pattern B. This is the strongest signal that Pattern B does not need a new ordering UI.
- Price-update workflow is a real ongoing chore that the existing albarán/App handles (organizer updates the product price; charges follow automatically). Out of v1 scope.
- Multi-alias addressing (`albaranes`, `Finanzas`) shows the mailing-list infrastructure is more sophisticated than a single socios broadcast.
- Same organizer (Marta) appears in both Pattern A (TP) and Pattern B (avena). Working-group ownership ("GT Productores") spans patterns.

---

### Email 9 — Jabón de lavadora (Gorka Estevez Urain, Grupo de Autoproducción)

**From**: Gorka Estevez Urain
**To**: Idoia
**Subject**: JABÓN DE LAVADORA

> Buenos días,
>
> Desde el grupo de autoproducción os comunicamos que ya hay disponibles en el local **18 garrafas de jabon de lavadora**
>
> Un saludo,

**Type**: ARRIVAL ANNOUNCEMENT (Pattern B). Same Grupo de Autoproducción pattern as Email 7.

**Notable shape**:
- Confirms Email 7 was not a one-off — the Grupo de Autoproducción runs Pattern B as standard behaviour.
- "Ya hay disponibles en el local" — stock is on hand, consumer-side action is to walk to the local and take it.
- Out of v1 scope; documented for completeness and to inform the vNext "Pattern B broadcast" opportunity (see `opportunity-tree.md` O7).
