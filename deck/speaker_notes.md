# Orbital Curbside — DECA Innovation Plan: speaker notes
Word-for-word scripts. Text in [brackets] is a stage cue, not spoken. "Q&A backup" lines are for judge questions.

## Slide 1: cover

HOOK (30 seconds, say it before anything else, slowly):
"Right now there are about forty-seven thousand tracked objects circling Earth, and a lot of them are dead: old satellites and rocket stages that nobody is coming to collect. Today, removing just one of them is a custom space mission that costs forty to ninety million dollars. So we asked a simple question: what if a spacecraft worked like a garbage truck, running a route and picking up ten pieces on one trip? And what if Earth itself did most of the driving? That's Orbital Curbside."

[Pause, then advance.]

Delivery tip: make eye contact on "garbage truck". Hold the clicker; do not read the slide.

## Slide 2: title

"Good morning. I'm Brandon Graff, founder and CEO of Orbital Curbside. I'm here today to show you a business that removes space junk the way a city removes trash: on a route, many pickups per trip, at a price customers can actually plan around."

[Advance after about 10 seconds. Do not read the school address aloud.]

Fill before competition: school name, street address, city/state/ZIP, presentation date, headshot.

## Slide 3: contents

"Here's the plan: what we do, the opportunity, who pays, why we're different, how it works, and what we're asking for."

[About 5 seconds. Advance.]

## Slide 4: overview

"Orbital Curbside is a space garbage truck. One electric spacecraft runs a route through a cluster of dead satellites or old rocket stages. At each stop it attaches a small rocket kit that drops the object into the atmosphere to burn up, then it drives on.

Customers pay a fixed fee per object, when it's confirmed coming down. We serve space agencies, satellite operators and insurers.

And the value is the price: our model says about twelve million dollars per removal, versus forty to ninety-three million in today's contracts."

Q&A backup: Why "modelled"? Because no one has flown this yet. Every number comes from our open-source model, benchmarked against NASA JPL's competition-winning solution, with every assumption listed in the appendix.

## Slide 5: problem

"This is low Earth orbit in our simulation, using this October's real catalogue. The European Space Agency tracks about forty-seven thousand objects; only about sixteen thousand still work.

ESA's own conclusion this year: even with no new launches, debris keeps growing, because collisions create pieces faster than they fall. That's the Kessler syndrome.

But the risk is concentrated. A 2021 study found that removing just the fifty most dangerous derelicts, mostly old rocket stages, would cut their collision risk roughly in half."

Q&A backup: Why not just let them fall? Above about 800 km, dead objects can stay up for a century or more. The SL-8 stages we target sit near 960 km.

## Slide 6: cost-today

"Governments have started paying to clean up. ESA's ClearSpace-1: eighty-six million euros for one object. Japan's ADRAS-J2: about eighty-two million dollars. This month the UK announced about eighty million to remove two satellites.

Every one is a custom mission for one or two objects. That's hiring a dedicated truck for every trash bag. At these prices, nobody can clean up thousands."

Q&A backup: The UK figure is per the 15 Oct 2026 announcement ("more than £60m" for two satellites; press reports ≈£61M). The SDA contract covers one deorbit plus options; the number of options is not public.

## Slide 7: why-now

"Why now? Three numbers.

Five years: the FCC now requires low-orbit satellites to deorbit within five years after their mission ends.

Zero point nine: since July, each satellite needs at least a ninety percent chance of disposing of itself. So up to one in ten can fail and still comply. That's a steady supply of customers.

And one point one to one point six billion dollars: analysts' estimate of the debris market in 2025, with removal growing fast."

Q&A backup: Market reports are paid analyst estimates and disagree by definition, so we show the range and don't build our plan on them. We build bottom-up from real contract prices.

## Slide 8: segments

"We have three customer segments, ordered by who pays first.

First, space agencies: ESA, JAXA, the UK, NASA, the Space Force. They're already signing removal contracts and buy with milestone payments. Their challenge: many dangerous objects belong to other countries.

Second, satellite operators like Iridium and OneWeb, who need a plan for satellites that die early. They're very price-sensitive.

