def _task_id_generator() -> Generator[int, None, None]:
    """Generate an incremental sequence of integers starting from 0.

    Yields:
        The next integer in the sequence.

    Examples:
        gen = _task_id_generator()
        next(gen)  # Yields 0
        next(gen)  # Yields 1
    """
    task_id = 0
    while True:
        yield task_id
        task_id += 1
        
