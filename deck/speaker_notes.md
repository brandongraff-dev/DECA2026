# Orbital Curbside — DECA Innovation Plan: speaker notes
Word-for-word scripts. Text in [brackets] is a stage cue, not spoken. "Q&A backup" lines are for judge questions.

## Slide 1: cover

HOOK (about 40 seconds; say it before anything else, slowly):
"Look up tonight and you won't see it. But right now, about forty-seven thousand objects that we can track are racing around Earth at about twenty-seven thousand kilometres an hour. Two out of every three are junk: dead satellites, old rocket parts and broken pieces.

When two of them crash, they shatter into thousands more. And the satellites we use every day, for maps, weather and the internet, have to fly through it.

Today, cleaning up just one piece of junk costs forty to ninety million dollars. We're building a cheaper way: a garbage truck for space. That's Orbital Curbside."

[Pause, then advance. Look at the judge on "garbage truck for space".]

## Slide 2: title

"Good morning. I'm Brandon Graff, founder and CEO of Orbital Curbside. I'm going to show you a problem most people have never heard of, why it matters to all of us, and a business that cleans it up the way a city collects trash: on a route, with many pickups per trip."

[About 10 seconds. Don't read the address aloud.]

Fill before competition: ZIP code and presentation date.

## Slide 3: contents

"Here's the plan: the problem, who pays to fix it, what makes us different, how it works, and what we're asking for."

[About 5 seconds. Advance.]

## Slide 4: overview

"Here's the whole idea on one slide.

Everyone working on space junk is asking: how do we grab it? That's a real engineering problem, and companies are solving it. We asked a different question: why does every piece of junk need its own rocket? That question is where the money is.

The problem: dead satellites and old rocket parts are piling up around Earth, and every crash makes more junk.

Our fix: one spacecraft that picks up ten pieces per trip, like a garbage truck on a route.

Who pays: space agencies first, then satellite companies and insurers, with a fixed fee for each piece we remove.

And the price: our model says about twelve million dollars per piece, including the launch. Today it's forty to ninety-three million."

Q&A backup: Why "our model"? Nobody has flown this yet. Every number comes from our open-source model, checked against NASA JPL's competition-winning solution, with every assumption in the appendix.

## Slide 5: junk

"This is every object in low orbit from this October's real catalogue. About forty-seven thousand objects are big enough to track. Only about sixteen thousand still work. The rest is junk: dead satellites, used rocket stages and broken pieces.

And they all move at about twenty-seven thousand kilometres an hour. Picture a highway where two of every three cars are abandoned wrecks, still moving at full speed.

And this isn't just a space problem. Your phone's maps, tomorrow's weather forecast and a lot of the internet run on satellites that fly through this. The International Space Station has had to swerve out of the way of junk forty-one times."

Q&A backup: The speed is basic orbital physics: 7.4 to 7.7 km/s between 400 and 1,000 km. Object counts: ESA Space Environment Statistics (DISCOSweb). Why not let them fall? Above about 800 km, dead objects can stay up for a century or more.

## Slide 6: crashes

"Here's the good news: we don't have to remove all forty-seven thousand.

More than half of them are small pieces from past crashes, far too many and too small to grab one by one.

The real danger is about five hundred big dead rocket stages and satellites, mostly one to nine tonnes each. They're the bombs. When two of them collide, one crash can make thousands of new pieces, like the two thousand two hundred from 2009.

Experts have ranked the fifty worst. Removing just those would cut the risk of junk-making crashes about in half.

NASA's models say we need to remove about five big objects a year just to keep low orbit from getting worse. And how many big dead objects has any cleanup spacecraft removed so far? Zero. The first attempt to even grab one is planned for 2027."

Q&A backup: One of our reusable trucks would do about 8 a year (our model), more than NASA's ~5 benchmark. "Zero so far" means no spacecraft has captured and removed a large derelict; ADRAS-J (2024) only inspected one, and ADRAS-J2 plans capture around 2027–28. Sources: ESA (more than half of tracked objects are fragments from 500+ breakups); McKnight, IAA memo (about 480 massive derelicts in LEO, about 810 tonnes); McKnight, Top 50 update presented at IAC 2025 (removing all 50 roughly halves debris-generating potential; the top 10 about 30%; reported by Ars Technica); Liou & Johnson, NASA (2009) and Liou (2011) (about 5 a year; NASA calls it a notional planning benchmark). About 8 a year = about 50 removals over about 6 years for one reused truck, our model. Also: the ISS has moved out of the way of junk 41 times since 1999 (NASA ODQN 29(3)). Honest limit: 34 of the 2025 top 50 are Russian/Soviet and 10 Chinese; about 30 are SL-16 and SL-8 stages. Our truck fits the 1.4-tonne SL-8s (a later route, with Russia's consent). The 9-tonne SL-16s need about 870 kg kits each, too heavy for a 10-stop truck, so they need a bigger tug or a partner.

