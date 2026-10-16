# Step 4: The Math, Layer by Layer (with results)

Every number in this file was produced by the code in `engine/` on 16 Oct 2026. Re-run instructions are in `README.md`.
**Simulated vs. real:** the orbits and catalogue are real (CelesTrak, 16 Oct 2026). The missions are simulated plans. Every price uses the assumptions listed in Layer 8.

---

## Layer 1: Orbital elements from public data
**For judges:** *"Every tracked object has a public address. We decode it into six numbers describing its orbit."*

- Source: CelesTrak GP data (TLEs) for 19,000+ objects, decoded with the official SGP4 library (`sgp4` 2.27). Object type and status come from CelesTrak SATCAT. Mass comes from McDowell's GCAT.
- Elements: semi-major axis *a* (size), eccentricity *e* (roundness), inclination *i* (tilt), RAAN Ω (which way the plane faces), argument of perigee ω, and mean anomaly *M*.
- Code: `ocmath/catalog.py`.

**Result: truck-friendly clusters found in the 2026 catalogue** (`results/clusters_2026.json`). They match McKnight et al.'s published cluster counts.

| Cluster | Objects | Typical mass | Plane drift | Planes spread over |
|---|---|---|---|---|
| SL-16 stages, 71°, ~845 km | 18 | 9,000 kg | −2.11°/day | 317° |
| **SL-8 stages, 83°, ~960 km** | **142** | 1,434 kg | −0.75°/day | 356° |
| SL-8 stages, 74°, ~750 km | 50 | 1,434 kg | −1.85°/day | 356° |
| SL-8 stages, 74°, ~1,500 km | 45 | 1,434 kg | −1.30°/day | 355° |
| **Dead 1st-gen Iridium, 86.4°** | **24** | 662 kg | −0.45°/day | 358° |
| Rocket bodies, sun-synchronous band | 173 | ~1,000 kg | +0.74 to +1.19°/day | 359° |

## Layer 2: J2 nodal precession (the conveyor belt)
**For judges:** *"Earth's bulge slowly twists every orbit. How fast depends on height and tilt, so a different parking lane means a different twist speed."*

dΩ/dt = −(3/2) · n · J2 · (R_E / p)² · cos i,  n = √(μ/a³),  p = a(1 − e²)

- Checks: a sun-synchronous orbit at 800 km comes out at 0.985°/day (true value 0.9856). The ISS orbit comes out at −4.95°/day.
- Sensitivities: dΩ̇/da = −3.5 Ω̇/a (higher orbit means slower twist) and dΩ̇/di = −Ω̇ tan i (tilt matters even more near the poles).
- **Upgrade found during validation:** the textbook formula ignores second-order (J2²) and J4 terms. They're only about 0.15% of the rate, but over 1,000+ days they add up to about 1° of error. For real-catalogue work we add a correction table built from SGP4's own internal rates (`set_rate_model("sgp4")`). It matches SGP4 to 5 digits. GTOC9 work keeps the pure J2 formula, because that is what its rules define.
- Code: `ocmath/j2.py`. Chart: `figures/*/02_drift_rates`.

## Layer 3: Transfer costs
**For judges:** *"Changing altitude is cheap. Twisting a plane is brutally expensive: 10° costs 1.3 km/s, roughly what it takes to land a spacecraft from orbit."*

- Plane angle between two orbits (spherical trig): cos θ = cos i₁ cos i₂ + sin i₁ sin i₂ cos ΔΩ
- Chemical (impulsive): Δv = √(v₁² + v₂² − 2v₁v₂ cos θ)
- Electric (Edelbaum 1961, low thrust): Δv = √(v₁² + v₂² − 2v₁v₂ cos(πθ/2))
- Same shape, so the comparison is easy to explain. With θ = 0, both reduce to a small altitude change (checked against an exact Hohmann transfer: 52.45 m/s both ways for 700 → 800 km).
- Code: `ocmath/transfers.py`.

## Layer 4: Rocket equation (Δv to kilograms)
m_final = m_initial · e^(−Δv / (Isp · g₀))

- Electric truck (sourced): 2× Busek BHT-1500, 0.202 N total, **Isp 1,710 s**. Chemical comparison: Isp 320 s [ASSUMPTION, typical bipropellant].
- **Key insight (Chart 3):** the electric truck needs *more* Δv (slow spirals are less efficient) but burns about **5× less propellant mass**. For a 19° plane gap: brute force now costs **1,094 kg** of a 2,000 kg truck; electric drifting for a year costs about **19 kg**.
- Deorbit kits (`ocmath/kits.py`): one burn lowers the perigee to 250 km (uncontrolled re-entry within months), or to 50 km (controlled re-entry) for very heavy objects. SL-8 kit ≈ 130 kg, Iridium kit ≈ 53 kg, SL-16 kit ≈ 870 kg. **That is why SL-16s are not truck-friendly.**

