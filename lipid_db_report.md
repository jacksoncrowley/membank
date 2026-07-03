# Lipid Membrane Properties Database — Provenance & Methods Report

**Version:** database v6 · **Compiled:** 2025-07-01
**Primary artifact:** `lipid_properties.csv` (4,032 rows) · **Consensus:** `lipid_consensus_summary.csv` (951 groups)

---

## 1. Purpose and scope

This database collects experimentally measured and computationally predicted
biophysical properties of lipid bilayer membranes, one reported value per row,
each traceable to a source DOI. It is built to **preserve disagreement**:
duplicate measurements of the same property at the same temperature by different
methods, force fields, or laboratories are kept as separate rows and never
averaged in the primary table. Reconciliation exists only in a derived summary
(`lipid_consensus_summary.csv`), which reports the spread rather than collapsing it.

**Current contents (v6):**

| Dimension | Coverage |
|---|---|
| Total value rows | 4,032 |
| Distinct lipid systems | 166 (single lipids + mixtures) |
| Distinct source DOIs | 489 |
| Experimental rows | 129 |
| Computational rows | 3,903 |
| Temperature range | −2.2 °C to 96.9 °C |

**Properties captured:** area per lipid (909), bilayer thickness $D_B$ (894),
order-parameter $|S_{CD}|$ plateau (2,203), hydrocarbon thickness $2D_C$ (22),
bending modulus $K_c$ (3), area-compressibility modulus $K_A$ (1).

---

## 2. Data sources

### 2.1 Experimental core

**Kučerka, Nagle, Katsaras (2011)** — *Fluid phase lipid areas and bilayer
thicknesses of commonly used phosphatidylcholines as a function of temperature*
(BBA Biomembranes), DOI `10.1016/j.bbamem.2011.07.022`. This is the master
experimental compilation: joint small-angle X-ray + neutron scattering analyzed
with the scattering-density-profile (SDP) model. Tables 1–3 supply area per
lipid, Luzzati thickness $D_B$, and hydrocarbon thickness $2D_C$ for seven PCs
(DLPC, DMPC, DPPC, DSPC, POPC, SOPC, DPhyPC) at 20/30/50/60 °C. **All 66 values
were extracted from the PDF text and verified digit-by-digit against the source
tables**, with gel-phase cells correctly excluded from the fluid-phase rows.

**Kučerka et al. (2008)** — joint neutron+X-ray SDP, DOI
`10.1529/biophysj.108.132662`. Provides the canonical DOPC (67.4 Å² at 30 °C)
and DPPC (63.0 Å² at 50 °C) areas; the DPPC value is a deliberate cross-check
against Kučerka 2011 (63.1 Å²).

**Rawicz et al. (2000)** — micropipette aspiration of giant vesicles, DOI
`10.1016/S0006-3495(00)76295-3`. Supplies bending modulus $K_c$ endpoints
(0.56–1.2 ×10⁻¹⁹ J across the saturated/monounsaturated chain-length series;
≈0.4 ×10⁻¹⁹ J for poly-cis-unsaturated chains) and the mean area-compressibility
modulus $K_A$ = 243 mN/m across 12 PCs.

**NMRlipids experimental databank** — 55 records of ²H-NMR order parameters, each
with a data DOI, temperature, composition, and full sample protocol. Yields 57
experimental $|S_{CD}|$ plateau values for POPC, DMPC, DOPC, POPG, POPE, POPS,
PAPC, PILPC, SDPC.

### 2.2 Computational backbone

**NMRlipids Databank** (`github.com/NMRLipids/BilayerData`, retrieved 2025-07-01,
repo state 2026-06-24). 885 published MD-simulation records, each carrying a
Zenodo/repository DOI, force field, temperature, and composition. From each
record we extracted:

- **Area per lipid** — box-area × 2 / lipid count, time-averaged over the
  post-equilibration trajectory (definition verified against the databank's own
  `analyze.py`).
- **Bilayer thickness $D_B$** — water/lipid density-crossover thickness (Gibbs
  dividing-surface / Luzzati-style; verified against `computeTH` source, *not*
  head–head). Converted nm → Å.
- **Order-parameter plateau** — per C–H $|S_{CD}|$, reduced to the sn-1 and sn-2
  acyl-chain plateau (maximum carbon-averaged $|S_{CD}|$) using NMRlipids
  universal atom naming (G1 = sn-1, G2 = sn-2, G3 = headgroup).

Force-field labels were normalized to 13 controlled-vocabulary families:
CHARMM36 (1,683 rows), Slipids (559), Lipid17 (346), Berger (314), ECC-lipids
(294), MacRog (161), GROMOS (144), OPLS (116), CHARMM-Drude (84), Lipid14 (78),
AMOEBA (28), GAFFlipid (12), and *other* (84, incl. force-field-development runs).
The verbatim original label is preserved in each row's `notes` field
(`FF_raw='…'`).

---

## 3. Methods and schema conventions

- **One row = one reported value.** See `lipid_db_schema.md` for the full
  20-column data dictionary and controlled vocabularies.
