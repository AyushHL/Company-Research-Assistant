import streamlit as st
import os
import warnings
from dotenv import load_dotenv

load_dotenv()

# Suppress the DuckDuckGo search warning
warnings.filterwarnings("ignore", category=RuntimeWarning, module="langchain_community.utilities.duckduckgo_search")
warnings.filterwarnings("ignore", category=RuntimeWarning, module="duckduckgo_search")

from langchain_core.messages import HumanMessage, AIMessage
from agent_graph import create_agent_graph

st.set_page_config(page_title="Company Research Assistant", layout="wide")

st.title("Company Research Assistant 🕵️‍♂️")
st.markdown("I help you research companies and generate account plans.")

# Sidebar for configuration
with st.sidebar:
    st.header("Configuration")
    # Pre-fill the API key and make it visible
    default_key = os.environ.get("GOOGLE_API_KEY", "")
    api_key = st.text_input("Google API Key", value=default_key)
    if api_key:
        os.environ["GOOGLE_API_KEY"] = api_key
    
    st.divider()
    st.markdown("### Features")
    st.markdown("- Research Companies")
    st.markdown("- Generate Account Plans")
    st.markdown("- Update Sections")

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

if "account_plan" not in st.session_state:
    st.session_state.account_plan = ""

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Enter company name or instruction..."):
    if not os.environ.get("GOOGLE_API_KEY"):
        st.error("Please enter your Google API Key in the sidebar.")
        st.stop()

    # Add user message to state
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Run the agent
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        
        # Prepare inputs for the graph
        # Convert session messages to LangChain format
        langchain_messages = []
        for msg in st.session_state.messages:
            if msg["role"] == "user":
                langchain_messages.append(HumanMessage(content=msg["content"]))
            elif msg["role"] == "assistant":
                langchain_messages.append(AIMessage(content=msg["content"]))
        
        inputs = {"messages": langchain_messages}
        
        # Stream the response
        try:
            # We use invoke instead of stream for simplicity with the graph state, but for better UX we could stream. 
            agent_app = create_agent_graph()
            result = agent_app.invoke(inputs)
            
            last_message = result["messages"][-1]
            full_response = last_message.content
            
            message_placeholder.markdown(full_response)
            
            # Check if there is an account plan in the response (heuristic)
            
        except Exception as e:
            st.error(f"An error occurred: {e}")
            full_response = "I encountered an error. Please check your API key and try again."

    # Add assistant response to state
    st.session_state.messages.append({"role": "assistant", "content": full_response})
