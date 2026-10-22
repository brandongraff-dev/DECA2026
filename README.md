# Orbital Curbside: multi-target debris removal engine, simulation and DECA materials

DECA Innovation Plan 2026-27 project by Brandon Graff. **Live demo:** https://claude.ai/artifact/RxGuDPANAdifw94SYwp76U

**Start here for competition:**
- Pitch deck (20 slides): `deck/OrbitalCurbside_deck.pdf`. Script: `deck/speaker_notes.md`
- Hook, timing and Q&A prep: `06_qa_prep_and_hook.md`
- Rubric audit and the placeholder checklist (fill these in!): `07_audit_and_placeholders.md`
- Paper (11 pages): `paper/OrbitalCurbside_paper.pdf`. One-page summary: `onepager/OrbitalCurbside_OnePager.pdf`
- Customer validation kit: `04_validation_kit.md`, contacts in `research/`, tracker `research/outreach_tracker.csv`
- 60-second recording plan: `05_recording_plan.md`. QR codes: `qr/`
- 3D concept model of the truck and its journey (launch → climb → capture → re-entry): https://claude.ai/artifact/2Zm9XkGrtmnhcBdUdxtxQb, source in `model/` (also inside the offline demo)

**Offline demo (Windows, nothing to install):** open `offline/OrbitalCurbside-Demo/`, double-click `Start Demo.bat` (see its README.txt).
Credits and licenses: `ATTRIBUTION.md`.

| Folder | What |
|---|---|
| `01_prior_work.md`, `02_names_and_plan.md`, `03_math_explained.md` | Research, plan, the math explained |
| `research/economics_inputs.md` | Every sourced cost number (with URLs and quotes) |
| `data/` | CelesTrak snapshot (16 Oct 2026), McDowell GCAT, GTOC9 dataset, JPL GTOC9 solution tables (parsed) |
| `engine/ocmath/` | Python library: catalog, J2, transfers, legs, sequencing, missions, kits, truck, economics, style |
| `engine/scripts/` | Runnable analyses (below) |
| `results/` | JSON outputs |
| `figures/paper`, `figures/deck` | Charts (light / navy), PNG + SVG |
| `sim/` | CesiumJS + satellite.js simulation source (published as the artifact) |
| `offline/OrbitalCurbside-Demo/` | No-internet demo package with launchers |
| `paper/`, `onepager/` | Paper and summary (HTML template + build script + PDF) |
| `deck/` | Snapshot of the Slides-artifact deck: slide HTML, images, PDF, speaker notes (`build_deck.py` rebuilds). The editable deck is the Slides artifact; re-export if you edit it there |
| `research/` | Sourced inputs, verified expert and industry contacts, outreach tracker |
| `model/` | 3D concept truck + journey (three.js, offline). Sized from `model/data/truck.json` (`engine/scripts/export_model.py`). Earth from NASA imagery (`model/earth.js`) |
| `model/backgrounds.html` | Renders the deck's Earth background plates (horizon, night, globe, debris swarm, orbit rings); `python model/capture_backgrounds.py` writes them to `figures/backgrounds/`. `python model/capture_clean.py` writes clean model renders to `figures/model_clean/` |

## Re-run everything
```bash
python3 -m venv .venv && . .venv/bin/activate
pip install numpy==2.5.4 scipy==1.18.1 sgp4==2.27 matplotlib==3.11.2 pandas==3.0.6
cd engine
python scripts/parse_jpl_tables.py          # JPL GTOC9 tables -> JSON (already included; to regenerate, download the
                                            #   PDF from doi:10.5281/zenodo.1139152 and run pdftotext -layout)
python -m scripts.benchmark_jpl_legs        # Benchmark 1: 113 legs vs JPL
python -m scripts.benchmark_mission10       # Benchmark 2: optimisers on Mission 10
python -m scripts.catalog_2026              # 2026 clusters
python -m scripts.truck_routes_2026         # 10-stop missions (electric + chemical)
python -m scripts.launch_options_2026       # getting to orbit: rideshare + climb vs dedicated launch; plans the first route
python -m scripts.validate_sgp4             # SGP4 + numerical validation
python -m scripts.pareto_economics          # Pareto / stops-per-truck sweep (~20 min, 4 cores)
python -m scripts.make_figures              # all charts
python -m scripts.export_sim                # data for the 3D simulation
python -m scripts.export_model              # numbers for the 3D truck model
cd .. && python sim/build_offline.py        # offline demo package
python paper/build_paper.py                  # paper PDF (needs playwright)
python deck/build_deck.py                    # deck PDF + speaker notes (needs playwright)
```
Data note: CelesTrak needs a browser-like User-Agent from some networks; it also rate-limits, so download politely.
