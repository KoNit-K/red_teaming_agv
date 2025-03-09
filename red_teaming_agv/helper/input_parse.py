from typing import Tuple

from red_teaming_agv.common.Target import Target


def print_available_options():
    """Print available categories and their details."""
    print("\nAvailable categories and sizes:")
    Target.print_category_info()
    print("\nAvailable target models:", Target.ALLOWED_TARGETS)
    print("\nFor index, you can specify a number (0-based) or 'All' to try all goals in the category")
    print("\nExample commands:")
    print("  category financial --index 0 --target gpt-4o-mini")
    print("  category bomb --index All --target gpt-4o-mini")




def parse_user_input() -> Tuple[str, str, str]:
    """Parse user input in the format 'category <name> --index <num> --target <model>'."""
    while True:
        try:
            user_input = input("\nEnter command (or 'help' for options, 'quit' to exit): ").strip()

            if user_input.lower() == 'quit':
                exit(0)

            if user_input.lower() == 'help':
                print_available_options()
                continue

            # Split the input into parts
            parts = user_input.split()

            if len(parts) != 6 or parts[0] != 'category' or parts[2] != '--index' or parts[4] != '--target':
                raise ValueError("Invalid command format")

            category = parts[1]
            index = parts[3]
            target = parts[5]

            # Validate category
            if category not in Target.get_all_categories():
                raise ValueError(f"Invalid category. Use 'help' to see available categories.")

            # Validate index
            if index.lower() != 'all':
                try:
                    index_num = int(index)
                    if index_num < 0 or index_num >= Target.get_category_size(category):
                        raise ValueError
                except ValueError:
                    raise ValueError(
                        f"Invalid index. Must be between 0 and {Target.get_category_size(category) - 1} or 'All'")

            # Validate target
            if target not in Target.ALLOWED_TARGETS:
                raise ValueError(f"Invalid target model. Choose from: {Target.ALLOWED_TARGETS}")

            return category, index, target

        except ValueError as e:
            print(f"Error: {str(e)}")
            continue