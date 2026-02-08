# Learning Plan

A personal learning repo for tracking self-study across multiple topics with structured 2-hour daily sessions.

## How It Works

Everything is markdown. No build tools, no apps — just files and git.

### Folder Structure

```
learning-plan/
├── README.md          # This file
├── PROGRESS.md        # Central dashboard: all topics, status, % complete
├── topics/            # One file per topic (the "input")
│   └── _template.md   # Copy this to create a new topic
├── plans/             # Generated 2hr/day learning plans (the "output")
├── log/               # Daily learning journal (one file per day)
└── completed/         # Archive of finished topics + plans
    ├── topics/
    └── plans/
```

## Workflow

### 1. Add a Topic

```bash
cp topics/_template.md topics/<topic-name>.md
```

Fill in the template with your motivation, current level, and goals. Use kebab-case for filenames (e.g., `rust-ownership.md`, `distributed-systems.md`).

### 2. Get a Plan

Ask Claude to read the topic file and generate a day-by-day learning plan:

> "Read `topics/rust-ownership.md` and generate a 2hr/day learning plan in `plans/`"

Claude will create `plans/rust-ownership.md` with daily sessions, checkboxes, and resources.

### 3. Schedule It

Claude assigns days to specific weekdays based on your active topic count. With 2-3 topics running in parallel, each topic gets 2-3 sessions per week:

- **2 topics:** Topic A on Mon/Wed/Fri, Topic B on Tue/Thu
- **3 topics:** Topic A on Mon/Thu, Topic B on Tue/Fri, Topic C on Wed/Sat

### 4. Daily Work

1. Open `plans/<topic-name>.md`, find your current day
2. Follow the tasks, check them off as you go
3. Write a log entry in `log/YYYY-MM-DD.md`

### 5. Track Progress

Ask Claude to update `PROGRESS.md` after each session or when generating/updating plans. The dashboard shows all active topics, completion percentage, and what's next.

### 6. Complete a Topic

When all days are checked off:

```bash
mv topics/<topic-name>.md completed/topics/
mv plans/<topic-name>.md completed/plans/
```

Then update `PROGRESS.md` to move the topic to the "Completed" table.

## Conventions

- **Filenames:** kebab-case, e.g., `rust-ownership.md`
- **Session length:** 2 hours per day
- **Parallel topics:** 2-3 at a time (more gets hard to sustain)
- **Log entries:** One file per day, even if you work on multiple topics
- **Dates:** YYYY-MM-DD format everywhere
