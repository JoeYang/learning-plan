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
- [x] Understand hook events and when each fires:
  - `PreToolUse` (block dangerous actions), `PostToolUse` (auto-format after edits)
  - `Notification` (desktop alerts when Claude needs attention)
  - `Stop` (verify quality when Claude finishes)
  - `SessionStart` (inject context after compaction)
  - Also discovered: `PermissionRequest`, `SessionEnd`, `SubagentStart/Stop`, `PreCompact`, `Setup`, `TeammateIdle`, `TaskCompleted`
- [x] Set up hooks in `~/.claude/settings.json`:
  - Notification hook with sound (notify-send + paplay)
  - PermissionRequest hook with distinct sound
  - Stop hook to detect uncommitted code changes
- [x] Understand the three hook types: command (shell), prompt (Haiku LLM), agent (subagent)
- [x] Learn hook exit codes: 0 = allow, 2 = block (with reason on stderr)
- [x] Learned actual schema structure: event → matcher objects → hooks array (nested deeper than docs suggest)
**Notes:** Notification + PermissionRequest hooks with sound = high value, low cost. Stop hook as lightweight change detector is practical. Agent hooks on Stop are expensive overkill — better to invoke strict-code-reviewer explicitly when needed. Auto-format hooks are useful if you have a formatter; protected files hooks overlap with deny rules.

### Session 6: MCP Servers — Connecting External Tools (~1hr)
**Objective:** Connect Claude to tools beyond the filesystem
- [x] Understand MCP basics: what it is, three transport types (HTTP, SSE, stdio)
- [x] Set up GitHub MCP server:
  - Tried deprecated `@modelcontextprotocol/server-github` (stdio) — learned packages get deprecated fast
  - Tried Docker image `ghcr.io/github/github-mcp-server` — needed sudo
  - Switched to official HTTP transport: `api.githubcopilot.com/mcp/`
- [x] Learn scopes: local (personal), project (team), user (all projects)
- [x] Understand `@` mentions for MCP resources
- [x] Use `/mcp` to check server status — debugged connection failures
- [x] Understand `.mcp.json` and environment variable expansion (`${VAR}`)
  - Key lesson: `${VAR}` only expands from Claude Code's process env, not `.bashrc`
  - Fix: add tokens to `env` block in `settings.json`
**Notes:** GitHub (HTTP), database, and custom internal tool MCPs are the practical ones. Most public MCP servers are demos not daily drivers. Ecosystem moves fast — check for deprecations. Remote HTTP transport is simplest when available.

### Session 7: Custom Subagents (~1hr)
**Objective:** Create specialized agents for your recurring tasks
- [x] Understand built-in subagents: Explore (read-only search), Plan (read-only design), Bash (commands only), general-purpose (everything)
- [x] Create custom subagents:
  - `strict-code-reviewer` (sonnet, user memory, all tools) — via `/agents`
  - `doc-sync` (sonnet, user memory, all tools) — via `/agents`
  - `architecture-explainer` (sonnet, project memory, read-only tools) — hand-written
  - `read-only-researcher` — via `/agents`
- [x] Persistent memory: `user` scope for cross-project knowledge, `project` scope for repo-specific architecture
- [x] Tool restrictions: `allowedTools` in frontmatter. Read-only agents are safer for exploration.
- [x] Subagent vs direct: use subagents for specialized personas, parallel work, protecting main context. Ask directly for quick tasks needing conversation context.
**Notes:** Key design decisions: memory scope (user vs project), tool restrictions (read-only for safety), model choice (sonnet for speed/cost, opus for complex analysis). The description field is critical — it's how Claude decides when to auto-invoke the agent.

### Session 8: Skills & Custom Slash Commands (~1hr)
**Objective:** Create reusable commands for your team's conventions
- [x] Understand how skills work — markdown files with YAML frontmatter in `.claude/skills/`
- [x] Created custom skills:
  - `/commit` — conventional commit workflow (user scope)
  - `/pr` — structured PR creation (user scope)
- [x] Invokable via `/skill-name` in any session
- [x] Explored `.claude/rules/` — path-specific auto-injected instructions (e.g., different rules for `src/` vs `tests/`)
- [x] Understood skills vs agents vs rules: skills = reusable prompts, agents = separate context/persona, rules = automatic path-based context
**Notes:** Keep skills short and procedural. One skill = one workflow. Start with 2-3 for frequent tasks, add more only when you catch yourself repeating. Project-scope skills for team conventions, user-scope for personal workflows.

