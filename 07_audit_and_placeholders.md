# Step 9: DECA rubric audit and placeholder checklist

Audited 16 Oct 2026 against the official **DECA Guide 2026–27, Innovation Plan (EIP)** pages 74–77:
- Pitch Deck Guidelines
- Presentation Guidelines
- Presentation Evaluation Form

Source PDF: https://cdn.prod.website-files.com/635c470cc81318fc3e9c1e0e/6a3c727b824720be717aa59f_HS_EIP_Guidelines.pdf

> **Not audited:** the **Penalty Point Checklist** (DECA Guide p. 60) was not in that PDF. Get it from your advisor and check the deck against it before submitting.

Deck: Slides artifact https://claude.ai/artifact/6f8NpoMRLD1zp9vsZ6h4Kf. It is private until you share it from the Share menu. A copy of the source is in `deck/` in the repo.

---

## A. Pitch deck format check

| Rule (DECA Guide) | Status | Where |
|---|---|---|
| Max 20 slides **including** appendix | ✅ exactly 20 | deck |
| Cover slide first; it need not be numbered "1" | ✅ unnumbered | slide 1 |
| Title slide numbered "2": "Innovation Plan", school name, school address, city/state/ZIP, participant names, date | ⚠️ "Innovation Plan" ✅, participant name ✅; **school name, address, city/state/ZIP, date are placeholders** | slide 2 |
| Table of contents follows, one slide, numbered "3" | ✅ | slide 3 |
| Body starts with I. Overview, numbered "4", in order I–VIII | ✅ I (4), II (5–7), III (8–10), IV (11–12), V (13–17), VI (18), VII (19), VIII (20) | deck |
| Every section titled, incl. bibliography and appendix | ✅ each slide has a section eyebrow ("III · Customer Segments") | all |
| Bibliography required | ✅ 24 sources, full list with links in paper | slide 19 |
| Numbering continues through bibliography and appendix | ✅ 19, 20 | – |
| Statement of Assurances and Academic Integrity: signed, submitted **separately**, not numbered | ❌ **you must sign and submit it** | separate |
| Presentation ≤ 15 min **including** judge questions | ✅ script ≈ 10 min + ~1 min demo, leaving ~4 min for questions | `06_qa_prep_and_hook.md` |
| No power or internet supplied | ✅ demo runs fully offline; **charge the laptop**, bring the deck as a PDF on USB too | `offline/` |
| Visuals hand-carried, set up by you, set-up time counts | ⚠️ practise opening laptop, deck and demo in under 60 s | – |
| Items left with judges: flyers and brochures OK | ✅ the one-page summary is a good leave-behind | `onepager/` |

---

## B. Presentation Evaluation Form: honest self-assessment

These are my estimates of where the **materials** sit today, not a prediction of your score. Your delivery decides a lot of the Technique points.

| # | Criterion (pts) | Evidence in deck | Likely band now | Biggest gap → fix |
|---|---|---|---|---|
| 1 | **Overview** (15): idea, segments, problem, why it's worth pursuing, with evidence | Slide 4 (about, model, customers, value $12.1M vs $40–93M); hook on slide 1 | Proficient–Exemplary | Make sure the closing "why worth pursuing" line is said with conviction |
| 2 | **Business Opportunity** (15): root causes, scope, urgency, relevance | 5 (47k objects, Kessler, top-50 study), 6 (real contract prices), 7 (FCC 5-yr, 0.9 rule, market range) | Proficient–Exemplary | Root cause is said aloud (collisions outpace decay); keep it in |
| 3 | **Customer Segments** (15): needs, behaviours, challenges, why chosen | 8 (3-segment table), 9 (Iridium CEO quote, 24 dead sats), 10 (SL-8 cluster, consent issue) | **Developing–Proficient** | **No interview evidence yet.** This is the weakest criterion. Run the validation kit and add 1–2 real findings to slides 8–9 (and appendix: questionnaire/letters, which DECA explicitly suggests) |
| 4 | **Unique Value Proposition** (15): single, clear, differentiated, with comparisons | 11 (one-line UVP), 12 (side-by-side vs one-object missions) | Proficient–Exemplary | Be ready for "hasn't this been done?" (Q&A Q1); honesty here helps |
| 5 | **Solution** (15): key features → problem/UVP, feasibility | 13 (park/drift/hop/tag + chart), 14 (JPL & SGP4 checks), 15 (live demo), 16 (economics), 17 (risks + roadmap) | Exemplary on technical feasibility; business feasibility depends on unvalidated costs | Get even one expert reaction on truck or kit cost |
| 6 | **Organization** (5) | Official I–VIII order, TOC with page numbers, section eyebrows | 4–5 | – |
| 7 | **Persuasion** (5) | Clear problem → price gap → mechanism → proof → ask | 4 | A real customer signal would make it 5 |
| 8 | **Delivery** (5): interactive techniques (e.g. visual storytelling) | Live 3D demo, story arc "garbage truck", QR to try it | 4–5 if rehearsed | Rehearse the demo hand-off; keep it ≤ 60 s |
| 9 | **Presentation Design** (5) | Consistent brand, real charts and sim images, large type | 4–5 | Fill title-slide placeholders and headshot |
| 10 | **Overall Impression** (5): professionalism, poise | – | depends on you | Business attire, eye contact, timed practice ×3 |

**Single highest-value action:** customer and expert interviews (Step 7 kit). They strengthen criteria 3, 5 and 7, and give you true answers for Q&A Q4.

---

## C. Placeholder checklist (fill all before competition)

### Deck (Slides artifact; source in `deck/project/slides/`)
| Placeholder | Slide | Notes |
|---|---|---|
| `[School name]` | 2 Title | |
| `[Street address]` | 2 Title | school address |
| `[City, State ZIP]` | 2 Title | |
| `[Presentation date]` | 2 Title | competition date (TBD) |
| `[headshot]` | 2 Title | upload a photo, or delete the circle |
| `[$__]` pre-seed ask | 18 Conclusion (slide text **and** script) | decide with your advisor; see Q&A Q20 |
| QR code on slide 18 | 18 | points to the sim artifact, already shared as “anyone with the link”. Re-check it opens on a phone |

### Paper and one-pager
| Placeholder | File |
|---|---|
| `[__School__]` (×2) | `paper/paper_numbers.json` → `SCHOOL`; rebuild with `.venv/bin/python paper/build_paper.py` |
| `[__School__]`, `[__school email__]` | `onepager/onepager.html`; re-export PDF |

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
| `[$__]` | the ask amount |

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
7. **The 24 dead first-generation Iridium satellites still in orbit**: some may re-enter. Re-run `engine/scripts/catalog_2026.py` to refresh.

---

## E. Before you submit or present

- [ ] Fill every placeholder in section C. Run `grep -rn "\[__\|\[\$__" .` to find leftovers.
- [ ] Sign the Statement of Assurances and Academic Integrity (separate document).
- [ ] Check the deck against the Penalty Point Checklist (DECA Guide p. 60; get it from your advisor).
- [ ] Export the deck to PDF and keep a copy on a USB stick (download from the Slides artifact).
- [ ] Test `offline/OrbitalCurbside-Demo/Start Demo.bat` on the competition laptop with Wi-Fi **off**.
- [ ] Scan the slide-18 QR with a phone to confirm the demo link opens (it is shared as “anyone with the link”).
- [ ] Rehearse three times with a timer: hook ≤ 35 s, pitch ≈ 11 min.
- [ ] Print 2–3 copies of the one-page summary to leave with judges.
- [ ] Consider making the GitHub repo **private** until after competition if you don't want others to see it early. It's public now, and the paper's byline links to it.