## Slide 7: cost-today

"So why hasn't anyone cleaned it up? Because it's expensive.

Governments have started paying: Europe, Japan, the UK and the US. But each one is a custom mission for one or two objects, at forty to ninety-three million dollars per piece. That's like hiring a whole garbage truck for every trash bag. At those prices, nobody can clean up thousands. So the real problem isn't the robot arm. It's that every pickup pays for its own rocket.

And why now? Because the rules just got stricter. In the US, dead satellites must now come down within five years, and up to one in ten satellites is allowed to fail at that. So there will always be some that need a pickup. Analysts put this market at over a billion dollars already."

Q&A backup: Contract values: ClearSpace-1 (ESA, 2020) €86M; ADRAS-J2 (JAXA, 2024) ≈¥13.2B; UK ADR (15 Oct 2026) "more than £60m" for two satellites; US SDA disposal service (Starfish, Jan 2026) $52.5M including options. Market reports are paid analyst estimates that disagree, so we don't build on them; we build bottom-up from contract prices.

## Slide 8: who-pays

"Who pays to take out the trash? Three customers, in the order they'll pay.

First, space agencies: Europe, Japan, the UK and the US. Their old rockets are up there, and they're already signing cleanup contracts.

Second, satellite companies like Iridium and OneWeb. They must bring dead satellites down within five years, and some will fail. But listen to Iridium's CEO: at millions per satellite, he said, it doesn't make sense. So companies need a much lower price, which is exactly what a route gives.

Third, insurers, who pay out when satellites are lost. They'll join once removal is proven."

Q&A backup: Why agencies first? They have budgets now. Companies own their satellites, which makes them legally simple, but they're price-sensitive, so they're early design partners. 24 dead first-generation Iridium satellites are still in orbit (Oct 2026 data); a 10-stop route through them models ≈$12.5M each. Rocket Lab agreed to buy Iridium in June 2026 (≈$8B).

## Slide 9: first-route

"So where do we start? With ten old rocket stages from the US, India and France.

We picked them for two reasons. First, they sit in the orbit band where cheap, shared SpaceX launches already go, so our truck makes its first pickup just eighty days after launch.

Second, no permission problem. Under space law, every object still belongs to the country that launched it. These belong to countries whose space agencies already pay for cleanup.

The bigger prize comes later: a hundred forty-two Soviet-era rocket stages, the same type that shows up on experts' list of the fifty most dangerous objects. But Russia must agree, and getting there takes a year of thrusting, so those cost about thirteen million each."

Q&A backup: The stages: 4 Indian PSLV, 4 French Ariane and 2 US (Agena, Delta) upper stages, 600–1,900 kg each, in the sun-synchronous band at 650–850 km. Legal basis: Outer Space Treaty, Article VIII (state of registry keeps jurisdiction and control). Are these the most dangerous objects? No, and say so: the first route is chosen for consent and cheap access, to prove the truck works. The most-dangerous list is mostly Russian/Soviet (34 of 50) and Chinese (10); 11 SL-8 stages were on the 2021 list (McKnight et al. 2021).

## Slide 10: one-trip

"Remember the question we asked: why does every piece need its own rocket? It doesn't. Today, every piece of junk gets its own custom mission, at forty to ninety-three million dollars each.

