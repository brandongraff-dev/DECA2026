# Step 9: DECA rubric audit and placeholder checklist

Audited 16 Oct 2026 against the official **DECA Guide 2026–27, Innovation Plan (EIP)** pages 74–77:
- Pitch Deck Guidelines
- Presentation Guidelines
- Presentation Evaluation Form

Source PDF: https://cdn.prod.website-files.com/635c470cc81318fc3e9c1e0e/6a3c727b824720be717aa59f_HS_EIP_Guidelines.pdf

Re-checked 6 Nov 2026 after the redesign, including the **Penalty Point Checklist** (DECA Guide 2026–27 p. 60: https://cdn.prod.website-files.com/635c470cc81318fc3e9c1e0e/6a3c6ee3d2b16972cb29b095_HS_PenaltyPointChecklist.pdf).

Deck source is now `deck/slides/*.html` (rebuild with `node deck/build_deck.js`). The old Slides artifact (https://claude.ai/artifact/6f8NpoMRLD1zp9vsZ6h4Kf) is the previous design and is out of date.

### Penalty Point Checklist: pitch deck
| Item (points) | Status |
|---|---|
| Statement of Assurances signed by participant **and** advisor, turned in with the deck; typed names not accepted (15) | ❌ **you must hand-sign it** |
| Limited to 20 slides (5 per extra slide) | ✅ 20, cover included |
| Slides numbered in sequence from the title slide to the last appendix slide (5) | ✅ cover unnumbered, title = 2 … appendix = 20 |
| Follows the Pitch Deck Guidelines outline (5) | ✅ I–VIII in order |
| Typed, 16:9; no handwritten corrections (5) | ✅ PDF is 1920×1080 (16:9), fonts embedded |

### Video, animation and the laptop
- The 2026–27 Presentation Guidelines allow your own equipment and sound: "Participants must furnish their own materials and equipment. No electrical power or internet connection will be supplied… Sound may be used, as long as the volume is kept at a conversational level." Set-up counts toward the 15 minutes. No penalty item mentions video.
- The deck is **uploaded as a PDF** (DECA Direct, Nov 2025: "videos may be embedded" but "will be converted to a PDF"), so slide 15 shows a still in the PDF. In the room, present from `deck/OrbitalCurbside_deck.html`, which plays `assets/demo_pickup.mp4` with no internet. You may present a different file from the one you uploaded ("Members may use any of the visual aids that meet the criteria").
- Laptop on **battery**: charge it fully. The clip is muted; you talk over it.

---

## A. Pitch deck format check

| Rule (DECA Guide) | Status | Where |
|---|---|---|
| Max 20 slides **including** appendix | ✅ exactly 20 | deck |
| Cover slide first; it need not be numbered "1" | ✅ unnumbered | slide 1 |
| Title slide numbered "2": "Innovation Plan", school name, school address, city/state/ZIP, participant names, date | ⚠️ "Innovation Plan" ✅, participant name ✅; **school name, address, city/state/ZIP, date are placeholders** | slide 2 |
| Table of contents follows, one slide, numbered "3" | ✅ | slide 3 |
| Body starts with I. Overview, numbered "4", in order I–VIII | ✅ I (4), II (5–7), III (8–9), IV (10–11), V (12–17), VI (18), VII (19), VIII (20) | deck |
| Every section titled, incl. bibliography and appendix | ✅ each slide has a section eyebrow ("III · Customer Segments") | all |
| Bibliography required | ✅ 24 entries (incl. CelesTrak collision page, NASA debris newsletter, NASA imagery credit); full list with links in paper | slide 19 |
| Numbering continues through bibliography and appendix | ✅ 19, 20 | – |
| Statement of Assurances and Academic Integrity: signed, submitted **separately**, not numbered | ❌ **you must sign and submit it** | separate |
| Presentation ≤ 15 min **including** judge questions | ⚠️ script ≈ 10½ min + ~1 min demo, leaving ~3½ min for questions. Tight: time your rehearsals | `06_qa_prep_and_hook.md` |
| No power or internet supplied | ✅ demo runs fully offline; **charge the laptop**, bring the deck as a PDF on USB too | `offline/` |
| Visuals hand-carried, set up by you, set-up time counts | ⚠️ practise opening laptop, deck and demo in under 60 s | – |
| Items left with judges: flyers and brochures OK | ✅ the one-page summary is a good leave-behind | `onepager/` |

---

## B. Presentation Evaluation Form: honest self-assessment

These are my estimates of where the **materials** sit today, not a prediction of your score. Your delivery decides a lot of the Technique points.

| # | Criterion (pts) | Evidence in deck | Likely band now | Biggest gap → fix |
|---|---|---|---|---|
| 1 | **Overview** (15): idea, segments, problem, why it's worth pursuing, with evidence | Slide 4: the non-obvious question ("Everyone asks how to grab junk; we asked why every piece needs its own rocket"), problem, fix, who pays, price ($12.2M vs $40–93M) | Proficient–Exemplary | Say the closing "why worth pursuing" line with conviction |
| 2 | **Business Opportunity** (15): root causes, scope, urgency, relevance | 5 (47k objects, 31k junk bar, why it matters to you: maps/weather/internet, ISS dodged 41×), 6 (47,000 → ~500 big derelicts → worst 50 ≈ half the risk; ~5 removals a year needed vs **0 so far**), 7 (**root cause named: the one-rocket-per-piece business model**; contract prices; **why now**: FCC 5-year and 1-in-10 rules, market range) | Proficient–Exemplary | Slide 6 answers "why not remove everything?"; know Q&A Q2b and Q2c cold |
| 3 | **Customer Segments** (15): needs, behaviours, challenges, why chosen | 8 (3 segments: why they care, how they buy; Iridium CEO quote), 9 (first route: US/India/France stages, consent; SL-8 later) | **Developing–Proficient** | **No interview evidence yet.** This is the weakest criterion. Run the validation kit and add 1–2 real findings to slide 8 (and the appendix: questionnaire/letters, which DECA explicitly suggests) |
| 4 | **Unique Value Proposition** (15): single, clear, differentiated, with comparisons | 10 (one trip, ten pickups vs one mission per piece; the promise), 11 ("We let Earth bring it to us"; 1,094 kg vs 19 kg) | Proficient–Exemplary | Be ready for "hasn't this been done?" (Q&A Q1); honesty here helps |
| 5 | **Solution** (15): key features → problem/UVP, feasibility | 12 (four steps with renders), 13 (the truck and its mass), 14 (JPL & SGP4 checks), 15 (live demo), 16 (the money), 17 (risks + roadmap) | Exemplary on technical feasibility; business feasibility depends on unvalidated costs | Get even one expert reaction on truck or kit cost |
| 6 | **Organization** (5) | Official I–VIII order, TOC with page numbers, section eyebrows | 4–5 | – |
| 7 | **Persuasion** (5) | Plain-language story: problem → why it matters → price gap → our idea → proof → money → ask | 4 | A real customer signal would make it 5 |
| 8 | **Delivery** (5): interactive techniques (e.g. visual storytelling) | Live 3D demo, story arc "garbage truck", QR to try it | 4–5 if rehearsed | Rehearse the demo hand-off; keep it ≤ 60 s |
| 9 | **Presentation Design** (5) | Redesigned 6 Nov 2026: black/white with one alarm red that only marks danger, Schibsted Grotesk, full-sentence headlines, hairline rules instead of boxes, charts drawn with real numbers, real catalogue and 3D-model imagery, a video on slide 15 | 4–5 | Fill title-slide placeholders and headshot |
| 10 | **Overall Impression** (5): professionalism, poise | – | depends on you | Business attire, eye contact, timed practice ×3 |

**Single highest-value action:** customer and expert interviews (Step 7 kit). They strengthen criteria 3, 5 and 7, and give you true answers for Q&A Q4.

---

## C. Placeholder checklist (fill all before competition)

### Deck (source: `deck/slides/`; rebuild with `node deck/build_deck.js`)
| Placeholder | Slide | Notes |
|---|---|---|
| ~~`[School name]`~~ | 2 Title | ✅ Winter Park High School |
| ~~`[Street address]`~~ | 2 Title | ✅ 1331 College Point (confirm with your advisor) |
| `[ZIP]` | 2 Title | city and state filled (Winter Park, FL); **add the ZIP** |
| `[Presentation date]` | 2 Title | competition date (TBD) |
| ~~`[headshot]`~~ | 2 Title | ✅ `deck/assets/headshot.png` |
| ~~`[$__]` pre-seed ask~~ | 18 Conclusion | ✅ filled: **$250K** (slide, script, Q&A Q20/Q20b) |
| QR code on slide 18 | 18 | points to the sim artifact, already shared as “anyone with the link”. Re-check it opens on a phone |

### Paper and one-pager
| Placeholder | File |
|---|---|
| ~~`[__School__]` (×2)~~ | ✅ paper: Winter Park High School (PDF rebuilt) |
| `[__school email__]` | `onepager/onepager.html` (school name ✅ filled); add your school email and re-export the PDF |

### Validation kit (`04_validation_kit.md`)
| Placeholder | Meaning |
|---|---|
| `[__Your full name__]`, `[__School__]`, `[__City, State__]`, `[__grade__]`, `[__school email__]` | your details in email templates |
| `[__Name, email__]` | DECA advisor (cc on every email) |
| `[__Last name__]`, `[__Name__]`, `[__Name or "Business Development team"__]`, `[__Name/team__]` | recipient, per email |
| `[__paper short title__]`, `[__title, year__]` | the expert's paper you cite, per email |
| `[__your state/university__]` | local university for the student-friendly faculty template |
| `[__X__]`, `[__exact quote__]`, `[__specific thing they said__]` | **only real interview results**: never fill these with guesses |

### Q&A sheet (`06_qa_prep_and_hook.md`)
| Placeholder | Meaning |
|---|---|
| `[__number__]` | how many people you've contacted |
| `[__N__]`, `[__finding__]` | real interview counts/findings |
| ~~`[$__]`~~ | ✅ the ask: $250K |

### Unknown numbers (model assumptions to validate, not placeholders)
These numbers are **assumptions**, labelled as such in the paper and appendix. They are not facts.

| Assumption | Base value |
|---|---|
| Deorbit kit unit cost | $1.5M; no public price exists. **Ask experts** |
| Truck hardware | $80M, inside NASA's $50–115M range |
| Operations | $5M per year |
| Insurance | 8% |
| Profit margin | 20% |
| Truck dry mass | 600 kg |
| Stay per stop | 10 days |

---

## D. Facts to re-check the week of competition

These were correct on 16 Oct 2026 but can change:

1. **UK ADR contract** (~£61M, 2 satellites, announced 15 Oct 2026). Check the final contract value.
2. **ESA object counts** (≈47,000 tracked / ≈16,000 working). ESA updates DISCOSweb statistics regularly.
3. **ADRAS-J2 schedule** (capture demo ~2027–28).
4. **FCC Part 100 / FCC 26-47**: check the effective date and any petitions.
5. **SpaceX rideshare price** ($7,000/kg in 2026, $7,500/kg in 2027).
6. **Market report ranges** ($1.1–1.6B).
7. **Rocket Lab's purchase of Iridium** (announced 29 Jun 2026, ~$8B, closing expected mid-2027). Check whether it has closed.
8. **The 24 dead first-generation Iridium satellites still in orbit**: some may re-enter. Re-run `engine/scripts/catalog_2026.py` to refresh.
9. **ISS debris-avoidance count** (41 manoeuvres since 1999, NASA ODQN 29(3)). A newer issue may raise it.
10. **Launch prices and schedules**: SpaceX rideshare $/kg and the 831 kg port limit; Rocket Lab Neutron's first flight (slipped to 2027) and price ($50–55M); Falcon 9 list price ($74M).

---

## E. Before you submit or present

- [ ] Fill every placeholder in section C. Run `grep -rn "\[__\|\[\$__" .` to find leftovers.
- [ ] Sign the Statement of Assurances and Academic Integrity (separate document).
- [ ] After filling placeholders, rebuild (`node deck/build_deck.js --png /tmp/oc_png && python3 deck/make_pptx.py /tmp/oc_png`) and copy the whole `deck/` folder to a USB stick.
- [ ] Test `deck/OrbitalCurbside_deck.html` on the competition laptop with Wi-Fi **off**: open it, press F, step to slide 15 and check the video plays.
- [ ] Test `offline/OrbitalCurbside-Demo/Start Demo.bat` on the competition laptop with Wi-Fi **off**.
- [ ] Scan the slide-18 QR with a phone to confirm the demo link opens (it is shared as “anyone with the link”).
- [ ] Rehearse three times with a timer: hook ≤ 35 s, pitch ≈ 11 min.
- [ ] Print 2–3 copies of the one-page summary to leave with judges.
- [ ] Consider making the GitHub repo **private** until after competition if you don't want others to see it early. It's public now, and the paper's byline links to it.
