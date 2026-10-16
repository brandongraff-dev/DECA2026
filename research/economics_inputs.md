# Orbital Curbside: sourced economics inputs

Research date: 16 Oct 2026. Every number below comes from the cited source. No number has been estimated or invented.

- **Type:** PRIMARY means a company, agency, government or peer-reviewed/conference paper. SECONDARY means press, a blog or an analyst.
- **How verified:**
  - [PDF] means the document was downloaded and its text was searched.
  - [FETCH] means the page was fetched and the quote was taken from the page text.
  - [API] means the data came from a live public pricing endpoint.
  - [SNIPPET] means the number appeared only in search-engine snippets because the page itself blocked fetching. Re-check these before you quote them in a final submission.
- Any number marked "(derived)" is a unit conversion I did. It is not a number from the source.

---

## 1. Launch prices

| Item | Value | Date | Source | Type | Verbatim / evidence |
|---|---|---|---|---|---|
| SpaceX rideshare (Transporter, SSO) price per kg | **$7,000/kg (2026); $7,500/kg (2027)**; earlier years $5,500 (2023), $6,000 (2024), $6,500 (2025) | Live config read 16 Oct 2026 | SpaceX rideshare price API used by the calculator on spacex.com/rideshare: https://api-rideshare.spacex.com/api/v2/price | PRIMARY [API] | JSON: `{"year": 2026, "pricePerKilogramUsd": 700000}`, `{"year": 2027, "pricePerKilogramUsd": 750000}`. The site JS divides these values by 100, so they are in cents: 700000 = $7,000/kg (derived). |
| Rideshare minimum purchase and maximum mass per port | Quarter plate 50 kg minimum; full plate 200 kg minimum; XL plate 300 kg minimum; **max 831 kg per port** | 16 Oct 2026 | Same API, plus the calculator JS at rideshare.spacex.com | PRIMARY [API] | `"quarterPlateMinSpendMassKg": 50`, `"xlPlateMaxMassKg": 831`. The JS says: "The max mass per port is 831kg. If additional mass is required, please contact rideshare@spacex.com". Takeaway: a 50 kg minimum at $7,000/kg gives a $350k entry price (derived). A servicer heavier than 831 kg needs a custom quote. |
| Rideshare entry price (press confirmation) | $350,000 for up to 50 kg to SSO, then $7,000/kg | Feb 27, 2026 | https://newspaceeconomy.ca/2026/02/27/spacex-rideshare-pricing-as-of-february-2026-what-it-costs-whats-included-and-how-buyers-budget-a-mission/ | SECONDARY [FETCH] | "publicly advertises its rideshare entry price to sun-synchronous orbit (SSO) as $350,000 for up to 50 kg" and "additional mass priced at $7,000 per kilogram beyond that baseline" |
| Rideshare separation system add-on (2026) | 8": $336,800; 15": $409,970; 24": $629,600 | 16 Oct 2026 | Same API | PRIMARY [API] | `"8\""... {"year": 2026, "costPerItem": 33680000}` (cents) |
| Bandwagon (mid-inclination) price | **NOT FOUND** (no separate public price) | — | — | — | The newspaceeconomy article says SpaceX's page "states that affordable rates are available for mid-inclination LEO" but gives no figure. |
| Falcon 9 dedicated launch, standard price | **$74 million** for up to 5.5 t to GTO, on the standard payment plan through 2026 (up from $70M in 2025) | Feb 24, 2026 | Spaceflight Now: https://spaceflightnow.com/2026/02/24/live-coverage-spacex-to-launch-29-starlink-satellites-on-falcon-9-rocket-from-cape-canaveral-8/ (it cites SpaceX's Capabilities & Services page) | SECONDARY [FETCH] | "...is $74 million, up from $70 million in 2025." I could not read the SpaceX Capabilities & Services page directly because it is a JavaScript app. |

## 2. Propellant prices

| Item | Value | Date | Source | Type | Verbatim / evidence |
|---|---|---|---|---|---|
| Xenon market price (global average) | **$3,000/kg (Q1 2025) falling to $2,780/kg (Q1 2026)**; US $2,900/kg Q1 2026 | Page updated 8 Sep 2026 | Expert Market Research: https://www.expertmarketresearch.com/price-forecast/xenon-price-trends | SECONDARY (analyst) [FETCH] | Global average "3,000" (Q1 2025) … "2,780" (Q1 2026). United States "USD 2,900/KG" (Q1 2026). |
| Xenon price range (EP industry) | $5,000 to $12,000/kg | May 24, 2024 | SETS (Hall thruster maker): https://sets.space/xenon-krypton-or-argon-propellants-for-hall-thruster-efficiency-properties-applications-and-cost/ | SECONDARY (industry blog; no source given) [FETCH] | "xenon can go as high as $5,000-$12,000 per kilo" |
| Krypton price range (EP industry) | $2,100 to $4,800/kg | May 24, 2024 | Same SETS article | SECONDARY [FETCH] | "krypton can cost $2,100-$4,800" |
| Argon price | $7 to $15/kg | May 24, 2024 | Same SETS article | SECONDARY [FETCH] | "It comes as cheap as $7-$15 per kilogram" |
| Xenon price volatility and the krypton/xenon ratio | Xenon $74/L (fall 2021) rose to $171/L (spring 2022). Krypton is "nearly ten times less expensive" | 2022 | Su, Marks & Jorns, IEPC-2022 (U. Michigan): https://pepl.engin.umich.edu/pdf/IEPC-2022-Su.pdf | PRIMARY (conference paper) [PDF] | "In fall of 2021, xenon was $74/L, while in spring of 2022, the price rose to $171/L. A potential alternative to xenon is krypton, which is nearly ten times less expensive". Note: $/L is per litre of gas, not per kg. |
| World xenon supply | 71,000 kg in 2023 | 2025 | Hurley, Simmonds & Hofer, AAS 25-023: https://pepl.engin.umich.edu/pdf/Hurley_AAS_2025.pdf | PRIMARY [PDF] | "the world supply of xenon for 2023 was 71,000 kg" |
| Older academic quote (dated) | Xenon £2,460/kg; krypton £185/kg (Air Liquide UK, small quantities) | c. 2019 | "Mission Cost for Gridded Ion Engines using Alternative Propellants", ResearchGate 336013332 | PRIMARY [SNIPPET] | Snippet only: "£2460 per kg for xenon, £185 per kg for krypton". Older than 2023. |
| A krypton price from a paper dated 2023 to 2026 | **NOT FOUND** | — | — | — | The only recent krypton figures are the industry/analyst ranges above. |

## 3. Hall-effect thruster specs

| Thruster | Power | Thrust | Isp | Total impulse / life | Source | Type |
|---|---|---|---|---|---|---|
| Busek BHT-600 | 600 W nominal (300 to 800 W) | 39 mN (Xe) | Up to 1500 s | Demonstrated 1.0 MN·s; predicted >1.5 MN·s. Propellants Xe/Kr/iodine | https://www.busek.com/bht600 | PRIMARY [FETCH] |
| Busek BHT-1500 | 1,500 W nominal (1,000 to 2,700 W) | 101 mN (Xe) | 1710 s | Predicted >6.5 MN·s. Xe/Kr/iodine | https://www.busek.com/bht1500 | PRIMARY [FETCH] |
| Safran PPS-1350 | 1,500 W | 90 mN | 1,660 s | 3.4 MN·s; 7,300 cycles; mass 5.3 kg | Wikipedia, citing Snecma datasheet: https://en.wikipedia.org/wiki/PPS-1350 (Safran's own page returned 403) | SECONDARY [FETCH] (Safran datasheet seen in search snippets: "qualified lifetime of 10,530 hours") |
| Safran PPS-5000 | 2.5 to 5 kW (5 kW rating for Boeing) | 150 to 300 mN | 1,730 to 2,000 s | 15 MN·s | Safran datasheet: https://www.safran-group.com/download/media/420283 | PRIMARY [SNIPPET]. Fetch was blocked (403). Snippet text: "Thrust (mN) 150 - 300", "Specific impulse (s) 1,730 - 2,000", "Total impulse (MN.s) 15" |
| Fakel SPT-100 (baseline / SPT-100B) | 1,350 W | 80 / 83 mN | 1,600 s | Lifetime/total impulse NOT FOUND | https://en.wikipedia.org/wiki/SPT-100 | SECONDARY [FETCH] |
| SpaceX Starlink V2-mini argon Hall thruster | 4.2 kW | 170 mN | 2500 s | 50% efficiency; 2.1 kg. Total impulse NOT FOUND | ISPreview, 27 Feb 2023 (reproduces SpaceX's spec graphic): https://www.ispreview.co.uk/index.php/wp-json/wp/v2/posts/33808. Via Satellite confirms 170 mN, "2.4 times the thrust and 1.5 times the specific impulse" of Gen1: https://www.satellitetoday.com/broadband/2023/02/27/spacex-shares-details-of-higher-bandwidth-v2-mini-starlink-satellites/ | SECONDARY [FETCH] |

Verbatim quotes:
- BHT-600: "Thrust: 39 mN (Xe)"; "Specific Impulse: Up to 1500 seconds"; "Demonstrated Impulse: 1.0 MN⋅s"
- BHT-1500: "Nominal Thrust: 101 mN (Xe)"; "Nominal Specific Impulse: 1710 seconds"; "Predicted Total Impulse: >6.5 MN⋅s"
- Starlink: "170 mN thrust", "2500 s specific impulse", "4.2 kW power", "2.1 kg mass"

Not looked up: Aerojet XR-5, SPT-140, Exotrail ExoMG. The task allowed 2 to 4 examples.

## 4. Spacecraft bus and servicer costs

| Item | Value | Date | Source | Type | Verbatim / evidence |
|---|---|---|---|---|---|
| Servicer hardware cost (1,000 kg dry, chemical, refuellable ADR servicer; Orbit Fab study as reproduced by NASA) | **$115.16M hardware**; $20.9M launch at $15,000/kg; **$136.1M per servicer** | Mar 10, 2023 | NASA OTPS report, Table 34 (see item 5 for the URL) | PRIMARY [PDF] | "Hardware a 1,000 $115,160,000 … Launch Cost @ $15,000/kg $20,925,000 … Cost per Servicer $136,085,000" |
| ELSA-M (Astroscale) design/build estimate, done by NASA | ~$50M to design and build plus ~$10M launch, so ~$60M per mission | Mar 10, 2023 | NASA OTPS report, App. C | PRIMARY (NASA estimate, not an Astroscale figure) [PDF] | "we estimate that it will cost about $50 million to design and build ELSA-m and that it can launch on a roughly $10 million booster, for a total cost per mission of about $60 million" |
| Multi-target solar-electric ADR demo (Duchek et al. 2015; 5 rocket stages of 1,400 kg each, SSO 500 to 1,000 km, lowered to 400 km) | $200M to $300M for development, which is $40M to $60M per disposal | 2015, cited 2023 | NASA OTPS report, App. C | PRIMARY [PDF] | "They estimated that the cost of developing the spacecraft for a demonstration mission would be $200 to $300 million. This corresponds to $40 to $60 million per disposal or $20 to $40 thousand per kilogram disposed." This is the closest published analog to Orbital Curbside. |
| ESA e.Deorbit (Envisat) cost cap | €150M, excluding launch and margins | c. 2015 | NASA OTPS report, App. C | PRIMARY [PDF] | "ESA established a cost cap for e.Deorbit development and operations of €150 million, excluding launch on a Vega C rocket and margins" |
| Aerospace Corp. constellation-backup ADR program | $26M per removal (10/yr for 5 yr) down to $6.5M per removal (100/yr for 25 yr), for targets up to 800 kg | 2022, cited 2023 | NASA OTPS report, App. C (Tibor et al. 2022) | PRIMARY [PDF] | "Their estimates correspond to $26 million per removal for the former and $6.5 million per removal for the latter" |
| Starfish Space Otter: NASA SSPICY inspection mission | $15M contract | Sep 26, 2024 | The Register: https://www.theregister.com/2024/09/26/nasa_sspicy_otter_starfish/ | SECONDARY [FETCH] | "a contract worth $15 million" |
| York S-Class small-sat bus | ~$675k to $1M per bus (2017–2018 reporting) | 2017–18 | GeekWire 2018 / Denverite 2017 | SECONDARY [SNIPPET]. Fetch returned 403. | Snippet: "ranging in cost from $675,000 to $1 million". Old figure; use with caution. |
| NASA/Aerospace SSCM published $/kg for buses | **NOT FOUND** | — | The SSCM19 paper (https://aerospace.org/sites/default/files/2020-05/SSCM19%20paper.pdf) gives the method only, with no $/kg | — | The model itself is restricted to US government and academic users. |
| OTPS replacement cost assumptions by satellite class | CubeSat/SmallSat $0.3M; small-constellation sat $3M; medium-constellation sat $20M; large-constellation sat $1M; bespoke commercial $500M; civil/military operational $820M | Mar 10, 2023 | NASA OTPS report, Table 5 | PRIMARY [PDF] | Table 5 "Cost Per Collision – Lost Vehicle" column |

## 5. NASA OTPS "Cost and Benefit Analysis of Orbital Debris Remediation" (Colvin, Karcz, Wusk; March 10, 2023)

URL: https://www.nasa.gov/wp-content/uploads/2023/03/otps_-_cost_and_benefit_analysis_of_orbital_debris_remediation_-_final.pdf. PRIMARY. The PDF was downloaded and its full text extracted with pdftotext.

**Cost assumptions for removing large debris**

| Parameter | Value | Verbatim |
|---|---|---|
| Controlled reentry, low cost | **$4,000/kg removed** (Orbit Fab, O'Leary et al. 2022) | "Our low-cost estimate is $4,000 per kilogram removed, corresponding to the most optimistic estimate from Orbit Fab's report" |
| Controlled reentry, high cost | **$60,000/kg** (Aerospace Corp., Tibor et al. 2022) | "Our high-cost estimate is $60,000 per kilogram removed, taken from an estimate by Aerospace Corporation" |
| Uncontrolled reentry (tug lowers debris to 350 km perigee), low cost | **$3,000/kg** | "Our low-end estimate of $3,000 per kilogram removed is based on the CONOPS described in the previous section." |
| Uncontrolled reentry, high cost | **$40,000/kg** for any LEO debris above 100 kg | "a high-end cost estimate is reasonably around $40,000 per kilogram for any piece of debris in LEO above 100 kg" |
| NASA's correction for refuelling launch cost | $7,464/kg (controlled) and $5,494/kg (uncontrolled) once refuelling launches are added | Tables 34 and 35: "Cost per Kg Removed $7,464" and "$5,494". The text says Orbit Fab "appear to have omitted the costs associated with launching the propellant for refueling" |
| Launch cost assumed | **$15,000/kg** (Orbit Fab architecture); $500/kg optimistic Starship case for the sweeper | "Launch Cost @ $15,000/kg"; "Optimistically assuming that SpaceX Starship could deliver a 100,000 kg sweeper to the operational orbit for $500 per kg" |
| Servicer cost | $136.1M each, including $115.16M hardware for 1,000 kg dry; 7 servicers in total | Table 34 (see item 4) |
| **Objects per servicer: multi-target IS considered** | Chemical-only with refuelling: **80 per servicer**. Chemical-electric with refuelling: **8.4**. Chemical-electric disposable: **2** | Table 33: "Debris Removed Per Servicer [#] 2 / 8.4 / 80". Text: "an all-chemical system could remove 80 pieces of debris per servicer, with an average mass of about 1,688 kg, compared to only about 8 pieces of debris for the servicer that relied on electric propulsion" |
| NASA's view on electric propulsion | Too slow for controlled reentry, and fewer removals before avionics end of life | "electric propulsion appears to be an unsuitable technology for performing the final maneuvers necessary for controlled reentry"; "electric propulsion systems can de-orbit far fewer pieces of debris than an all-chemical system before the servicer's avionics reaches its end of life. We did not have time to explore this tradeoff" |
| Deorbit kits / attach-and-leave modules | Not analysed; flagged as possibly the cheapest option | "We did not have time to assess the potential for small, disposable propulsion modules that might be able to permanently attach to a piece of debris and de-orbit it over a long period time. Single-use spacecraft or disposable modules deployed from a mothership may provide the lowest cost option for uncontrolled reentry." This is the gap Orbital Curbside targets. |
| Orbit Fab campaign size | 480 objects, 810,000 kg in total, $3.3B over 15 years | "remove 480 pieces of debris over 15 years at a total cost of $3.3 billion" |
| ClearSpace-1 cost reference | ~€100M in total, ~$1M/kg (112 kg target) | "The mission is estimated to cost €100 million… The total cost corresponds to ~ $1 million per kilogram removed" |
| Top 50 total mass used | 260,880 kg | Table 9: Tug Controlled Reentry [Low] $4,000 × 260,880 kg = $1,044M. Uncontrolled [Low] $3,000 gives $783M |

**Benefit and risk numbers**

| Parameter | Value | Verbatim |
|---|---|---|
| Benefit of removing the McKnight Top 50 | **~$3.5M in the first year**, rising to **~$1.1B over 25 years** | "the expected reduction in risk valued at around $3.5 million in the first year after removal"; "rises over a span of 25 years to about $1.1 billion" |
| Damage if a Top 50 collision happens | **$111M per year** (lasting 5 years in the example); annual probability **3.13%** | "if a collision happens, it will cause about $111M of damage per year on average. Factoring in the probability of such a collision, the annual risk is about $3.5M." |
| Avoided cost of satellite interactions with the Top 50 | Only **$10k per year** | "satellite interactions with the Top 50 would have produced a cost of only $10k" |
| Single-collision scenario value | Up to $184M conditional benefit | "the benefit associated with avoiding some of these collisions could be over $180M" |
| Operator cost per warning | $3 (commercial bespoke) to $154 (civil operational/military); $200 (human spaceflight) | Table 5 |
| Operator cost per maneuver (labour) | $462 (commercial) / $769 (civil, military) / $8,000 (human spaceflight); ISS propellant ~$1M per maneuver | Table 5; "the corresponding average cost per maneuver is about $1 million" (ISS, cargo at ~$70k/kg) |
| Engineer labour rate | $80/hour | "We assign the standard labor rate for an engineer to be about $80 per hour" |
| Break-even for controlled reentry | At least 24 more years at $4k/kg; 94 years at $60k/kg ($15.6B) | "At $60k per kilogram, the total cost to remove the debris would be $15.6 billion. It would take 94 years for that cost to equal its benefits. Even with the lowest cost estimate of $4,000 per kilogram, costs don't equal benefits for at least another 24 years." |
| Insurance | Not modelled | "orbital debris appears to have a limited influence on why insurance policies are purchased and how premiums are set (Tibor et al. 2022). Thus, we did not prioritize insurance premiums for analysis" |

## 6. Real debris-removal contracts

| Mission | Value | Objects | What's included | Date | Source | Type | Verbatim |
|---|---|---|---|---|---|---|---|
| ESA ClearSpace-1 | **€86M** ESA contract, plus ~€24M raised by ClearSpace | 1 (Vespa adapter, 112 kg). Later re-targeted to PROBA-1 per press (I did not re-verify this). | Service purchase: launch, rendezvous, capture with 4 arms, then deorbit of chaser and target together | 1 Dec 2020 | https://www.esa.int/Newsroom/Press_Releases/ESA_purchases_world-first_debris_removal_mission_from_start-up | PRIMARY [FETCH via curl] | "ESA has signed an €86 million contract with an industrial team led by Swiss start-up ClearSpace SA to purchase a unique service: the first removal of an item of space debris from orbit." "With a mass of 112 kg…" "The combined 'space robot' chaser plus the Vespa target will then be deorbited" |
| UK ADR (ClearSpace UK) | **"more than £60m"** (gov.uk). Press reports **~£61M ($80M)**. The July 2025 tender budget was £75.6M | **2** UK-licensed defunct satellites (unnamed) | Design, build and operate a refuellable servicer. Launch 2029 from SaxaVord. Both removed "by 2032". First mission to dispose of more than one satellite | 15 Oct 2026 | gov.uk: https://www.gov.uk/government/news/world-first-mission-puts-uk-expertise-to-work-to-help-clean-up-space. SatNews: https://satnews.com/2026/10/15/clearspace-wins-61-million-prime-contract-for-uk-dual-satellite-debris-removal-mission/. Tender: https://www.gov.uk/government/news/uk-launches-tender-for-mission-to-clean-up-space-and-safeguard-vital-services | PRIMARY (gov.uk) + SECONDARY (SatNews) [FETCH/API] | gov.uk: "Government backs new spacecraft with more than £60m to remove two defunct satellites from orbit by 2032." "The mission marks the first time a spacecraft has disposed of more than one satellite in this way." SatNews: "a prime contract valued at approximately £61 million ($80 million)". Tender (3 Jul 2025): "initiating a £75.6 million tender"; "This follows £11 million already invested since 2021" |
| Astroscale ELSA-M (final phase 4) | **€13.95M** (~$15M / £11.78M) from UKSA and ESA. Earlier phases ~€18M (press; not re-verified) | 1 Eutelsat OneWeb client satellite (prepared, with docking plate) for the demo | Phase 4: flight-model AIT, launch, commissioning, docking, deorbiting and release of the client | 22 Jul 2024 | https://astroscale.com/en/news/astroscale-uk-secures-contract-for-final-phase-of-elsa-m-in-orbit-demonstration | PRIMARY [FETCH] | "has secured EUR 13.95 million (approximately USD 15 million or GBP 11.78 million)"; "Set to launch during the fiscal year ending in April 2026." |
| Astroscale ADRAS-J2 (JAXA CRD2 Phase II) | **~¥13.2 billion** including tax (≈$82M per Payload Space) | 1 unprepared Japanese H-IIA upper stage | Approach, inspection, capture with robotic arm, deorbit | 20 Aug 2024 | https://astroscale.com/en/news/astroscale-japan-secures-contract-for-phase-ii-of-jaxas-commercial-removal | PRIMARY [FETCH] | "approximately 13.2 billion yen (including tax)"; "remove and deorbit the rocket body using in-house robotic arm technologies" |
| Starfish Space, SDA end-of-life disposal (PWSA) | **$52.5M** | 1 initial deorbit plus options for "multiple additional deorbits". Exact number NOT disclosed | Build, launch and operate an Otter servicer; launch 2027. Paid as an initial payment, then per service performed (Breaking Defense / GeekWire) | 21 Jan 2026 | https://www.starfishspace.com/press-release/starfish-space-awarded-first-ever-end-of-life-disposal-contract-for-a-leo-constellation/ and https://breakingdefense.com/2026/01/sda-taps-starfish-for-first-of-its-kind-satellite-disposal-service/ | PRIMARY [FETCH] | "awarded a $52.5 million contract by the U.S. Space Force's Space Development Agency (SDA)"; "The mission begins with an initial deorbit, with options for multiple additional deorbits."; "The mission is targeting launch in 2027." |

## 7. Iridium's offer to pay for removal

| Item | Value | Date | Source | Type | Verbatim |
|---|---|---|---|---|---|
| Original article | Caleb Henry, "Iridium would pay to deorbit its 30 defunct satellites — for the right price", SpaceNews | 30 Dec 2019 | https://spacenews.com/iridium-would-pay-to-deorbit-its-30-defunct-satellites-for-the-right-price/ | SECONDARY (press) | SpaceNews returned HTTP 429 every time, so I could not read the article directly. The quotes below come from sources that quote it. |
| Desch's price | **$10,000 per deorbit**, described as "intentionally provocative" | Dec 2019 | ABA Business Law Today (Jan 2022) quoting SpaceNews: https://businesslawtoday.org/2022/01/on-clearing-earths-orbital-debris-enforcing-outer-space-treaty-in-us/ | SECONDARY [FETCH] | "Desch somewhat jokingly floated the idea of paying $10,000"; Desch: "I expect the cost is really in the millions or tens of millions, at which price I know it doesn't make sense"; "Incremental ops cost saved is zero"; "Decreased risk to my network equals zero (all are well below)"; "Decreased regulatory risk is zero (I spend the $$, and someone else runs into something)"; "Removing 1 or 2 things from a catalog of 100,000 is perhaps worth only PR value."; "intentionally provocative and for thought purposes." |
| NASA confirmation | Iridium said it would like to pay for removal of 30 defunct satellites | 2023 (pub. Feb 2024) | NASA Small Spacecraft State of the Art, Deorbit chapter: https://www.nasa.gov/wp-content/uploads/2024/02/13.soa-deorbit-2023.pdf | PRIMARY [PDF] | "In December 2019, Iridium stated that they would like to pay for an active deorbit system to remove 30 of their defunct satellites (48)" |
| Count of defunct first-gen Iridium satellites | **30** (of 95 launched 1997–2002), per Jonathan McDowell in 2019. **7** have perigee below 600 km and **23** sit higher, expected to stay at least ~100 years | Dec 2019 / Jan 2020 | Advanced Television (3 Jan 2020) citing SpaceNews: https://www.advanced-television.com/?p=148977 | SECONDARY [FETCH] | "Ninety-five Iridium craft were orbited between 1997 and 2002 and over time 30 of these malfunctioned." "23 craft are between 100-200 kms higher"; "could be expected to stay in orbit for at least 100 years" |
| Count as of 2025–2026 | **NOT FOUND**. Some low-perigee units have likely reentered since 2019, but I found no published current count | — | Press coverage of McKnight's IAC 2025 Top 50 says 3 US objects are Iridium satellites (newspaceeconomy.ca). The SDC9 interim list (April 2025) instead attributes its 2 US objects to Spot satellites | SECONDARY | — |
| Tethers Unlimited response | Needs "one to two orders of magnitude higher" than $10k | Jan 23, 2020 | SpaceNews (https://spacenews.com/tethers-unlimited-says-early-results-of-deorbit-hardware-test-promising/) | SECONDARY [SNIPPET] (blocked by 429) | Snippet: "somewhere between one to two orders of magnitude higher" |

## 8. The insurance angle

| Item | Value | Date | Source | Type | Verbatim |
|---|---|---|---|---|---|
| Quote "I've yet to see a convincing business plan…" | **NOT FOUND**. Several exact-phrase and related searches found no match. Do not attribute it to anyone. | — | — | — | — |
| Annual space insurance gross premiums | **$550M to $600M expected for 2025** ("typical of the last five years") | 17 Aug 2025 | Seradata (David Todd) via SatNews: http://satnews.com/2025/08/17/space-insurance-promising-start-to-the-year-marred-only-by-methanesat-claim/ | SECONDARY (industry data) [FETCH] | "A gross premium of $550-600 million is expected (typical of the last five years)." |
| Earlier premium data point | $475M gross premiums written in 2020; $425M losses | 1 Sep 2021 | Bloomberg via Claims Journal: https://www.claimsjournal.com/news/national/2021/09/01/305747.htm | SECONDARY [FETCH] | Insurers wrote "$475 million in gross premiums" … "paid $425 million in losses" (according to Seradata) |
| Market profitability, 2025 | ~$500M net profit to insurers in 2025; claims for 2023/24 fell from $1.9B to $1.5B | 8 Jan 2026 | Gallagher Specialty Q4 2025: https://specialty.ajg.com/plane-talking/space-market-update-q4-2025 | SECONDARY (broker) [FETCH] | "2025 is on track to deliver circa.USD500m of net profit to insurers" |
| Insurers' conditional interest in debris removal (SPADRIBs) | Six underwriters (via AHJ Miller) offered up to **$500M per operator**, on conditions | 2024 (article 25 Feb 2026) | Earth.org (Jan Lee): https://earth.org/who-will-pay-to-clean-up-space-junk/ | SECONDARY [FETCH] | Conditions: "A spacecraft company clearly demonstrates it can de-orbit third party space debris" and "The agencies regulating space launch make Spadribs mandatory." Iain Reynolds (Peak Re): "It is not addressing the existing problem – it's a preventive measure to prevent the problem getting worse" |
| Insurer co-authored the Top 50 paper | Chris Kunstadter (AXA XL) is a co-author of McKnight et al. 2021 | 2021 | Acta Astronautica 181 (see item 9) | PRIMARY [PDF] | Affiliation listed as "AXA XL, 200 Liberty Street…" |

## 9. Target population: SL-8 and SL-16 rocket bodies and the McKnight Top 50

| Item | Value | Date | Source | Type | Verbatim / evidence |
|---|---|---|---|---|---|
| SL-16 (Zenit-2 2nd stage) mass | **9,000 kg** (McKnight 2021/2025 tables). An earlier McKnight table gives 8,300 kg | 2021 / 2025 | McKnight et al. 2021, Table 4; SDC9 2025, Table 1 | PRIMARY [PDF] | Table rows: "SL-16 R/B … 71.0 9000" |
| SL-8 (Kosmos-3M 2nd stage) mass | **1,435 kg** (1,434 kg in the earlier McKnight table) | 2021 / 2025 | Same | PRIMARY [PDF] | "SL-8 R/B … 82.9 1435" |
| SL-16 cluster | **~18 to 20 SL-16s at ~840–850 km, 71°**. Cluster C840 (810 to 890 km) holds 91 massive objects averaging 3,202 kg | 2021; Apr 2025 | McKnight et al. 2021; McKnight et al., "An Update of the Top 50 List", 9th European Conf. on Space Debris (SDC9), Apr 2025: https://conference.sdo.esoc.esa.int/proceedings/sdc9/paper/4/SDC9-paper4.pdf | PRIMARY [PDF] | 2021: "18 SL-16 rocket bodies with six of the payloads deployed by these R/Bs plus two SL-12 R/B that are not in C850." 2025 Table 2: "C840 810/890 91/3,202" |
| SL-8 clusters | ~150 SL-8 at ~950 km/83°; ~65 at ~1,500 km/74°; ~50 at ~750 km/74°. 2025 clusters: C975 (890 to 1,100 km) 350 objects averaging 1,280 kg; C775 (700 to 810 km) 145 objects averaging 1,519 kg | Undated McKnight IAA memo (cites 2014–15 work), and Apr 2025 | McKnight, "Proposed Series of Orbital Debris Remediation Activities", IAA: https://iaaspace.org/wp-content/uploads/iaa/Scientific%20Activity/debrisminutes03166.pdf; SDC9 2025 Table 2 | PRIMARY [PDF] | IAA table: "SL-8 rocket body / 1,434kg ~150 ~215,000 950km/83°"; "SL-16 rocket body / 8,300kg ~20 ~100,000 850km/71°"; "TOTAL DERELICTS IN LEO ~480 ~810,000kg". SDC9: "C975 890/1100 350/1,280" |
| Total number of SL-8 / SL-16 still in orbit (catalogue count) | **NOT FOUND** as a single published current number. CelesTrak SATCAT was unreachable from this environment (connection reset). The approximate cluster counts above are the best available. | — | — | — | — |
| 2021 Top 50 composition | **39 rocket bodies and 11 payloads**. SL-16 R/Bs fill **ranks 1–20 plus #35 (21 in total)**. **11 SL-8 R/Bs** (ranks 27, 30, 37, 40–43, 45, 47, 48, 50). 80% abandoned before 2001 | Jan 2021 | McKnight et al., "Identifying the 50 statistically-most-concerning derelict objects in LEO", Acta Astronautica 181 (2021) 282–291, doi:10.1016/j.actaastro.2021.01.021. Open copy: https://iris.cnr.it/bitstream/20.500.14243/421877/1/prod_443448-doc_159316.pdf | PRIMARY [PDF] | "39 of the top 50 SMC objects are rocket bodies (RBs), and only 11 are payloads"; "Ellipse 3 has 11 very tightly-bunched SL-8 R/Bs". The full ID list is in Table 4, e.g. #1 SATNO 22566, #2 22220, #3 31793 … #21 ENVISAT 27386 |
| 2025 interim Top 50 (preferred "50/700/615 Rule") | **42 rocket bodies and 8 payloads**; **19 SL-16 and 10 SL-8** (my count of Table 3 rows); Russia 32, PRC 11, Japan 3, Europe 2, US 2; average mass ~5,150 kg; C840 24, C775 16, C975 5 | Apr 2025 | SDC9 paper above | PRIMARY [PDF] | Table 4: "Rocket Bodies 39 36 42"; "The one constant across all the lists is the SL-16 R/Bs in Cluster 840." #1 is "28353 (SL-16 R/B) … 9000 844 71.0 2004" |
| Final 2025 Top 50 (IAC 2025, Sydney) | 34 Russian/Soviet (30 of them SL-16/SL-8 parts), 10 China, 3 US, 2 Europe, 1 Japan. Envisat ranks #2 behind an SL-16 | 7 Oct 2025 | heise online: https://www.heise.de/en/news/Experts-identify-the-50-most-dangerous-pieces-of-space-debris-10728122.html. newspaceeconomy.ca (25 Oct 2025) lists IDs | SECONDARY [FETCH] | heise: "a total of 34 objects, 30 of which are parts of the SL-16 and SL-8 rockets". newspaceeconomy: "44 are rocket bodies and 6 are payloads". I could not get the official LeoLabs/IAC PDF, so the per-object IDs are unverified. |

## 10. Casualty-risk rule

| Item | Value | Date | Source | Type | Verbatim |
|---|---|---|---|---|---|
| US rule | Casualty risk from surviving debris (>15 J) **< 1 in 10,000** for direct or atmospheric reentry | Nov 2019 | US Government Orbital Debris Mitigation Standard Practices, Nov 2019 update: https://orbitaldebris.jsc.nasa.gov/library/usg_orbital_debris_mitigation_standard_practices_november_2019.pdf | PRIMARY [PDF] | "The risk of human casualty from surviving components with impact kinetic energies greater than 15 joules should be less than 0.0001 (1 in 10,000)." |
| International acceptance | Widely used, including by ESA | current | ESA, Reentry and collision avoidance: https://www.esa.int/Space_Safety/Space_Debris/Reentry_and_collision_avoidance | PRIMARY [FETCH via curl] | "A 1-in-10 000 probability threshold for the casualty risk of a single uncontrolled reentry is commonly accepted by space agencies and nation states." |
| Fraction of mass that survives reentry | 20 to 40% | current | ESA, same page | PRIMARY | "In such cases, 20-40% of the spacecraft mass may survive reentry to reach the ground." |
| Rocket-body context | Casualty areas are often modelled at ≥10 m²; ~80% of 2010–2020 rocket-body reentries exceeded 1 in 10,000 | Oct 2022 | Byers, Wright, Boley & Byers, AMOS 2022 / arXiv 2210.02188: https://arxiv.org/pdf/2210.02188 | PRIMARY (conference paper) [PDF] | "they frequently have casualty areas modelled at 10m2 or larger"; "it is estimated that 80% of rocket bodies that reentered from 2010 to 2020 had a casualty expectancy higher than 1-in-10,000" |
| Mass threshold above which controlled reentry is required | **NOT FOUND** as an official number. The rule is set on casualty risk and casualty area, not mass. An older NASA guideline (NSS 1740.14, Guideline 7-1) limited total casualty area to 8 m² to stay under 1 in 10,000; this came from a search snippet and I did not verify it. | — | — | — | Practical meaning: each SL-16 (9,000 kg) is a strong candidate for a controlled reentry. NASA OTPS: "Controlled reentry may be required for some large debris, particularly those in the Top 50". Whether an SL-8 (1,435 kg) would need one depends on a debris-casualty analysis (e.g. NASA DAS). |

---

## What was NOT FOUND (do not estimate these)

1. A public Bandwagon (mid-inclination) price per kg.
2. The Falcon 9 price directly from spacex.com (the page is JS-only). The $74M figure is from Spaceflight Now.
3. A krypton price per kg from a 2023–2026 paper. Only industry and analyst ranges exist.
4. Total impulse for the Starlink argon thruster and the SPT-100.
5. A published $/kg for small-sat buses from NASA SSCM.
6. Any source for the quote "I've yet to see a convincing business plan…".
7. The number of defunct first-gen Iridium satellites still in orbit in 2025–2026. The last published figure is 30 (in 2019).
8. A current catalogue count of all SL-8 and SL-16 rocket bodies in orbit. CelesTrak was unreachable.
9. The official IAC 2025 Top 50 PDF (only press summaries).
10. An official mass threshold for requiring controlled reentry.
11. The exact number of deorbits in the Starfish/SDA contract (not disclosed).

## Notes for the cost model

- **Closest analog to Orbital Curbside:** NASA OTPS's statement that "disposable modules deployed from a mothership may provide the lowest cost option for uncontrolled reentry" is exactly this concept. NASA flagged it as not analysed.
- **NASA's multi-target numbers:** NASA's own multi-target electric servicer numbers are 8.4 removals per servicer (Orbit Fab chemical-electric with refuelling). Duchek et al. (2015) estimated $200M to $300M for 5 rocket stages, which is $40M to $60M each.
- **Benchmark range per kg:** NASA's range for uncontrolled reentry is $3,000 to $40,000 per kg removed. For a 1,435 kg SL-8, that is about $4.3M to $57M per object (derived: 1,435 × rate).
- **What the real contracts imply per object (derived, simple division):**
  - UK ADR: ~£30M per object (£61M / 2).
  - ADRAS-J2: ~¥13.2B for 1 object.
  - ClearSpace-1: €86M for 1 object of 112 kg.
- **Launch:** Rideshare at $7,000/kg (2026) only covers payloads up to 831 kg per port. A 1,000 to 1,500 kg servicer needs a custom rideshare quote or a share of a dedicated launch ($74M Falcon 9 list price).
