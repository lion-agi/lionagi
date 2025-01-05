==================================================
Strategies
==================================================
This subpackage orchestrates how multiple instructions get executed:
- **Sequential** one-by-one steps.
- **Concurrent** all in parallel.
- **Chunk** modes for partial concurrency or partial sequential handling.
- **Hybrid** modes, e.g. concurrent chunks or sequential chunks.


--------------------
``params.py`` (Models)
--------------------
.. module:: lionagi.operations.strategies.params
   :synopsis: Common parameter models

**Key Exports**:

.. class:: StrategyParams
   Basic fields like:
   - `instruct`: list of instructions
   - `session`: session object
   - `branch`: branch object
   - `auto_run`: whether sub-instructions are automatically run, etc.

.. class:: ChunkStrategyParams(StrategyParams)
   Adds a `chunk_size` and an `rcall_params`.

.. class:: HybridStrategyParams(ChunkStrategyParams)
   Outer/inner modes for more advanced sequences.

-------------------
``base.py`` (Core)
-------------------
.. module:: lionagi.operations.strategies.base
   :synopsis: Base class for an “executor” strategy

**Key Exports**:

.. class:: StrategyExecutor
   Provides the interface: ``execute() -> list[InstructResponse]``.

   Subclasses must implement how instructions are scheduled or chunked.

---------------------
``sequential.py``
---------------------
.. module:: lionagi.operations.strategies.sequential
   :synopsis: Simple sequential strategy

**Key Exports**:

.. class:: SequentialExecutor(StrategyExecutor)

   Runs instructions one after the other.

----------------------
``concurrent.py``
----------------------
.. module:: lionagi.operations.strategies.concurrent
   :synopsis: Fully concurrent strategy

**Key Exports**:

.. class:: ConcurrentExecutor(StrategyExecutor)

   Spawns each instruction in parallel, collecting all results.

---------------------------
``sequential_chunk.py``
---------------------------
.. module:: lionagi.operations.strategies.sequential_chunk
   :synopsis: Chunking in sequential manner

**Key Exports**:

.. class:: SequentialChunkExecutor(StrategyExecutor)

   Break instructions into chunks. Process chunks in sequence.  
   Within each chunk, run instructions one-by-one (or another approach).

----------------------------
``concurrent_chunk.py``
----------------------------
.. module:: lionagi.operations.strategies.concurrent_chunk
   :synopsis: Chunks processed concurrently

**Key Exports**:

.. class:: ConcurrentChunkExecutor(ConcurrentExecutor)

   Inherits concurrency logic but chunks sets of instructions (bcall usage).

---------------------------------------------
``hybrid_sequential_concurrent_chunk.py``
---------------------------------------------
.. module:: lionagi.operations.strategies.hybrid_sequential_concurrent_chunk
   :synopsis: Outer = sequential, inner = concurrent

**Key Exports**:

.. class:: SequentialConcurrentChunkExecutor(StrategyExecutor)

   Splits instructions into chunks.  Processes each chunk **sequentially**,  
   but within a chunk, instructions run **concurrently**.

---------------------------------------------
``hybrid_concurrent_sequential_chunk.py``
---------------------------------------------
.. module:: lionagi.operations.strategies.hybrid_concurrent_sequential_chunk
   :synopsis: Outer = concurrent, inner = sequential

**Key Exports**:

.. class:: ConcurrentSequentialChunkExecutor(StrategyExecutor)

   Splits instructions into chunks, launching them in parallel,  
   but processes the instructions in each chunk sequentially.


-----------------
``run_instruct.py``
-----------------
.. module:: lionagi.operations.strategies.run_instruct
   :synopsis: Example single-step runner

**Key Exports**:

.. function:: run_instruct(ins: Instruct, session: Session, branch: Branch, auto_run: bool, ...)

   A convenience function for recursively running an instruction (and sub-instructions) 
   in a single pass. Used internally by some strategy classes.

------------
Summary Note
------------
``lionagi.operations.strategies`` provides flexible ways to run big sets of instructions:
- chunk them,
- run them in parallel,
- or combine parallel and sequential phases.
