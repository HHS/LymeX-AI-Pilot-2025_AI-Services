import importlib
import sys
import os
import asyncio
import inspect

def print_usage_and_exit():
    print("Usage: python run_tools.py <nested.folder.tool.name>")
    sys.exit(1)

def main():
    # Ensure project root is on sys.path so 'tools' can be imported as a package
    project_root = os.path.dirname(os.path.abspath(__file__))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)

    if len(sys.argv) < 2:
        print_usage_and_exit()

    tool_path = sys.argv[1]

    # Automatically add 'tools.' prefix if not present and folder exists
    if not tool_path.startswith("tools."):
        tools_dir = os.path.join(project_root, "tools")
        # Only add 'tools.' if the 'tools' folder exists and input isn't already in another top-level package
        if os.path.isdir(tools_dir):
            tool_path = f"tools.{tool_path}"

    try:
        module = importlib.import_module(tool_path)
    except ModuleNotFoundError as e:
        print(f"Could not import module: {tool_path}")
        print(e)
        sys.exit(1)

    if not hasattr(module, "run"):
        print(f"Module '{tool_path}' does not have a 'run' function.")
        sys.exit(1)

    run_func = module.run

    if inspect.iscoroutinefunction(run_func):
        asyncio.run(run_func())
    else:
        run_func()

if __name__ == "__main__":
    main()