Third, insurers, who want to retire risk but will wait for a proven demo.

We chose them because they already carry the cost of debris."

Q&A backup: Why not start with operators? They have the clearest legal right (they own the objects), but the smallest budgets. Agencies have budgets now. We pursue both, with operators as early design partners.

## Slide 9: operators

"Operators are our Product A. In 2019, Iridium's CEO said he'd pay to remove his dead satellites, and joked about ten thousand dollars each. But at millions, he said, it doesn't make sense.

Twenty-four of those dead Iridium satellites are still up there. On a ten-stop route through them, our model gives about twelve million dollars each, eight times cheaper than one mission per object, but still far above ten thousand. Finding the price operators will say yes to is the first thing my interviews test."

Q&A backup: Why would an operator pay at all? To meet the five-year rule, to avoid collision liability and maneuvers near its own fleet, and for reputation. The FCC's 0.9 success rule means some satellites will always fail.

## Slide 10: agencies

"Product B is for agencies. Each dot here is an object we downloaded. The dead ones, in orange, line up in tight clusters, and clusters are routes.

The best is the SL-8 cluster: a hundred forty-two old Soviet rocket stages, about two hundred tonnes, all at the same height and tilt. They'll stay up for a century.

The honest catch: these belong to Russia, and the owner must consent. So we start with partner-nation objects and use this cluster to prove the technology."

Q&A backup: Legal basis: Outer Space Treaty (1967), Article VIII: the state of registry keeps jurisdiction and control over its objects. Partner-nation targets exist in the sun-synchronous band (173 rocket bodies in our data).

## Slide 11: uvp-statement

"Here's what makes us different: we don't chase the junk, we let Earth bring it to us.

Earth bulges at the equator, and that bulge slowly swings every orbit around, at a speed that depends on height. So instead of burning fuel to turn toward the next target, our truck parks at a slightly different height and waits for the target's orbit to swing over to meet it."

[Pause after the headline. Let it land.]

Q&A backup: Is the drift trick new? No. It was used in GTOC9 (2017) and studied by Di Carlo, Vasile and others, and in a 2026 IAC paper. What's new here is pricing it as a customer-facing service on the live 2026 catalogue, with two products and a reusable truck.

## Slide 12: uvp-compare

"Side by side. Today's missions remove one or two objects per launch, at forty to ninety-three million dollars each, burning fuel to change orbits.

We remove ten per route, and about a hundred per reusable truck. Our model says about twelve million per object, four and a half with reuse. Ten stops use just fifty-six kilograms of xenon. And our software picks the route from the live catalogue. Every assumption is in the appendix."

Q&A backup: Who else does multi-target? Astroscale ELSA-M and ClearSpace are working on servicing more than one client object, and research tugs exist. We know of no company publicly selling a priced, drift-planned multi-stop route on today's catalogue; we'd welcome being corrected.

## Slide 13: how-it-works

"Four steps: park, drift, hop, tag.

Park at a slightly different height than the next target. Drift while Earth's bulge closes the gap for free. Hop with a short, gentle electric burn. Tag the object with a small rocket kit that drops it into the atmosphere, then drive on.

The chart shows why waiting matters. Closing a nineteen-degree gap right away takes about one thousand ninety-four kilograms of propellant, more than half the truck. Drifting for a year takes about nineteen."

Q&A backup: The formula is the J2 nodal precession rate, dΩ/dt = −1.5·n·J2·(R/p)²·cos i. We correct it with second-order terms so it matches the SGP4 model used for real satellite tracking (slide 14).

## Slide 14: proof

"How do you know a high-schooler's math is right? I checked it against the best.

In 2017, ESA ran a global competition to plan exactly this kind of route. NASA's Jet Propulsion Laboratory won and published every leg. I rebuilt all one hundred thirteen. My total lands within two point two percent of theirs.

Against SGP4, the model used to track real satellites, my orbit planes match within six hundredths of a degree. And four search methods compete to pick the best of two point four times ten to the twenty-first possible routes."

Q&A backup: Our model is about 2% optimistic, which is why the plan carries a 10% Δv margin. The four methods are beam search, simulated annealing, a genetic algorithm and ant colony optimisation.

