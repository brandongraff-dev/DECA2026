# Step 7: Customer & Expert Validation Kit

**Goal:** replace our biggest guesses with real answers from real people, and get quotes or letters you can put in the deck appendix. (DECA explicitly allows "sample questionnaires used, letters sent and received" in the appendix.)

**Ground rules (honesty):**
- Record only what people actually said. If nobody answers a question, the deck says "not yet validated". It never says what we *think* they'd say.
- Quote someone by name only with their permission. Otherwise write "a satellite-operations engineer at a LEO constellation operator".
- A "no", or "that price is too high", is a **useful result**. Judges respect "we learned X and changed Y".

**Safety (you're a minor emailing strangers):** use your **school email**, CC your DECA advisor on first contact, do calls on video in a school setting or with a parent or advisor aware, and never share your home address or phone number.

---

## 1. What we need to learn (the hypotheses)
These come straight from our assumption table and tornado chart (the biggest price movers come first).

| # | Hypothesis | Model value now | Who can confirm it | Question # |
|---|---|---|---|---|
| H1 | Truck hardware costs **$50–115M** | $80M base | ADR companies, thruster makers, aerospace profs | E3 |
| H2 | One deorbit kit costs **$0.5–3M** | $1.5M base | ADR companies, propulsion and kit makers | E3 |
| H3 | Operators with dead satellites would pay **~$10–20M per removal** | price ≈ $15.1M (cost $12.1M) | Operators (Product A) | C3, C4 |
| H4 | Agencies buy removal as a **service contract per object** | contracts $40–93M/object today | Agencies, ADR companies, policy experts | C5, E5 |
| H5 | Customers accept a **1–2 year** route if it's ~5× cheaper | time–price menu | Operators, agencies | C4 |
| H6 | Capturing *unprepared, tumbling* stages and attaching a kit is feasible with 10 days per stop | 10 days, 20 m/s | ADR engineers, GNC professors | E2 |
| H7 | 1.4-t SL-8 stages can re-enter **uncontrolled** within the 1-in-10,000 casualty limit | assumed OK | Re-entry and debris experts | E4 |
| H8 | Our route physics is credible (J2 drift, Edelbaum, SGP4 check, GTOC9 benchmark) | validated vs JPL ±2% | Astrodynamics professors | E1 |

## 2. Who to contact (strategy)
Verified names and official contact routes are in `research/contacts_academic.md` and `research/contacts_industry.md`.

1. **Professors and researchers who wrote the papers we build on** (Strathclyde, PoliMi, Glasgow, ESA ACT, NTU/Magdrive, LeoLabs...). They're the most likely to reply to a student who has read their work. **Highest response rate; contact these first.**
2. **ADR companies** (Astroscale, ClearSpace, Starfish, KMI, Turion, D-Orbit). Ask for engineering realism and cost ranges, not secrets. Expect polite, short answers.
3. **Satellite operators** (Iridium, Eutelsat OneWeb, Planet, Spire, Globalstar, ORBCOMM). These are the **actual customers** for Product A. Hardest to reach; aim for sustainability or space-safety staff.
4. **Insurers and space-safety groups** (AXA XL, Secure World Foundation, Space Data Association). They test the "who pays and why" story.
5. **Local option:** a professor at the nearest university aerospace or mechanical engineering department [__your state/university__]. An in-person 20 minutes is worth five emails.

**Volume math:** cold emails to experts typically get a minority of replies, so send ~25–30 emails to get ~5–8 conversations. Start **this week**; replies take 1–3 weeks. Follow up once after 7–10 days.

## 3. Email templates
Keep emails **short** (under 150 words), specific to *their* work, with one clear small ask. Fill every [__].

### A. To a researcher whose paper you used
> **Subject:** High-school student using your [__paper short title__]: 3 quick questions?
>
> Dear Professor [__Last name__],
>
> I'm a high-school [__grade__] at [__School__] building a DECA business plan around multi-target debris removal. Your paper [__title, year__] was central to my work: I built a Python model of J2-drift transfers, checked it against JPL's GTOC9 legs (within ~2% overall), and applied it to today's SL-8 rocket-body cluster.
>
> Would you be willing to answer three short questions by email, or join a 15-minute video call in the next few weeks? I've attached a one-page summary of the project.
>
> Thank you for your time,
> [__Your full name__] · [__School__], [__City, State__]
> DECA advisor: [__Name, email__] (cc'd)

### B. To an ADR company or industry engineer
> **Subject:** Student project on per-removal pricing: 15 minutes of reality-checking?
>
> Hello [__Name or "Business Development team"__],
>
> I'm a high-school student at [__School__] preparing a DECA Innovation Plan about pricing debris removal per object when one servicer visits ~10 targets. My cost model has two big unknowns: servicer hardware cost and deorbit-kit cost. I'd be grateful for a 15-minute call, or a reply to two questions, to check whether my ranges are realistic. Ballpark answers are fine, and I won't quote you without permission.
>
> One-page summary attached. Thank you!
> [__Name__] · [__School__] · advisor [__Name, email__] (cc)

### C. To a satellite operator (customer discovery)
> **Subject:** How do you plan for satellites that can't deorbit themselves?
>
> Hello [__Name/team__],
>
> I'm a high-school student researching end-of-life options for LEO operators under the FCC's five-year disposal rule (now Part 100, with a 0.9 disposal-success requirement). I'm trying to understand how operators think about satellites that fail before they can deorbit: how often it happens, and what a removal service would need to cost to be worth considering.
>
> Could I ask you 4–5 questions in a 15-minute call or by email? Your answers would stay anonymous unless you say otherwise.
>
> Thank you,
> [__Name__] · [__School__] · advisor [__Name, email__] (cc)

### D. Follow-up (send once, 7–10 days later)
> Hi [__Name__], just following up on my note below in case it got buried. Even a two-line reply to question 1 would help a lot. Thank you! [__Name__]

### E. Thank-you (same day as the interview)
> Thank you for your time today. The point about [__specific thing they said__] changes how I'm modelling [__X__]. May I quote you by name in my presentation as "[__exact quote__]"? If you'd prefer, I'll keep it anonymous.

## 4. Interview guides (choose 5–8 questions; 15–20 minutes)

### Customer guide (operators and agencies): Products A and B
- **C1.** Walk me through what happens today when one of your satellites fails before it can deorbit itself. Who decides what to do, and does anything happen? *(listen for: frequency, owner, current cost of "doing nothing")*
- **C2.** How much do dead objects in your orbits cost you today: conjunction warnings, avoidance manoeuvres, insurance, regulatory paperwork? *(tests the pain; NASA OTPS estimates per-manoeuvre labour at $462–769)*
- **C3.** If a service could remove one of your dead satellites, what price would make it a clear yes? A maybe? A no? *(write all three numbers down; don't suggest ours first)*
- **C4.** Would you accept waiting 12–24 months for removal if it cost about a fifth of a one-off mission? What's the longest acceptable wait? *(tests the time–price menu, H5)*
- **C5.** How would you want to buy it: a per-object fee, a subscription, an insurance-style bond, or a government contract? Who signs off?
- **C6.** What would worry you most: liability if something goes wrong, damage to an active satellite, re-entry risk, data sharing?
- **C7.** Which regulations or requirements (FCC Part 100, 0.9 disposal success, ESA Zero Debris) most affect your end-of-life planning?
- **C8.** Who else should I talk to?  *(always ask this one)*

### Expert guide (researchers and engineers)
- **E1.** I modelled transfers with secular J2 drift plus Edelbaum spirals, matched JPL's GTOC9 legs within about 2%, and checked plane errors with SGP4 (0.07° at 960 km; drag matters at 750 km). What's the biggest thing this simplified model would get wrong in a real mission?
- **E2.** Is 10 days per stop and a ~20 m/s approach allowance realistic for capturing an *unprepared, tumbling* SL-8 stage and attaching a kit? What would you assume?
- **E3.** For a ~600 kg electric servicer with a capture arm, is $50–115M a reasonable hardware range? And for a small solid-motor deorbit kit, is $0.5–3M per unit plausible at production volume?
- **E4.** Would an uncontrolled re-entry of a 1.4-tonne SL-8 stage meet a 1-in-10,000 casualty limit, or would it need a controlled re-entry?
- **E5.** Who do you think will actually pay for removing abandoned Soviet-era rocket bodies?
- **E6.** Is the "reusable truck plus kit pods" idea used or rejected anywhere you know of? Why?
- **E7.** Who else should I talk to?

**Technique:** ask about *their past and present* ("what happens today...") before any hypothetical ("would you..."). Don't pitch; listen. Record numbers exactly as said.

## 5. Interview log (copy once per interview)
```
Date / format (call, email):
Person + role + organisation:            Quote permission: yes / anonymous / no
Category: operator / agency / ADR company / researcher / insurer / other
Hypotheses touched: H1 H2 H3 H4 H5 H6 H7 H8
Key answers (verbatim where possible):
 -
Numbers they gave (with units and context):
 -
Surprises / what changes in our model:
 -
Referrals (who else to contact):
 -
Follow-up sent? (date)
```

## 6. Turning results into the deck (no fabrication)
- One "What we heard" slide: number of interviews by category, 3–4 short quotes (with permission), and **"what we changed"** arrows (e.g. "kit cost assumption $1.5M → $X after 3 engineers' ranges").
- Appendix: the questionnaire, the email you sent, and the anonymised interview log table.
- Re-run `engine/ocmath/economics.py` with any new numbers. Every chart updates automatically.

## Tracker
`research/outreach_tracker.csv`: one row per contact (name, organisation, category, route, date sent, follow-up date, status, hypotheses, notes). Open it in Excel or Google Sheets.
