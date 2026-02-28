import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent.agent.update_agent import UpdateAgent
from agent.agent.search_agent import SearchAgent
from agent.agent.display import Display


def main():
    print("Knower")
    print("Mode: [u]pdate / [s]earch ? ", end="")
    mode = input().strip().lower()

    if mode in ("u", "update"):
        agent = UpdateAgent()
        label = "Update"
    else:
        agent = SearchAgent()
        label = "Search"

    print(f"\n{label} agent ready. Ctrl+C to quit.\n")
    print("-" * 50)

    while True:
        try:
            user_input = input("\nUser: ").strip()
            if not user_input:
                continue

            display = Display()
            for event in agent.process(user_input):
                display.event(event)

            print("\n\n" + "-" * 50)

        except KeyboardInterrupt:
            print("\n\nBye.")
            sys.exit(0)
        except Exception as e:
            print(f"\nError: {e}")


if __name__ == "__main__":
    main()