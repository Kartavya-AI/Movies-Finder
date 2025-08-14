import asyncio
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.schema import SystemMessage
from mcp_use import MCPAgent, MCPClient
from langsmith import traceable
import streamlit as st

async def main():
    # Load environment variables
    load_dotenv()
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    os.environ['LANGSMITH_API_KEY'] = os.getenv('LANGSMITH_API_KEY')
    os.environ['LANGSMITH_TRACING'] = 'true'
    os.environ['LANGCHAIN_TRACING_V2'] = 'true'
    os.environ['LANGCHAIN_ENDPOINT'] = 'https://api.smith.langchain.com'
    os.environ['LANGCHAIN_PROJECT'] = 'movies-finder'
    os.environ['LANGUAGE'] = 'en-US'

    config_file = "browser_mcp.json"

    print("Initializing chat...")
    
    # Create MCPClient from configuration dictionary
    if "client" not in st.session_state:
        st.session_state.client = MCPClient.from_config_file(config_file)
    if "llm" not in st.session_state:
        st.session_state.llm = ChatOpenAI(model="gpt-3.5-turbo",base_url="https://openrouter.ai/api/v1",max_tokens=200,temperature=0.7)
    if "agent" not in st.session_state:
        st.session_state.agent = MCPAgent(llm=st.session_state.llm, client=st.session_state.client, max_steps=5, memory_enabled=True)
        st.session_state.agent.set_system_message(
            "You are an assistant. Always respond strictly in English. "
            "If you receive or retrieve any content in another language, "
            "translate it to English before replying."
        )

    if "history" not in st.session_state:
        st.session_state.history = []
    if "input" not in st.session_state:
        st.session_state.input = ""

    @traceable(project_name="movies-finder")
    async def run_agent(user_input):
        return await st.session_state.agent.run(user_input)

    @traceable(project_name="movies-finder")
    def send_message():
        user_input = st.session_state.input.strip()
        if not user_input:
            return
        st.session_state.history.append(("user", user_input))
        with st.spinner("Assistant is typing..."):
            try:
                assistant_response = asyncio.run(run_agent(user_input))
            except Exception as e:
                assistant_response = f"Error: {str(e)}"
        st.session_state.history.append(("assistant", assistant_response))
        st.session_state.input = ""
    st.title("Interactive MCP Agent chat")

    for role,message in st.session_state.history:
        if role == "user":
            st.markdown(f"**You:** {message}")
        else:
            st.markdown(f"**Assistant:** {message}")

    
    st.text_input("Enter your message:",key="input",on_change=send_message)

    if st.button("Clear history"):
        if "client" in st.session_state and st.session_state.client.sessions:
            asyncio.run(st.session_state.client.close_all_sessions())
        st.session_state.history.clear()

if __name__ == "__main__":
    asyncio.run(main())
