# Orbital Curbside: hook, timing plan and Q&A prep

DECA Innovation Plan (EIP), 2026–27. The presentation is 15 minutes, **including** judge questions. The judge plays a venture capitalist deciding whether the concept is viable and worth exploring further. No power or internet is supplied, so charge the laptop and use the offline demo.

Every number below comes from our model files (`results/*.json`, `paper/paper_numbers.json`) or a cited source in the paper. Items marked **[__]** are placeholders you must fill in.

---

## 1. The 30-second hook (cover slide)

> "Right now there are about forty-seven thousand tracked objects circling Earth, and a lot of them are dead: old satellites and rocket stages that nobody is coming to collect. Today, removing just one of them is a custom space mission that costs forty to ninety million dollars. So we asked a simple question: what if a spacecraft worked like a garbage truck, running a route and picking up ten pieces on one trip? And what if Earth itself did most of the driving? That's Orbital Curbside."

Delivery:
- Say it slowly; it's about 85 words, so 30–35 seconds.
- Look at the judge on "garbage truck" and on "Earth itself did most of the driving".
- Don't read the slide.

**10-second version** (for hallway or elevator use):
> "Orbital Curbside is a space garbage truck. One electric spacecraft removes ten dead satellites per trip by letting Earth's bulge line their orbits up, at about an eighth of today's price per object."

---

## 2. Timing plan (target 11 minutes, leaving about 4 for questions)

| Slides | Section | Target time |
|---|---|---|
| 1–3 | Hook, title, contents | 0:50 |
| 4 | I. Overview | 0:35 |
| 5–7 | II. Business Opportunity | 1:50 |
| 8–10 | III. Customer Segments | 2:10 |
| 11–12 | IV. Unique Value Proposition | 1:00 |
| 13–14 | V. Solution: how it works, proof | 1:25 |
| 15 | Live demo (offline) | 0:45–1:00 |
| 16–17 | V. Solution: economics, risks and roadmap | 1:20 |
| 18 | VI. Conclusion and ask | 0:45 |
| 19–20 | Bibliography and appendix (not presented; for questions) | – |

The full spoken script is about 1,390 words, which is about 10 minutes at a calm pace, plus about 1 minute of demo.

**Practise with a timer.** If you're past 6:00 when you reach slide 11, shorten the demo to 30 seconds.

**Demo fallback:** if the laptop or demo fails, stay on slide 15. The screenshot is the same scene; say "this is the route from our simulation" and continue.

---

## 3. Likely judge questions and answers

Keep each answer to 20–30 seconds: answer, one piece of evidence, then stop.

### Is it new? Is it real?

**Q1. Hasn't someone already done this?**
> "The physics, yes. Using Earth's bulge to plan multi-target routes was studied for ESA's 2017 GTOC9 competition and by researchers like Di Carlo and Vasile, and again in a 2026 IAC paper. What's new is turning it into a priced service: two products, on today's real catalogue, with a cost model and a reusable truck. Nobody we found is selling that."

**Q2. Who are your competitors?**
> "Astroscale and ClearSpace are building capture missions, mostly one or two objects per contract. Starfish Space has a US disposal contract. We see them as potential partners, because they're solving capture. Our edge is the route planning and the per-object price."

**Q3. Why should we believe a high-school student's math?**
> "I checked it against NASA JPL's winning GTOC9 solution: across their 113 legs I'm within 2.2 percent, with a correlation of 0.99. I also checked my orbit predictions against SGP4, the model used for real satellite tracking, and they match within 0.06 degrees. The code and data are public in my repository."

### Customers and market

**Q4. Has anyone said they'd pay?**
> Answer honestly from your interview log.
> - If you have no interviews yet: "Not yet. Customer validation is the first thing this funding pays for. I've drafted the interview guide and contacted [__number__] people."
> - If you have interviews: give **real** counts and quotes only, for example "[__N__] interviews; [__finding__]."
>
> **Never invent a result.**

**Q5. Iridium's CEO said $10,000 per satellite. You're at $12 million. Isn't that a fail?**
> "It's a real gap and I show it on purpose. We're about eight times cheaper than one mission per object, and reuse takes us to about $4.4 million. Operators may never pay the full cost. That's why agencies, who already pay $40 to $90 million per object, are our first customer, and why pricing is my first interview question."

**Q6. How big is the market?**
> "Analysts put debris monitoring and removal at about $1.1 to $1.6 billion in 2025, with removal alone around $150 million and growing fast. These reports disagree, so I don't build on them. I build bottom-up: public removal contracts already total hundreds of millions of dollars, at $40 to $93 million per object."

