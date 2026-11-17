# Avatar Weather Card – picture sets

Ready-made picture sets for the [Avatar Weather Card](https://github.com/carlosteiner/avatar-weather-card) integration for Home Assistant.
All characters are invented; no picture shows a real person.

The integration reads `index.json` (*Settings → Picture sets → Get more sets*) and installs a set as a NEW set, so your own sets are never touched.
Each set is a zip with the pictures (`.webp`, transparent), `series.json` (name, author, licence, soles line of every picture) and `prompts.txt` (the prompt file used to generate them).

## Sets
See `index.json`. The zips are attached to the releases of this repository (tag `<id>-v<version>`), not stored in the code.

## Add or update a set
1. In the Home Assistant panel: *Settings → Picture sets → Rename / details* (name, author, **licence**, credits, version), then *Export zip*.
2. Create a GitHub release with the tag `<id>-v<version>` (e.g. `amanda-v1.0.0`) and attach the zip. `id` and `version` must match the `series.json` inside the zip, and name, author and licence must be filled in.
3. That is all: the *Update the catalog* action (`.github/workflows/update-index.yml`) checks the zip, writes size, sha256 and url into `index.json` and commits it to `main`. If the zip is not valid the action fails and its log says why. Deleting the release removes the set from the catalog.

`tools/update_index.py` is the script the action runs; it can also be run by hand (`python3 tools/update_index.py --zip <zip> --tag <id>-v<version> --repo <owner/repo>`).

Anyone can propose a set: open an issue or a pull request with the zip (or a link to it). Only share pictures you may share under the licence you state.
