
Introducing Context Repositories: Git-based Memory for Coding Agents
February 12, 2026

We're introducing Context Repositories, a rebuild of how memory works in Letta Code based on programmatic context management and git-based versioning. Letta Code stores a copy of the agent’s context in the local filesystem, meaning agents can leverage their full terminal and coding capabilities (including writing scripts and spawning subagents) to manage context, such as progressive disclosure and rewriting context for learning in token-space. In comparison, prior approaches to memory limited agents to MemGPT-style memory tools or virtual filesystem operations.

Context Repositories are git-backed, so every change to memory is automatically versioned with informative commit messages. Git tracking also enables concurrent, collaborative work across multiple subagents, which can manage divergence and conflicts between learned context through standard git operations. This expands the design space for token-space learning architectures: agents can reflect on past experience with divide-and-conquer strategies that spread processing across subagents, or maintain multiple memory subagents that each focus on different aspects of learning while resolving their findings back into a shared repository.

Virtual memory as local filesystems 
Files are simple, universal primitives that both humans and agents can work with using familiar tools. Following the Unix philosophy, agents can chain standard tools for complex queries over memory, use bash for batch operations (e.g., for file in /memory/*/; do ...;), or write scripts to process memory programmatically.

Agents on the Letta API live on the server, but Letta Code agents clone their memory repository to the local filesystem, giving the agent a local copy of its memory that stays in sync regardless of where the client is running:


Progressive memory disclosure
Files in the context repository are designed for progressive disclosure, similar to patterns recommended for agent skills. The filetree structure is always in the system prompt, so folder hierarchy and file names act as navigational signals. Each memory file also includes frontmatter with a description of its contents, similar to the YAML frontmatter in Anthropic's SKILL.md files:


The system/ directory designates which files are always fully loaded into the system prompt:


Because agents have programmatic access to the repository, they can manage their own progressive disclosure by reorganizing the file hierarchy, updating frontmatter descriptions, and moving files in and out of system/ to control what's pinned to context as they learn over time.

Memory agents and memory swarms
Multi-agent systems have proven remarkably effective for complex coding tasks (with examples from Cursor and Anthropic coordinating agent swarms for complex tasks). Memory formation and learning in agents are single-threaded: if an agent wants to learn from data or a prior trajectory, it processes it sequentially (such with sleep-time agents current), because there's been no mechanism to coordinate concurrent writes to memory. Git changes this. By giving each subagent an isolated worktree, multiple subagents can process and write to memory concurrently, then merge their changes back through git-based conflict resolution. 

As an example, we updated our /init tool to optionally learn from existing Claude Code and Codex histories by fanning out processing across concurrent subagents. Each subagent reflects on a slice of history in its own worktree, and the results are merged back into "main" memory. 


More generally, allowing copies of memory to diverge temporarily opens up flexible patterns for offline processing, where multiple memory subagents can work concurrently without blocking the main thread.

Memory skills
Memory repositories are agnostic to the mechanism for memory management, but open up more possibilities for how memory and context engineering can be designed. Letta Code has built-in skills and subagents for memory management designed to work with Context Repositories:

Memory initialization: Bootstraps new agents by exploring the codebase and reviewing historical conversation data (from Claude Code/Codex) using concurrent subagents that work in git worktrees to create the initial hierarchical memory structure.
‍Memory reflection:  A background "sleep-time" process that periodically reviews recent conversation history and persists important information into the memory repository with informative commit messages. It works in a git worktree to avoid conflicts with the running agent and merges back automatically.‍
Memory defragmentation: Over long-horizon use, memories inevitably become less organized. The defragmentation skill backs up the agent's memory filesystem, then launches a subagent that reorganizes files, splitting large files, merging duplicates, and restructuring into a clean hierarchy of 15–25 focused files.
Next steps 
You can enable memory repositories for your agents by running the  /memfs command to enable it for existing agents. The command will detach the memory(...) tool from your agent, and sync your existing memory blocks to a git-backed memory filesystem.

Install Letta Code with npm install -g @letta-ai/letta-code