**Q7. Why agencies first and not operators?**
> "Agencies have budgets now: ESA, JAXA, the UK and the US Space Development Agency have all signed contracts. Operators own their objects, which makes them legally simpler, but they're price-sensitive. So operators are early design partners, and agencies are first revenue."

**Q8. Why would insurers care?**
> "Insurers carry the cost of collisions and failed satellites. A proven removal service lets them offer removal-backed policies. They won't commit before a demo, so they're third."

### Technology and feasibility

**Q9. How do you actually grab the object?**
> "That's the hardest, least-proven part, and I say so. Nobody has captured a tumbling rocket stage yet. Japan's ADRAS-J2 plans to try around 2027–28. Our plan is to partner with whoever proves capture, not invent our own arm."

**Q10. What's in the deorbit kit?**
> "A small solid rocket motor plus an attachment and avionics. It lowers the object's lowest point to 250 km, so it re-enters within months. For a 1.4-tonne SL-8 stage it's about 130 kg. The price is my biggest unknown: I assume $1.5 million each, and I'm testing that with experts."

**Q11. Why electric propulsion?**
> "Electric engines are about five times more fuel-efficient. Ten stops take just 56 kg of xenon. To be honest, it only changes cost per object by 1 to 3 percent versus chemical, because fuel is cheap. The real win is reuse: an electric truck can run about ten routes without in-space refuelling."

**Q12. Why does waiting help?**
> "Earth's equatorial bulge makes every orbit plane slowly rotate, faster at lower heights. If I park slightly above or below a target, the planes drift into line for free. Closing a 19-degree gap by brute force costs about 1,094 kg of propellant; drifting for a year costs about 19 kg."

**Q13. Isn't 220 days slow?**
> "Time costs money, about $5 million a year in operations, so my planner prices time explicitly. For the electric truck one day is worth about 11 m/s of Δv. The 220-day route is the cost-optimal trade, not just the fuel-optimal one."

**Q14. What about falling debris hurting someone?**
> "Small objects burn up completely. Heavy ones get a controlled re-entry over the open ocean. That's also why we don't target the 9-tonne SL-16 stages: their kits would weigh about 870 kg."

**Q15. Can you legally touch those Soviet rocket stages?**
> "Not without Russia's consent. Article VIII of the Outer Space Treaty keeps objects under their owner's control. So the SL-8 cluster is our technical model, and our first contracts target customers' own satellites and partner-nation objects."

### Money

**Q16. Where do your cost numbers come from?**
> "Launch from SpaceX's published rideshare price, truck hardware from NASA's 2023 cost study ($50 to $115 million), and xenon from market data. Kit cost, operations and insurance are my own assumptions, and they're marked as such in the appendix."

**Q17. What's your biggest risk to the price?**
> "Truck hardware. Across NASA's range it swings cost per removal from $8.8 million to $15.8 million. Fuel barely matters."

**Q18. How confident is the $12.1 million?**
> "I ran 20,000 Monte Carlo cases on the uncertain inputs. Eighty percent land between $11.0 million and $15.2 million. That's model uncertainty, not flight data."

**Q19. What would you charge, and how do you make money?**
> "A fixed fee per object, paid on confirmed deorbit. At a 20 percent margin that's about $15.1 million per object on a single route, falling with reuse. The final price depends on what interviews show customers will pay."

**Q20. What exactly is the ask for?**
> "[$__] for twelve months: complete customer and expert interviews, a design study for the deorbit kit, and a signed pathfinder or capture partner."
>
> Fill in the amount with your advisor; don't invent one in the room.

**Q21. What happens next if we fund you?**
> "First, validate pricing with operators and agencies. Then sign a capture partner. Then a pathfinder with two or three stops for one paying customer, around 2028–29. The first ten-stop truck follows from 2029."

### If you don't know

> "That's a great question, and I don't know yet. Here's how I'd find out: [who you'd ask or what you'd test]."

Judges reward honesty over bluffing.

---

## 4. Numbers to memorise

| What | Number |
|---|---|
| Tracked objects / working (ESA, Oct 2026) | ≈47,000 / ≈16,000 |
| Today's price per object (public contracts) | $40–93M |
| Our route | 10 SL-8 stages, 220 days, 56 kg xenon |
| Cost per removal (one route) | $12.1M (P10–P90 $11.0–15.2M) |
| Same truck, one object | ≈$96M |
| Reusable truck, 10 routes | ≈$4.4M per object, ~100 objects, ~8 years |
| Price at 20% margin | ≈$15.1M |
| JPL benchmark | 113 legs, within 2.2%, r = 0.99 |
| SGP4 check | 0.06° median plane error |
| SL-8 cluster | 142 stages, ~960 km, 83° |
| FCC rules | 5-year deorbit; 0.9 disposal reliability |
