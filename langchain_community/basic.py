from langchain_oci import ChatOCIGenAI
import streamlit as st
import time

model = ChatOCIGenAI(
    model_id="cohere.command-r-plus-08-2024",
    service_endpoint="https://inference.generativeai.us-chicago-1.oci.oraclecloud.com",
    compartment_id="ocid1.compartment.oc1..aaaaaaaa4mlehopmvdluv2wjcdp4tnh2ypjz3nhhpahb4ss7yvxaa3be3diq",
    model_kwargs={"temperature": 0},
)

st.title('🦜🔗 LangChain with ChatOCIGenAI')

st.session_state.messages = []


# React to user input
if prompt := st.chat_input("What is up?"):
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
   
    # Generate assistant response using Bedrock LLM and LangChain
    response = model.invoke(prompt, temperature=0.7)

    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        st.markdown(response.content)
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response.content})
