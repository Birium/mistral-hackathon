import asyncio
import os

_queue: asyncio.Queue = asyncio.Queue()

async def put(item): 
    await _queue.put(item)

async def worker():
    while True:
        item = await _queue.get()
        await process(item)   # stub: writes dummy file to vault
        _queue.task_done()

async def process(item):
    # STUB: write a dummy .md file to vault and log
    vault_path = os.getenv("VAULT_PATH", "/vault")
    path = f"{vault_path}/bucket/update-{item['id']}.md"
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        content = item['payload'].content if hasattr(item['payload'], 'content') else item['payload'].get('content', '')
        f.write(f"---\ncreated: now\nupdated: now\ntokens: 0\n---\n\n{content}")
    print(f"[queue] processed update-{item['id']}")