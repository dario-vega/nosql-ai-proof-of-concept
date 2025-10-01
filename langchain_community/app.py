import streamlit as st
import time
import uuid
from langchain_oci import ChatOCIGenAI
#from langchain_community.chat_message_histories import NoSQLDBChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.output_parsers import StrOutputParser

## Initialize the session_id in the streamlit session 
if 'session_id' not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
    print ("\n\n\n")
    print ("Welcome to ChatOCIGenAI with NoSQLDBChatMessageHistory")
    print ("======================================================")

# Replicate Credentials
with st.sidebar:
    st.title('🦜🔗 LangChain Oracle NoSQL Bot')

    st.subheader('Models and parameters')
    selected_model = st.sidebar.selectbox('Choose a model', ['Cohere Command', 'xAI.Grok-3'], key='selected_model')
    if selected_model == 'Cohere Command':
        llm = 'cohere.command-r-plus-08-2024'
    elif selected_model == 'xAI.Grok-3':
        llm = 'xai.grok-3'
    else:
        llm = 'cohere.command-r-plus-08-2024'    
    temperature = st.sidebar.slider('temperature', min_value=0.01, max_value=2.0, value=0.7, step=0.1)
    top_p = st.sidebar.slider('top_p', min_value=0.01, max_value=1.0, value=0.95, step=0.01)
    top_k = st.sidebar.slider('top_k', min_value=5, max_value=100, value=50, step=1)
    max_tokens = st.sidebar.slider('max_tokens', min_value=32, max_value=700, value=100, step=10)
    with_history = st.sidebar.toggle('With Memory Context', value=True)
    st.markdown('📖 Learn about this project (https://github.com/dario-vega/nosql-ai-proof-of-concept/')

model = ChatOCIGenAI(
    model_id=llm ,  
    service_endpoint="https://inference.generativeai.us-chicago-1.oci.oraclecloud.com",
    compartment_id="ocid1.compartment.oc1..aaaaaaaa4mlehopmvdluv2wjcdp4tnh2ypjz3nhhpahb4ss7yvxaa3be3diq",
    model_kwargs={"temperature": temperature, "max_tokens": max_tokens, "top_p": top_p, "top_k": top_k},
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
    if with_history:
        config = {"configurable": {"session_id": session_id}}
        response = chain_with_history.invoke({"question": prompt}, config=config)
    else:
        response = model.invoke(prompt, temperature=0.7)

    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        if with_history:
            st.markdown(response)
        else:
            st.markdown(response.content)
    # Add assistant response to chat history
    if with_history:
        st.session_state.messages.append({"role": "assistant", "content": response})
    else: 
        st.session_state.messages.append({"role": "assistant", "content": response.content})
 
    debug_info = history._debug.replace('\n', '<br><li>')
    st.markdown(f"🔍 **🐞 Measurement:**{debug_info}", unsafe_allow_html=True)
    
history.close_handle()
 
