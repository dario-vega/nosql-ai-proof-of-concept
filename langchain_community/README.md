# NoSQLDBChatMessageHistory 

Chatbots are expected to understand not only their immediate queries but also the context of their ongoing conversations. 
For developers, the challenge lies in creating a chatbot that can scale seamlessly while maintaining conversation history across multiple sessions. 
Oracle NoSQL Database, OCI Generative AI, and LangChain can provide a powerful combination for building robust, context-aware chatbots.

## Overview

NoSQLDBChatMessageHistory with LangChain for chat history

You can benefit from the following key advantages when using NoSQL with LangChain to manage chat history:

- Enhanced user experience – By using NoSQL for chat history, your chatbot can deliver a consistent and personalized experience. Users can pick up conversations where they left off, and the chatbot can use past interactions to inform its responses.
- Seamless integration – LangChain provides a seamless way to integrate with NoSQL, enabling you to store and retrieve chat messages with minimal overhead. By using LangChain’s NoSQLDBChatMessageHistory class, you can automatically manage chat history as part of the conversation flow, allowing the chatbot to maintain context over time.
- Enhanced scalability – When building chatbots that interact with thousands or even millions of users, managing context becomes a non-trivial problem. The scalability of NoSQL means that your chatbot can store and retrieve conversation history in real time, no matter how many users are interacting with it simultaneously.

## Prerequisites

- Python 3.x
- fastmcp (installed automatically via requirements.txt)
- OCI SDK (installed via requirements.txt)
- Valid OCI configuration file with credentials

## Installation

1. Clone this repository.
2. Install required dependencies using pip:
   ```
   pip install -r requirements.txt
   ```
3. Set up your OCI config file at ~/.oci/config

## OCI Configuration

The server requires a valid OCI config file with proper credentials. 
The default location is ~/.oci/config. For instructions on setting up this file, 
see the [OCI SDK documentation](https://docs.oracle.com/en-us/iaas/Content/API/Concepts/sdkconfig.htm).


## Create a UI with Streamlit

Streamlit is an open-source application framework that enables you to build and deploy web applications with just a few lines of Python code. 
It’s particularly useful for prototyping and testing AI applications, because it allows you to quickly create interactive interfaces without 
requiring extensive frontend development skills.

Let’s explore an example of how you can set up a Streamlit application to interact with our OCI Generative AI powered chatbot. 
It uses NoSQLDBChatMessageHistory with LangChain for chat history


```
streamlit run app.py
```

## Security

The server uses OCI's built-in authentication and authorization mechanisms, including:
- OCI config file-based authentication
- Signer-based authentication for specific endpoints

