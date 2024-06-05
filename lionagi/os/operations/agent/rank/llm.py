from typing import List, Dict, Any, Optional, Callable
import logging
from lionagi.os.collections.node.node import Node

# Logger Setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Reranker:
    def __init__(self, model, service=None):
        self.model = model
        self.service = service

    async def learn_from_interaction(self, interaction_data: Dict[str, Any]) -> None:
        try:
            self.model.update(interaction_data)
            logger.info("Model updated with interaction data.")

            if self.service:
                await self.service.send_data_for_ranking(interaction_data)
                logger.info("Interaction data sent to ranking service.")
        except Exception as e:
            logger.error(f"Error in learn_from_interaction: {e}")

    async def adapt_response_strategy(self, context: Dict[str, Any]) -> Dict[str, Any]:
        try:
            adaptation_strategy = self.model.determine_strategy(context)
            logger.info("Adaptation strategy determined based on context.")
            return adaptation_strategy
        except Exception as e:
            logger.error(f"Error in adapt_response_strategy: {e}")
            return {}

    async def rerank(
        self,
        nodes: List[Node],
        query_bundle,
        batch_size: int = 10,
        top_n: int = 10,
        format_node_batch_fn: Optional[Callable] = None,
        parse_choice_select_answer_fn: Optional[Callable] = None,
    ) -> List[Node]:
        if not nodes:
            return []

        initial_results: List[Node] = []
        for idx in range(0, len(nodes), batch_size):
            nodes_batch = nodes[idx : idx + batch_size]
            fmt_batch_str = (
                format_node_batch_fn(nodes_batch)
                if format_node_batch_fn
                else str(nodes_batch)
            )

            raw_response = self.model.predict(fmt_batch_str, query_bundle.query_str)

            choices, relevances = (
                parse_choice_select_answer_fn(raw_response, len(nodes_batch))
                if parse_choice_select_answer_fn
                else ([], [])
            )
            choice_idxs = [int(choice) - 1 for choice in choices]
            choice_nodes = [nodes_batch[idx] for idx in choice_idxs]
            relevances = relevances or [1.0 for _ in choice_nodes]
            initial_results.extend(
                [
                    Node(data=node.data, score=relevance)
                    for node, relevance in zip(choice_nodes, relevances)
                ]
            )

        return sorted(initial_results, key=lambda x: x.score or 0.0, reverse=True)[
            :top_n
        ]
