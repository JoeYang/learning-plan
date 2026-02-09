# Learning Plan: Claude Code Mastery

**Start date:** 2026-02-09
**Target completion:** Ongoing (evolving topic)
**Schedule:** ~2 hours/week, flexible
**Status:** in-progress

> This is a living plan. Claude Code ships features fast — sessions may be reordered, added, or replaced as the tool evolves. The goal is broad coverage, not rigid sequencing.

---

## Phase 1: Foundations & Daily Workflow (Weeks 1-2)

### Session 1: Keyboard Shortcuts & Navigation (~1hr)
**Objective:** Build muscle memory for the shortcuts you'll use every day
- [x] Learn and practice core shortcuts:
  - `Ctrl+C` (cancel), `Ctrl+L` (clear screen), `Ctrl+O` (verbose output)
  - `Shift+Tab` (cycle permission modes: normal → plan → auto-accept)
  - `Option/Alt+P` (switch model), `Option/Alt+T` (toggle extended thinking)
  - `Ctrl+G` (edit in external editor — great for long prompts)
  - `Ctrl+B` (background running task), `Ctrl+T` (toggle task list)
  - `Esc Esc` (rewind/summarize)
  - `Up/Down` arrows for command history, `Ctrl+R` for reverse search
- [x] Try vim mode (`/vim`) — decide if it fits your workflow
- [x] Try `!` prefix for quick bash commands without Claude processing
- [x] Run `/terminal-setup` to enable enhanced key support (Shift+Enter for multiline, etc.)
**Notes:** List which shortcuts you actually use vs which feel forced

### Session 2: Slash Commands & Session Management (~1hr)
**Objective:** Know what every slash command does so you reach for the right one
- [x] Run through all slash commands — try each one at least once:
  - `/status`, `/cost`, `/context` (understand your usage)
  - `/compact [focus]` (compress context — try with and without focus instructions)
  - `/model` (switch models mid-session, adjust effort level)
  - `/resume` (session picker — learn filters: `P` preview, `R` rename, `/` search, `B` branch filter)
  - `/rename` (name your sessions for easy resumption)
  - `/rewind` (checkpoint management — undo changes)
  - `/export` (save conversations)
  - `/copy` (copy last response to clipboard)
  - `/stats` (usage patterns and streaks)
  - `/debug` (troubleshoot when things go wrong)
  - `/doctor` (health check)
- [x] Practice session workflow: start → name → work → compact → resume next day
**Notes:** Which commands will you use daily vs occasionally?

### Session 3: CLAUDE.md & Project Configuration (~1hr)
**Objective:** Set up CLAUDE.md properly — this is the single biggest lever for quality
- [x] Study the three CLAUDE.md scopes:
  - `CLAUDE.md` or `.claude/CLAUDE.md` — project-level, shared with team
  - `~/.claude/CLAUDE.md` — user-level, all projects
  - `.claude/CLAUDE.local.md` — personal overrides, not committed
- [x] Write a CLAUDE.md for one of your projects covering:
  - Architecture overview (what the system does, key components)
  - Tech stack and conventions (language, frameworks, patterns)
  - Key file locations (where to find what)
  - Common commands (build, test, run, deploy)
  - Things Claude should know (gotchas, preferences, rules)
- [x] Write a `~/.claude/CLAUDE.md` for your personal preferences across all projects
- [ ] Use `/memory` to edit CLAUDE.md from within a session
**Notes:** Before/after comparison — does Claude give better responses with good CLAUDE.md?

### Session 4: Permissions & Safety (~1hr)
**Objective:** Understand the permission system so you can be fast without being reckless
- [x] Study permission modes and when to use each:
  - **default** — prompt for each action (safe, slow)
  - **plan** — read-only exploration (safest for investigation)
  - **acceptEdits** — auto-approve file edits (good for trusted refactoring)
  - **bypassPermissions** — auto-approve everything (use carefully)
- [x] Configure allow/deny rules in settings:
  - Allow common safe commands: `Bash(npm test)`, `Bash(npm run build)`, etc.
  - Deny dangerous patterns: `Read(.env*)`, `Bash(rm -rf *)`
- [x] Learn the rule syntax: prefix match, glob patterns, domain restrictions
- [x] Practice switching modes with `Shift+Tab` during a real task
- [x] Explore `.claude/settings.json` vs `.claude/settings.local.json` vs `~/.claude/settings.json`
**Notes:** What's your default mode? What rules did you add?

---

## Phase 2: Extending Claude Code (Weeks 3-4)

### Session 5: Hooks — Automated Guardrails & Workflows (~1hr)
**Objective:** Use hooks to make certain things always happen, without relying on prompts
- [ ] Understand hook events and when each fires:
  - `PreToolUse` (block dangerous actions), `PostToolUse` (auto-format after edits)
  - `Notification` (desktop alerts when Claude needs attention)
  - `Stop` (verify quality when Claude finishes)
  - `SessionStart` (inject context after compaction)
- [ ] Set up your first hooks using `/hooks` interactive menu:
  - Desktop notification hook (get alerted when Claude needs input)
  - Auto-format hook (run prettier/formatter after file edits)
  - Protected files hook (block edits to .env, lock files, etc.)
- [ ] Understand the three hook types: command (shell), prompt (Haiku LLM), agent (subagent)
- [ ] Learn hook exit codes: 0 = allow, 2 = block (with reason on stderr)
**Notes:** Which hooks are worth the setup? Which are over-engineering?

