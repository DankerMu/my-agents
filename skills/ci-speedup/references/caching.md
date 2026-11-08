# Caching

A cache is worth what its restore saves minus what its restore costs. Measure both, because a 3 GB restore that takes 44 s in a job that only needs ruff is a net loss.

## Prefer the setup action's own cache

| Toolchain | Built-in cache | Notes |
|---|---|---|
| Node | `actions/setup-node` with `cache: npm` / `pnpm` / `yarn` | Caches the download store, not `node_modules`; `npm ci` still runs (~40–60 s on large trees) |
| Go | `actions/setup-go` | Module and build cache on by default (`cache: true`) |
| Python (uv) | `astral-sh/setup-uv` with `enable-cache: true` | Key includes the lockfile; `cache-suffix` separates differently sized environments |
| Python (pip) | `actions/setup-python` with `cache: pip` | Download cache only |
| Rust | `Swatinem/rust-cache@v2` | Caches `~/.cargo` and `target/`, prunes stale artifacts itself |

## When to cache the installed tree instead

When the install itself dominates, as with `npm ci` on a large lockfile, cache `node_modules` directly with `actions/cache`. Run the install only on a miss:

- **Key** = `runner.os` + runtime version + lockfile hash. Leave out any one of them and the job restores a tree built for another OS, ABI or lockfile.
- **No `restore-keys` fallback for an installed tree.** A partial match restores a tree that doesn't match the lockfile, and the job skips the install. Use fallbacks only for download caches, where a stale entry is merely slower.
- `templates/setup-toolchain.yml` implements this, together with the sized Python environments.

## Size the cache to the job

- **Jobs that run only linters** (ruff, vulture, eslint): install only the dev group, from its own cache (`cache-suffix`). They never restore the full environment.
- **Jobs that only build the frontend** don't restore Python, Rust or Go caches.
- **Caching `.venv` instead of the uv cache** rarely pays when the environment is large (CUDA wheels). `uv sync` from a warm uv cache takes seconds.

## The 10 GB repository quota

- Each repository gets 10 GB of Actions cache. Past that, GitHub evicts the least recently used entries, which can include the main-branch cache every job relies on.
- Main-branch caches are visible to all branches. A cache written by a PR (`refs/pull/N/merge`) can be restored only by that PR, so it is dead weight once the PR merges.
- **Stale candidates**, as listed by `ci_timings.py report`:
  - entries superseded by a newer key from the same family on the same ref, for example an old Python patch version or an old lockfile hash;
  - PR-scoped entries.
- **Deleting caches is outward-facing.** List the candidates with their sizes and reasons, and delete only after the user confirms: `gh cache delete <id> --repo OWNER/NAME`.

## Measuring cache effects honestly

- **The first run after a key change is cold by definition.** Every job pays the full install, as with `npm ci` taking 61 s on open-webui. It says nothing about the steady state.
- **Judge on at least two warm runs.** Runner variance reaches ±30%: the same Playwright group took 2.0 min on one run and 3.0 min on the next. Report medians over several runs, not one.
