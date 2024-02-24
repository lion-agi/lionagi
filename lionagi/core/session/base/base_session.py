from abc import ABC
from lionagi.schema.data_logger import DataLogger
from ..branch import Branch



class Session(Branch, ABC):

    def __init__(
            self,
            system: System | str | Dict[str, Any] | None = None,
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

        super().__init__(
            branch_name=default_branch_name,
            system=system, sender=sender, llmconfig=llmconfig, service=service, actions=actions,
            instruction_sets=instruction_sets, action_manager=action_manager, messages=messages,
            persist_path=persist_path, datalogger=datalogger, **kwargs
        )

        self.default_branch = self
        self.session_logger = DataLogger(persist_path=persist_path)
        self.branches = branches or {}
        self.mail_manager = MailManager(self.branches)


    @property
    def all_messages(self) -> DataFrame:


        dfs = deque()
        for _, v in self.branches:
            dfs.append(to_df(v.messages))
        return to_df(to_list(dfs, flatten=True, dropna=True))

    @property
    def all_responses(self) -> DataFrame:

        dfs = deque()
        for _, v in self.branches:
            dfs.append(to_df(v.responses))
        return to_df(to_list(dfs, flatten=True, dropna=True))

    @property
    def all_assistant_responses(self) -> DataFrame:


        dfs = deque()
        for _, v in self.branches:
            dfs.append(to_df(v.assistant_responses))
        return to_df(to_list(dfs, flatten=True, dropna=True))

    @property
    def all_action_responses(self) -> DataFrame:

        dfs = deque()
        for _, v in self.branches:
            dfs.append(to_df(v.action_response))
        return to_df(to_list(dfs, flatten=True, dropna=True))

    @property
    def all_action_requests(self) -> DataFrame:

        dfs = deque()
        for _, v in self.branches:
            dfs.append(to_df(v.action_request))
        return to_df(to_list(dfs, flatten=True, dropna=True))

    @property
    def info(self) -> Dict[str, Any]:

        dict_ = {}
        for k, v in self.branches.items():
            dict_[k] = v.info

        return dict_

    @property
    def sender_info(self) -> Dict[str, Any]:

        dict_ = {}
        for k, v in self.branches.items():
            dict_[k] = v.sender_info

        return dict_

    @property
    def default_branch_name(self):
        return self.default_branch.branch_name


    def _concat_logs(self):

        for _, v in self.branches:
            self.session_logger.extend(v.datalogger.logs)

    def log_to_csv(
            self, filename: str = 'log.csv', file_exist_ok: bool = False,
            timestamp: bool = True, time_prefix: bool = False, verbose: bool = True,
            clear: bool = True, **kwargs):


        self._concat_logs()
        self.session_logger.to_csv(
            filepath=filename, file_exist_ok=file_exist_ok, timestamp=timestamp,
            time_prefix=time_prefix, verbose=verbose, clear=clear, **kwargs
        )

    def log_to_json(
            self, filename: str = 'log.json', file_exist_ok: bool = False,
            timestamp: bool = True, time_prefix: bool = False, verbose: bool = True,
            clear: bool = True, **kwargs):

        self._concat_logs()
        self.session_logger.to_json(
            filename=filename, file_exist_ok=file_exist_ok, timestamp=timestamp,
            time_prefix=time_prefix, verbose=verbose, clear=clear, **kwargs
        )

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

    def delete_branch(self, branch: str | Branch, verbose: bool = True) -> bool:


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


        from_branch = self.get_branch(branch=from_branch)
        to_branch = self.get_branch(branch=to_branch)
        to_branch.merge_branch(from_branch, update=update)

        if del_:
            if from_branch == self.default_branch:
                self.default_branch = to_branch
            self.delete_branch(from_branch, verbose=False)

    def collect(self,
                sender: str | Branch | list[str] | list[Branch] | None = None) -> None:


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


        self.collect()
        self.send()
        if receive_all:
            for branch in self.branches.values():
                branch.receive_all()
