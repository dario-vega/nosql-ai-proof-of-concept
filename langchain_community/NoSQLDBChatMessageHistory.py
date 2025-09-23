from typing import TYPE_CHECKING, Dict, List, Optional, Sequence
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.messages import (
    BaseMessage,
    messages_from_dict,
    messages_to_dict,
)
from borneo import (Regions, NoSQLHandle, NoSQLHandleConfig,
                    PutRequest,QueryRequest, DeleteRequest, TableRequest, GetRequest, PutOption,QueryIterableResult, GetTableRequest,
                    TableNotFoundException, TableLimits, State, TimeToLive)
from borneo.iam import SignatureProvider
from borneo.kv import StoreAccessTokenProvider

# import the time module
import time


#global oracleNoSQL 
#oracleNoSQL = None;

class NoSQLDBChatMessageHistory(BaseChatMessageHistory):
    """Chat message history that stores history in Oracle NoSQL DB.

    Args:
        region: region to connect
        table_name: name of the table to use
        compartment_id: name of the compartment to use
        session_id: arbitrary key that is used to store the messages
            of a single chat session.
        ttl: Optional Time-to-live (TTL) in minutes
        ru,wu,storage : default limits for the table
        SAME AUTH as for ChatOCIGenAI
        auth_type: str
           The authentication type to use, e.g., API_KEY (default), SECURITY_TOKEN, INSTANCE_PRINCIPAL, RESOURCE_PRINCIPAL.
        auth_profile: Optional[str]
          The name of the profile in ~/.oci/config, if not specified , DEFAULT will be used.
        auth_file_location: Optional[str]
          Path to the config file, If not specified, ~/.oci/config will be used.

    """
    def __init__(
        self,
        region: str,
        table_name: str,
        compartment_id: str,
        session_id: str,
        ttl: Optional[int] = None,
        auth_type: Optional[str] = "API_KEY",
        auth_profile: Optional[str] = "DEFAULT",
        auth_file_location: Optional[str] = "~/.oci/config",        
        ru: Optional[str] = 10,
        wu: Optional[str] = 10,
        storage: Optional[str] = 1,
    ):
        
        self.region = region
        self.table = table_name
        self.compartment_id = compartment_id
        self.session_id = session_id
        self.ttl = ttl

        print("Connecting to the Oracle NoSQL Cloud Service: " + self.session_id + session_id)
        
        if auth_type == "API_KEY":
           provider = SignatureProvider(config_file=auth_file_location, profile_name=auth_profile);
        elif auth_type == "INSTANCE_PRINCIPAL":
           provider = SignatureProvider.create_with_instance_principal();
        elif auth_type == "RESOURCE_PRINCIPAL":
           provider = SignatureProvider.create_with_resource_principal();        
        else:
           raise IllegalArgumentException('Unknown environment: ' + nosql_env)
        config = NoSQLHandleConfig(self.region, provider).set_logger(None)
        config.set_default_compartment(self.compartment_id)
        #if oracleNoSQL is None:
        #   oracleNoSQL = NoSQLHandle(config)
        # self.handle  = oracleNoSQL
        self.handle = NoSQLHandle(config)

        # creating table if not exists - avoid borneo.exception.OperationThrottlingException: Tenant exceeded DDL operation rate limit.
        try:
            getTableRequest = GetTableRequest().set_table_name(self.table)
            result = self.handle.get_table(getTableRequest)
            print('After get table: ' + str(result))
        except TableNotFoundException as e:
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
        start_time = time.time()
        request = GetRequest().set_key({'id': self.session_id}).set_table_name(self.table)
        result = self.handle.get(request)
        if result.get_value() is None:
          retrieved_messages = []
        else:
          retrieved_messages = result.get_value()['items']
        messages = messages_from_dict(retrieved_messages)
        end_time = time.time()
        elapsed_time = end_time - start_time
        print("Retrieve the messages from NoSQLDB: " + self.session_id  + " " + str(elapsed_time) )
        return messages

    @messages.setter
    def messages(self, messages: List[BaseMessage]) -> None:
        raise NotImplementedError(
            "Direct assignment to 'messages' is not allowed."
            " Use the 'add_messages' instead."
        )

    def add_messages(self, messages: Sequence[BaseMessage]) -> None:        
        """Append the message to the record in NoSQLDB"""
        existing_messages = messages_to_dict(self.messages)
        existing_messages.extend(messages_to_dict(messages))
        
        start_time = time.time()
        request = PutRequest().set_table_name(self.table)
        if self.ttl is not None:
            request.set_ttl (TimeToLive.of_hours(self.ttl))
        request.set_value({"id":self.session_id , "items":existing_messages})
        result = self.handle.put(request)
        end_time = time.time()
        elapsed_time = end_time - start_time
        print("Append the messages to NoSQLDB: " + self.session_id  + " " + str(elapsed_time) )      


    def clear(self) -> None:
        """Clear session memory from NoSQLDB"""
        print("Delete the messages to NoSQLDB: " + self.session_id )      
        request = DeleteRequest().set_key({'id': self.session_id}).set_table_name(self.table)
        result = self.handle.delete(request)

    def close_handle(self) -> None:
        """Clear session memory from NoSQLDB"""
        if self.handle is not None:
           print("Close the connection to the Oracle NoSQL Cloud Service")
           self.handle.close()