---

## Phase 3: Advanced Patterns (Weeks 5-6)

### Session 9: Plan Mode & Extended Thinking (~1hr)
**Objective:** Know when to slow Claude down for better results
- [x] Plan mode workflow: Shift+Tab → read-only exploration → produce plan → approve → implement
  - Claude can Read/Glob/Grep/WebSearch but NOT Edit/Write/Bash
  - Best for: multi-file refactoring, unfamiliar codebases, risky changes, architectural decisions
  - Not worth it for: single file edits, clear instructions, mechanical changes
- [x] Extended thinking (Option/Alt+T): explicit reasoning phase before responding
  - Best for: complex bugs, multi-file dependencies, architectural tradeoffs, algorithm implementation
  - Not worth it for: formatting, renaming, boilerplate, simple tasks
- [x] Effort levels (/model): low/medium/high reasoning depth, separate from thinking toggle
  - Low = fast/cheap, High = thorough, combine with thinking for maximum analysis
- [x] Practical patterns: investigate-then-implement, thinking-for-debugging, plan-review-execute, effort-for-cost-control
**Notes:** Plan mode is valuable because YOU get to review before code is touched — it's a checkpoint. Thinking helps when you'd need to think hard yourself. Both add latency and cost — use for hard problems, skip for mechanical tasks.

### Session 10: Agent Teams & Parallel Work (~1hr)
**Objective:** Understand multi-agent coordination for complex tasks
- [x] Enable agent teams: set `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` in settings
- [x] Try a simple team task:
  - Spawned teacher + tutor agents, observed coordination via task lists and messages
  - Experienced live team: lead coordinating, routing messages, shutting down agents
- [x] Learn display modes: in-process (`Shift+Up/Down`), tmux (split panes)
- [x] Understand when teams help vs when a single agent is better
- [x] Try git worktrees for truly parallel work on separate branches
**Notes:** Teams shine for parallel independent work (4+ hours, clean splits). Single agent better for tightly coupled tasks, debugging, quick fixes (< 1hr). tmux mode configured via `"teammateMode": "tmux"` in settings. Coordination overhead is real — messaging latency, context duplication, sync delays. Worktrees eliminate branch-switching overhead for parallel work.

### Session 11: Headless Mode & Automation (~1hr)
**Objective:** Use Claude Code programmatically in scripts and CI/CD
- [x] Run basic headless commands: `claude -p "Summarize this project"`
- [x] Try structured output: `claude -p "..." --output-format json`
- [x] Use `--allowedTools` to restrict what headless Claude can do
- [x] Try continuing conversations: `--resume` with session IDs
- [x] Experiment with `--append-system-prompt` for per-run instructions
- [x] Brainstorm: where could you use headless Claude in your workflow?
  - Pre-commit code review
  - Automated PR descriptions
  - Test generation on file changes
  - Documentation updates
**Notes:** `-p` flag is the key to headless mode. `--output-format json` gives parseable results with cost, session_id, and error status. `--allowedTools` is critical for safety in CI — restrict to read-only for reviews. `--resume` with session IDs enables multi-step stateful workflows. `--append-system-prompt` adds per-run instructions on top of CLAUDE.md. Sweet spot for automation: tasks too nuanced for linters but too tedious for humans. Always weigh cost, frequency, reliability, and whether a deterministic tool could do it instead.

### Session 12: Context Management & Performance (~1hr)
**Objective:** Master the art of keeping Claude effective in long sessions
- [x] Study context window usage with `/context` visualization
- [x] Practice strategic compaction: `/compact Focus on X, discard Y`
- [x] Understand how `SessionStart` hooks can re-inject context after compaction
- [x] Learn when to start a fresh session vs compact vs continue
- [x] Try `@` file references to include specific files in your prompt
- [x] Experiment with prompt structure — what gets better results?
  - Goal-first vs context-first
  - Short specific prompts vs detailed instructions
  - "Explore then implement" vs "just do it"
**Notes:** `/context` shows token breakdown by category — system, tools, messages, free space. Strategic `/compact` with focus instructions beats auto-compaction: tell it what to keep and what to drop. `SessionStart` hooks re-inject critical context after compaction or resume — use for dynamic state (git branch, recent commits). Decision framework: continue under 50%, compact at 50-70% when pivoting, fresh session at 70%+ or when confused. `@file` references inline files directly — no tool overhead, predictable context usage. Prompt structure: goal-first, be as short as possible but as detailed as necessary, explore before implementing in unfamiliar territory.

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
