import time
import uuid
from langchain_oci import ChatOCIGenAI
#from langchain_community.chat_message_histories import NoSQLDBChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.output_parsers import StrOutputParser

session_id = str(uuid.uuid4())
llm = 'cohere.command-r-plus-08-2024'
llm = 'xai.grok-3'
temperature = 0.7
top_p = 0.95
top_k = 50
max_tokens = 100
with_history = True

model = ChatOCIGenAI(
    model_id=llm ,  
    service_endpoint="https://inference.generativeai.us-chicago-1.oci.oraclecloud.com",
    compartment_id="ocid1.compartment.oc1..aaaaaaaa4mlehopmvdluv2wjcdp4tnh2ypjz3nhhpahb4ss7yvxaa3be3diq",
    model_kwargs={"temperature": temperature, "max_tokens": max_tokens, "top_p": top_p, "top_k": top_k},
)

## Initialize the NoSQLDB chat message history
from  NoSQLDBChatMessageHistory import NoSQLDBChatMessageHistory
table_name = "SessionTable"
compartment_id="ocid1.compartment.oc1..aaaaaaaa4mlehopmvdluv2wjcdp4tnh2ypjz3nhhpahb4ss7yvxaa3be3diq"
history = NoSQLDBChatMessageHistory(
    table_name=table_name,
    session_id=session_id,
    compartment_id=compartment_id,
    region="us-ashburn-1",
    ttl=6
)

# Create the chat prompt template
prompt_template = ChatPromptTemplate.from_messages(
    [
        ("system", "You are a helpful assistant."),
        MessagesPlaceholder(variable_name="history"),
        ("human", "{question}"),
    ]
)

# Combine the prompt with the ChatOCIGenAI LLM
chain = prompt_template | model | StrOutputParser()



# Integrate with message history
chain_with_history = RunnableWithMessageHistory(
    chain,
    lambda session_id: history,   
    input_messages_key="question",
    history_messages_key="history",
)

while True:
    prompt = input("Enter something (type 'bye' to stop): ")
    if prompt.lower() == 'bye':
        print("Goodbye!")
        break
    print(f"You entered: {prompt}")
    # Generate assistant response using ChatOCIGenAI LLM and LangChain
    if with_history:
        config = {"configurable": {"session_id": session_id}}
        response = chain_with_history.invoke({"question": prompt}, config=config)
    else:
        response = model.invoke(prompt, temperature=0.7)

    # Display assistant response 
    #if with_history:
    #   print(response)
    #else:
    #   print(response.content)
    print(history._debug)
 
history.close_handle()
 
