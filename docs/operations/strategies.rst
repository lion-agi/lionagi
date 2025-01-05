.. _lionagi-exec-strategies:

===================================
Execution Strategies & Executors
===================================

LionAGI can run instructions using various strategies:

* Sequential
* Concurrent
* Chunk-based combos

Below are references to each strategy class in `lionagi.operations.strategies`.

.. autoclass:: lionagi.operations.strategies.base.StrategyExecutor
   :members:

.. autoclass:: lionagi.operations.strategies.sequential.SequentialExecutor
   :members:

.. autoclass:: lionagi.operations.strategies.concurrent.ConcurrentExecutor
   :members:

.. autoclass:: lionagi.operations.strategies.sequential_chunk.SequentialChunkExecutor
   :members:

.. autoclass:: lionagi.operations.strategies.concurrent_chunk.ConcurrentChunkExecutor
   :members:

.. autoclass:: lionagi.operations.strategies.params.StrategyParams
   :members:

.. autoclass:: lionagi.operations.strategies.params.ChunkStrategyParams
   :members:

.. autoclass:: lionagi.operations.strategies.params.HybridStrategyParams
   :members:
