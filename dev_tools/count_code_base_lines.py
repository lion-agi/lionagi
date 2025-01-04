import os
from collections import defaultdict


def analyze_file(file_path):
    with open(file_path, encoding="utf-8") as file:
        lines = file.readlines()

    stats = {
        "total_lines": len(lines),
        "code_lines": 0,
        "comment_lines": 0,
        "blank_lines": 0,
        "docstring_lines": 0,
    }

    in_docstring = False
    docstring_delimiter = None

    for line in lines:
        stripped = line.strip()

        if not stripped:
            stats["blank_lines"] += 1
            continue

        if in_docstring:
            stats["docstring_lines"] += 1
            if stripped.endswith(docstring_delimiter):
                in_docstring = False
            continue

        if stripped.startswith("'''") or stripped.startswith('"""'):
            stats["docstring_lines"] += 1
            in_docstring = True
            docstring_delimiter = stripped[0] * 3
            if stripped.endswith(docstring_delimiter) and len(stripped) > 3:
                in_docstring = False
            continue

        if stripped.startswith("#"):
            stats["comment_lines"] += 1
        else:
            stats["code_lines"] += 1

    return stats


def analyze_package(package_path):
    total_stats = defaultdict(lambda: defaultdict(int))
    file_stats = {}

    for root, _, files in os.walk(package_path):
        for file in files:
            if file.endswith((".py", ".pyx", ".pyd")):
                file_path = os.path.join(root, file)
                relative_path = os.path.relpath(file_path, package_path)
                stats = analyze_file(file_path)
                file_stats[relative_path] = stats

                file_type = "Python"
                if file.endswith(".pyx"):
                    file_type = "Cython"
                elif file.endswith(".pyd"):
                    file_type = "Python DLL"

                for key, value in stats.items():
                    total_stats[file_type][key] += value

    return total_stats, file_stats


def print_analysis(total_stats, file_stats):
    print("Package Analysis:")
    print("=================")

    grand_total = defaultdict(int)
    for file_type, stats in total_stats.items():
        print(f"\n{file_type} Files:")
        print(f"  Total Lines: {stats['total_lines']}")
        print(f"  Code Lines: {stats['code_lines']}")
        print(f"  Comment Lines: {stats['comment_lines']}")
        print(f"  Docstring Lines: {stats['docstring_lines']}")
        print(f"  Blank Lines: {stats['blank_lines']}")

        for key, value in stats.items():
            grand_total[key] += value

    print("\nGrand Total:")
    print(f"  Total Lines: {grand_total['total_lines']}")
    print(f"  Code Lines: {grand_total['code_lines']}")
    print(f"  Comment Lines: {grand_total['comment_lines']}")
    print(f"  Docstring Lines: {grand_total['docstring_lines']}")
    print(f"  Blank Lines: {grand_total['blank_lines']}")

    print("\nTop 10 Files by Code Lines:")
    sorted_files = sorted(
        file_stats.items(), key=lambda x: x[1]["code_lines"], reverse=True
    )
    for file, stats in sorted_files[:10]:
        print(f"  {file}: {stats['code_lines']} code lines")


if __name__ == "__main__":
    print("Lion Analysis")
    package_path = "./lionagi"  # Replace with your package path
    total_stats, file_stats = analyze_package(package_path)
    print_analysis(total_stats, file_stats)

    print("\nDev Tool Analysis")
    package_path = "./tests"  # Replace with your package path
    total_stats, file_stats = analyze_package(package_path)
    print_analysis(total_stats, file_stats)
