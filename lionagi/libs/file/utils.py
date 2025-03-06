
    
        
    
    
    
    
    
    
    
    

    
    file_size: int | None = None
    name: str
    extension: str
    



class Document(Node):
    
    
    
    
    
    
    
    
    
    ...





class Source(BaseModel):
  
    
    






    directory: str | Path,
    file_types: list[str] | None = None,
    max_workers: int | None = None,
    ignore_errors: bool = False,
    verbose: bool = False,
    recursive: bool = False,



    
def dir_to_doc():
    
    
    
    
    
    
    
    ...




















def dir_to_files(
    directory: str | Path,
    file_types: list[str] | None = None,
    max_workers: int | None = None,
    ignore_errors: bool = False,
    verbose: bool = False,
    recursive: bool = False,
) -> list[Path]:

    directory_path = Path(directory)
    if not directory_path.is_dir():
        raise ValueError(
            f"The provided path is not a valid directory: {directory}"
        )

    def process_file(file_path: Path) -> Path | None:
        try:
            if file_types is None or file_path.suffix in file_types:
                return file_path
        except Exception as e:
            if ignore_errors:
                if verbose:
                    logging.warning(f"Error processing {file_path}: {e}")
            else:
                raise ValueError(f"Error processing {file_path}: {e}") from e
        return None

    file_iterator = (
        directory_path.rglob("*") if recursive else directory_path.glob("*")
    )
    try:
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [
                executor.submit(process_file, f)
                for f in file_iterator
                if f.is_file()
            ]
            files = [
                future.result()
                for future in as_completed(futures)
                if future.result() is not None
            ]

        if verbose:
            logging.info(f"Processed {len(files)} files from {directory}")

        return files
    except Exception as e:
        raise ValueError(f"Error processing directory {directory}: {e}") from e