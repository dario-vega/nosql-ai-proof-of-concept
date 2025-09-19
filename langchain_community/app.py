import streamlit as st
import time
import uuid
from langchain_oci import ChatOCIGenAI
#from langchain_community.chat_message_histories import NoSQLDBChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.output_parsers import StrOutputParser

st.title('🦜🔗 LangChain Oracle NoSQL Bot')
## Initialize the session_id in the streamlit session 
if 'session_id' not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
    print ("\n\n\n")
    print ("Welcome to ChatOCIGenAI with NoSQLDBChatMessageHistory")
    print ("======================================================")
    
model = ChatOCIGenAI(
    model_id="cohere.command-r-plus-08-2024", # "xai.grok-3" ,  
    service_endpoint="https://inference.generativeai.us-chicago-1.oci.oraclecloud.com",
    compartment_id="ocid1.compartment.oc1..aaaaaaaa4mlehopmvdluv2wjcdp4tnh2ypjz3nhhpahb4ss7yvxaa3be3diq",
    model_kwargs={"temperature": 0, "max_tokens": 100},
)


## Initialize the NoSQLDB chat message history
from  NoSQLDBChatMessageHistory import NoSQLDBChatMessageHistory
table_name = "SessionTable"
session_id = st.session_state.session_id
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


# Load messages from NoSQLDB and populate chat history
if "messages" not in st.session_state:
    st.session_state.messages = []
   
    # Load the stored messages from NoSQLDB
    stored_messages = history.messages 
   
    # Populate the session state with the retrieved messages
    for msg in stored_messages:
        role = "user" if msg.__class__.__name__ == "HumanMessage" else "assistant"
        st.session_state.messages.append({"role": role, "content": msg.content})

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# React to user input
if prompt := st.chat_input("What is up?"):
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
   
    # Generate assistant response using ChatOCIGenAI LLM and LangChain
    config = {"configurable": {"session_id": session_id}}
    response = chain_with_history.invoke({"question": prompt}, config=config)
    #response = model.invoke(prompt, temperature=0.7)

    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        st.markdown(response)
        #st.markdown(response.content)
    # Add assistant response to chat history
    #st.session_state.messages.append({"role": "assistant", "content": response.content})
    st.session_state.messages.append({"role": "assistant", "content": response})
     
