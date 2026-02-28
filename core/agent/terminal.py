import sys
import os

# Add the parent directory (core/) to sys.path so we can import 'env' and other root modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent.update_agent import UpdateAgent
from agent.search_agent import SearchAgent


def main():
    print("🧠 Knower")
    print("Mode: [u]pdate / [s]earch ? ", end="")
    mode = input().strip().lower()

    if mode in ("u", "update"):
        agent = UpdateAgent()
        label = "Update"
    else:
        agent = SearchAgent()
        label = "Search"

    print(f"\n✓ {label} agent ready.")
    print("Ctrl+C to quit.\n")
    print("-" * 50)

    while True:
        try:
            user_input = input("\n→ ").strip()
            if not user_input:
                continue
            print()
            agent.process(user_input)
            print("\n" + "-" * 50)

        except KeyboardInterrupt:
            print("\n\nBye.")
            sys.exit(0)
        except Exception as e:
            print(f"\n❌ {e}")


if __name__ == "__main__":
    main()