We run a route instead. One truck, one launch, ten stops. Because the expensive parts, the spacecraft and the launch, are shared by ten pickups, our model comes out at about twelve million dollars per piece.

And we price it like a garbage route: a fixed fee per piece, paid only when it's confirmed coming down."

Q&A backup: Is multi-target removal new? The idea has been studied (ESA's GTOC9 contest in 2017, Di Carlo and Vasile, a 2026 IAC paper), and Astroscale and ClearSpace are working on servicing more than one object. We know of no company selling a priced, multi-stop route on today's catalogue; we'd welcome being corrected.

## Slide 11: secret

"So how can one truck reach ten objects cheaply? Here's the secret: we don't chase the junk. We let Earth bring it to us.

Every orbit slowly swings around Earth, like the hand of a clock. And lower orbits swing faster, because Earth isn't a perfect ball; it bulges at the equator.

So our truck parks a little higher or lower than its next target, and simply waits until the two line up, like the hands of a clock meeting.

The difference is huge. Turning with fuel to close one of these gaps would take about a thousand kilograms of propellant. Waiting a year takes about nineteen."

Q&A backup: The swing is called nodal precession, caused by Earth's oblateness (the J2 term): dΩ/dt = −1.5·n·J2·(R/p)²·cos i. Our planner prices waiting time against fuel, so routes aren't just fuel-optimal; they're cost-optimal.

## Slide 12: how-it-works

"Here's one trip, in four steps.

One: the truck rides a shared SpaceX rocket, the cheapest seat to space.

Two: it climbs to the junk's height and drifts, letting Earth line up the next target.

Three: a robot arm holds the old rocket, and the truck latches on a small rocket kit.

Four: the kit fires, the old rocket falls into the atmosphere and burns up, and the truck drives on to the next stop. Ten times per trip."

Q&A backup: The kit lowers the stage's lowest point to 250 km so it re-enters within months; heavy objects get a controlled re-entry over the ocean. Kits weigh about 85 kg each on our first route. The arm and capture are the least-proven part; Japan's ADRAS-J2 plans to demonstrate capture around 2027–28.

## Slide 13: truck

"This is the truck, from our 3D model. At launch it weighs about one thousand six hundred fifty kilograms, about as heavy as a car.

It has electric engines that run on xenon gas and are about five times more fuel-efficient than chemical rockets. A robot arm to hold each old rocket steady. Ten rocket kits, one for each pickup. And solar wings that power the engines.

More than half its launch weight is the kits. The fuel for the whole trip is only about two hundred kilograms."

Q&A backup: Mass budget (first route): kits 852 kg, dry truck 600 kg, xenon 198 kg. Two Hall thrusters, 0.202 N each class, Isp 1,710 s. "5× more efficient" compares specific impulse (≈1,710 s vs ≈300 s for a chemical engine). An electric truck can run about five routes before its thrusters wear out.

## Slide 14: proof

"How do you know a high-schooler's math is right? I checked it against the best.

In 2017, the European Space Agency held a contest to plan exactly this kind of route. NASA's Jet Propulsion Laboratory won, and published every move. I rebuilt all one hundred thirteen. My fuel totals land within two point two percent of theirs. Each dot here is one move; on the line is a perfect match.

I also checked my orbit predictions against SGP4, the model used to track real satellites. They match within six hundredths of a degree."

Q&A backup: 0.06° median on the SL-8 route; 0.30° on our first route. Our model is about 2% optimistic, so plans carry a 10% fuel margin. Four search methods (beam search, simulated annealing, genetic algorithm, ant colony) compete to pick the best of 2.4×10²¹ possible routes.

## Slide 15: demo

[VIDEO CUE: the presenter deck plays the 29-second clip on this slide automatically, muted. Talk over it. Press → to move on. Optional live demo instead: open Start Demo.bat (offline), Scene 3, then "See the truck in 3D" → "The journey". If anything fails, stay on the video.]

"Here's one pickup, from our 3D model, sized from our own numbers.

The truck pulls up to an old rocket stage that's been tumbling for decades. The arm grabs the ring where it once held its satellite. Small thruster puffs stop the spin. A kit latches on, the light turns green, and the truck backs away.

Then the kit fires, and the stage drops into the atmosphere and burns up. The truck drives on to the next stop.

Ten of these per trip. Sixteen months. About two hundred kilograms of fuel for the whole trip."

[Clip: 29 seconds. Then advance.]

Q&A backup: The route comes from our Python planner; the online demo propagates every object with SGP4. The truck is a concept sized from our mass budget, not a flight design.

## Slide 16: economics

"Now the money. Every number here includes the launch.

Today's missions cost forty to ninety-three million per piece. As a sanity check, if our truck picked up just one piece, our model says ninety-seven million: right in line with today.

But with ten pickups on one trip, it drops to about twelve million per piece. And if we keep the truck and just send up new kits, about five million, for around fifty pickups.

Out of twenty thousand simulated cases, eighty percent land between eleven and fifteen million. The biggest unknown is what the truck itself costs, and that's what I'm working hardest to pin down."

Q&A backup: Where the money goes on one route: truck $80M, kits $15M (10 × assumed $1.5M), launch ≈$12.5M ($7,500/kg × 1,650 kg), operations ≈$7M, insurance ≈$7M. Price at a 20% margin: ≈$15.3M. A dedicated rocket instead of a rideshare adds $4–7M per piece.

## Slide 17: risks-roadmap

"What could stop us? Four things, and here's what we do about each.

Grabbing it: nobody has grabbed a tumbling old rocket yet. Japan plans to try in 2027 or 2028, and we'll partner with whoever proves it rather than invent our own arm.

Cost: our prices are estimates, so I'm testing them with experts.

Permission: every object belongs to its country, so our first route uses American, Indian and French stages.

Falling pieces: heavy objects are steered to burn up over the open ocean.

The plan: talk to customers and experts this year, sign a partner, fly a small test trip, then our first ten-pickup truck from 2029."

Q&A backup: Why not build the arm ourselves? It's the hardest, least-proven part, and funded companies (Astroscale, ClearSpace) are already on it. Our edge is the route and the pricing. A rideshare as heavy as our truck needs a custom quote above the 831 kg standard port limit.

## Slide 18: conclusion

"Every crash makes more junk, so waiting makes this problem bigger and more expensive. Three things to remember. One: we don't need to remove all the junk; taking out the worst fifty would cut the danger about in half. Two: cleaning up costs forty to ninety-three million dollars per piece today; our route brings it to about twelve, including the launch. Three: Earth does the steering, and the math is checked against NASA.

Our ask: two hundred fifty thousand dollars in pre-seed funding for twelve months, to finish customer interviews, design the rocket kit, and sign a partner for a test trip.

We don't chase the junk. We let Earth bring it to us. Thank you; I'm happy to take your questions."

Q&A backup: The QR opens the online 3D demo (shared by link); the offline copy is on the laptop. Why about 50 pickups per reused truck? The thrusters are rated for about 13 MN·s of total impulse, enough for about 5.7 ten-stop routes; we count 5.

## Slide 19: bibliography

[Do not present this slide aloud. It's here for judges. If asked: "Every number in this deck traces to one of these sources or to our own model, and the paper lists each with a link."]

Q&A backup: Earth images are rendered by us from NASA's public-domain imagery; charts and truck renders are our own model output. Cesium, satellite.js and three.js credits are in ATTRIBUTION.md.

## Slide 20: appendix

[Backup slide: use only if judges ask about assumptions.]

"Here's every assumption behind the cost numbers. Anything marked 'assumption' is my estimate; the kit price has no public number at all, so it's a top question in my expert interviews.

The bars show what moves the price. Truck hardware matters most: across NASA's range it swings our cost per piece from about nine to sixteen million. Xenon price barely moves it, which is why we say fuel is nearly free, but hardware and time are not."

Q&A backup: Kit mass comes from the rocket equation. SL-16 stages (≈9 t) would need ≈870 kg kits, so they don't suit a multi-stop truck.
