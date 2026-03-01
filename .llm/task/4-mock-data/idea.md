```
vault/
├── overview.md
├── tree.md
├── profile.md
├── tasks.md
├── changelog.md
│
├── bucket/
│   ├── misc-expenses-june2025.md
│   └── potential-client-outreach-notes.md
│
├── inbox/
│   ├── 2025-07-09-nexus-scope-message/
│   │   ├── review.md
│   │   └── whatsapp-export.md
│   ├── 2025-07-12-voice-note-migration/
│   │   ├── review.md
│   │   └── transcript.md
│   └── 2025-07-14-invoice-unnamed/
│       ├── review.md
│       └── invoice-extract.md
│
└── projects/
    ├── autonoma/
    │   ├── description.md
    │   ├── state.md
    │   ├── tasks.md
    │   ├── changelog.md
    │   └── bucket/
    │       ├── angel-round-term-sheet.md
    │       ├── architecture-notes-feb2025.md
    │       └── beta-user-feedback-session1.md
    │
    ├── client-nexus/
    │   ├── description.md
    │   ├── state.md
    │   ├── tasks.md
    │   ├── changelog.md
    │   └── bucket/
    │       ├── contract-sow-v2.md
    │       ├── milestone-2-delivery-email.md
    │       └── client-call-notes-2025-06-18.md
    │
    ├── client-meridian/
    │   ├── description.md
    │   ├── state.md
    │   ├── tasks.md
    │   ├── changelog.md
    │   └── bucket/
    │       ├── contract-sow.md
    │       ├── training-data-spec.md
    │       └── kickoff-call-notes-2025-05-02.md
    │
    ├── bali-villa/
    │   ├── description.md
    │   ├── state.md
    │   ├── tasks.md
    │   ├── changelog.md
    │   └── bucket/
    │       ├── contractor-quote-cv-mitra-bali.md
    │       ├── whatsapp-contractor-june2025.md
    │       └── permit-status-update.md
    │
    └── ironman-lombok/
        ├── description.md
        ├── state.md
        ├── tasks.md
        ├── changelog.md
        └── bucket/
            ├── race-guide-lombok-2026.md
            └── training-plan-base-phase.md
```

**Professional**

`autonoma/` — Eddie's own SaaS product. AI agent orchestration layer he's building with a co-founder. Has outside money (small angel round, ~$40K), 3 beta users, and a Q3 launch target he's slipping on. This one is messy — evolving architecture, a key decision to drop Postgres for SQLite buried three changelogs ago, and a current blocker on billing (Stripe integration). The demo value here: decisions that are easy to search for but hard to find manually.

`client-nexus/` — A fintech client. Fixed-price contract, $18K across three milestones. Milestone 2 delivered, payment pending. Milestone 3 due August 15. The client has a compliance requirement forcing AWS — a constraint that drove several technical decisions that are scattered across `description.md` and `changelog.md`. This project is the main anchor for the inbox items (more below).

`client-meridian/` — A smaller healthtech client. $8,500 fixed scope. Currently blocked — they haven't handed over the training data they owe Eddie. The "abandoned feature" (real-time coaching, dropped in week 3) lives in the changelog. Lighter project, slower pace, useful contrast to Nexus.

**Personal**

`bali-villa/` — Eddie is building a small villa in Canggu. Budget $85K, contractor hired, permits delayed. Has a bucket with contractor quotes and a WhatsApp conversation transcript. Good for showing that the vault isn't just professional — and for testing the update agent's ability to route financial and logistical information.

`ironman-lombok/` — Training for Ironman Lombok, March 2026. Currently in base phase. Target finish time under 12 hours. Weekly mileage logs, a race calendar, gear decisions. Lightweight but gives `state.md` a very different texture from the others — pure personal, metrics-heavy.

---

**Inbox — three items, all orbiting Nexus**

This is where the demo gets interesting. All three items create genuine routing ambiguity:

1. `2025-07-09-client-message-scope/` — A WhatsApp export from the Nexus client contact. They're asking about "adding a dashboard view" — but Eddie also discussed a dashboard feature with the Meridian client two weeks ago. The agent can't confidently assign this to Nexus without reading both `description.md` files and checking whether a dashboard is already in scope anywhere. The `review.md` exposes exactly that traversal.

2. `2025-07-12-voice-note-migration/` — A 3-minute voice note transcription. Eddie says "we need to move the migration before the 15th or the client won't be able to test in time." This clearly concerns Nexus (the August 15 deadline), but the word "migration" also appears in Autonoma's changelog in the context of a database migration. The agent surfaces the ambiguity rather than guessing.

3. `2025-07-14-invoice-unnamed/` — A PDF-to-text extract of an invoice for $340 from a cloud infrastructure provider. No project name mentioned. Could be Nexus (AWS, client-reimbursable), Autonoma (Eddie's own infra), or even a personal expense. The `review.md` lists what the agent checked, what it found in both `description.md` files regarding infrastructure ownership, and asks one precise question: "Is this AWS bill reimbursable by Nexus, or does it belong to Autonoma's operating costs?"