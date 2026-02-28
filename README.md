# Memory Manager — Project Overview

## The Context

This project was born from a simple observation: memory in AI today is **locked**. It lives in Claude Code, in OpenClaw, in Cursor, in ChatGPT. Each tool has its own memory, in its own silo, incompatible with everything else. You switch tools, you start from scratch. You want to use two tools together, they share nothing.

This isn't a memory quality problem. It's an **architecture** problem.

There was already a first attempt with a project called MCPMEM — knowledge graphs, Neo4j, a relationship engine between entities. The idea was solid on paper. In practice: too complex, too atomic, not usable day-to-day. A knowledge graph is an excellent tool for what it does. But an agent doesn't really know what to do with it. You send a query, you get a node, you can navigate its connections — but it's too unstructured, too fragmented for an LLM to build a coherent understanding from it. And for a human who just wants to see what's in their memory, it's opaque.

This project starts from scratch, with everything we've learned since then.

---

## What We Want to Build

A **standalone memory service**, local-first, that maintains a file structure of Markdown files, and exposes a simple interface to deposit information and retrieve context from it.

Two operations, that's it:

**→ Send information.** You give anything as input — a summary, a conversation, a note, a project context. The service understands, structures, and updates the memory. You get a confirmation that it's been integrated.

**→ Search for context.** You send a query. The service returns relevant Markdown, extracted from your memory, ready to be used wherever you want — in a prompt, in a terminal, in an interface.

It's a **standalone tool**. Not directly tied to an agent. Not tied to an IDE. Not tied to any particular tool. It sits on the side. You call it when you need it, from wherever you want. You ask a question from a CLI, you get Markdown back. You call it from an MCP, you get Markdown back. It's the same interaction, everywhere, always.

---

## Why Markdown Files

This is the central design choice of the project, and it deserves explanation.

Markdown files are simple, portable, readable by both humans and LLMs. A well-organized file structure is something an agent can navigate in a **repeatable and predictable** way. There are patterns, conventions, known places to look. An agent that knows the structure knows exactly where to go without having to explore blindly.

That's the real power: the structure is always the same. The information inside is unstructured and constantly evolving — but the way to search for it is repeatable. You can build precise search algorithms, checkpoints, exploration strategies. You know you're searching in this project and not in others. You narrow the scope, apply the right tools (semantic, keywords, file navigation), and get relevant context without having to read everything.

The files are also **directly accessible**. You can open them in Obsidian, in VS Code, in a terminal. You see exactly what the system has stored. No black box. No proprietary interface required to look at your own memory.

This is a choice the ecosystem is converging toward. Claude Code built their memory on markdown files. OpenClaw too. Letta Code as well. This is not a coincidence — it's simply what works.

---

## Why a Separate Process and Not the Agent Itself

Today, when an agent wants to retrieve something from memory, it uses its own tools: grep, read, bash, tree. It explores. It reads files. It searches.

The problem isn't that it costs tokens — even though that's true. The real problem is that **all this exploration work takes up space in the main agent's context window**. And the context window is its capacity to think.

An agent that starts saturating its context window becomes less and less effective at its main task. Around 40,000 tokens occupied, reasoning quality starts to decline. At 100,000, 120,000 tokens, the agent can no longer hold a coherent thought on a complex task. If a significant portion of that window is absorbed by memory search — reading files, analyzing them, building a representation of what's in them — there's not much left for the actual work.

And on top of that, there's a second problem: a generalist agent doesn't have the right tools to interact with a specific memory file structure. It can do grep, but it doesn't know the internal structure, the conventions, the strategic places to look. It explores blindly while a specialized process knows the map perfectly.

**The idea is separation of concerns:**

The main agent does the work — it codes, it responds, it reasons, it produces.

The memory service is expert in one single thing: maintaining and querying this file structure. It has purpose-built tools for that, an intimate knowledge of the structure, and it can be invoked as a tool. The main agent calls it, gets clean and relevant context back, and continues its task — its context window barely touched.

---

## Local-First

Memory lives locally. Like Obsidian. It's a volume of files on your machine, managed by a service running locally.

The files belong to you. You can read them directly, modify them, version them in a private repo. Nothing is on someone else's servers.

If someday you want to access your memory from a cloud tool — ChatGPT, Gemini — you expose the service on a public URL. If you want to sync your memory so you don't lose it, you push it to a repo. But that's optional. The default is local.

---

## Connectivity

This service is designed to be **plugged in everywhere**. The same memory, accessible from all the tools you use.

Via MCP (Model Context Protocol), any compatible agent can call the service — Claude Code, Cursor, a custom agent, a script. Via a local API, any program can interact with it. Via a CLI, you directly, without any intermediary.

That's the real differentiator compared to existing solutions. They're all locked into an ecosystem. What you want is a memory that follows you, regardless of the tool you're using today or tomorrow.

---

## What This Memory Contains

We have an intuition of what it should contain — and that intuition is already fairly clear. But the exact structure of the memory, how it organizes itself, what it stores precisely and how, is something that hasn't been defined yet. It's actually one of the central questions of the project.

What we already know is that the memory needs to accommodate very different things:

A **global memory about you** — who you are, your preferences, your habits, the way you work, your recurring constraints. Stable things that evolve slowly but should always be available in context.

**Projects** — each project with its own logic, its state, its history, what was decided, what remains to be done. A project can be huge or tiny. Starting a startup or planning a birthday. Developing a feature or finding a new apartment. A project is a project.

**Episodic memory** — what happened, important interactions, ideas that emerged, research that was done. Temporal context that has value at a given point in time.

**Tasks** — tied to a project or standalone, with priorities that change.

But beyond these intuitive categories, the real structure — how the files are organized, what each type of file contains, how an agent knows where to look for what — that's what remains to be defined and tested.

---

## What We're Not Doing

This is not a SaaS product. Not yet, and maybe never. It's first and foremost a tool that works for yourself.

This is not an autonomous agent running in the background and taking initiative. Memory updates when you ask it to, not on its own.

This is not a project manager with an elaborate interface. The interface, if it exists, is an optional window into what's happening — not the product itself.

And this is not a knowledge graph. Not because knowledge graphs are bad — they have their use for other things. But for this use case, a Markdown file structure that an agent can navigate in a structured and predictable way is infinitely more suited.

---

## What Doesn't Exist Yet and Why We're Building It

Existing solutions all have the same fundamental problem: they're locked. claude-mem works with Claude Code and its hooks. OpenClaw is its own ecosystem. Letta Code is their infrastructure. OneContext is a closed cloud proxy.

What they do well, we'll take. Hybrid search algorithms (semantic + keywords). The concept of progressive disclosure in file navigation. The separation between episodic and semantic memory. The idea of an observer agent that extracts structured context.

But all of that, we're putting it in a tool that **belongs to you**, that runs **on your machine**, and that **connects everywhere**.

That's what doesn't exist.
