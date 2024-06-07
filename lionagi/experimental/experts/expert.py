import random
import asyncio
from lionagi.libs import SysUtil
from lionagi.core.collections import iModel, pile, Pile
from lionagi.core.session.session import Session, Branch
from lionagi.core.collections.util import get_random_config, DEFAULT_EXPERT_MODEL_LIST
from typing import Any, Optional, Dict, List, Union
import aiohttp
from datetime import datetime


from lionagi.libs import SysUtil

DEFAULT_JUDGE_SYSTEM = "Act as a critical judge"
DEFAULT_JUDGE_SCORE_INSTRUCTION = "Based on the context, score the model output for relevance and coherence"
DEFAULT_JUDGE_ASSIGN_INSTRUCTION = "Based on the context, select a judgement for the model output"

class Expert:
    """
    The Expert class facilitates interactions with models, manages sessions, 
    and handles knowledge and experience for better decision-making and scoring.
    
    Attributes:
        session (Session): The current session object.
        ln_id (str): Unique identifier for the expert.
        timestamp (str): Timestamp of the creation.
        knowledge (Pile): Pile of knowledge.
        experience (Pile): Pile of experience.
    """

    def __init__(
        self,
        session: Optional[Session] = None,
        system: Optional[str] = None,
        branches: Optional[Dict] = None,
        tools: Optional[List] = None,
        imodel: Optional[iModel] = None,
        knowledge: Optional[Pile] = None,
        experience: Optional[Pile] = None,
        query_knowledge_config: Optional[Dict] = None,
        query_experience_config: Optional[Dict] = None,
    ):
        """
        Initializes the Expert class.

        Args:
            session (Optional[Session]): The session object.
            system (Optional[str]): The default system message for the session.
            branches (Optional[Dict]): Branches for the session.
            tools (Optional[List]): Tools to be used in the session.
            imodel (Optional[iModel]): The model to be used.
            knowledge (Optional[Pile]): The knowledge pile.
            experience (Optional[Pile]): The experience pile.
            query_knowledge_config (Optional[Dict]): Configuration for querying knowledge.
            query_experience_config (Optional[Dict]): Configuration for querying experience.
        """
        self.ln_id: str = SysUtil.create_id()
        self.timestamp: str = SysUtil.get_timestamp(sep=None)[:-6]
        
        if not session:
            self.session = Session(
                system=system,
                branches=branches,
                system_sender=self.ln_id,
                user=self.ln_id,
                tools=tools,
                imodel=imodel,
            )
        else:
            session.system_sender = self.ln_id
            self.session = session

        self.knowledge = knowledge or pile()
        self.experience = experience or pile()

        self.query_knowledge_tool = self.knowledge.as_query_tool(**(query_knowledge_config or {}))
        self.query_experience_tool = self.experience.as_query_tool(**(query_experience_config or {}))

        self.session.default_branch.register_tools([self.query_knowledge_tool, self.query_experience_tool])

    def refresh(self, verbose: bool = True) -> None:
        """
        Refreshes the knowledge and experience tools.

        Args:
            verbose (bool): If true, prints the refresh status.
        """
        self.query_knowledge_tool = self.knowledge.as_query_tool()
        self.query_experience_tool = self.experience.as_query_tool()
        branch = self.session.default_branch
        branch.tool_manager.registry["query_knowledge"] = self.query_knowledge_tool
        branch.tool_manager.registry["query_experience"] = self.query_experience_tool
        if verbose:
            print("Knowledge and experience refreshed.")

    def size(self) -> int:
        """
        Returns the size of the combined knowledge and experience.

        Returns:
            int: The total size.
        """
        return len(self.knowledge) + len(self.experience)

    def __len__(self) -> int:
        return 1

    async def query_knowledge(self, query: str, **kwargs) -> Any:
        """
        Queries the knowledge pile with the given query.

        Args:
            query (str): The query string.
            **kwargs: Additional keyword arguments for querying.

        Returns:
            Any: The response from the knowledge pile query.
        """
        idx1 = len(self.knowledge.query_response)
        try:
            response = await self.knowledge.query_pile(query, **kwargs)
            self.experience += self.knowledge.query_response[idx1:]
            return response
        except Exception as e:
            print(f"Error querying knowledge: {e}")
            raise

    async def query_experience(self, query: str, **kwargs) -> Any:
        """
        Queries the experience pile with the given query.

        Args:
            query (str): The query string.
            **kwargs: Additional keyword arguments for querying.

        Returns:
            Any: The response from the experience pile query.
        """
        idx1 = len(self.experience.query_response)
        try:
            response = await self.experience.query_pile(query, **kwargs)
            self.experience += self.experience.query_response[idx1:]
            return response
        except Exception as e:
            print(f"Error querying experience: {e}")
            raise

    async def chat(self, *args, branch: Optional[Branch] = None, new_branch: bool = False, **kwargs) -> Any:
        """
        Handles chatting with the expert, optionally creating a new branch.

        Args:
            *args: Positional arguments for the chat method.
            branch (Optional[Branch]): The branch to use for the chat. Defaults to None.
            new_branch (bool): If True, creates a new branch for the chat. Defaults to False.
            **kwargs: Additional keyword arguments for the chat method.

        Returns:
            Any: The response from the chat method.
        """
        try:
            if new_branch:
                branch = self.session.new_branch()
            else:
                branch = branch or self.session.default_branch

            idx1 = len(branch.messages)
            response = await branch.chat(*args, **kwargs)
            self.experience += branch.messages[idx1:]
            return response
        except Exception as e:
            print(f"Error during chat: {e}")
            raise

    async def score(
        self,
        instruction: Optional[str] = None,
        context: Optional[Dict] = None,
        system: Optional[str] = None,
        **kwargs
    ) -> float:
        """
        Scores the model output based on the given instruction and context.

        Args:
            instruction (Optional[str]): The instruction for scoring.
            context (Optional[Dict]): The context for scoring.
            system (Optional[str]): The system message.
            **kwargs: Additional keyword arguments for scoring.

        Returns:
            float: The score of the model output.
        """
        try:
            branch = Branch(system=system, imodel=self.session.imodel)
            form = await branch.direct(
                instruction=instruction,
                context=context,
                score=True,
                score_range=(0, 1),
                score_num_digits=3,
                **kwargs
            )
            return form.score
        except Exception as e:
            print(f"Error during scoring: {e}")
            raise

    async def select(
        self,
        candidates: List[str],
        instruction: Optional[str] = None,
        context: Optional[Dict] = None,
        system: Optional[str] = None,
        num_judge: int = 3,
        **kwargs
    ) -> tuple:
        """
        Selects the best candidate based on average scores from multiple judges.

        Args:
            candidates (List[str]): List of candidates to be scored.
            instruction (Optional[str]): The instruction for scoring.
            context (Optional[Dict]): The context for scoring.
            system (Optional[str]): The system message.
            num_judge (int): Number of judges to score each candidate.
            **kwargs: Additional keyword arguments for scoring.

        Returns:
            tuple: The best candidate and its score.
        """
        async def inner_score(candidate):
            try:
                branch = Branch(system=system, imodel=self.session.imodel)
                form = await branch.direct(
                    instruction=instruction,
                    context={"context": context, "candidate": candidate},
                    score=True,
                    score_range=(0, 1),
                    score_num_digits=3,
                    **kwargs
                )
                return form.score
            except Exception as e:
                print(f"Error during candidate scoring: {e}")
                raise

        async def get_avg_score(candidate):
            tasks = [inner_score(candidate) for _ in range(num_judge)]
            return sum(await asyncio.gather(*tasks)) / num_judge
        
        try:
            system = system or DEFAULT_JUDGE_SYSTEM
            instruction = instruction or DEFAULT_JUDGE_SCORE_INSTRUCTION
            context = {"context": context}

            tasks = [get_avg_score(candidate) for candidate in candidates]
            scores = await asyncio.gather(*tasks)
            
            outputs = [(idx, candidate, scores[idx]) for idx, candidate in enumerate(candidates)]
            return sorted(outputs, key=lambda x: x[2], reverse=True)[0]
        except Exception as e:
            print(f"Error during selection: {e}")
            raise

    async def assign_intrinsic_reward(
        self,
        instruction: Optional[str] = None,
        context: Optional[Dict] = None,
        system: Optional[str] = None,
        candidate: Optional[str] = None,
    ) -> float:
        """
        Assigns an intrinsic reward based on the given instruction and context.

        Args:
            instruction (Optional[str]): The instruction for scoring.
            context (Optional[Dict]): The context for scoring.
            system (Optional[str]): The system message.
            candidate (Optional[str]): The candidate to be scored.

        Returns:
            float: The assigned intrinsic reward.
        """
        try:
            system = system or DEFAULT_JUDGE_SYSTEM
            instruction = instruction or DEFAULT_JUDGE_ASSIGN_INSTRUCTION
            
            branch = Branch(system=system, imodel=self.session.imodel)
            reward = await branch.direct(
                instruction=instruction,
                context={"context": context, "candidate": candidate},
                select_choices=["highly effective", "effective", "moderate", "poor", "bad"],
                reason=True,
            )
            match reward.selection:
                case "highly effective":
                    return 1.0
                case "effective":
                    return 0.7
                case "moderate":
                    return 0.5
                case "poor":
                    return 0.2
                case "bad":
                    return 0.0
                case _:
                    return 0.0
        except Exception as e:
            print(f"Error during intrinsic reward assignment: {e}")
            raise

    @staticmethod
    def random_model( 
        model_list=DEFAULT_EXPERT_MODEL_LIST,
        temperature_range = (0.7, 1.2),
        top_p_range = (0.8, 1.0),
        frequency_penalty_range = (0.0, 0.5),
        presence_penalty_range = (0.0, 0.5),
        max_tokens = 1000,  
    ):
        config = get_random_config(
            model_list=model_list,
            temperature_range=temperature_range,
            top_p_range=top_p_range,
            frequency_penalty_range=frequency_penalty_range,
            presence_penalty_range=presence_penalty_range,
            max_tokens=max_tokens,
        )
        return iModel(**config)
        
    async def automate_knowledge_update(self, update_interval: int = 24, data_source_url: str = None) -> None:
        """
        Schedules periodic updates to the knowledge pile from an external data source.

        Args:
            update_interval (int): The interval in hours between updates.
            data_source_url (str): The URL of the external data source.
        """
        while True:
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(data_source_url) as response:
                        if response.status == 200:
                            new_data = await response.json()
                            self.knowledge.add_data(new_data)
                            print(f"Knowledge updated at {datetime.now()}")
                        else:
                            print(f"Failed to update knowledge. Status code: {response.status}")
            except Exception as e:
                print(f"Error during knowledge update: {e}")
            
            await asyncio.sleep(update_interval * 3600)
            
            
    def summarize_experience(self, ratio: float = 0.2) -> str:
        """
        Generates a summary of the accumulated experience.

        Args:
            ratio (float): The compression ratio for the summary.

        Returns:
            str: The summary of the experience.
        """
        try:
            SysUtil.check_import("gensim", "summarization", "summarize")
            from gensim.summarization import summarize
            
            experience_text = " ".join([str(exp) for exp in self.experience])
            summary = summarize(experience_text, ratio=ratio)
            return summary
        except Exception as e:
            print(f"Error during experience summarization: {e}")
            return ""
        
    def provide_contextual_suggestions(self, context: str, num_suggestions: int = 5) -> List[str]:
        """
        Provides suggestions based on the current context and historical data.

        Args:
            context (str): The current context.
            num_suggestions (int): The number of suggestions to provide.

        Returns:
            List[str]: The list of suggestions.
        """
        try:
            relevant_experience = [exp for exp in self.experience if context in str(exp)]
            suggestions = random.sample(relevant_experience, min(num_suggestions, len(relevant_experience)))
            return suggestions
        except Exception as e:
            print(f"Error providing contextual suggestions: {e}")
            return []
        
    def detect_anomalies(self) -> List[Any]:
        """
        Detects anomalies in the experience data.

        Returns:
            List[Any]: The list of detected anomalies.
        """
        try:
            if len(self.experience) < 10:  # Ensure enough data points
                return []
            
            SysUtil.check_import(
                package_name="sklearn", 
                module_name="ensemble", 
                import_name="IsolationForest", 
                pip_name="scikit-learn"
            )
            
            from sklearn.ensemble import IsolationForest

            model = IsolationForest(contamination=0.1)
            experience_data = [exp.to_vector() for exp in self.experience]
            model.fit(experience_data)
            anomalies = model.predict(experience_data)
            return [self.experience[idx] for idx, anomaly in enumerate(anomalies) if anomaly == -1]
        except Exception as e:
            print(f"Error detecting anomalies: {e}")
            return []
        