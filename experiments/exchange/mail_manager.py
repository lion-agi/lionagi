from collections import deque
from pydantic import Field, field_validator
from lionagi.libs import AsyncUtil
from lionagi.core.generic import Worker, Transfer, Node, Mail, Signal


class MailManager(Worker):
    
    clients: dict[str, Node] = Field(
        default_factory=dict,
        description="The clients of the mail manager - {client_id: source}"
    )
    
    transfers: dict[str, Transfer] = Field(
        default_factory=dict,
        description="The transfers of the mail manager - {client_id: transfer}"
    )

    @field_validator("sources", mode="before")
    def _validate_clients(cls, values):
        if isinstance(values, Node):
            return {values.id_: values}
        elif isinstance(values, list) and isinstance(values[0], Node):
            return {v.id_: v for v in values}
        elif isinstance(values, dict) and isinstance(list(values.values())[0], Node):
            return {v.id_: v for _, v in values.items()}
        elif isinstance(values, dict):
            return values
        else:
            raise ValueError("Failed to add source, please input list or dict.")

    def collect(self, sender: str | Node):
        client = sender
        try:
            client = client if isinstance(client, Node) else self.clients[client]
            if client.id_ not in self.clients:
                raise ValueError(f"Sender {sender} is not connected with the mail manager.")
        except KeyError:
            raise ValueError(f"Sender {sender} is not connected with the mail manager.")
    
        if client.id_ not in self.transfers:
            self.transfers[client.id_] = Transfer()
    
        while client.mailbox.sequence_out:
            mail_id = client.mailbox.sequence_out.popleft()
            mail_: Mail | Signal = client.mailbox.pile.pop(mail_id)
            
            if mail_.recipient not in self.clients:
                raise ValueError(
                    f"Recipient {mail_.recipient} is not connected with the mail manager."
                )

            if mail_.recipient not in self.transfers:
                self.transfers[mail_.recipient] = Transfer()
                
            recipient_transfer = self.transfers[mail_.recipient]

            if mail_.sender not in recipient_transfer:
                recipient_transfer.schedule[mail_.sender] = deque()
    
            recipient_transfer.schedule[mail_.sender].append(mail_)
    
    def deliver(self, sender: str | Node):
        client_id = sender.id_ if isinstance(sender, Node) else sender
        client_transfer = self.transfers.get(client_id, Transfer())
        if client_transfer.is_empty:
            return
        
        for recipient in list(client_transfer.keys()):
            mails = client_transfer.schedule.pop(recipient)
            
            if sender not in self.clients[recipient].mailbox.sequence_in:
                self.clients[recipient].mailbox.sequence_in[sender] = mails
            
            else:
                while mails:
                    mail_ = mails.popleft()
                    self.clients[recipient].mailbox.sequence_in[sender].append(mail_.id_)
                    self.clients[recipient].mailbox.pile[mail_.id_] = mail_

    def collect_all(self):
        for client in self.clients:
            self.collect(client)
            
    def deliver_all(self):
        for client in self.clients:
            self.deliver(client)

    def forward(self):
        self.collect_all()
        self.deliver_all()
    
    async def perform(self, refresh_time=1):
        while not self.stopped:
            self.forward()
            await AsyncUtil.sleep(refresh_time)

    def add_client(self, client: Node, transfer: Transfer = Transfer()):
        if client.id_ in self.clients:
            raise ValueError(f"Client {client.id_} already exists.")
        self.clients[client.id_] = client
        self.transfers[client.id_] = transfer

    def remove_client(self, client: str | Node):
        client_id = client.id_ if isinstance(client, Node) else client
        self.clients.pop(client_id, None)
        self.transfers.pop(client_id, None)
