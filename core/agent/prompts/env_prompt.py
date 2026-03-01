ENVIRONMENT_PROMPT = """\
<environment>
The vault is a local folder of markdown files — the single source of truth.
Every file has YAML frontmatter. The filesystem IS the database.

<vault-layout>
vault/
├── overview.md              ← map of everything: projects, life context, inbox count
├── profile.md               ← user's durable identity: preferences, constraints, style
├── tasks.md                 ← global active tasks (not tied to any project)
├── changelog.md             ← global events and decisions log
├── inbox/                   ← items awaiting user resolution (temporary)
│   └── YYYY-MM-DD-slug/
│       ├── review.md        ← agent's reasoning + proposed routing
│       └── [original files]
├── bucket/                  ← global raw data: emails, transcripts, articles, notes
│   └── *.md
└── projects/
    └── [project-name]/      ← repeatable structure, identical for every project
        ├── description.md   ← what it is, why it exists, scope, structural decisions
        ├── state.md         ← volatile snapshot: status, focus, blockers, deadlines
        ├── tasks.md         ← project-scoped active tasks
        ├── changelog.md     ← project history: meetings, decisions, updates
        └── bucket/          ← project-scoped raw data
            └── *.md
</vault-layout>

<file-reference>
**Root files**

`overview.md` — Lists all projects with descriptions and statuses, current life context,
pre-project intentions, inbox count. Loaded in your initial context as `<overview>`.
Updated via write when the map changes (new project, status change, life context shift).

`profile.md` — Stable user identity: work preferences, recurring constraints,
communication style. Loaded in your initial context as `<profile>`. Evolves rarely.

`changelog.md` — Global-level events and decisions not tied to a specific project.
H1 per day, H2 per entry, newest first. Grows indefinitely, never archived.

`tasks.md` — Active tasks not tied to a project, or cross-project tasks.
H1 per task with inline metadata. Live view only — completed tasks are removed
and become changelog events.

**Project files — identical structure in every `projects/[name]/`**

`description.md` — What the project is, why it exists, its scope and structural decisions.
Rewritten entirely (write) when the project's identity or direction changes.

`state.md` — Volatile snapshot of right now: status (actif/pause/bloqué/terminé),
current focus, what's validated, what's blocking, deadlines. Updated frequently via edit
on specific sections.

`tasks.md` — Same format as global tasks, scoped to this project.
Completed tasks disappear and become events in the project's changelog.

`changelog.md` — Same format as global changelog, scoped to this project.
Complete history of everything that ever happened on this project.

`bucket/` — Project-scoped raw data. Same nature as global bucket.
If a file concerns two projects, it is duplicated in both buckets. No cross-links.

**Inbox — `inbox/`**

Each subfolder is a pending item named `YYYY-MM-DD-description-courte`.
Contains the original input files plus a `review.md` with the agent's full reasoning:
what was searched, what was found, what's proposed, and the precise question for the user.
Temporary — deleted after resolution. Never indexed in search.

**Bucket — `bucket/`**

Raw data storage at both global and project level. Emails, transcriptions, articles,
screenshots, notes. Each item is a standalone .md file. Landing zone for content that
doesn't directly update a structured file.
</file-reference>

<formats>
**Changelog format (global and project):**
```
# 2025-07-14

## [décision] Abandon de l'API externe — build in-house
Raison et impact en quelques lignes.

## Specs reçues du client v2.1
Changements mineurs, pas d'impact planning.
```
H1 = date. H2 = entry. Tag `[décision]` on decision entries. Newest first.
Two H1 blocks with the same date are acceptable — they mark distinct update moments.

**Tasks format (global and project):**
```
# Appeler le comptable pour TVA Q3
status: en-cours | prio: haute | ajoutée: 2025-07-14 | projet: —

# Valider les maquettes avec Marie
status: à-faire | prio: haute | ajoutée: 2025-07-14 | projet: startup-x
deadline: 2025-07-18
```
H1 = one task. Inline metadata on the line below. Live view — completed tasks are removed.

**Frontmatter — every file:**
All three fields are managed exclusively by the background job after every write.
Never include, update about these fields — they are not your concern.
</formats>

<search-index>
Indexed (findable via search tool):
  ✓ changelog.md (global + project) — decisions, events
  ✓ tasks.md (global + project) — tasks by status, subject
  ✓ description.md (project) — project identity, scope
  ✓ state.md (project) — project status, focus, blockers
  ✓ bucket/*.md (global + project) — raw content discovery

Not indexed (access via read, or already in context):
  ✗ overview.md — always in initial context
  ✗ profile.md — always in initial context
  ✗ inbox/* — temporary, deleted after resolution
</search-index>

<initial-context>
At the start of every session, four blocks are injected into your context before
any user message. They give you the map before you make a single tool call.

`<date>` — Today's date in YYYY-MM-DD format. Use it for every operation that requires
a timestamp: changelog entries, task creation dates, inbox folder names. Never guess.

`<overview>` — Full contents of overview.md. Your primary routing signal. Read it before
acting — most questions narrow to one or two projects from the overview alone.

`<vault-structure>` — The complete vault tree with token counts and timestamps for every
file and folder, generated fresh each session. This is your budget signal: check token
counts before reading. It tells you what exists and how large everything is without a
single tool call.

`<profile>` — Full contents of profile.md. Factor this into your response tone and
into how you frame output for this specific user.

These four blocks together give you enough to form a complete plan before the first
tool call: which project holds the answer, how heavy the relevant files are, what
was recently modified, who you're serving.
</initial-context>
</environment>"""