# CLAUDE.md — Lipid Membrane Properties Database

Guidance for Claude Code building an **interactive website** on top of this
literature-curated database. Read this before touching the data or designing the
UI. The dataset was assembled through a careful, source-verified literature
review; the rules below exist to keep that fidelity intact in the web app.

---

## What this project is

A fully-sourced database of lipid bilayer **biophysical properties** — area per
lipid, bilayer thickness, acyl-chain order parameters, and a few mechanical
moduli — collected from experiment and molecular-dynamics simulation. Every
value is traceable to a source DOI. The purpose of the website is to let users
**browse, filter, compare, and visualize** these properties across lipids,
temperatures, methods, and force fields — *including where sources disagree*.

**The single most important design principle:** one row = one reported value
from one source at one condition. **Disagreements are the point, not noise.**
The same property for the same lipid at the same temperature may appear many
times (different labs, methods, force fields) with different values. Never
average, dedupe, or "clean away" these in the data layer. Reconciliation belongs
in a *derived* view, and even there you report the spread, never collapse it.

---

## Files (the whole dataset)

| file | rows | what it is |
|---|---|---|
| `data/lipid_properties.csv` | 4,032 | **Primary table.** One reported value per row, 20 columns. This is the source of truth. |
| `data/lipid_consensus_summary.csv` | 951 | Derived reconciliation. Groups by (lipid, property, chain, type, 5 °C temperature bin) and reports n/mean/median/std/min/max/spread%. **Generated from the primary table — never hand-edit.** |
| `lipid_db_schema.md` | — | Human data dictionary (design intent + full controlled vocabularies, including terms not yet populated). |
| `data/candidates.csv` | 20 | Queued literature (PubMed hits) for gap properties (Tm, diffusion). Not yet extracted. |
| `data/source_doi_table.csv` | — | Index of the 489 distinct DOIs × type × row-count. Good backing for a "Sources" page. |
| `lipid_db_report.md` | — | Provenance & methods narrative (sources, extraction, known disagreements, gaps). Good backing for an "About / Methods" page. |
| `fig_coverage.png`, `fig_apl_vs_temp.png` | — | Reference figures. The web app should render its own interactive versions; use these to sanity-check that yours tell the same story. |

Nothing here needs a database server — it is small enough to ship as static CSV/JSON
and query client-side. If you build an API, treat the CSV as immutable input and
generate any derived tables at build time.

---

## `lipid_properties.csv` — column reference

Verified against the actual file (4,032 rows, 20 columns):

| column | type | notes for the UI |
|---|---|---|
| `entry_id` | int | Unique stable row id. Use as the React key / permalink anchor. |
| `lipid_system` | str | Canonical display name. Single: `POPC`. Mixture: `POPC:CHOL (8:1)` — components colon-separated, molar ratio in parens. 166 distinct. **Primary facet.** |
| `lipid_components` | str | Colon-separated component list (`POPC:CHOL`) **or** a single component (`POPC`). ⚠️ See "component quirk" below. |
| `composition` | str | Molar ratio for mixtures (`8:1`, `71:4`); the literal string `single` for single-component lipids. **Not blank** for singles. |
| `property` | enum(6) | `order_param_SCD_plateau` (2203), `area_per_lipid` (909), `thickness_DB` (894), `thickness_2DC` (22), `bending_modulus_Kc` (3), `area_compressibility_KA` (1). |
| `value` | float | The number, in `unit`. **12 rows are null** (simulations where the plateau carbon was absent) — filter these out of plots, don't render as 0. |
| `unit` | enum | `dimensionless` (order params), `A^2` (APL), `A` (thickness), `J` (Kc), `mN/m` (KA). Thickness is stored in Å here even though the schema allows nm. |
| `uncertainty` | float | ± error, same unit. Null in ~76% of rows (most simulations report none). Render error bars only when present. |
| `temperature_C` | float | °C. 41 distinct values, −2 to 97 °C. 4 rows null. **Primary axis** for scatter plots. |
| `phase` | enum | All rows currently `fluid`. Keep the column/filter — gel-phase data may be added. |
| `hydration` | str | All rows currently `fully_hydrated`. Same — keep for future. |
| `type` | enum(2) | `computational` (3903) / `experimental` (129). **The key color/shape distinction in every figure.** |
| `method` | enum(4) | `MD_simulation` (3903), `SAXS+SANS_SDP` (68), `2H-NMR` (57), `micropipette_aspiration_GUV` (4). |
| `force_field` | str | 13 families (see below). **Null for all 129 experimental rows** — that is correct, not missing data. |
| `source_doi` | str | DOI without `https://doi.org/` prefix. 489 distinct. 13 rows blank (databank entries lacking a DOI — `source_citation` carries them). Link out as `https://doi.org/{doi}`. |
| `source_citation` | str | Short `FirstauthorYYYY` or `NMRlipidsDatabank_ID###`. 889 distinct. |
| `source_locator` | str | `Table 1`, `Abstract`, `NMRlipids BilayerData sim ID 630`, etc. |
| `extraction_confidence` | enum(2) | `high` (953, digit-verified table values + abstract key results) / `medium` (3079, programmatically reduced sim observables). Surface this — it is a data-quality signal. |
| `notes` | str | Free text: caveats, unit conversions, `FF_raw='...'` (verbatim original force-field label), contributing carbon, cross-references. Useful in a row-detail popover. |
| `date_added` | date | ISO ingest date. |

