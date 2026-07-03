# Lipid Membrane Property Database — Schema & Data Dictionary

**Design principle:** one row = one reported property value from one source at one
condition. Disagreements between sources, methods, or temperatures are preserved as
separate rows and never averaged away. Reconciliation happens in a derived summary
table, not by editing raw rows.

File: `lipid_properties.csv`

## Columns

| column | type | required | description |
|---|---|---|---|
| `entry_id` | int | yes | Stable unique row id (monotonic). |
| `lipid_system` | str | yes | Canonical human-readable system. Single: `POPC`. Mixture: `POPC:CHOL (4:1)`, `POPC:POPE (3:1)`. |
| `lipid_components` | str | yes | Pipe-separated component list. `POPC` or `POPC\|CHOL`. Enables per-component queries. |
| `composition` | str | no | Molar ratio for mixtures, e.g. `4:1`, `70:30`. Blank for single-component. |
| `property` | enum | yes | See **Property vocabulary**. |
| `value` | float | yes | Numeric value in the stated `unit`. |
| `unit` | enum | yes | See **Unit vocabulary**. |
| `uncertainty` | float | no | Reported ± error (same unit). Blank if none given. |
| `temperature_C` | float | yes | Temperature in °C. Convert from K on ingest. |
| `phase` | enum | no | `Lalpha` (fluid/liquid-crystalline), `Lbeta`/`Lbeta'` (gel), `LC` (crystalline), `Lo`, `Ld`, `HII`. |
| `hydration` | str | no | `fully_hydrated`, `excess_water`, `RH_97`, `<n>_waters_per_lipid`. |
| `type` | enum | yes | `experimental` or `computational`. |
| `method` | enum | yes | See **Method vocabulary**. |
| `force_field` | str | cond. | Required when `type=computational`. e.g. `CHARMM36`, `Slipids`, `Lipid17`, `MARTINI2`, `MARTINI3`, `GROMOS-CKP`, `Berger`. Blank for experimental. |
| `source_doi` | str | yes* | DOI without the `https://doi.org/` prefix. `*` blank only for databank/book entries lacking a DOI — then fill `source_citation`. |
| `source_citation` | str | yes | Short form `FirstauthorYYYY`, e.g. `Kucerka2011`. |
| `source_locator` | str | no | Where in the source: `Table 2`, `Fig 3`, `p. 3079`, databank record id. |
| `extraction_confidence` | enum | yes | `high` (value read directly from a table), `medium` (read from text/figure), `low` (estimated/digitized from a plot). |
| `notes` | str | no | Free text: caveats, unit conversions applied, related-row cross-refs. |
| `date_added` | date | yes | ISO date the row was added. |

## Property vocabulary (`property`)

| value | meaning | usual unit |
|---|---|---|
| `area_per_lipid` | Area per lipid (APL), A_L | `A^2` |
| `thickness_DB` | Bilayer thickness, Luzzati D_B (= V_L / A_L × 2) | `nm` or `A` |
| `thickness_DHH` | Head-to-head thickness (electron-density peak-to-peak), D_HH | `nm` or `A` |
| `thickness_2DC` | Hydrocarbon thickness, 2·D_C | `nm` or `A` |
| `thickness_Dpp` | Phosphate-to-phosphate distance | `nm` or `A` |
| `thickness_dHH_steric` | Steric / Luzzati D' where distinguished | `nm` or `A` |
| `volume_lipid` | Lipid molecular volume, V_L | `A^3` |
| `order_param_SCD` | |S_CD| deuterium order parameter (specify carbon in notes) | `dimensionless` |
| `order_param_SCD_plateau` | Plateau |S_CD| of the acyl-chain region | `dimensionless` |
| `Kc` / `bending_modulus` | Bending rigidity κ_c | `J` or `kT` |
| `KA` / `area_compressibility` | Area compressibility modulus K_A | `mN/m` |
| `diffusion_lateral` | Lateral diffusion coefficient D_lat | `um^2/s` or `cm^2/s` |
| `Tm` | Main gel–fluid transition temperature | `C` |

Extend this list as recurring properties appear; add the new term here in the same edit
that introduces its first row.

## Unit vocabulary (`unit`)

`A^2`, `A^3`, `A`, `nm`, `nm^2`, `dimensionless`, `mN/m`, `J`, `kT`, `um^2/s`, `cm^2/s`, `C`.
Store the value in the unit as reported; note any conversion in `notes`. Angstrom and nm
thickness rows may coexist — the reconciliation step normalizes for comparison.

## Method vocabulary (`method`)

**Experimental**
- `SAXS` — small-angle X-ray scattering
- `SANS` — small-angle neutron scattering
- `SAXS+SANS_SDP` — joint refinement, scattering-density-profile model (Kučerka/Nagle)
- `XRAY_diffraction` — lamellar X-ray diffraction (older electron-density profiles)
- `2H-NMR` — deuterium NMR order parameters
- `1H-NMR` / `NMR_relaxation`
- `neutron_diffraction`
- `densitometry` — molecular volume from density
- `micropipette` — micropipette aspiration (K_A, κ_c)
- `flicker_spectroscopy` — thermal shape fluctuations (κ_c)
- `FRAP` / `SPT` — diffusion
- `DSC` — calorimetry (T_m)

**Computational**
- `MD_atomistic` — all-atom MD (force field in `force_field`)
- `MD_united_atom`
- `MD_coarsegrained` — CG MD (MARTINI etc.)
- `MC` — Monte Carlo
- method sub-technique for a derived property (e.g. splay-modulus method for κ_c) goes in `notes`.

## Conventions

- Temperatures stored in °C; K→°C = K − 273.15, noted if converted.
- For mixtures, `lipid_system` carries the ratio; `composition` repeats it machine-readably.
- Per-carbon S_CD profiles: store the **plateau** value as `order_param_SCD_plateau` and
  point `source_locator` at the full profile table rather than one row per carbon, unless a
  specific carbon is the quantity of interest (then `order_param_SCD` + carbon in `notes`).
- One DOI can produce many rows (multiple lipids/temperatures/properties) — expected.