## Layer 5: Wait vs. burn, one leg
**For judges:** *"We don't chase the junk; we park in a different lane and let Earth bring its orbit to us."*

Leg timeline: spiral out to the drift orbit → drift for time τ → spiral in → ride along with the target.

τ is solved in closed form so that the plane gap closes exactly:

 G(τ) = C + τ(Ω̇_B − Ω̇_d) = 0 (mod 360°),  C = gap₀ + spiral corrections

This is the classic "wait time" dt = ΔΩ / |Ω̇₁ − Ω̇₂|, extended to include spiral time. If the gap can't close in time, the leftover angle is paid for with a plane change. The drift orbit's altitude (600–1,500 km; we stay above the crowded sub-600 km shells) and tilt (±3°) are searched on a grid.

- **Bug found and fixed:** the first version coasted for the whole leg and depended on grid luck (about 11° of error on long near-polar legs). The closed-form τ removed that problem.
- Code: `ocmath/legs.py`.

## Layer 6: Sequencing (which objects, in what order)
**For judges:** *"10 stops have 3.6 million possible orders, and choosing 10 of the 142 SL-8 stages has 2.4 × 10²¹ ordered options. Every option changes as orbits drift. We use four nature- and logistics-inspired search methods and let them compete."*

| Problem | Possible orders |
|---|---|
| Order 10 fixed objects | 10! = 3,628,800 |
| Order 20 fixed objects | 20! ≈ 2.4 × 10¹⁸ |
| Pick + order 10 of 24 dead Iridiums | ≈ 7.1 × 10¹² |
| Pick + order 10 of 142 SL-8 stages | ≈ 2.4 × 10²¹ |

The methods are beam search, simulated annealing (with "swap in an unused object" moves, so it chooses *which* objects too), a genetic algorithm, and ant colony. A **dynamic-programming timer** then picks every leg's wait time *jointly* (it can accept a pricier hop now if that sets up cheaper hops later). Code: `ocmath/sequencing.py`.

### Benchmark against the 2017 world champions (GTOC9, JPL)
1. **Physics check, all 113 legs of JPL's winning route** (same endpoints, dates and travel times): our model totals **24,574 m/s vs JPL's 25,136 m/s (−2.2%)**, with per-leg correlation **r = 0.99**. JPL's launch masses are rebuilt to within 0.3 kg. Doing the same legs *without* waiting for drift costs **2.0× the fuel**. Chart: `04_benchmark_jpl`.
2. **Optimiser check, GTOC9 Mission 10** (10 objects; all routes scored by our model):

| Method | Launch mass |
|---|---|
| JPL's route (our model) | 3,478.6 kg |
| JPL's order + our DP timer | 3,380.5 kg |
| **Beam search + annealing, from scratch** | **3,387.7 kg** |
| Simulated annealing / genetic algorithm | 3,602.5 kg |
| Ant colony | 3,908.4 kg |
| Beam search alone | 4,040.8 kg |

**Honest reading:** our hybrid optimiser independently finds a route as good as JPL's order *in our model*. It does **not** prove we beat JPL, because our model is about 2% optimistic. No single method wins: beam search finds good neighbourhoods and annealing polishes them.

## Layer 7: Validation with better physics
**For judges:** *"We re-checked every meeting point with SGP4, the official propagator for these catalogue entries (it includes air drag), and flew the drift orbits through a full numerical simulation."*

| Route | Target plane error at meeting (median / max) | Extra Δv to correct each drift leg (median / max) |
|---|---|---|
| SL-8 83°, ~960 km | **0.06° / 0.08°** | **2.6 / 10.4 m/s** |
| Dead Iridium, ~780 km | 0.18° / 0.40° | 7.9 / 17.0 m/s |
| SL-8 74°, ~750 km | 0.74–0.89° / 0.97° | 60 / 87 m/s |

The 20 m/s per-stop approach allowance plus a 10% fuel margin covers the first two routes. **The 750 km cluster shows the effect of air drag** (our planner has no drag). Missions there must re-plan each leg with fresh tracking data, which is standard operational practice. Code: `scripts/validate_sgp4.py` (SGP4 + an RK8 integrator with J2/J3/J4 gravity).

## Layer 8: Economics
**For judges:** *"The truck, the launch and the team are big fixed costs. Ten stops split them ten ways."*

