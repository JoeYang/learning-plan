# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Repo Is

A markdown-only personal learning tracker. No build system, no code — just structured markdown files and git.

## Structure

- `topics/` — Topic definitions (copy `_template.md` to create new ones)
- `plans/` — Day-by-day learning plans (one per topic)
- `log/` — Daily journal entries (`YYYY-MM-DD.md`)
- `completed/` — Archive for finished topics and plans
- `PROGRESS.md` — Central dashboard with active/completed topic tables

## Conventions

- Filenames: kebab-case (e.g., `cpp-trading-systems.md`)
- Dates: YYYY-MM-DD everywhere
- Plan checkboxes: `- [ ]` for pending, `- [x]` for done
- When creating a new topic, match the format in `topics/_template.md`
- When creating a new plan, match the format in existing plans (header metadata, day-by-day sections with objectives, checkboxes, key concepts, resources)
- When updating progress, update both the plan checkboxes and the `PROGRESS.md` dashboard table (days done, percentage, next session)

## Workflow

When asked to mark sessions as done: update `- [ ]` to `- [x]` in the plan file, increment "Days Done" in `PROGRESS.md`, update the percentage, and advance "Next Session".

When asked to add a new topic: create both `topics/<name>.md` and `plans/<name>.md`, add a row to the Active Topics table in `PROGRESS.md`.

When a topic is completed: move files to `completed/topics/` and `completed/plans/`, move the row from Active to Completed in `PROGRESS.md`.

## Session Quiz

After each session, offer a 10-question interactive multiple-choice quiz using the AskUserQuestion tool (one question at a time). Quiz guidelines:

- Cover all topics from the completed session
- Mix question types: conceptual understanding, applied scenarios, and "what would you do" tradeoff questions
- 4 answer choices per question, one correct
- After each answer, give immediate feedback with a brief explanation (whether correct or not)
- At the end, report the final score (e.g., 8/10) and note any weak areas to review
- If the user scores below 7/10, suggest reviewing the missed topics before the next session
