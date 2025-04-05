from datetime import datetime

from config import compress, compress_prefix, compression_iterations, config

from lionagi.libs.file.concat import concat


async def to_txt(config=config):
    if not str(config["dir"]).endswith("/"):
        config["dir"] = str(config["dir"]) + "/"

    fps = []
    if config["crates"]:
        for j in config["crates"]:
            if str(j).startswith("/"):
                fps.append(config["dir"] + str(j[1:]))
            else:
                fps.append(config["dir"] + str(j))

    dt = datetime.now().strftime("%Y%m%d")
    prefix = config.get("prefix")
    postfix = config.get("postfix")

    pre_fx = prefix + "_" if prefix else ""
    post_fix = "_" + postfix if postfix else ""
    filename = config["output_dir"] + "/" + f"{pre_fx}{dt}{post_fix}.txt"

    filenames = [filename]
    if compression_iterations:
        for i in range(1, compression_iterations + 1):
            filenames.append(
                config["output_dir"]
                + "/"
                + f"{compress_prefix}{pre_fx}{dt}{post_fix}_compressed_{i}.txt"
            )
    out = concat(
        data_path=fps,
        file_types=config["file_types"],  # File types to include
        output_dir=config["output_dir"],  # Output directory
        output_filename=filenames[0],
        exclude_patterns=config["exclude_patterns"],
        verbose=True,
        threshold=200,
        return_files=True,  # Return the list of files processed
        return_fps=True,  # Return the file paths used for concatenation
    )
    out["output_filenames"] = filenames  # Add the filenames used for
    if not compress or not len(filenames) > 1:
        return out

    from lionagi import iModel
    from lionagi.libs.token_transform.symbolic_compress_context import (
        symbolic_compress_context,
    )
    from lionagi.libs.token_transform.types import TokenMappingTemplate

    chat_model = iModel(
        model="openrouter/google/gemini-2.0-flash-001",
        limit_requests=20,
        limit_tokens=30_000,
    )
    compressed_outs = []
    prev_file = filenames[0]
    for i in filenames[1:]:
        nxt_file = i
        compressed = await symbolic_compress_context(
            url_or_path=prev_file,  # The text to compress
            encode_token_map=TokenMappingTemplate.LION_EMOJI,
            output_path=nxt_file,
            chat_model=chat_model,
        )
        compressed_outs.append(compressed)
        prev_file = nxt_file

    out["comressed_files"] = compressed_outs  # Store the compressed files
    return out


if __name__ == "__main__":
    import asyncio

    async def main():
        out = await to_txt()
        print("Concatenation and compression completed.")

        for idx, item in enumerate(out["output_filenames"]):
            print("Compressed files:")
            if idx > 20:
                print(
                    f"Skipping printing more than 20 filenames for brevity. There are {len(out['output_filenames'])} total."
                )
                break
            print(f"{idx + 1}: {item}")

    asyncio.run(main())
