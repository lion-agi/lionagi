prefix = "full"
postfix = "source_codes"
crates = ["lionagi"]

compress_prefix = ""
compress = True
compress_cumulative = False
compression_iterations = 1

config = {
    "dir": "/Users/lion/lionagi/",
    "output_dir": "/Users/lion/lionagi/dev/data/lionagi",
    "prefix": prefix,
    "postfix": postfix,
    "crates": crates,
    "exclude_patterns": [".venv"],
    "file_types": [".py"],
}