## Slide 15: demo

[LIVE DEMO CUE: switch to the laptop and open Start Demo.bat (offline). Click Scene 3 "The garbage truck" and press play. If the demo fails, stay on this slide; the image is the same scene.]

"Let me show you. This is a 3D simulation using the real orbits of the SL-8 rocket stages as of October sixteenth. The orange line is our truck.

Watch how it doesn't chase each stage. It sits at a slightly different height, the orbits swing into line, and then it hops over and tags the stage.

Ten rocket stages. Two hundred twenty days, about seven months. Fifty-six kilograms of xenon for the whole route. And this all runs offline in a web browser; you can scan the code at the end to try it."

[Demo: 45–60 seconds max. Then return to slides.]

Q&A backup: The route is computed by our Python planner and exported to the simulation; satellite.js propagates every object with SGP4 in the browser.

## Slide 16: economics

"Now the money. With our truck removing just one object, our model says about ninety-six million dollars, right in line with today's contracts. That's our sanity check.

Ten stops on one route: about twelve million per object. Across twenty thousand Monte Carlo runs, eighty percent land between eleven and fifteen million.

Reuse the truck for ten routes: about four point four million per object.

The biggest unknown is the truck's own cost, fifty to a hundred fifteen million, and that's what I'm working hardest to pin down."

Q&A backup: Where does the money go on one route? Mostly truck hardware ($80M base), then kits ($15M for 10 at an assumed $1.5M each), then launch (~$15M). Propellant is under $0.2M. Electric vs chemical changes cost per removal by only ~1–3%; the levers are stops per route and reuse.

## Slide 17: risks-roadmap

"Our four biggest risks. Capture: nobody has grabbed a tumbling rocket stage yet, so we watch Japan's ADRAS-J2 and partner with whoever proves it. Cost: our prices are estimates, so I'm testing them with experts. Legal: owners keep control of their objects, so we start with customers' own and partner-nation objects. Safety: heavy objects get a controlled re-entry over the ocean.

The roadmap: validate this year, sign a capture partner, fly a small pathfinder, then our first ten-stop truck from 2029."

Q&A backup: Why not build the capture system ourselves? It's the hardest, least-proven part, and two funded companies (Astroscale, ClearSpace) are already working on it. Our edge is the route and the pricing, not the arm. Dates after 2027 are targets, not commitments.

## Slide 18: conclusion

"Three things to remember. One: removing one object costs forty to ninety-three million dollars today; our route models about twelve. Two: Earth's bulge does the steering, and the math is checked against NASA JPL. Three: one reusable truck can remove about a hundred dangerous objects.

Our ask: [$__] in pre-seed funding for twelve months, to finish customer validation, design the deorbit kit, and sign a pathfinder partner.

We don't chase the junk. We let Earth bring it to us. Thank you; I'm happy to take your questions."

Q&A backup: Why 13 a year? The electric truck's 10-route campaign takes ~7.8 years in our model (285-day routes incl. kit-pod pickups). Its thrusters' rated life allows about 17 routes. The QR opens the online 3D demo (shared by link); the offline copy is on the laptop.

## Slide 19: bibliography

[Do not present this slide aloud. It is here for judges to review. If asked: "Every number in this deck traces to one of these sources or to our own model, and the paper lists each with a link."]

Q&A backup: Images and charts are our own (simulation screenshots and model output). Cesium and satellite.js credits are in ATTRIBUTION.md in the project repository.

## Slide 20: appendix

[Backup slide: use only if judges ask about assumptions.]

"Here's every assumption behind the cost numbers. Anything marked 'assumption' is my estimate, and the kit price is the one with no public number at all, so it's a top question in my expert interviews.

The tornado chart shows which inputs matter. Truck hardware cost dominates: across NASA's range it swings our cost per removal from about eight point eight to fifteen point eight million. Xenon price and fuel margin barely move it, which is why we say fuel is nearly free but time and hardware are not."

Q&A backup: Kit mass comes from the rocket equation. SL-16 stages (≈9 t) would need ≈870 kg kits, so they're not suited to a multi-stop truck.
