# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

A Home Assistant custom integration (`custom_components/nps_parks`) that tracks visits to US National Parks/NPS sites via the National Park Service API. Distributed through HACS. A companion Lovelace card lives in a separate repo (`FCjosh/lovelace-nps-parks-card`); a built copy of it is vendored at `config/www/nps-parks-card.js` for the dev instance only.

## Commands

- `scripts/setup` — installs Python requirements (`requirements.txt`) and the Claude Code CLI. Run once, e.g. after container creation.
- `scripts/develop` — creates `config/` (a scratch Home Assistant instance) if missing via `hass --script ensure_config`, adds `custom_components` to `PYTHONPATH`, then runs `hass --config ./config --debug`. This is how you run a live HA instance against your working copy of the integration without symlinks. It blocks in the foreground — background it (e.g. `nohup scripts/develop > /tmp/ha.log 2>&1 &`) to poll logs/curl instead of waiting on it. Home Assistant will be reachable on port 8123.
  - **First boot after a fresh devcontainer is expected to log errors for `camera`/`stream`/`frontend`/`cloud`** (`ModuleNotFoundError` for `numpy`, `hass_frontend`, `av`, etc.) — `default_config` pulls those in, and their extra pip deps aren't preinstalled, so HA pip-installs them mid-boot but the same boot's import attempt loses the race (and/or hits a stale import-path cache) even though the packages land on disk successfully. Just kill and restart `scripts/develop` once; the second boot finds everything already installed and comes up clean, including the frontend (verify with `curl -s -o /dev/null -w '%{http_code}' http://localhost:8123/` → `200`).
  - `go2rtc` will keep failing every boot with "Could not find go2rtc docker binary" — that's just this devcontainer lacking the go2rtc binary (used for camera streaming) and is unrelated to `nps_parks`; ignore it.
- `scripts/lint` — runs `ruff format .` then `ruff check . --fix`. This is the only lint/test command in the repo; there is no separate test suite or type-check command.
- Repo is meant to be opened in the devcontainer defined by `.devcontainer.json` (Python 3.14, Node, ffmpeg/libturbojpeg/libpcap for HA deps); `scripts/setup` is the container's `postCreateCommand`.

CI (`.github/workflows/lint.yml`) runs `ruff check .` and `ruff format . --check` on Python 3.14. `.github/workflows/validate.yml` runs `hassfest` and `hacs/action` validation (integration manifest/structure checks) on push, PR, and a daily cron — keep `manifest.json` and `hacs.json` valid.

## Architecture

Standard HA integration shape, entry point `custom_components/nps_parks/__init__.py`:

- **`coordinator.py`** — `NPSParksCoordinator(DataUpdateCoordinator)` is the single source of truth. On each refresh it hits `BASE_URL` (`https://developer.nps.gov/api/v1/parks`, `limit=500`) with the user's API key and stores the raw list of NPS site dicts as coordinator data. Also owns an `NPSParksStorage` instance and transient UI state (`tracked_park_codes`, `selected_park_code`). Update cadence is read from config entry options (`CONF_UPDATE_INTERVAL`) via `UPDATE_INTERVAL_MAP` in `const.py`.
- **`data.py`** — `NPSParksStorage` wraps `homeassistant.helpers.storage.Store` (key `nps_parks.visited`) to persist the set of visited park codes across restarts, independent of coordinator refreshes.
- **`entity.py`** — `NPSParksEntity(CoordinatorEntity)` base class; all entities share one `DeviceInfo` (a single "NPS Parks" device — there is no per-park device).
- **Platforms** (`sensor.py`, `select.py`, `button.py`) all read `entry.runtime_data` (the coordinator) rather than `hass.data`.
  - `sensor.py`: one `NPSParksSensor` per tracked park site (state = `visited`/`unvisited`, attributes = lat/long parsed out of the API's `latLong` string, description, designation, states, url, first image) plus four `NPSParksStatsSensor` aggregates (total/visited/unvisited/percentage). Entity set is filtered by the `CONF_DESIGNATIONS` option; when designations change, sensors for now-excluded parks are actively removed from the entity registry (not just skipped) in `async_setup_entry`.
  - `select.py`: single searchable dropdown entity (`NPSParkSelectEntity`) mapping full park name → park code, used to pick a park for the mark-visited/unvisited buttons.
  - `button.py`: refresh button (`coordinator.async_request_refresh`) and mark-selected-visited/unvisited buttons that act on `coordinator.selected_park_code` and then call `coordinator.async_set_updated_data(coordinator.data)` to push a state refresh without re-fetching from the API.
- **`services.py`** / **`services.yaml`** — registers `nps_parks.mark_visited` / `nps_parks.mark_unvisited`, taking a `park_code` string directly (usable from automations without needing the select/button UI).
- **`config_flow.py`** — single required field (API key), validated by making a live `limit=1` request to the NPS API before saving. Options flow lets the user change update interval and designation filter after setup; changing options triggers `async_reload_entry` (full reload) via `__init__.py`.

### Designation grouping (`designations.py`)

The NPS API returns many free-text `designation` strings (e.g. "National Historic Site", "Memorial Parkway"). `DESIGNATION_GROUPS` maps a small set of user-facing group names (shown in the options flow, `NPS_DESIGNATIONS`) to the sets of raw API designation strings that belong to each group — this is the only place that knowledge lives, and it needs updating if the NPS API introduces a new designation string. `DESIGNATION_GROUP_EXCEPTIONS` handles specific `parkCode`s that should count toward a group despite having no matching (or blank) designation in the API (e.g. American Samoa, `npsa`, under "National Park"). `filter_parks(parks, selected_groups)` is the single shared entry point for applying this filter — both `sensor.py` (building tracked entities) and `select.py` (building the dropdown options) call it rather than re-deriving the included/excluded sets themselves.

## Code style

- Ruff is configured (`.ruff.toml`) with `select = ["ALL"]` against `home-assistant/core`'s own ruff config, targeting Python 3.14. Run `scripts/lint` before committing; CI enforces both check and format.