### Force-field families (`force_field`)
CHARMM36 (1683), Slipids (559), Lipid17 (346), Berger (314), ECC-lipids (294),
MacRog (161), GROMOS (144), OPLS (116), CHARMM-Drude (84), `other` (84 — includes
force-field-development and small-molecule FFs), Lipid14 (78), AMOEBA (28),
GAFFlipid (12). The raw pre-normalization label is preserved in `notes` as `FF_raw='…'`.

---

## Data-fidelity rules (do not violate in the web layer)

1. **Never average or dedupe in the data layer.** Multiple rows with the same
   lipid/property/temperature are intended. A comparison view shows them side by
   side; a summary view shows mean **and** min/max/spread. If your chart shows a
   single line where the data has a cloud, you have hidden the science.
2. **Experimental vs. computational must stay visually distinct** everywhere —
   color and marker shape. Experimental is the sparse, high-value anchor (129
   rows); simulation is the bulk (3903). Don't let sim volume bury the exp points.
3. **`force_field` is null for experimental rows by design.** Don't fill it,
   don't drop those rows for lacking it.
4. **Filter null `value` (12 rows) out of plots** — never coerce to 0.
5. **Every value links to its source.** A row detail must expose `source_doi`
   (→ `https://doi.org/…`), `source_citation`, and `source_locator`. This is the
   whole point of the database; the DOI is not optional chrome.
6. **`thickness_DB` is Luzzati / Gibbs-dividing-surface thickness**, NOT
   head-to-head (D_HH) and NOT phosphate-to-phosphate. Label it precisely in the
   UI so users don't compare it against the wrong quantity from other databases.
   For simulations it is the water/lipid density-crossover thickness.
7. **Order parameter is stored as the chain _plateau_** (`order_param_SCD_plateau`),
   the max carbon-averaged |S_CD| for a chain — not per-carbon profiles. sn-1 vs
   sn-2 chain is recorded in `notes` (and in the consensus table's `chain` column).
   Don't present it as a full S_CD-vs-carbon profile; the source has that.
8. **Regenerate `lipid_consensus_summary.csv` from the primary CSV** if you change
   binning — don't treat it as independent input. Its 5 °C `T_bin` grouping is a
   choice you can re-make, but it must derive from the raw rows.

---

## Domain gotchas the review surfaced

- **Component quirk.** For a mixture like `POPC:CHOL (8:1)`, `lipid_components`
  appears both as the full `POPC:CHOL` string **and**, on other rows, as a single
  component `POPC`. If you build a "filter by component" facet by splitting
  `lipid_components` on `:`, verify against `lipid_system` rather than trusting
  `lipid_components` alone. The schema doc mentions a `|` pipe separator — the
  **actual data uses `:`**; trust the data.
- **DSPC 60 °C is a known red flag, not a bug to fix.** Simulation APL there runs
  ~13 Å² below experiment because some runs labeled "fluid" are actually
  gel-phase at that temperature. A good comparison view *shows* this outlier; do
  not silently drop or correct it.
- **POPC order-parameter spread is real.** sn-1 plateau ranges 0.16–0.40 across
  10 force fields at 25 °C. The extremes come from FF-development / small-molecule
  force fields (labeled `other`). This is the headline "force fields disagree"
  story — feature it, don't smooth it.
- **Coverage is uneven and honest about it.** PCs (POPC alone = 1037 rows) are
  dense; PE/PS/PG and mixtures thinner; Tm and lateral diffusion are genuine gaps
  (`candidates.csv` holds queued sources — they were deliberately **not**
  hardcoded from memory to preserve source fidelity). Don't imply uniform coverage.
- **One DOI → many rows is normal** (one paper reports many lipids × temperatures
  × properties). A "Sources" page should group by DOI and show row counts
  (`source_doi_table.csv` already has this).

---

## Suggested site structure (starting point, not a mandate)

- **Explorer / table** — faceted filter on lipid_system, property, type,
  force_field, temperature range; each row links to its DOI. This is the core.
- **Property vs. temperature** — scatter, one facet per lipid, exp vs sim by
  color/shape (mirror `fig_apl_vs_temp.png` but interactive with hover→source).
- **Coverage** — values-per-lipid, split by property and type (mirror
  `fig_coverage.png`).
- **Compare** — pick a (lipid, property, temperature bin); show every reported
  value with its source and the consensus spread. This is where "disagreement is
  the feature" pays off.
- **Sources / About** — driven by `source_doi_table.csv` and `lipid_db_report.md`.

Recommended stack for a static, source-linked dataset this size: a static site
(Vite/Next static export or plain React) that loads the CSV (or a build-time JSON
conversion) and filters client-side. No backend required. Keep the CSV as the
committed source of truth; generate JSON/derived tables in a build step so the
provenance stays inspectable in git.

---

## Extending the database later

- Add a new property by first adding its term to the vocabulary in
  `lipid_db_schema.md` **in the same change** that introduces its first row.
- New rows must carry a `source_doi` (or `source_citation` if the source truly
  has no DOI). No value enters without provenance.
- After adding rows, regenerate `lipid_consensus_summary.csv` and the figures.
- The full vocabulary in `lipid_db_schema.md` lists properties, methods, phases,
  and units that are defined but not yet populated (e.g. `thickness_DHH`,
  `volume_lipid`, `Tm`, `diffusion_lateral`, gel phases, coarse-grained MD). The
  UI's filters should be built from the *data present*, but the schema tells you
  what may appear as coverage grows.