### 2026 mission results (launch 1 Jan 2029, 10 stops each, planned with the economic price of time)
The planner minimises Δv + λ·days, where λ comes from the cost model (one day of operations vs. the propellant and launch cost of 1 m/s): λ ≈ 11 m/s/day electric, ≈ 2.7 chemical. This made the SL-8 route 2.4× faster (525 → 220 days) **and** cheaper.

| Route | Engine | Δv | Propellant | Kits | Launch mass | Days |
|---|---|---|---|---|---|---|
| SL-8 83° (Product B) | electric | 678 m/s | 56 kg | 1,327 kg | 1,982 kg | 220 |
| | chemical | 574 m/s | 277 kg | 1,327 kg | 2,203 kg | 195 |
| Dead Iridium (Product A) | electric | 3,937 m/s | 225 kg | 526 kg | 1,351 kg | 555 |
| | chemical | 2,290 m/s | 936 kg | 526 kg | 2,062 kg | 480 |

### Price per removal (base assumptions)
- **10-stop electric truck, SL-8 cluster: $12.1M per removal** (uncertainty P10–P90: $11.0M–$15.2M from a 20,000-run Monte Carlo). At a 20% margin, the price is about $15.1M.
- Same cost model, one mission per object: **$96.2M** (8× more).
- Public single-object contracts: ClearSpace-1 ≈ $93M, ADRAS-J2 ≈ $82M, NASA's ELSA-M estimate ≈ $60M, UK/ClearSpace 2026 ≈ $40M per object.
- Stops per truck: 3 → $33M, 5 → $21M, 10 → $12.1M, 15 → $9.8M, 20 → $8.3M per removal (Chart 7).
- **Reusable truck, restocked with kit pods:** about **$4.4M per removal** after 100 removals over about 8 years (Chart 10).

### What the numbers really say (important for Q&A)
1. **The business lever is stops per truck plus reuse, not the engine.** Electric and chemical trucks cost within about 1–3% of each other per removal in the dense SL-8 cluster, because the truck hardware, kits and operations dominate (tornado, Chart 8).
2. **Why electric anyway:** one xenon load lasts about 10 routes (about 320 kg total; thrusters rated for about 17 routes). A chemical truck needs about 200 kg of propellant **transferred in orbit every route**, which nobody does routinely yet. Electric also handles spread-out targets (Iridium) without the launch mass ballooning.
3. **Fuel is nearly free; time is not.** Faster routes are often *cheaper* because the operations team costs about $5M/yr (Chart 6).
4. The two biggest uncertainties are **truck hardware cost** and **kit unit cost**. Those are the first things to ask about in customer and expert interviews.

### Assumption table (sources in `research/economics_inputs.md`)

| Parameter | Low / Base / High | Status |
|---|---|---|
| Truck hardware | $50M / $80M / $115M | Low and high **sourced** (NASA OTPS 2023); base [ASSUMPTION] |
| Deorbit kit unit cost | $0.5M / $1.5M / $3M | **[ASSUMPTION]**, needs validation |
| Launch price | $7,000 / $7,500 / $15,000 per kg | **sourced** (SpaceX rideshare API; NASA OTPS) |
| Xenon | $2,780 / $2,780 / $12,000 per kg | **sourced** (analyst, industry) |
| Operations | $3M / $5M / $10M per year | **[ASSUMPTION]** |
| Insurance | 5% / 8% / 12% of hardware + launch | **[ASSUMPTION]** |
| Fuel margin | 10% / 10% / 25% | Engineering choice, justified by Layers 6–7 |
| Truck dry mass | 600 kg | **[ASSUMPTION]** |
| Stay per object / approach Δv | 10 days / 20 m/s | **[ASSUMPTION]** |
| Kit motor Isp / inert mass | 285 s / 12 kg + 15% | **[ASSUMPTION]** |
| Kit pod carrier | 150 kg, $4M | **[ASSUMPTION]** |
| EUR → USD | 1.08 | **[ASSUMPTION]** |

## Limitations (also in the paper)
- Circular-orbit, secular dynamics. Along-track phasing and proximity operations are an allowance, not simulated.
- No drag in the planner, which matters below about 800 km (see Layer 7).
- Capturing a tumbling, unprepared rocket stage is the hardest engineering step. We don't model it; Astroscale's ADRAS-J2 will be the first real test (2027–28).
- Casualty risk: uncontrolled re-entry of 1.4-tonne SL-8 stages must be shown to meet the 1-in-10,000 limit, object by object.
- Costs are estimates. The biggest unknowns (truck and kit cost) are flagged for interviews.
- Every cost figure is a model output, not a quote.
