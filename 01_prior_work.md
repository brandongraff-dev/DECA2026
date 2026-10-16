# Step 1: Prior-Work Verification (checked 16 Oct 2026)

Status key: **VERIFIED** = read in a primary source. **SECONDARY** = reported by press or a third party, not yet checked against a primary source. **NOT READ** = exists, but full text not accessed.

---

## 1. GTOC9 "The Kessler Run" (2017): VERIFIED, and it is almost exactly our problem

- Run by ESA's Advanced Concepts Team. Fictional scenario set in 2060: plan debris-removal missions covering **123 debris objects in sun-synchronous orbits** after a Kessler-style cascade. The cost formula per mission = a base launch cost (which rises the later a mission is submitted) + a penalty that grows with spacecraft mass. [ESA GTOC portal](https://sophia.estec.esa.int/gtoc_portal/?p=814), [Kelvins problem page](https://kelvins.esa.int/gtoc9-kessler-run/problem/)
- **Winner: JPL** (Anastassios Petropoulos, Daniel Grebow et al.). It was JPL's 4th GTOC win. Their solution removes all 123 objects with **10 spacecraft over about 8 years**, total score **731.28 MEUR**. Methods: branch-and-bound exploiting natural nodal (RAAN) drift, beam search, ant colony optimization, and a genetic algorithm. [ESA article](https://www.esa.int/Enabling_Support/Space_Engineering_Technology/Rocket_scientists_challenge_do_the_Kessler_run), [JPL results on Zenodo](https://zenodo.org/records/1139152), [Petropoulos paper](https://human-competitive.org/sites/default/files/petropoulos-paper.pdf)
- Other published entries: NUDT 786.21 MEUR (12 missions), Tsinghua 829.58, Strathclyde 918.98, DLR 949.85 (figures as quoted in arXiv:2607.22974); Penn State ARGoPs, 20 missions. [ARGoPs paper](https://argops.psu.edu/files/2017/09/argops-gtoc-9-19ak7ih.pdf)
- The dataset is public on Kelvins, and this container can reach it. **We can use it as our benchmark.**

## 2. Closest recent work: the core idea is already published

**Iskender (NTU Singapore), Felicetti (Cranfield), Gokturk (ITU), Tellett & Baker (Magdrive Ltd), "Drift-Aware Multi-Target Space Tug Logistics Using Natural Orbital Precession," arXiv:2607.22974, 25 Jul 2026, presented at IAC 2026 (Antalya, 5–9 Oct 2026).** [arXiv](https://arxiv.org/abs/2607.22974)
- Same core idea as ours, nearly in the same words: "Rather than treating J2 as a disturbance to be cancelled, the drift-aware paradigm exploits nodal precession as a propulsive substitute."
- Uses the GTOC9 catalog and JPL's mission split. Optimizes target order (greedy + 2-opt), per-leg drift time (differential evolution), and the transfer type per leg (direct burn / natural wait / altitude-only drift orbit / 3-parameter drift orbit). Lands within about 1.5% of JPL's cost.
- **What it does NOT do** (our openings): no cost-per-removal or pricing model (it uses only the GTOC9 competition cost formula); no fleets (listed as future work); no depot; no collision-risk-based target selection; no current real catalog (GTOC9 plus synthetic cases only); no time-vs-cost Pareto front; impulsive burns only (low-thrust is listed as future work).
- **Watch out:** a companion business paper, "Space Postman and ATLAS: Enabling startup participation in the orbital logistics economy" (IAC-26,E6,1,10,x115070), packages this as a commercial mission-design platform plus a tug (Magdrive is a UK propulsion company). **NOT READ.** This is effectively a *competitor concept*, and our deck must acknowledge it.

Other sequencing work (all use J2 drift and treat the problem as a time-dependent traveling salesman problem):
- Izzo et al. (2015), "Evolving solutions to TSP variants for active space debris removal" (the GTOC9 organizers' own groundwork). NOT READ.
- "Optimization of Active Debris Removal Missions with Multiple Targets," J. Spacecraft & Rockets (ant colony). [AIAA](https://arc.aiaa.org/doi/abs/10.2514/1.A33883)
- NSGA-II multi-debris LEO planning, Adv. Space Res. 2024; it "naturally employs the RAAN drift originating from J2." [ScienceDirect](https://www.sciencedirect.com/science/article/abs/pii/S0273117724001285)

## 3. Risk-based target selection: already studied (so not new by itself)

- Barea, Urrutxua & Cadarso (2020): pick objects to **maximize total criticality (CSI index)** under delta-v and time budgets, then sequence them. [Acta Astronautica](https://www.sciencedirect.com/science/article/abs/pii/S0094576520300436)
- Borelli & Colombo (Politecnico di Milano), "Space debris index definition for multi-purpose ADR mission design," Adv. Space Res. vol. 77 (2026). Combines an environmental-impact index with feasibility in multi-objective optimization. [ScienceDirect](https://www.sciencedirect.com/science/article/pii/S0273117725014863)
- MIT Risk Index plus a genetic algorithm; Hazard Criticality Index plus random-key optimization (SECONDARY, via search summaries).
- McKnight (LeoLabs) et al., "50 statistically most concerning derelict objects in LEO," updated at IAC 2025. 88% are rocket bodies, and 34 of the 50 are Soviet/Russian. Removing all 50 cuts LEO risk by about half; removing the top 10 cuts it by about 30%. (SECONDARY: [SpaceNews/Ars coverage](https://threatbeat.com/threats/removing-these-50-objects-from-orbit-would-cut-danger-from-space-junk-in-half/); primary: [ESA SDC9 paper](https://conference.sdo.esoc.esa.int/proceedings/sdc9/paper/4/SDC9-paper4.pdf), NOT READ yet.)

## 4. Fleets and depots: partly studied

- Refueling-station and refuel-aware multi-debris planners (reinforcement learning, MCTS), arXiv Feb 2026: [2602.05075](https://arxiv.org/pdf/2602.05075), [2602.05091](https://arxiv.org/pdf/2602.05091), [2602.17685](https://arxiv.org/pdf/2602.17685).
- Multi-servicer planning (2017, particle swarm); auction/ant-colony coordination of multiple servicers (Stuart et al. 2016); "multispacecraft to multidebris" allocation ([Space journal](https://spj.science.org/doi/10.34133/space.0141)); GEO depot "revolver mode" (Zhao et al. 2021, [Wiley](https://onlinelibrary.wiley.com/doi/10.1155/2021/8284022)).
- No paper found that combines a J2-drift fleet + depot + economics, but the pieces exist.

## 5. Economics of multi-target removal: thin, but not empty

- Tuttle et al., AMOS 2023 poster: one servicer removing 10 objects costs roughly **3.25x less** than 10 dedicated servicers. [AMOS PDF](https://amostech.com/TechnicalPapers/2023/Poster/Tuttle.pdf). SECONDARY (search summary); must read before citing.
- "Cost Estimation for the Active Debris Removal of Multiple Priority Targets" (older, FY00 dollars). [ResearchGate](https://www.researchgate.net/publication/271526167_Cost_Estimation_for_the_Active_Debris_Removal_of_Multiple_Priority_Targets)
- NASA OTPS, "Cost and Benefit Analysis of Orbital Debris Remediation" (Mar 2023). [PDF](https://www.nasa.gov/wp-content/uploads/2023/03/otps_-_cost_and_benefit_analysis_of_orbital_debris_remediation_-_final.pdf). Key numbers still to extract.

## 6. Industry and competitors (status as of Oct 2026)

| Company | What | Status | Source |
|---|---|---|---|
| Astroscale (Japan/UK) | ADRAS-J (inspected an H-IIA upper stage); **ADRAS-J2** = first actual removal of that stage; **ELSA-M** = magnetic-plate client removal | ADRAS-J2 launch agreement with Isar signed 1 Sep 2026, target 2027–28; ELSA-M on Isar Spectrum "FY2028 or later" | [SpaceWatch](https://spacewatch.global/2026/09/isar-aerospace-to-launch-astroscale-japans-adras-j2-debris-removal-mission/), [European Spaceflight](https://europeanspaceflight.com/isar-aerospace-to-launch-astroscale-elsa-m-orbital-debris-removal-mission/) |
| ClearSpace (Switzerland/UK) | ClearSpace-1 (ESA, target now PROBA-1); UK national ADR mission | **UK prime contract ~£61M (~$80M), 15 Oct 2026**, to remove **two** UK satellites, mission ~2029 | [SatNews](https://satnews.com/2026/10/15/clearspace-wins-61-million-prime-contract-for-uk-dual-satellite-debris-removal-mission/) |
| Starfish Space (US) | Otter servicer/docking vehicle | SDA end-of-life disposal contract, $52.5M (Jan 2026, SECONDARY); Space Force Otter $54.5M | [Space.com](https://space.com/space-exploration/launches-spacecraft/us-space-force-awards-1st-of-its-kind-usd52-million-contract-to-deorbit-its-satellites), [Starfish](https://www.starfishspace.com/mission/) |
| Magdrive / "Space Postman" | Drift-aware routing platform + ATLAS tug (concept) | IAC 2026 paper | arXiv:2607.22974 |

Key business signal: **governments are now buying removals with real money** (UK ~$80M for 2 objects; SDA ~$52.5M for constellation disposal). That gives a real price anchor of roughly **$40M per object** for the UK mission (contract value ÷ 2; a crude anchor, not a true unit price).

Market size: estimates vary widely by definition. Monitoring + removal is about $1.1–1.6B (2025), growing ~8–10%/yr (Mordor, ResearchAndMarkets). Removal-only is about $0.15B (2025) to $0.55B (2029) (The Business Research Company). All are paid analyst reports; we can cite the headline figures only, and should say so.

## 7. Regulation: VERIFIED from primary FCC documents

- **FCC 22-74** (Second Report & Order, adopted 29 Sep 2022): LEO satellites (below 2,000 km) disposing by uncontrolled re-entry must dispose "as soon as practicable following end of mission, and no later than five years after the end of the mission." The rule applies to satellites **launched after 29 Sep 2024** (two-year grandfathering), and it covers both US licensees **and non-US operators seeking US market access**. Waivers are considered case by case. Satellites already in orbit are exempt. [FCC 22-74](https://docs.fcc.gov/public/attachments/FCC-22-74A1.pdf)
- **2025–26 update:** "Space Modernization for the 21st Century" (NPRM Oct 2025) → **Report & Order FCC 26-47, adopted 22 Jul 2026**, creating **Part 100**. The five-year rule is kept, but reworded as a certification: space stations "will be designed and operated to de-orbit no later than five years after the end of the mission," and the "probability of success of disposal of 0.9 or greater." [FCC 26-47](https://docs.fcc.gov/public/attachments/FCC-26-47A1.pdf)
  - **Why this matters for us:** a 0.9 success requirement means up to about 1 in 10 satellites may fail to dispose of themselves and still comply. Those failed satellites are exactly the market for a removal service.
- ESA's Zero Debris approach also moved to a 5-year LEO limit (ESA Space Environment Report 2026 text).

## 8. Debris population: VERIFIED from ESA

- ESA DISCOSweb (updated 14 Oct 2026): **~47,080 objects regularly tracked**, of which **~15,900 are still functioning**; MASTER-8 model (Feb 2026): **68,450 objects >10 cm**, **1.5 million 1–10 cm**, **230 million 1 mm–1 cm**; **>660 fragmentation events**; >17,400 tonnes in orbit. [DISCOSweb statistics](https://sdup.esoc.esa.int/discosweb/statistics/)
- ESA Space Environment Report 2026 (data to end 2025): "Even if no new satellites were launched, the debris population would continue to increase because fragmentation events generate debris faster than they can naturally reenter." In 2025, 300+ launches put 4,000+ payloads in orbit. ESA's "Health Index" jumped from about 4 to 50 in one year. [ESA SER 2026](https://www.esa.int/Space_Safety/Space_Debris/ESA_Space_Environment_Report_2026)
- Comparison point, ESA SER 2025 (data to end 2024): ~40,000 tracked, ~11,000 active payloads. [ESA SER 2025](https://www.esa.int/Space_Safety/Space_Debris/ESA_Space_Environment_Report_2025)
- Kessler & Cour-Palais (1978) for Kessler syndrome (classic citation; full reference to add).

## 9. DECA rules: VERIFIED against the 2026–27 guide (pp. 74–77)

Your summary was accurate on every point. Additions:
- Each participant may bring a copy of the pitch deck or note cards.
- **Set-up time counts toward the 15 minutes.** The laptop demo must start fast.
- Sound is allowed at conversational volume. No wheeled carts. No food or drinks. No generators.
- The judge lets you present uninterrupted, then asks questions "if time remains." Plan about 10 min of pitch + about 5 min of Q&A.
- The **Penalty Point Checklist is on p. 60 of the DECA Guide**, which is not in the PDF I read. Please get it from your advisor or the full guide.

## 9b. Electric-propulsion (low-thrust) drift trucks: ALSO already published

- **Di Carlo, Romero Martin & Vasile (Strathclyde), "Automatic trajectory planning for low-thrust active removal mission in Low-Earth Orbit," Adv. Space Res. 59(5):1234–1258 (2017).** VERIFIED (full text read). A low-thrust servicer (0.5–10 N for 1,000 kg) removes up to 10 objects per year at 800–1,400 km altitude, on real catalog objects (e.g., NORAD 40342 → 40338 in 42 days). Delta-v comes from an Edelbaum-derived model, and RAAN is matched by **parking in an orbit and letting J2 drift do the work** ("RAAN adjustment – drift"). Both a deorbit-kit strategy and a "drag it down and come back" strategy are studied. Sequencing uses a bio-inspired (Physarum) discrete optimizer. **No cost or price model.** [Strathprints](https://strathprints.strath.ac.uk/58837/)
- "Low-Thrust Propulsion and Drift Orbit Optimization for Multi-Client Servicing Missions in Low Earth Orbit," J. Astronautical Sciences (2026). Paywalled; NOT READ. The title says it does low-thrust + drift-orbit + multi-target. [Springer](https://link.springer.com/article/10.1007/s40295-026-00580-4)
- Glasgow group (Viavattene, Ceriotti et al., Acta Astronautica 193, 2022): machine-learning-assisted design of low-thrust multi-debris-removal missions.
- NASA "EP Shepherd" paper: electric tugs "can only remove a few objects per mission due to limited propellant. Unless a cost-effective way that removes tens of objects per mission can be found, it is not clear that any of the ideas so far proposed will be economically viable." [NTRS](https://ntrs.nasa.gov/api/citations/20140002496/downloads/20140002496.pdf). **This is useful framing for us.**

**Conclusion:** neither the J2-drift conveyor belt nor running it with an electric engine is new. What we found NO published version of: **a priced, customer-facing comparison** (cost per removal vs. mission time) of an electric drift-truck against chemical drift-trucks and one-object-per-mission services, run on the current catalog and split into an operator product and an agency product.

## 10. Data access from this container

- CelesTrak: **blocked** (connection reset). Space-Track.org: reachable but needs a free account login. GTOC9 data (Kelvins), McDowell's GCAT catalog (planet4589.org), PyPI and the jsDelivr CDN: reachable.
