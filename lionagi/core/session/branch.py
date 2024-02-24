from .base.base_branch import BaseBranch



class Branch(BaseBranch):

    def __init__(self, branch_name=None, system=None, messages=None, service=None,
                 sender=None, llmconfig=None, actions=None, datalogger=None,
                 persist_path=None, instruction_sets=None, action_manager=None, **kwargs):

        # init base conversation class
        super().__init__(messages=messages, datalogger=datalogger,
                         persist_path=persist_path, **kwargs)

        # add branch name
        self.branch_name = branch_name
        self.sender = sender or 'system'

        # add action manager and register actions
        self.action_manager = action_manager if action_manager else ActionManager()
        if actions:
            try:
                self.register_actions(actions)
            except Exception as e:
                raise TypeError(f"Error in registering actions: {e}")

        # add service and llmconfig
        self.service, self.llmconfig = self._add_service(service, llmconfig)
        self.status_tracker = StatusTracker()

        # add instruction sets
        self.instruction_sets = instruction_sets

        # add pending ins and outs for mails
        self.pending_ins = {}
        self.pending_outs = deque()

        # add system
        system = system or 'you are a helpful assistant'
        self.add_message(system=system)

    @classmethod
    def from_csv(cls, filepath, branch_name=None, service=None, llmconfig=None,
                 actions=None, datalogger=None, persist_path=None, instruction_sets=None,
                 action_manager=None, read_kwargs=None, **kwargs):

        self = cls._from_csv(
            filepath=filepath, read_kwargs=read_kwargs, branch_name=branch_name,
            service=service, llmconfig=llmconfig, actions=actions, datalogger=datalogger,
            persist_path=persist_path, instruction_sets=instruction_sets,
            action_manager=action_manager, **kwargs)

        return self

    @classmethod
    def from_json(cls, filepath, branch_name=None, service=None, llmconfig=None,
                  actions=None, datalogger=None, persist_path=None, instruction_sets=None,
                  action_manager=None, read_kwargs=None, **kwargs):

        self = cls._from_json(
            filepath=filepath, read_kwargs=read_kwargs, branch_name=branch_name,
            service=service, llmconfig=llmconfig, actions=actions, datalogger=datalogger,
            persist_path=persist_path, instruction_sets=instruction_sets,
            action_manager=action_manager, **kwargs)

        return self

    def messages_describe(self) -> Dict[str, Any]:

        return {
            "total_messages": len(self.messages),
            "summary_by_role": self._info(),
            "summary_by_sender": self._info(use_sender=True),
            "instruction_sets": self.instruction_sets,
            "registered_actions": self.action_manager.registry,
            "messages": [
                msg.to_dict() for _, msg in self.messages.iterrows()
            ],
        }

    @property
    def has_actions(self) -> bool:

        return self.action_manager.registry != {}

    # todo: also update other attributes
    def merge_branch(self, branch: 'Branch', update: bool = True) -> None:

        message_copy = branch.messages.copy()
        self.messages = self.messages.merge(message_copy, how='outer')
        self.datalogger.extend(branch.datalogger.logs)

        if update:
            self.instruction_sets.update(branch.instruction_sets)
            self.action_manager.registry.update(
                branch.action_manager.registry
            )
        else:
            for key, value in branch.instruction_sets.items():
                if key not in self.instruction_sets:
                    self.instruction_sets[key] = value

            for key, value in branch.action_manager.registry.items():
                if key not in self.action_manager.registry:
                    self.action_manager.registry[key] = value

    # ----- action manager methods ----- #
    def register_actions(self, actions: Union[BaseActionNode, List[BaseActionNode]]) -> None:

        if not isinstance(actions, list):
            actions = to_list(actions, flatten=True, dropna=True)
        self.action_manager.register_actions(actions=actions)

    def delete_actions(
            self, actions: Union[bool, T, List[T], str, List[str], List[Dict[str, Any]]],
            verbose: bool = True
    ) -> bool:

        if isinstance(actions, list):
            if SysUtil.is_same_dtype(actions, str):
                for act_ in actions:
                    if act_ in self.action_manager.registry:
                        self.action_manager.registry.pop(act_)
                if verbose:
                    print("actions successfully deleted")
                return True
            elif SysUtil.is_same_dtype(actions, _cols):
                for act_ in actions:
                    if act_.name in self.action_manager.registry:
                        self.action_manager.registry.pop(act_.name)
                if verbose:
                    print("actions successfully deleted")
                return True
        if verbose:
            print("actions deletion failed")
        return False

    def send(self, recipient: str, category: str, package: Any) -> None:


        mail_ = BaseMail(
            sender=self.sender, recipient=recipient, category=category,
            package=package)
        self.pending_outs.append(mail_)

    def receive(self, sender: str, messages: bool = True, actions: bool = True,
                service: bool = True, llmconfig: bool = True) -> None:

        skipped_requests = deque()
        if sender not in self.pending_ins:
            raise ValueError(f'No package from {sender}')
        while self.pending_ins[sender]:
            mail_ = self.pending_ins[sender].popleft()

            if mail_.category == 'messages' and messages:
                if not isinstance(mail_.package, pd.DataFrame):
                    raise ValueError('Invalid messages format')
                MessageUtil.validate_messages(mail_.package)
                self.messages = self.messages.merge(mail_.package, how='outer')
                continue

            elif mail_.category == 'actions' and actions:
                if not isinstance(mail_.package, BaseActionNode):
                    raise ValueError('Invalid actions format')
                self.action_manager.register_actions([mail_.package])

            elif mail_.category == 'provider' and service:
                if not isinstance(mail_.package, BaseService):
                    raise ValueError('Invalid provider format')
                self.service = mail_.package

            elif mail_.category == 'llmconfig' and llmconfig:
                if not isinstance(mail_.package, dict):
                    raise ValueError('Invalid llmconfig format')
                self.llmconfig.update(mail_.package)

            else:
                skipped_requests.append(mail_)

        self.pending_ins[sender] = skipped_requests

    def receive_all(self) -> None:

        for key in list(self.pending_ins.keys()):
            self.receive(key)

    @staticmethod
    def _add_service(service, llmconfig):
        service = service or OAIService
        if llmconfig is None:
            if isinstance(service, OpenAIService):
                from lionagi.integrations.provider import oai_schema
                llmconfig = oai_schema["chat/completions"]["config"]
            else:
                llmconfig = {}
        return service, llmconfig

    def _is_invoked(self) -> bool:
        content = self.messages.iloc[-1]['content']
        try:
            if (to_dict(content)['action_response'].keys() >=
                    {'function', 'arguments', 'output'}):
                return True
        except ValueError:
            return False

    # noinspection PyUnresolvedReferences
    async def call_chatcompletion(self, sender=None, with_sender=False, **kwargs):

        await ChatFlow.call_chatcompletion(
            self, sender=sender, with_sender=with_sender, **kwargs
        )

    async def chat(
            self,
            instruction: Union[Instruction, str],
            context: Optional[Any] = None,
            sender: Optional[str] = None,
            system: Optional[Union[System, str, Dict[str, Any]]] = None,
            actions: Union[bool, T, List[T], str, List[str]] = False,
            out: bool = True,
            invoke: bool = True,
            **kwargs) -> Any:

        return await ChatFlow.chat(
            self, instruction=instruction, context=context,
            sender=sender, system=system, actions=actions,
            out=out, invoke=invoke, **kwargs
        )

    async def ReAct(
            self,
            instruction: Union[Instruction, str],
            context=None,
            sender=None,
            system=None,
            actions=None,
            num_rounds: int = 1,
            **kwargs):

        return await ChatFlow.ReAct(
            self, instruction=instruction, context=context,
            sender=sender, system=system, actions=actions,
            num_rounds=num_rounds, **kwargs
        )

    async def auto_followup(
            self,
            instruction: Union[Instruction, str],
            context=None,
            sender=None,
            system=None,
            actions: Union[bool, T, List[T], str, List[str], List[Dict]] = False,
            max_followup: int = 3,
            out=True,
            **kwargs
    ) -> None:

        return await ChatFlow.auto_followup(
            self, instruction=instruction, context=context,
            sender=sender, system=system, actions=actions,
            max_followup=max_followup, out=out, **kwargs
        )
