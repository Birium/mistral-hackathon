https://www.canva.com/design/DAG2KoK203w/duvoIHpRy7zUYRXafYvZlQ/edit?utm_content=DAG2KoK203w&utm_campaign=designshare&utm_medium=link2&utm_source=sharebutton

# Mcpmem - Smithery Prize 🏆

**Memory with context, time, and portability—built for LLMs that know you.**

---

## The Problem We're Solving

Context engineering is the biggest bottleneck for LLM adoption. ChatGPT's Memory feature exists, but it's fundamentally broken:

- **No control**: You mention something once, it haunts you forever—no editing, only deletion
- **No structure**: Flat memory with no relationships, no time dimension, no organization
- **No evolution**: Information piles up with equal weight. Facts change, preferences shift, but the memory stays static
- **No portability**: Locked into one provider's ecosystem

**The real issue?** Most people don't use complex prompting techniques. They ask simple questions like *"reply to this email"* or *"write this document"* and get generic responses that don't fit. Then they spend forever going back and forth trying to fix it—starting from scratch every time.

**What's missing?** A memory system that understands **relationships** and **time**. When you tell your AI "I now prefer Nike over Adidas," it shouldn't just add a new fact—it should *update* the knowledge graph, deprecate old preferences, and maintain the connection between related information. That's how real memory works.

People need their AI to **actually understand them** and **evolve with them**, but there's no good way to build and maintain that ultra-personalized, living context.

---

## Our Approach

**Portable, visual, temporal memory—no maintenance burden.**

1. **Temporal Knowledge Graphs (Graphiti + Neo4j)**: The game-changer. Memories aren't just stored—they form **relationships over time**. 
   - "Claire liked Adidas" → "Claire sold Adidas stock" → "Claire now prefers Nike"
   - Entities connect, preferences evolve, outdated facts expire naturally
   - **Ultra-personalization that adapts to you** as your life changes

2. **MCP (Model Context Protocol)**: Plug memory into *any* modern LLM app. Zero lock-in, maximum portability. Your memory graph travels with you.

3. **Obsidian-style visualization**: Explore your memory as an interactive graph. Search episodes, trace connections, see *why* the AI knows what it knows.

**What you get:**
- Automatic memory creation from LLM interactions (chat histories, documents, notes—everything can be stored)
- A living knowledge graph that updates relationships constantly
- Search, edit, delete—full user control
- Transport your memory graph anywhere via MCP

Think **"Google Drive for LLM Context"**—one intelligent memory system that works with any LLM you prefer, learns from every interaction, and evolves with you.

*(Note: Add/delete tools are WIP due to hackathon time constraints, but the core search and temporal graph engine are live.)*

---

<img width="1728" height="992" alt="image" src="https://github.com/user-attachments/assets/29b59c32-2499-4260-964e-d232eb32c4f1" />
<img width="891" height="863" alt="image" src="https://github.com/user-attachments/assets/156c9e1c-f2c2-4920-b9f6-a9ceb0eb0ed7" />
<img width="898" height="857" alt="image" src="https://github.com/user-attachments/assets/545b65d9-aebe-4251-a32d-5605bee05a32" />


## How to Launch

### 1. Environment setup
```bash
cp .env.example .env
# Fill in required keys (Neo4j, LLM API, etc.)
```

### 2. Start services
```bash
docker compose build
docker compose up
```

### 3. Seed the database
```bash
curl -X POST http://localhost:8000/neo4j/seed
```

### 4. Explore your memory
- **Web UI**: [http://localhost:5173](http://localhost:5173) – visualize and interact with the graph.
- **Test MCP**:
  ```bash
  npx @modelcontextprotocol/inspector http://localhost:8000
  ```
    - Auth method: **SSE**
    - URL: `http://localhost:8000/mcp/sse`
    - Try the **`search`** tool!

---

## Acknowledgments

Built with 🫩 for **Cursor Hackathon Singapore**.  
Thank you to the organizers for the energy, the community, and the tight deadlines that make magic happen.

—The Mcpmem Team