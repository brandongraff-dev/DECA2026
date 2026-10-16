# Step 2: Company Names + Taglines

Checks done on 16 Oct 2026: a quick web search for an existing space company with the name, plus a GoDaddy domain lookup. **These are not trademark searches.** Before you print anything, search USPTO (tmsearch.uspto.gov) for your final pick.

| # | Name | Tagline | Conflict search | Domain |
|---|---|---|---|---|
| 1 | **Orbital Curbside** | "Curbside pickup for dead satellites." | None found | orbitalcurbside.com available |
| 2 | **Gyre Orbital** | "Ride the drift. Clear the orbit." (Ocean gyres are where garbage patches collect, a double meaning.) | None found | gyreorbital.com available |
| 3 | **HaloHaul** | "Ten pickups. One launch." | None as a company; "Halo" is also a NASA Gateway module and a Microsoft game brand | halohaul.com available |
| 4 | **Slowburn Space** | "Patience is a propellant." (Fits the electric engine: a slow, gentle burn.) | Common phrase, many unrelated brands | slowburn.space taken |
| 5 | **NodalHaul** | "Hauling junk on Earth's schedule." | None found | nodalhaul.com available |
| 6 | **Sweepline** | "One sweep. Ten satellites." | None in space; it's also a geometry-algorithm term | sweepline.space available |
| 7 | **JunkBelt** | "Earth's own conveyor belt for space junk." | None found | junkbelt.com available |
| 8 | **Driftline** | "We don't chase junk. We wait for it." | Many unrelated Driftline brands (racing, marine) | driftline.space taken |
| 9 | **Tidewater Orbital** | "Ride the tide. Clear the sky." | Tidewater Inc. is a real NYSE marine company; possible confusion | tidewaterorbital.com available |
| 10 | **Precession Labs** | "Patience is a propellant." | No company found, but the .com is registered | precessionlabs.com taken |

**My top three:**
- **Orbital Curbside.** A business judge understands it in one second.
- **Gyre Orbital.** The most "real startup" sounding, with a hidden meaning to explain in the pitch.
- **HaloHaul.** The punchiest.

"Patience is a propellant." is strong enough to use as the tagline with any of them.

---

# Step 3: Project Plan

## What we are claiming (keep this sentence honest everywhere)
> "The physics of riding Earth's J2 drift is known; researchers proved it in competitions and papers (GTOC9 2017, Di Carlo 2017, Iskender 2026). Nobody has turned it into a **price list**. We built the first public quote engine that prices an **electric-propulsion drift truck** against today's single-object missions, on the **2026 catalog**, for two kinds of customers."

## Stages

| Stage | Output | Depends on | Est. effort |
|---|---|---|---|
| 0. Prior work | `01_prior_work.md` ✅ | – | done |
| 1. Brand | Name, tagline, palette, logo direction | your pick | 1 session |
| 2. Data | GTOC9 set; 2026 TLE snapshot; object type and size info; McKnight top-50 list | **your downloads** (CelesTrak is blocked here) | 1 session |
| 3. Math engine | Python package: elements → J2 drift → chemical and electric (Edelbaum) transfer costs → wait-vs-burn optimizer → sequencers (beam / SA / GA / ACO) → SGP4 check → economics → Pareto | 2 | 3–5 sessions |
| 4. Benchmarks | Chemical model vs JPL GTOC9 (how close do we get?); EP model vs Di Carlo 2017 legs | 3 | 1–2 sessions |
| 5. Customer validation | Contact list, email template, interview questions (**start early: replies take weeks**) | 1 | 1 session; then your interviews |
| 6. Simulation | Cesium + satellite.js artifact → wired to route JSON → offline bundle → 60-s recording plan → QR | 3 | 3–4 sessions |
| 7. Paper | 6–10 pages + 1-page plain summary, figures from stages 3–4 | 3, 4 | 2 sessions |
| 8. Deck | 20 slides, notes, 30-s hook, Q&A sheet | all | 2–3 sessions |
| 9. Audit | Rubric check + placeholder checklist | all | 1 session |

## Task list (math engine detail)
1. `elements.py`: parse TLEs → a, e, i, RAAN, ω, M; classify (payload / rocket body / debris).
2. `j2.py`: RAAN-rate function + drift-rate charts vs altitude and inclination.
3. `transfers.py`: Hohmann; combined plane change via spherical trig; **Edelbaum low-thrust** (Δv and time for a given thrust/mass); drift-leg model (park at Δa, wait, return).
4. `rocket.py`: Tsiolkovsky for chemical (Isp ≈ 300–340 s) and EP (Isp ≈ 1,500–3,000 s, labeled assumptions).
5. `leg_optimizer.py`: for each pair (A→B, start time) find the cheapest parking altitude and wait time, under a time budget.
6. `sequencer.py`: beam search, simulated annealing, genetic algorithm, ant colony; the same cost model feeds all four; a search-space-size table.
7. `validate_sgp4.py`: re-propagate the best routes with SGP4 and report RAAN and altitude errors at each rendezvous.
8. `economics.py`: truck cost + launch + ops + propellant → price per removal; single-target baseline anchored to real contracts (UK/ClearSpace); Pareto of mission days vs $/object; sensitivity ("tornado") chart.
9. `export_route.py`: JSON for the simulation.

## Timeline
This depends on your first competition date. Tell me the date and I'll pin each stage to a calendar week. Default if you don't know yet: everything done 3 weeks before districts, leaving 3 weeks to rehearse.
