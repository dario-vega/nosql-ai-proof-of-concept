from typing import TYPE_CHECKING, Dict, List, Optional, Sequence
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.messages import (
    BaseMessage,
    HumanMessage,
    SystemMessage,
    messages_from_dict,
    messages_to_dict,
)
from borneo import (Regions, NoSQLHandle, NoSQLHandleConfig,
                    PutRequest,QueryRequest, DeleteRequest, TableRequest, GetRequest, PutOption,QueryIterableResult,
                    TableLimits, State,TimeToLive)
from borneo.iam import SignatureProvider
from borneo.kv import StoreAccessTokenProvider

class NoSQLDBChatMessageHistory(BaseChatMessageHistory):
    """Chat message history that stores history in Oracle NoSQL DB.

    Args:
        region: region to connect
        table_name: name of the table to use
        compartment_id: name of the compartment to use
        session_id: arbitrary key that is used to store the messages
            of a single chat session.
        ru,wu,storage : default limits for the table
    """
    def __init__(
        self,
        region: str,
        table_name: str,
        compartment_id: str,
        session_id: str,
        ru: Optional[str] = 10,
        wu: Optional[str] = 10,
        storage: Optional[str] = 1,
    ):
        self.region = region
        self.table = table_name
        self.compartment_id = compartment_id
        self.session_id = session_id
        print("Connecting to the Oracle NoSQL Cloud Service")
        provider = SignatureProvider();
        config = NoSQLHandleConfig(self.region, provider).set_logger(None)
        config.set_default_compartment(self.compartment_id)
        self.handle = NoSQLHandle(config)
        # creating table if not exists
        statement = ('Create table if not exists {} (id STRING, items JSON, primary key(id))').format(self.table)
        request = TableRequest().set_statement(statement).set_table_limits(TableLimits(ru, wu, storage))
        self.handle.do_table_request(request, 50000, 3000)

    @property
    def messages(self) -> List[BaseMessage]:
        """Retrieve the messages from NoSQLDB"""
        # messages: List[BaseMessage] = [
        #     HumanMessage(
        #           content="Who build pyramides"
        #     ),
        #     model.invoke([HumanMessage("Who build pyramides")])
        # ]
        # stored_messages = messages_to_dict(messages)
        print("Retrieve the messages from NoSQLDB")
        request = GetRequest().set_key({'id': self.session_id}).set_table_name(self.table)
        result = self.handle.get(request)
        if result.get_value() is None:
          retrieved_messages = []
        else:
          retrieved_messages = result.get_value()['items']
        messages = messages_from_dict(retrieved_messages)
        return messages

    @messages.setter
    def messages(self, messages: List[BaseMessage]) -> None:
        raise NotImplementedError(
            "Direct assignment to 'messages' is not allowed."
            " Use the 'add_messages' instead."
        )

    def add_messages(self, messages: Sequence[BaseMessage]) -> None:        
        """Append the message to the record in NoSQLDB"""
        print("Append the messages to NoSQLDB")
        existing_messages = messages_to_dict(self.messages)
        existing_messages.extend(messages_to_dict(messages))
        
        request = PutRequest().set_table_name(self.table)
        request.set_value({"id":self.session_id , "items":existing_messages})
        result = self.handle.put(request)

    def clear(self) -> None:
        """Clear session memory from NoSQLDB"""
        request = DeleteRequest().set_key({'id': self.session_id}).set_table_name(self.table)
        result = handle.delete(request)
        print('After delete: ' + str(result))