- **Disagreements preserved.** No averaging in `lipid_properties.csv`. The
  consensus table groups by (lipid, property, type, 5 °C temperature bin, chain)
  and reports n, mean, median, std, min, max, spread %, source count, and
  force-field count.
- **Order parameters** are stored as chain plateaus (sn-1 / sn-2), with the
  contributing carbon recorded in `notes`. Full per-carbon profiles remain in the
  cited source; the database points to them rather than duplicating every carbon.
- **Extraction confidence** is graded: *high* for digit-verified table values
  (Kučerka 2011) and abstract-stated key results; *medium* for programmatically
  reduced simulation observables and plateau estimates.

---

## 4. Coverage

![Database coverage: reported values per lipid, by property and source type]({{artifact:art_74e55357-7bc0-4dc5-930e-90ac8d68e2f4}})

Coverage is densest for the phosphatidylcholines and for the three core
structural properties (APL, $D_B$, $S_{CD}$). Computational data dominate by
volume (the NMRlipids Databank), while experimental anchors concentrate on the
well-studied PCs. Non-PC headgroups (PE, PS, PG) and mixtures are present but
more thinly covered, and mechanical/dynamic properties (bending, area
compressibility, diffusion, transition temperatures) are the sparsest.

---

## 5. Known disagreements

### 5.1 Area per lipid — experimental vs. simulation

For the well-covered PCs, force-field-averaged simulation APL agrees with the
experimental SDP values to within ~1–3 Å²:

| lipid_system | T_bin | computational | experimental | Δ(sim−exp) |
| --- | --- | --- | --- | --- |
| DMPC | 30C | 59.9 | 59.9 | +0.01 |
| DMPC | 50C | 63.9 | 63.3 | +0.60 |
| DMPC | 60C | 63.9 | 65.7 | −1.81 |
| DOPC | 30C | 69.3 | 67.4 | +1.93 |
| DPPC | 50C | 60.9 | 63.1 | −2.15 |
| DPPC | 60C | 62.4 | 65.0 | −2.57 |
| DSPC | 60C | 50.9 | 63.8 | −12.95 |
| POPC | 30C | 64.3 | 64.3 | −0.03 |
| SOPC | 30C | 64.3 | 65.5 | −1.19 |
| SOPC | 60C | 67.5 | 69.4 | −1.93 |

The **DSPC 60 °C** row is a deliberate red flag: the simulation median (50.9 Å²)
falls ~13 Å² below experiment (63.8 Å²), indicating one or more DSPC simulations
labeled "fluid" are in fact gel-phase at that temperature. Such cases are
surfaced by the reconciliation rather than hidden.

![Area per lipid vs temperature: experimental anchors within the simulation spread]({{artifact:art_91e78c71-dd66-4148-8983-0b27e74da2e0}})

### 5.2 Order parameters — force-field spread

The POPC plateau $|S_{CD}|$ shows the widest inter-force-field disagreement in
the database. At 25 °C across 10 force fields, the sn-1 plateau ranges
0.16–0.40 (median 0.22) and the sn-2 plateau 0.11–0.37 (median 0.21). The
extremes are genuine: the high outliers come from force-field-development runs
and the low ones from small-molecule force fields (Sage/Espaloma) being tested
on lipids — both correctly labeled *other*. Above 40 °C, where only mature force
fields contribute, the spread collapses to <15%.

### 5.3 Bilayer thickness $D_B$

Simulation $D_B$ spreads are 20–46% for the best-covered lipids (POPC 25 °C:
35.7–55.4 Å over 93 simulations), reflecting both real force-field differences
and the mixing of gel/fluid states within a nominal temperature bin.

---

## 6. Coverage gaps and candidate queue

The following are documented as sparse and are held in `candidates.csv`
(20 literature candidates from a PubMed/OpenAlex sweep) for future extraction:

- **Transition temperatures ($T_m$)** — the canonical compilations
  (Koynova & Caffrey 1998; Nagle & Tristram-Nagle 2000) return metadata-only
  through openly accessible routes; values were **not** hardcoded from memory to
  preserve source fidelity.
- **Lateral diffusion coefficients** — no accessed source yet; candidates queued.
- **Bending / area-compressibility moduli** beyond the Rawicz anchors.

---

## 7. Reproducibility

Every row carries `source_doi`, `source_citation`, and `source_locator` (page,
table, or simulation ID). The NMRlipids extraction is fully scripted from the
public `BilayerData` repository tarball; the Kučerka 2011 values are
text-verified against the PDF. Property definitions were confirmed against the
databank's own analysis source code rather than assumed.

**Artifacts:**
- `lipid_properties.csv` — primary value-level database (4,032 rows)
- `lipid_consensus_summary.csv` — chain-aware reconciliation (951 groups)
- `lipid_db_schema.md` — data dictionary
- `candidates.csv` — queued literature for gap properties
- `source_doi_table.csv` — DOI × type × count index
- `fig_coverage.png`, `fig_apl_vs_temp.png` — coverage & disagreement figures
