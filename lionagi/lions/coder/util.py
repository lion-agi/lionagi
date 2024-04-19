"""
Utilities for the coder
"""

# basing on rUv https://gist.github.com/ruvnet/4b41ee8eaabd6e72cf18b6352437c738

def extract_code_blocks(code):
    # Extract code blocks from the generated code
    code_blocks = []
    lines = code.split('\n')
    inside_code_block = False
    current_block = []

    for line in lines:
        if line.startswith('```'):
            if inside_code_block:
                code_blocks.append('\n'.join(current_block))
                current_block = []
                inside_code_block = False
            else:
                inside_code_block = True
        elif inside_code_block:
            current_block.append(line)

    if current_block:
        code_blocks.append('\n'.join(current_block))

    return '\n\n'.join(code_blocks)

def install_dependencies(required_libraries=["lionagi"]):
    missing_libraries = []

    for library in required_libraries:
        try:
            import importlib
            importlib.import_module(library)
        except ImportError:
            missing_libraries.append(library)

    if missing_libraries:
        for library in missing_libraries:
            print(f"Installing {library}...")
            import subprocess
            import sys
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", library])
            except subprocess.CalledProcessError as e:
                print(f"Error occurred while installing {library}: {str(e)}")
                print("Please check the error message and ensure you have the necessary permissions to install packages.")
                print("You may need to run the script with administrative privileges or use a virtual environment.")
        print("Installation completed.")