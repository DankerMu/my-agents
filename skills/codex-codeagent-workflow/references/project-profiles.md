# Project Profiles

A project profile maps the generic risk packs and expanded-triggers in
`issue-risk-contract.md` onto one concrete project's surfaces. Profiles are
pluggable: pick the one that matches the repository, or use the **Generic**
profile. Nothing in the core workflow assumes a specific profile.

A profile contributes:

- entry surfaces (where changes and risk concentrate)
- contracts (what callers/consumers depend on)
- risk axes (how this kind of project breaks)
- typical evidence (what proves a change is safe)
- optional domain risk packs (added to the core packs)
- optional domain expanded-triggers (added to the core triggers)

Selection: in Phase 0 step 0, infer the profile from repo files (language,
build system, directory layout, manifests). Record it in the fixture as
`Project profile: <name>`. When no profile matches, use `Generic`.

## Generic (default)

- Entry surfaces: the changed files plus their direct callers and any public entrypoint they sit behind.
- Contracts: public API/function signatures, CLI flags, config keys, data schema/format, return shapes, persisted state.
- Risk axes: input validation, error/rollback paths, backward compatibility, concurrency/ordering, resource bounds, security/path safety.
- Typical evidence: build/lint, unit plus integration tests on touched modules, boundary/failure-case tests, unchanged-consumer regression.
- Domain risk packs: none beyond the core packs.
- Domain expanded-triggers: none beyond the core triggers.

Use Generic for ordinary application, service, library, or tooling repositories.
Extend it by writing a new profile section below when a domain has recurring
risk surfaces the core packs do not name.

## SHUD Solver

- Entry surfaces: `src/main.cpp`, `src/Model*`, `src/classes/*`, `Makefile`, example inputs.
- Contracts: model input files, config/control files, initial condition/restart files, output file names and units.
- Risk axes: numerical stability, CVODE/SUNDIALS integration, OpenMP/thread behavior, runtime performance, file output cadence, restart/IC compatibility, mass/water balance.
- Typical evidence: compile, small example run, output schema check, conservation/numerical sanity, crash/NaN guard.
- Domain risk packs: Numerical stability / conservation / NaN; Solver runtime / performance / threading.
- Domain expanded-triggers: `solver`, `CVODE`, `SUNDIALS`, `OpenMP`, `thread`, `restart`, `initial condition`.

## rSHUD Package

- Entry surfaces: `R/*`, `src/*`, `tests/testthat`, `DESCRIPTION`, exported functions.
- Contracts: R function signatures, return classes, column names, units, CRS, parser/writer formats, compatibility wrappers.
- Risk axes: public API compatibility, testthat/R CMD check, GIS geometry/CRS, timeseries parsing, SHUD input/output readers, Rcpp behavior, CRAN-sensitive dependencies.
- Typical evidence: focused testthat, `R CMD check` or package test command, parser round trip, fixture read/write.
- Domain risk packs: Geospatial / CRS / shapefile sidecars; Time series / forcing / temporal boundaries.
- Domain expanded-triggers: `Rcpp`, `S3`, `S4`, exported R function, compatibility wrapper, `CRS`, `geometry`, `projection`.

## AutoSHUD Pipeline

- Entry surfaces: `GetReady.R`, `Step*.R`, `Rfunction/*`, `SubScript/*`, `Example/*`.
- Contracts: project config, global/caller environment, Step artifacts, SHUD input files, GIS sidecars, forcing CSV and `meteoCov`.
- Risk axes: step ordering, legacy branch compatibility, `source()` environment, geospatial CRS/schema, NetCDF/raster discovery, file publish/rollback, external command paths.
- Typical evidence: focused Rscript tests, Step-style synthetic fixture, legacy branch smoke, output file/schema assertions.
- Domain risk packs: Geospatial / CRS / shapefile sidecars; Time series / forcing / temporal boundaries.
- Domain expanded-triggers: `NetCDF`, `raster`, `shapefile`, `CRS`, `geometry`, `projection`, `Step`, `config`, `global`, `source()`, generated SHUD input.

## Domain Risk Packs

These packs are contributed by scientific/geospatial profiles above. Add them to
the core Risk Packs only when the active profile lists them.

- Geospatial / CRS / shapefile sidecars
- Time series / forcing / temporal boundaries
- Numerical stability / conservation / NaN
- Solver runtime / performance / threading

## Adding a Profile

To target a new project family, add a section with the six profile fields above.
Keep domain packs and triggers in the profile, not in `issue-risk-contract.md`,
so the core contract stays portable.
