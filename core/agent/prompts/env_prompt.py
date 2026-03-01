ENVIRONMENT_PROMPT = """\
<environment>
The vault is a folder of markdown files on the local filesystem. Every file has YAML
frontmatter with `created`, `updated`, and `tokens` fields. The vault is the single
source of truth — everything the user has ever stored lives here, structured and searchable.

Here is what each part of the vault contains and what kind of answers you will find there.

**`overview.md`** — The map of everything in the vault. Lists all projects with short
descriptions and their status, current life context, pre-project intentions, and inbox count.
This is already in your context at session start. It tells you which projects exist,
what each one is about, and where things stand — before you open a single file.
When a user asks "what projects are active?" or "is there anything about X?",
overview.md is your first orientation point.

**`profile.md`** — The user's durable identity: preferences, work habits, communication style,
recurring constraints. Already in your context. Use it to calibrate your response tone
and understand the person you are serving.

**`changelog.md` (global)** — Events and decisions at the global level — not tied
to any one project. Life pivots, meta-decisions, cross-project themes.
Format: H1 per day (`# 2025-07-14`), H2 per entry, newest first.
Decisions are tagged `[décision]` in the H2. This grows indefinitely and is never archived.

**`tasks.md` (global)** — Active tasks not tied to a specific project, or cross-project tasks.
Format: H1 per task with inline metadata (`status: en-cours | prio: haute | ajoutée: 2025-07-14`).
This is a live view — only active tasks exist here. Completed tasks have been removed
and live on as events in changelogs.

**`inbox/`** — Folders of items awaiting user resolution. Each folder contains a `review.md`
with a previous agent's reasoning and the original input files. This is temporary content —
not indexed in search. If you need to look at inbox contents, use `tree` and `read` directly.

**`bucket/` (global)** — Raw data storage: emails, transcriptions, articles, screenshots, notes.
Things that entered the system as-is. Each item is a markdown file with frontmatter.

**Project files (`projects/[name]/`)** — Each project always contains the same structure:

`description.md` — What the project is, why it exists, its scope, its structural decisions.
Read this to understand what a project is about at a deep level.

`state.md` — Volatile snapshot of right now: current status (actif/pause/bloqué/terminé),
current focus, what's validated, what's blocking, active deadlines.
This is the file that answers "where does this project stand?"

`tasks.md` — Same format as global tasks, scoped to this project only.

`changelog.md` — Same format as global changelog, scoped to this project.
The complete history: meetings, decisions, updates, milestones. Everything that ever
happened on this project is here, newest first.

`bucket/` — Project-specific raw data. Same nature as the global bucket, but scoped.

**What is indexed in search — and therefore findable via the `search` tool:**
All changelogs (global + project), all tasks (global + project), all descriptions,
all states, all buckets (global + project).

**What is NOT indexed — and must be accessed via `read` or `tree` directly:**
overview.md, profile.md, everything in inbox/.
These files are either always in your initial context or are temporary content.
</environment>"""