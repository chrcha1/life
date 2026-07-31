# The Weave

A one-page life dashboard, hosted on GitHub Pages, with `data.json` in this repo as the database. Two ways it changes: a daily brain-dump chat with Claude reweaves the page, and the app itself writes directly to the repo (checkboxes, vocabulary, game results) when sync is on.

Live at **https://chrcha1.github.io/life/** — open it on your phone → Share → **Add to Home Screen** and it installs as an app.

## Sync (the "database")

Reads are public (it's just `data.json` on Pages). Writes go through the GitHub API with a token you save once per device:

1. [Create a fine-grained personal access token](https://github.com/settings/personal-access-tokens/new) — Repository access: **only `life`** → Permissions → **Contents: read & write**. Nothing else.
2. On the dashboard, tap **Sync**, paste it, save.

From then on that device reads the freshest `data.json` straight from the API and pushes every change as a commit (`app sync: N changes`). Offline or token-less devices queue changes in localStorage and flush them when sync comes back. Concurrent writes are safe: the app refetches, replays its pending changes on top, and retries once on conflict.

## Vocabulary builder

- **Add words** the moment you see them — word, optional definition, optional "where I saw it". Games work best with a definition.
- **Daily round**: words come due on a spaced-repetition schedule (Leitner boxes 1–5; intervals 1 / 2 / 4 / 7 / 14 days). The round mixes question types: pick the meaning, pick the word, type the word from its definition (box 3+), and self-graded recall for words without definitions.
- Right answer → up a box, longer until you see it again. Wrong → back to box 1, returns tomorrow.
- The round is date-seeded, so it's the same round on every device all day. Nothing due? Play a practice round (doesn't touch the schedule).
- Rounds stitch a green thread into the weave and build their own review streak.
- All of it lives in the `vocab` section of `data.json`. **Claude is told at check-in to pass this section through untouched** — the app owns it.

## The daily loop

1. Tap **Check in with Claude**. It opens a Claude chat pre-filled with what you checked off and jotted today.
2. Talk out your brain dump (voice works great on mobile).
3. Claude hands back a complete new `data.json`; commit it (or, with sync on, most of the mechanical state is already committed — Claude's job is the curation: sorting the dump, clearing done items, weaving the day's row).

## How the pieces fit

- **`data.json`** — everything: calendar, routine, brain dump, quick wins, open loops (weight 1–3), want-to-dos, project ideas, questions, vocabulary, weave history.
- **Checkboxes** — with sync on they commit immediately (`done: true`, `doneAt` stamped); without it they live in localStorage until the next check-in.
- **Jots** — stay on-device and ride along on the next check-in; Claude folds them in.
- **The weave** — one cell per day; thread colors record the kind of day: moss = brain dump, amber = quick win, clay = loop closed, rust = did a want-to, sand = project time, sage = vocab round.
- **`sw.js`** — offline support. Shell and data are network-first, so updates land immediately; the cache is only a fallback. If you change the shell, bump `CACHE` (`weave-v2` → `weave-v3`).

## Notes

- This repo is public (GitHub Pages on a free plan requires it) — keep anything truly private out of the brain dump, or move to a private repo with GitHub Pro.
- Starter vocabulary words are marked "delete freely."
