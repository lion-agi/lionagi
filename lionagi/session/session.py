from collections import deque
from typing import Any, Dict, List, Optional, Tuple, Union

from pandas import DataFrame


from lionagi.util import to_list, to_df
from lionagi.schema import BaseActionNode, DataLogger
from lionagi.provider import Services
from lionagi.action import ActionManager
from lionagi.branch import Branch
from lionagi.mail import MailManager
from lionagi.message import Instruction, System



class Session:
    """
    Manages multiple conversation branches within a conversational system, providing
    functionalities for branch management, message aggregation, logging, and session
    data persistence.

    This class initializes with configurations for a default branch and setups logging
    and mail management infrastructure. It supports dynamic branch creation, message
    handling, and interaction with language learning models (LLMs).

    Attributes:
        branches (Dict[str, Branch]): A dictionary mapping branch names to Branch instances.
        default_branch (Branch): The Branch instance set as the default for the session.
        datalogger (DataLogger): A DataLogger instance for logging session activities.
        mail_manager (MailManager): Manages mail across branches for message handling.
        llmconfig (Dict): Configuration for the LLM service in the default branch.

    Methods:
        all_messages(self) -> pd.DataFrame:
            Aggregates all messages from each branch into a single DataFrame.

        all_responses(self) -> pd.DataFrame:
            Aggregates all responses from assistants across branches into a DataFrame.

        concat_logs(self):
            Consolidates logs from all branches into the session's datalogger.

        log_to_csv(self, filename: str = 'log.csv', file_exist_ok: bool = False,
                   timestamp: bool = True, time_prefix: bool = False, verbose: bool = True,
                   clear: bool = True, **kwargs):
            Exports the consolidated session logs to a CSV file.

        new_branch(self, branch_name: Optional[str] = None, **kwargs) -> None:
            Creates and adds a new conversation branch to the session.

        get_branch(self, branch: Optional[Union[Branch, str]] = None,
                   get_name: bool = False) -> Union[Branch, Tuple[Branch, str]]:
            Retrieves a branch based on its name or direct reference.

        change_default_branch(self, branch: Union[str, Branch]) -> None:
            Sets a new default branch for the session.

        delete_branch(self, branch: Union[Branch, str], verbose: bool = True) -> bool:
            Removes a specified branch from the session.

        merge_branch(self, from_branch: Union[str, Branch], to_branch: Union[str, Branch],
                     update: bool = True, del_: bool = False) -> None:
            Merges data and configurations from one branch to another.

        collect_send_all(self, receive_all: bool = False):
            Collects and sends messages across all branches, optionally processing all
            pending incoming messages.

        chat(self, instruction: Union[Instruction, str], **kwargs) -> Any:
            Conducts an asynchronous chat exchange, processing instructions and optionally
            invoking actions.

        auto_followup(self, instruction: Union[Instruction, str], max_followup: int = 3,
                      **kwargs) -> Any:
            Generates follow-up actions based on previous chat interactions.

    Examples:
        Initializing a session with a default branch and custom logging:
        >>> session = Session(default_branch_name='main', persist_path='/logs/')
        >>> session.new_branch('Support', system='Welcome to Support Branch')

        Aggregating and logging messages:
        >>> all_messages = session.all_messages()
        >>> session.log_to_csv('all_messages.csv')
    """

    def __init__(
            self,
            system: System | str | Dict[str, Any] | None = None,
            default_branch: Branch | None = None,
            default_branch_name: str | None = None,
            sender: str | None = None,
            llmconfig: Dict | None = None,
            service: Any = None,
            branches: Dict[str, Branch] | None = None,
            actions: BaseActionNode | List[BaseActionNode] | None = None,
            instruction_sets: Dict | None = None,
            action_manager: ActionManager | None = None,
            messages: DataFrame | None = None,
            datalogger: DataLogger | None = None,
            persist_path: str | None = None,
            **kwargs: Any
    ):
        """
        Initializes a new Session instance, setting up branches, logging, and mail management
        for managing multiple conversation branches within a conversational system.

        Args:
            default_branch (Branch | None): A pre-existing Branch instance to set as the default.
                If None, a new default branch is created.
            default_branch_name (str | None): The name of the default branch. Used if initializing
                a new default branch.
            system (System | str | Dict[str, Any] | None): Initial system message or configuration
                for the default branch.
            sender (str | None): Default sender name for system messages in the default branch.
            llmconfig (Dict | None): Configuration for the LLM service in the default branch.
            service (Any): LLM service instance for natural language processing in the default branch.
            branches (Dict[str, Branch] | None): Existing branches to be used instead of creating
                a new default branch.
            actions (BaseTool | List[BaseActionNode] | None): Tools to register with the default branch's
                action manager.
            instruction_sets (Dict | None): Instruction sets for structured interactions in the default
                branch.
            action_manager (ActionManager | None): An action manager for managing actions within the
                default branch.
            messages (DataFrame | None): Preloaded conversation messages for the default branch.
            datalogger (DataLogger | None): A DataLogger instance for logging session activities.
                If None, a new DataLogger is initialized.
            persist_path (str | None): Path for persisting session data and logs.
            **kwargs (Any): Additional keyword arguments for initializing the default branch.

        Attributes are set based on the provided arguments, with default values initialized where
        necessary.
        """

        self.branches = branches or {}
        self.default_branch = default_branch or Branch(
            sender=sender,
            branch_name=default_branch_name or 'main', system=system, llmconfig=llmconfig,
            service=service, actions=actions, instruction_sets=instruction_sets,
            persist_path=persist_path, messages=messages, **kwargs)

        self.service = self.default_branch.service
        self.datalogger = datalogger or DataLogger(persist_path=persist_path)
        self.mail_manager = MailManager(self.branches)

    @property
    def all_messages(self) -> DataFrame:
        """
        Compiles all messages from each branch into a single pandas DataFrame, providing
        an aggregated view of messages across the entire session.

        This property iterates through each branch, aggregates their messages, and combines
        them into one DataFrame for a comprehensive overview of all messages within the session.

        Returns:
            DataFrame: A pandas DataFrame containing all messages from the session's branches,
            structured according to the message schema defined in the Branch class.

        Example:
            >>> all_msgs = session.all_messages
            >>> print(all_msgs.head())
        """

        dfs = deque()
        for _, v in self.branches:
            dfs.append(to_df(v.messages))
        return to_df(to_list(dfs, flatten=True, dropna=True))

    @property
    def all_responses(self) -> DataFrame:
        """
        Aggregates all responses from assistants across each branch into a single pandas
        DataFrame, useful for analysis and reporting on conversational outcomes.

        Each branch's responses are collected and merged, offering a centralized dataset
        for examining the responses generated by the system or assistants within the session.

        Returns:
            DataFrame: A pandas DataFrame consolidating all responses from the session's
            branches, formatted to align with the response schema used in Branch instances.

        Example:
            >>> all_responses = session.all_responses
            >>> print(all_responses.head())
        """

        dfs = deque()
        for _, v in self.branches:
            dfs.append(to_df(v.responses))
        return to_df(to_list(dfs, flatten=True, dropna=True))

    @property
    def all_assistant_responses(self) -> DataFrame:
        """
        Collects all assistant-generated responses from each branch, combining them into
        a single pandas DataFrame for a centralized view of system interactions.

        This property facilitates an aggregated analysis of how the system's assistants
        have responded across different conversation contexts within the session.

        Returns:
            DataFrame: A pandas DataFrame containing all assistant-generated responses
            from all branches, adhering to the assistant response schema defined in
            Branch instances.

        Example:
            >>> assistant_responses = session.all_assistant_responses
            >>> print(assistant_responses.head())
        """

        dfs = deque()
        for _, v in self.branches:
            dfs.append(to_df(v.assistant_responses))
        return to_df(to_list(dfs, flatten=True, dropna=True))

    @property
    def all_action_responses(self) -> DataFrame:
        """
        Aggregates all action responses from each branch into a single pandas DataFrame,
        offering insights into the outcomes of actions taken across the session.

        This property collects responses generated by actions within each branch, merging
        them into a unified view. It's particularly useful for evaluating the effectiveness
        and reach of actionable responses system-wide.

        Returns:
            DataFrame: A pandas DataFrame that consolidates all action responses from the
            session's branches, formatted according to the action response schema outlined
            in Branch instances.

        Example:
            >>> all_action_responses = session.all_action_responses
            >>> print(all_action_responses.head())
        """
        dfs = deque()
        for _, v in self.branches:
            dfs.append(to_df(v.action_response))
        return to_df(to_list(dfs, flatten=True, dropna=True))

    @property
    def all_action_requests(self) -> DataFrame:
        """
        Compiles all action requests from each branch into a single pandas DataFrame,
        providing a comprehensive overview of requested actions across the session.

        By aggregating action requests, this property facilitates an analysis of the types
        and frequencies of actions initiated by users or automated systems within the session.

        Returns:
            DataFrame: A pandas DataFrame containing all action requests across the session's
            branches, adhering to the schema for action requests defined in Branch instances.

        Example:
            >>> all_action_requests = session.all_action_requests
            >>> print(all_action_requests.head())
        """
        dfs = deque()
        for _, v in self.branches:
            dfs.append(to_df(v.action_request))
        return to_df(to_list(dfs, flatten=True, dropna=True))

    @property
    def info(self) -> Dict[str, Any]:
        """
        Summarizes session information by aggregating key metrics and details from each branch,
        returning a dictionary with branch names as keys and their info dictionaries as values.

        This property provides a high-level overview of the session's structure and activity,
        including the number of messages, responses, and other relevant metrics from each branch.

        Returns:
            Dict[str, Any]: A dictionary mapping each branch name to its corresponding info
            dictionary, which includes metrics and details specific to that branch.

        Example:
            >>> session_info = session.info
            >>> for branch_name, branch_info in session_info.items():
            >>>     print(f"{branch_name}: {branch_info}")
        """
        dict_ = {}
        for k, v in self.branches.items():
            dict_[k] = v.info

        return dict_

    @property
    def sender_info(self) -> Dict[str, Any]:
        """
        Provides a summary of sender-specific information from each branch, aggregating
        metrics and details related to message senders across the session.

        This property compiles sender-related statistics, such as message counts and sender
        identities, offering insights into the distribution and activity of senders within
        the conversational system.

        Returns:
            Dict[str, Any]: A dictionary where each key is a branch name, and its value is
            another dictionary containing sender-specific metrics for that branch.

        Example:
            >>> sender_info = session.sender_info
            >>> for branch_name, info in sender_info.items():
            >>>     print(f"{branch_name}: {info}")
        """
        dict_ = {}
        for k, v in self.branches.items():
            dict_[k] = v.sender_info

        return dict_

    @property
    def default_branch_name(self):
        return self.default_branch.branch_name

    def concat_logs(self):
        """
        Consolidates logs from all branches into the session's datalogger, preparing them for
        unified export or analysis. This method aggregates log entries recorded in each
        branch's individual datalogger.

        Before exporting session logs to ensure comprehensive coverage, `concat_logs` should
        be invoked to include all branch-specific logs in the session-wide datalogger.

        Example:
            >>> session.concat_logs()
            This prepares the session-wide datalogger with logs from all branches.
        """

        for _, v in self.branches:
            self.datalogger.extend(v.datalogger.logs)

    def log_to_csv(
            self, filename: str = 'log.csv', file_exist_ok: bool = False,
            timestamp: bool = True, time_prefix: bool = False, verbose: bool = True,
            clear: bool = True, **kwargs):
        """
        Exports the consolidated session logs to a CSV file, optionally applying a timestamp
        to the filename for uniqueness and allowing for clear versioning of log files.

        Before executing, `concat_logs` is invoked to ensure that logs from all branches are
        merged into the session's datalogger. This method facilitates easy sharing and
        analysis of session activities.

        Args:
            filename (str): The name or path of the CSV file to export the logs to. Default is 'log.csv'.
            file_exist_ok (bool): If False, raises an error if the file already exists. Default is False.
            timestamp (bool): If True, appends a timestamp to the filename. Default is True.
            time_prefix (bool): If True, prefixes the filename with a timestamp. Default is False.
            verbose (bool): If True, prints a success message upon export completion. Default is True.
            clear (bool): If True, clears the datalogger's logs after exporting. Default is True.
            **kwargs: Additional keyword arguments passed to the DataLogger's to_csv method.

        Example:
            >>> session.log_to_csv('session_logs.csv', timestamp=True)
            This exports the session logs to 'session_logs.csv', appending a timestamp for uniqueness.
        """

        self.concat_logs()
        self.datalogger.to_csv(
            filepath=filename, file_exist_ok=file_exist_ok, timestamp=timestamp,
            time_prefix=time_prefix, verbose=verbose, clear=clear, **kwargs
        )

    def log_to_json(
            self, filename: str = 'log.json', file_exist_ok: bool = False,
            timestamp: bool = True, time_prefix: bool = False, verbose: bool = True,
            clear: bool = True, **kwargs):
        """
        Exports the consolidated session logs to a JSON file. This function first consolidates
        logs from all branches by invoking `concat_logs`, then exports the aggregated logs.

        Args:
            filename (str): The name of the JSON file to export the logs to.
            file_exist_ok (bool): If set to False, an error is raised if the file already exists.
            timestamp (bool): If True, a timestamp is appended to the filename to ensure uniqueness.
            time_prefix (bool): If True, the filename is prefixed with the current timestamp for sorting.
            verbose (bool): If True, outputs a message upon successful completion of the export.
            clear (bool): If True, clears all logs from the datalogger after the export is complete.
            **kwargs: Additional keyword arguments passed to the `DataLogger.to_json` method.
        """

        self.concat_logs()
        self.datalogger.to_json(
            filename=filename, file_exist_ok=file_exist_ok, timestamp=timestamp,
            time_prefix=time_prefix, verbose=verbose, clear=clear, **kwargs
        )

    @classmethod
    def from_csv(
            cls,
            filepath: str,
            default_branch_name: str | None = None,
            system: System | str | Dict[str, Any] | None = None,
            sender: str | None = None,
            llmconfig: Dict | None = None,
            service: Any = None,
            actions: BaseActionNode | List[BaseActionNode] | None = None,
            instruction_sets: Dict | None = None,
            action_manager: ActionManager | None = None,
            persist_path: str | None = None,
            read_kwargs: Dict | None = None,
            **kwargs: Any
    ) -> 'Session':
        """
        Creates a new Session instance from conversation data stored in a CSV file. Initializes
        a default branch with the data loaded from the specified CSV file, along with any
        additional configurations provided.

        Args:
            filepath (str): Path to the CSV file containing conversation data.
            default_branch_name (str | None): Name for the default branch. If not provided,
                'main' is used.
            system (System | str | Dict[str, Any] | None): Initial system message or configuration
                for the default branch.
            sender (str | None): Default sender name for system messages in the default branch.
            llmconfig (Dict | None): Configuration for the LLM service in the default branch.
            service (Any): LLM service instance for natural language processing in the default branch.
            actions (BaseActionNode | List[BaseTool] | None): Tools to register with the default branch's
                action manager.
            instruction_sets (Dict | None): Instruction sets for structured interactions in the
                default branch.
            action_manager (ActionManager | None): An action manager for managing actions within the
                default branch.
            persist_path (str | None): Path for persisting session data and logs.
            read_kwargs (Dict | None): Additional keyword arguments passed to `pd.read_csv()` when
                loading the CSV file.
            **kwargs (Any): Additional keyword arguments for initializing the session and the
                default branch.

        Returns:
            Session: An initialized Session instance with a default branch loaded from the CSV file.

        Example:
            >>> session = Session.from_csv('data/conversations.csv', default_branch_name='Support')
            This creates a new session with conversation data loaded from 'data/conversations.csv',
            setting up a default branch named 'Support'.
        """

        default_branch = Branch.from_csv(
            sender=sender,
            filepath=filepath, branch_name=default_branch_name or 'main',
            system=system, llmconfig=llmconfig, service=service, actions=actions,
            instruction_sets=instruction_sets, persist_path=persist_path,
            action_manager=action_manager, read_kwargs=read_kwargs)

        self = cls(
            default_branch=default_branch, datalogger=datalogger,
            persist_path=persist_path, **kwargs
        )

        return self

    @classmethod
    def from_json(
            cls,
            filepath: str,
            default_branch_name: str | None = None,
            system: System | str | Dict[str, Any] | None = None,
            sender: str | None = None,
            llmconfig: Dict | None = None,
            service: Any = None,
            actions: BaseActionNode | List[BaseActionNode] | None = None,
            instruction_sets: Dict | None = None,
            action_manager: ActionManager | None = None,
            persist_path: str | None = None,
            read_kwargs: Dict | None = None,
            **kwargs: Any
    ) -> 'Session':
        """
        Initializes a Session instance from conversation data stored in a JSON file, creating
        a default branch with the imported data and any additional configurations provided.

        Args:
            filepath (str): Path to the JSON file containing conversation data.
            default_branch_name (str | None): Name for the default branch. Defaults to 'main'
                if not specified.
            system (System | str | Dict[str, Any] | None): Initial system message or configuration
                for the default branch.
            sender (str | None): Default sender name for system messages in the default branch.
            llmconfig (Dict | None): Configuration for the LLM service in the default branch.
            service (Any): LLM service instance for natural language processing in the default branch.
            actions (BaseActionNode | List[BaseTool] | None): Tools to register with the default branch's
                action manager.
            instruction_sets (Dict | None): Instruction sets for structured interactions in the
                default branch.
            action_manager (ActionManager | None): An action manager for managing actions within the
                default branch.
            persist_path (str | None): Path for persisting session data and logs.
            read_kwargs (Dict | None): Additional keyword arguments for `pd.read_json()` when
                loading the JSON file.
            **kwargs (Any): Further keyword arguments for initializing the session and its default branch.

        Returns:
            Session: A newly initialized Session instance with a default branch configured with
            the JSON file data.

        Example:
            >>> session = Session.from_json('data/conversations.json', default_branch_name='CustomerService')
            This creates a new session with conversation data loaded from 'data/conversations.json',
            setting up a default branch named 'CustomerService'.
        """

        default_branch = Branch.from_json(
            sender=sender,
            filepath=filepath, branch_name=default_branch_name or 'main',
            system=system, llmconfig=llmconfig, service=service, actions=actions,
            instruction_sets=instruction_sets, persist_path=persist_path,
            action_manager=action_manager, read_kwargs=read_kwargs)

        self = cls(
            default_branch=default_branch, datalogger=datalogger,
            persist_path=persist_path, **kwargs
        )

        return self

    def to_csv(
            self,
            filepath: str | None = None,
            branch: str | Branch = 'all',
            file_exist_ok: bool = False,
            timestamp: bool = True,
            time_prefix: bool = False,
            verbose: bool = True,
            clear: bool = True,
            **kwargs: Any
    ):
        """
        Exports conversation data to a CSV file, with options to target a specific branch or all
        branches for the export. This method facilitates the sharing and analysis of conversation
        data outside the session environment.

        Args:
            filepath (str | None): Path to the CSV file where data will be exported. If not provided,
                a default naming scheme based on the branch name and timestamp is used.
            branch (str): Specifies the branch to export. Use 'all' to export data from all branches.
                Default is 'all'.
            file_exist_ok (bool): If False, raises an error if the target file already exists.
                Default is False.
            timestamp (bool): If True, appends a timestamp to the filename to ensure uniqueness.
                Default is True.
            time_prefix (bool): If True, prefixes the filename with a timestamp for easy sorting.
                Default is False.
            verbose (bool): If True, prints a message upon successful export. Default is True.
            clear (bool): If True, clears the branch's messages after export. Default is True.
            **kwargs (Any): Additional keyword arguments for the export process, passed directly
                to the underlying pandas DataFrame to_csv method.

        This method first checks if the export involves all branches or a single branch, aggregating
        messages accordingly. It then proceeds to export the data to a CSV file, applying any specified
        filename modifications such as timestamp addition.

        Example:
            >>> session.to_csv(filepath='all_conversations.csv', branch='all')
            This exports the conversation data from all branches to 'all_conversations.csv'.
        """

        if branch == 'all':
            self.default_branch.messages = self.all_messages
            self.default_branch.to_csv(
                filepath=filepath, file_exist_ok=file_exist_ok, timestamp=timestamp,
                time_prefix=time_prefix, verbose=verbose, clear=clear, **kwargs
            )
        else:
            branch = self.get_branch(branch)
            branch.to_csv(
                filepath=filepath, file_exist_ok=file_exist_ok, timestamp=timestamp,
                time_prefix=time_prefix, verbose=verbose, clear=clear, **kwargs
            )

    def to_json(
            self,
            filepath: str | None = None,
            branch: str | Branch | None = None,
            file_exist_ok: bool = False,
            timestamp: bool = True,
            time_prefix: bool = False,
            verbose: bool = True,
            clear: bool = True,
            **kwargs: Any
    ):
        """
        Exports conversation data to a JSON file, targeting either a specific branch or all
        branches within the session. This method offers a structured format for conversation
        data, suitable for integrations and further processing.

        Args:
            filepath (str | None): Path or name of the JSON file to export the data to. If None,
                a default naming scheme based on the branch name and timestamp will be used.
            branch (str): Specifies the branch to export. Use 'all' to include data from every branch.
                Default is 'all'.
            file_exist_ok (bool): If set to False, an error is raised if the output file already exists.
                Default is False.
            timestamp (bool): Adds a timestamp to the filename to ensure uniqueness. Default is True.
            time_prefix (bool): Prefixes the filename with a timestamp for sorting purposes. Default is False.
            verbose (bool): If True, outputs a success message upon completion. Default is True.
            clear (bool): If True, clears the data from the branch or branches after exporting. Default is True.
            **kwargs (Any): Additional keyword arguments for the exporting process, passed directly
                to the pandas DataFrame `to_json` method.

        This method aggregates conversation data according to the specified branch parameter and
        then exports it to a JSON file. The process includes options for filename customization
        and data handling post-export.

        Example:
            >>> session.to_json(filepath='conversation_data.json', branch='CustomerInquiries')
            This command exports data from the 'CustomerInquiries' branch to 'conversation_data.json'.
        """

        if branch is None or branch == 'all':
            for _, v in self.branches:
                v.to_json(
                    filepath=filepath, file_exist_ok=file_exist_ok, timestamp=timestamp,
                    time_prefix=time_prefix, verbose=verbose, clear=clear, **kwargs
                )
        else:
            branch = self.get_branch(branch)
            branch.to_json(
                filepath=filepath, file_exist_ok=file_exist_ok, timestamp=timestamp,
                time_prefix=time_prefix, verbose=verbose, clear=clear, **kwargs
            )

    def register_actions(self, actions):
        """
        Registers one or more actions with the action manager of the default branch. This method
        allows for the dynamic addition of actions to enhance the conversation capabilities of the
        session's default branch.

        Args:
            actions (Union[BaseActionNode, List[BaseTool]]): A single actions or a list of actions to be registered.

        Example:
            >>> session.register([new_faq_tool, booking_tool])
        """

        self.default_branch.register_actions(actions)

    def new_branch(
            self,
            branch_name: str | None = None,
            system: System | str | Dict[str, Any] | None = None,
            sender: str | None = None,
            messages: DataFrame | None = None,
            instruction_sets: Dict | None = None,
            action_manager: ActionManager | None = None,
            service: Any = None,
            llmconfig: Dict | None = None,
            actions: BaseActionNode | List[BaseActionNode] | None = None,
            datalogger: DataLogger | None = None,
            persist_path: str | None = None,
            **kwargs: Any
    ) -> None:
        """
        Creates and adds a new conversation branch to the session. This method initializes
        a Branch instance with specified configurations and registers it within the session,
        enhancing the system's capability to manage diverse conversation flows.

        Args:
            branch_name (str | None): The name of the new branch. Must be unique across the session.
            system (System | str | Dict[str, Any] | None): Initial system message or configuration
                for the new branch.
            sender (str | None): Default sender name for system messages in the new branch.
            messages (DataFrame | None): Preloaded conversation messages for the new branch.
            instruction_sets (Dict | None): Instruction sets for structured interactions in the new branch.
            action_manager (ActionManager | None): An action manager for managing actions within the
                new branch.
            service (Any): LLM service instance for natural language processing in the new branch.
            llmconfig (Dict | None): Configuration for the LLM service in the new branch.
            actions (BaseTool | List[BaseActionNode] | None): Tools to register with the new branch's
                action manager.
            datalogger (DataLogger | None): A DataLogger instance for logging activities in the new branch.
            persist_path (str | None): Path for persisting data and logs related to the new branch.
            **kwargs (Any): Additional keyword arguments for branch initialization.

        This method facilitates the dynamic addition of branches to the session, allowing for
        tailored conversation management and specialized interactions within distinct branches.

        Example:
            >>> session.new_branch(branch_name='TechnicalSupport', system='Welcome to Technical Support')
            This command creates a new branch named 'TechnicalSupport' with a welcome message.
        """

        if branch_name in self.branches.keys():
            raise ValueError(
                f'Invalid new branch name {branch_name}. Branch already existed.')

        new_branch = Branch(
            branch_name=branch_name,
            system=system,
            messages=messages,
            sender=sender,
            service=service or self.service,
            llmconfig=llmconfig or self.llmconfig,
            actions=actions,
            action_manager=action_manager,
            instruction_sets=instruction_sets,
            datalogger=datalogger,
            persist_path=persist_path,
            **kwargs
        )

        self.branches[branch_name] = new_branch
        self.mail_manager.sources[branch_name] = new_branch
        self.mail_manager.mails[branch_name] = {}

    def get_branch(
            self,
            branch: str | Branch | None = None,
            get_name: bool = False
    ) -> Branch | tuple[Branch, str]:
        """
        Retrieves a branch from the session based on its name or direct reference. If no branch
        is specified, returns the default branch. This method facilitates accessing branches for
        operations like message sending, logging, and actions management.

        Args:
            branch (str | Branch | None): The name of the branch or the Branch instance to retrieve.
                If None, the default branch is returned.
            get_name (bool): If True, returns a tuple of (Branch instance, branch name). Useful for
                cases where both the instance and its name are needed.

        Returns:
            Branch | tuple[Branch, str]: The requested Branch instance, or a tuple of the Branch
            instance and its name if get_name is True.

        Raises:
            ValueError: If the specified branch name does not exist or the branch reference is invalid.

        Example:
            >>> my_branch = session.get_branch("CustomerService")
            >>> my_branch, branch_name = session.get_branch(get_name=True)
            Both examples demonstrate how to retrieve a branch, with the second example also
            retrieving the branch's name.
        """

        if isinstance(branch, str):
            if branch not in self.branches.keys():
                raise ValueError(f'Invalid branch name {branch}. Not exist.')
            else:
                if get_name:
                    return self.branches[branch], branch
                return self.branches[branch]

        elif isinstance(branch, Branch) and branch in self.branches.values():
            if get_name:
                return (
                    branch,
                    [key for key, value in self.branches.items() if value == branch][0]
                )
            return branch

        elif branch is None:
            if get_name:
                return self.default_branch, self.default_branch_name
            return self.default_branch

        else:
            raise ValueError(f'Invalid branch input_ {branch}.')

    def change_default_branch(self, branch: str | Branch) -> None:
        """
        Sets a new default branch for the session. This method allows dynamically changing the
        session's focal point to another existing branch, facilitating shifts in conversational
        focus or operational context.

        Args:
            branch (str | Branch): The name of the branch or the Branch instance to set as the
            new default.

        Raises:
            ValueError: If the specified branch does not exist within the session.

        Example:
            >>> session.change_default_branch("AfterSalesSupport")
            This sets the "AfterSalesSupport" branch as the new default branch for the session.
        """

        branch_ = self.get_branch(branch)
        self.default_branch = branch_

    def delete_branch(self, branch: str | Branch, verbose: bool = True) -> bool:
        """
        Removes a specified branch from the session. This operation deletes the branch's reference
        from the session, effectively removing its configuration, messages, and actions from the
        session context.

        Args:
            branch (str | Branch): The name of the branch or the Branch instance to delete.
            verbose (bool): If True, prints a confirmation message upon successful deletion.

        Returns:
            bool: True if the branch was successfully deleted, False otherwise.

        Raises:
            ValueError: If attempting to delete the default branch, or the specified branch does not exist.

        Example:
            >>> session.delete_branch("TemporaryBranch")
            Deletes the "TemporaryBranch" from the session and confirms deletion if verbose is True.
        """

        _, branch_name = self.get_branch(branch, get_name=True)

        if branch_name == self.default_branch_name:
            raise ValueError(
                f'{branch_name} is the current default branch, please switch to another branch before delete it.'
            )
        else:
            self.branches.pop(branch_name)
            # self.mail_manager.sources.pop(branch_name)
            self.mail_manager.mails.pop(branch_name)
            if verbose:
                print(f'Branch {branch_name} is deleted.')
            return True

    def merge_branch(
            self,
            from_branch: str | Branch,
            to_branch: str | Branch,
            update: bool = True,
            del_: bool = False
    ) -> None:
        """
        Merges data and configurations from one branch into another within the session. This
        method allows for the consolidation of conversational data, actions, and configurations
        from multiple branches, streamlining session management.

        Args:
            from_branch (str | Branch): The source branch to merge from.
            to_branch (str | Branch): The target branch to merge into.
            update (bool): If True, updates existing entries in the target branch with those from
            the source. If False, retains existing entries in the target branch unchanged.
            del_ (bool): If True, deletes the source branch after merging.

        Raises:
            ValueError: If either the source or target branch does not exist within the session.

        Example:
            >>> session.merge_branch("TemporaryConversations", "MainConversations", del_=True)
            Merges data from "TemporaryConversations" into "MainConversations" and deletes the
            "TemporaryConversations" branch.
        """

        from_branch = self.get_branch(branch=from_branch)
        to_branch = self.get_branch(branch=to_branch)
        to_branch.merge_branch(from_branch, update=update)

        if del_:
            if from_branch == self.default_branch:
                self.default_branch = to_branch
            self.delete_branch(from_branch, verbose=False)

    def collect(self,
                sender: str | Branch | list[str] | list[Branch] | None = None) -> None:
        """
        Initiates the collection of messages from specified branches or all branches if none are
        specified. This method prepares the messages for sending, aggregation, or analysis by
        gathering them into a central location within the session.

        Args:
            sender (str | Branch | list[str] | list[Branch] | None): The branch(es) from which to
            collect messages. If None or not specified, messages will be collected from all branches.

        This method is especially useful for preparing messages for bulk processing or analysis,
        allowing for efficient message management across different conversation branches.

        Example:
            >>> session.collect("CustomerService")
            >>> session.collect(sender=["SalesInquiries", "TechnicalSupport"])
            These commands collect messages from the "CustomerService" branch and then from both
            "SalesInquiries" and "TechnicalSupport" branches, respectively.
        """

        if sender is None:
            for branch in self.branches.keys():
                self.mail_manager.collect(branch)
        else:
            if not isinstance(sender, list):
                sender = [sender]
            for branch in sender:
                if isinstance(branch, Branch):
                    branch = branch.name
                if isinstance(branch, str):
                    self.mail_manager.collect(branch)

    def send(self,
             recipient: str | Branch | list[str] | list[Branch] | None = None) -> None:
        """
        Dispatches collected messages to their intended recipients from specified branches or all
        branches if none are specified. This method facilitates the outward flow of messages,
        ensuring they reach their designated targets.

        Args:
            recipient (str | Branch | list[str] | list[Branch] | None): The branch(es) whose messages
            are to be sent. If None or not specified, messages from all branches will be dispatched.

        This method supports targeted message delivery within the session, enhancing the conversational
        system's responsiveness and interaction capabilities.

        Example:
            >>> session.send("CustomerFeedback")
            >>> session.send(recipient=["OrderProcessing", "ReturnsAndRefunds"])
            These commands send messages to the "CustomerFeedback" branch and then to both
            "OrderProcessing" and "ReturnsAndRefunds" branches, respectively.
        """

        if recipient is None:
            for branch in self.branches.keys():
                self.mail_manager.send(branch)
        else:
            if not isinstance(recipient, list):
                recipient = [recipient]
            for branch in recipient:
                if isinstance(branch, Branch):
                    branch = branch.name
                if isinstance(branch, str):
                    self.mail_manager.send(branch)

    def collect_send_all(self, receive_all: bool = False) -> None:
        """
        Performs a complete cycle of collecting and sending messages across all branches within the
        session. Optionally, it can also trigger the reception of all pending messages, ensuring a
        full synchronization of conversational states.

        Args:
            receive_all (bool): If True, after collecting and sending, it will trigger all branches
            to process (receive) all pending incoming messages, completing the communication cycle.

        This method is designed for comprehensive message management, facilitating a synchronized
        state across all conversation branches, thereby enhancing overall session coherence and
        efficiency.

        Example:
            >>> session.collect_send_all()
            >>> session.collect_send_all(receive_all=True)
            The first command collects and sends messages across all branches. The second command
            additionally processes all pending incoming messages.
        """

        self.collect()
        self.send()
        if receive_all:
            for branch in self.branches.values():
                branch.receive_all()

    def setup_default_branch(self, **kwargs):
        """
        Configures the default branch with the provided parameters. This method allows for the reconfiguration
        of the default branch's settings and properties, applying new configurations as needed.

        This method primarily serves internal purposes and should be used with caution, as it directly affects
        the session's operational context and default conversational flow.

        Args:
            **kwargs: Keyword arguments corresponding to the Branch class's initialization parameters, used to
                reconfigure the default branch.

        Example:
            >>> session.setup_default_branch(system="Updated system message", sender="NewDefaultSender")
        """

        self._setup_default_branch(**kwargs)
        self._verify_default_branch()

    def _verify_default_branch(self):
        if self.branches:
            if self.default_branch_name not in self.branches.keys():
                raise ValueError('default branch name is not in imported branches')
            if self.default_branch is not self.branches[self.default_branch_name]:
                raise ValueError(
                    f'default branch does not match Branch object under {self.default_branch_name}')

        if not self.branches:
            self.branches[self.default_branch_name] = self.default_branch

    def _setup_default_branch(
            self, system, sender, default_branch, default_branch_name, messages,
            instruction_sets, action_manager, service, llmconfig, actions, persist_path,
            logger
    ):

        branch = default_branch or Branch(
            name=default_branch_name, service=service, llmconfig=llmconfig,
            actions=actions,
            action_manager=action_manager, instruction_sets=instruction_sets,
            messages=messages, persist_path=persist_path, logger=logger
        )

        self.default_branch = branch
        self.default_branch_name = default_branch_name or 'main'
        if system:
            self.default_branch.add_message(system=system, sender=sender)

        self.llmconfig = self.default_branch.llmconfig

    async def chat(self, instruction: Union[Instruction, str],
                   context: Optional[Any] = None,
                   sender: Optional[str] = None,
                   system: Optional[Union[System, str, Dict[str, Any]]] = None,
                   actions: Union[bool, BaseActionNode, List[BaseActionNode], str, List[str]] = False,
                   out: bool = True, invoke: bool = True, branch: Branch | str = None,
                   **kwargs) -> Any:
        """
        Conducts an asynchronous chat exchange, processing instructions and optionally
        invoking actions.

        Args:
            branch:
            instruction: The chat instruction, either as a string or Instruction object.
            context: Optional context for enriching the chat conversation.
            sender: Optional identifier for the sender of the chat message.
            system: Optional system message or configuration for the chat.
            actions: Specifies actions to invoke as part of the chat session.
            out: If True, sends the instruction as a system message.
            invoke: If True, invokes the specified actions.
            **kwargs: Additional keyword arguments to pass to the model calling.
        """
        branch = self.get_branch(branch)

        return await branch.chat(
            instruction=instruction, context=context,
            sender=sender, system=system, actions=actions,
            out=out, invoke=invoke, **kwargs
        )

    async def ReAct(self, instruction: Union[Instruction, str],
                    context: Optional[Any] = None,
                    sender: Optional[str] = None,
                    system: Optional[Union[System, str, Dict[str, Any]]] = None,
                    actions: Union[bool, BaseActionNode, List[BaseActionNode], str, List[str]] = False,
                    num_rounds: int = 1, branch=None, **kwargs) -> Any:
        """
        Performs a reason-action cycle with optional actions invocation over multiple rounds,
        simulating decision-making processes based on initial instructions and available actions.

        Args:
            branch:
            instruction: Initial instruction for the cycle, as a string or Instruction object.
            context: Context relevant to the instruction, enhancing the reasoning process.
            sender: Identifier for the message sender, enriching the conversational context.
            system: Initial system message or configuration for the chat session.
            actions: Tools to be invoked during the reason-action cycle.
            num_rounds (int): Number of reason-action cycles to execute.
            **kwargs: Additional keyword arguments for customization and actions invocation.
        """
        branch = self.get_branch(branch)

        return await branch.ReAct(
            instruction=instruction, context=context,
            sender=sender, system=system, actions=actions,
            num_rounds=num_rounds, **kwargs
        )

    async def auto_followup(
            self,
            instruction: Union[Instruction, str],
            context=None,
            sender=None,
            system=None,
            persist_path: Union[
                bool, BaseActionNode, List[BaseActionNode], str, List[str], List[Dict]] = False,
            max_followup: int = 3,
            out=True,
            branch=None,
            **kwargs
    ) -> Any:
        """
        Automatically generates follow-up actions based on previous chat interactions
        and actions invocations.

        Args:
            branch:
            instruction: The initial instruction for follow-up, as a string or Instruction.
            context: Context relevant to the instruction, supporting the follow-up process.
            sender: Identifier for the message sender, adding context to the follow-up.
            system: Initial system message or configuration for the session.
            persist_path: Specifies actions to consider for follow-up actions.
            max_followup (int): Maximum number of follow-up chats allowed.
            out (bool): If True, outputs the result of the follow-up action.
            **kwargs: Additional keyword arguments for follow-up customization.
        """
        branch = self.get_branch(branch)

        return await branch.auto_followup(
            instruction=instruction, context=context,
            sender=sender, system=system, persist_path=persist_path,
            max_followup=max_followup, out=out, **kwargs
        )

    # def add_instruction_set(self, name: str, instruction_set: InstructionSet) -> None:
    #     """
    #     Adds an instruction set to the current active branch.
    #
    #     Args:
    #         name (str): The name of the instruction set.
    #         instruction_set (InstructionSet): The instruction set to add.
    #     """
    #     self.default_branch.add_instruction_set(name, instruction_set)
    #
    # def remove_instruction_set(self, name: str) -> bool:
    #     """
    #     Removes an instruction set from the current active branch.
    #
    #     Args:
    #         name (str): The name of the instruction set to remove.
    #
    #     Returns:
    #         bool: True if the instruction set is removed, False otherwise.
    #     """
    #     return self.default_branch.remove_instruction_set(name)