### Session 6: MCP Servers — Connecting External Tools (~1hr)
**Objective:** Connect Claude to tools beyond the filesystem
- [ ] Understand MCP basics: what it is, three transport types (HTTP, SSE, stdio)
- [ ] Set up at least one MCP server:
  - GitHub MCP (if not already using gh CLI)
  - A database MCP (if relevant to your work)
  - Or browse available servers and pick one relevant to you
- [ ] Learn scopes: local (personal), project (team), user (all projects)
- [ ] Try `@` mentions for MCP resources: `@github:repos/...`, `@postgres:schema://...`
- [ ] Use `/mcp` to check server status and authenticate
- [ ] Understand `.mcp.json` and environment variable expansion (`${VAR}`)
**Notes:** Which integrations are actually useful vs cool-but-not-worth-it?

### Session 7: Custom Subagents (~1hr)
**Objective:** Create specialized agents for your recurring tasks
- [ ] Understand built-in subagents: Explore (fast search), Plan (architecture), Bash, General-purpose
- [ ] Create a custom subagent using `/agents` or by writing a markdown file in `.claude/agents/`:
  - Define name, description, allowed tools, model
  - Write a focused system prompt for a task you do often (code review, test writing, etc.)
- [ ] Try persistent memory for subagents (`memory: user` or `memory: project`)
- [ ] Experiment with tool restrictions — what happens when a subagent has limited tools?
- [ ] Compare: when should you use a subagent vs just asking Claude directly?
**Notes:** What custom agents are worth maintaining?

### Session 8: Skills & Custom Slash Commands (~1hr)
**Objective:** Create reusable commands for your team's conventions
- [ ] Understand how skills work — markdown files with YAML frontmatter
- [ ] Create a custom skill for something you do repeatedly:
  - Commit convention enforcer
  - PR creation template
  - Code review checklist
  - Test generation pattern
- [ ] Try using skills from within a session with `/skill-name`
- [ ] Explore `.claude/rules/` for path-specific rules (e.g., different rules for `src/` vs `tests/`)
**Notes:** Skills that saved time vs skills that were more work to maintain than they're worth

---

## Phase 3: Advanced Patterns (Weeks 5-6)

### Session 9: Plan Mode & Extended Thinking (~1hr)
**Objective:** Know when to slow Claude down for better results
- [ ] Practice plan mode workflow:
  - Start with `Shift+Tab` to enter plan mode
  - Explore codebase, ask clarifying questions
  - Review the plan Claude produces
  - Approve and switch to implementation mode
- [ ] Try extended thinking (`Option/Alt+T`) on a genuinely hard problem:
  - Complex architectural decision
  - Tricky bug with multiple possible causes
  - Multi-file refactoring
- [ ] Experiment with effort levels for Opus 4.6 (low/medium/high)
- [ ] Compare results: same problem with vs without extended thinking
**Notes:** When does plan mode / thinking mode actually help vs just slow you down?

### Session 10: Agent Teams & Parallel Work (~1hr)
**Objective:** Understand multi-agent coordination for complex tasks
- [ ] Enable agent teams: set `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` in settings
- [ ] Try a simple team task:
  - Spawn 2-3 agents for different aspects of a review or implementation
  - Observe how they coordinate via task lists and messages
- [ ] Learn display modes: in-process (`Shift+Up/Down`), tmux (split panes)
- [ ] Understand when teams help vs when a single agent is better
- [ ] Try git worktrees for truly parallel work on separate branches
**Notes:** Is the coordination overhead worth it? For what types of tasks?

### Session 11: Headless Mode & Automation (~1hr)
**Objective:** Use Claude Code programmatically in scripts and CI/CD
- [ ] Run basic headless commands: `claude -p "Summarize this project"`
- [ ] Try structured output: `claude -p "..." --output-format json`
- [ ] Use `--allowedTools` to restrict what headless Claude can do
- [ ] Try continuing conversations: `--resume` with session IDs
- [ ] Experiment with `--append-system-prompt` for per-run instructions
- [ ] Brainstorm: where could you use headless Claude in your workflow?
  - Pre-commit code review
  - Automated PR descriptions
  - Test generation on file changes
  - Documentation updates
**Notes:** What automation is worth building?

### Session 12: Context Management & Performance (~1hr)
**Objective:** Master the art of keeping Claude effective in long sessions
- [ ] Study context window usage with `/context` visualization
- [ ] Practice strategic compaction: `/compact Focus on X, discard Y`
- [ ] Understand how `SessionStart` hooks can re-inject context after compaction
- [ ] Learn when to start a fresh session vs compact vs continue
- [ ] Try `@` file references to include specific files in your prompt
- [ ] Experiment with prompt structure — what gets better results?
  - Goal-first vs context-first
  - Short specific prompts vs detailed instructions
  - "Explore then implement" vs "just do it"
**Notes:** What context management strategies actually work for you?

---

## Phase 4: Ongoing Mastery (Week 7+)

_This phase is intentionally open-ended. Add sessions as new features ship or as you discover gaps in your workflow._

### Ideas for future sessions:
- [ ] Chrome integration (`claude --chrome`) for web testing
- [ ] Output styles — create custom response formats
- [ ] Plugin system — install and create plugins
- [ ] Team configuration — shared settings, skills, and agents for collaborative projects
- [ ] IDE-specific features deep dive (VS Code or JetBrains)
- [ ] Debugging Claude Code itself (`/debug`, `/doctor`, verbose mode)
- [ ] Cost optimization — when to use Haiku vs Sonnet vs Opus
- [ ] Security hardening — sandboxing, network restrictions, managed configs
- [ ] New features as they release (check changelog periodically)
