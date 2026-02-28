from tools.tool_base import BaseTool

def tree(path: str = ".") -> str:
    """
    Explore the structure of the vault.
    Returns a string representation of the directory tree and file sizes.
    """
    return (
        f"[DUMMY TREE] Structure for path: '{path}'\n"
        f"- projects/\n"
        f"  - startup-x/\n"
        f"    - state.md (2k tokens)\n"
        f"    - changelog.md (15k tokens)\n"
        f"- profile.md (300 tokens)\n"
    )

def read(path: str) -> str:
    """
    Read the contents of a specific file in the vault.
    """
    return (
        f"[DUMMY READ] Content of '{path}':\n"
        f"# Mock Content\n"
        f"This is a mock file content returned by the dummy read tool.\n"
        f"The project is currently blocked waiting for client feedback."
    )

# Instantiate the tools so they can be imported and used by the agents
TreeTool = BaseTool(tree)
ReadTool = BaseTool(read)