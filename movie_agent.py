import os
import streamlit as st
from dotenv import load_dotenv
from langchain.memory import ConversationBufferMemory
from langchain.agents import initialize_agent, AgentType
from langchain_openai import ChatOpenAI
from tools import tools

# --- Load environment variables ---
load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
TMDB_API_KEY = os.getenv("TMDB_API_KEY")

if not OPENROUTER_API_KEY:
    st.error("OPENROUTER_API_KEY must be set in .env")
    st.stop()
if not TMDB_API_KEY:
    st.error("TMDB_API_KEY must be set in .env")
    st.stop()

os.environ["OPENAI_API_KEY"] = OPENROUTER_API_KEY
os.environ["OPENAI_BASE_URL"] = "https://openrouter.ai/api/v1"

# --- LLM setup ---
llm = ChatOpenAI(
    model="deepseek/deepseek-chat",
    temperature=0.6
)

# --- Initialize memory in session state ---
if "memory" not in st.session_state:
    st.session_state.memory = ConversationBufferMemory(
        memory_key="chat_history",
        return_messages=True
    )

# --- Initialize agent in session state ---
if "agent" not in st.session_state:
    st.session_state.agent = initialize_agent(
        tools,
        llm,
        agent=AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION,
        memory=st.session_state.memory,
        verbose=False,
        handle_parsing_errors=True,
        max_iterations=2
    )

# --- Streamlit UI ---
st.title("🎬 Movie Finder Agent")
st.write("Ask me for movie recommendations based on your mood, genre, or actor!")

user_input = st.chat_input("Type your request here...")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if user_input:
    with st.chat_message("user"):
        st.write(user_input)

    try:
        response = st.session_state.agent.invoke({"input": user_input})["output"]

        # Clean up duplicates
        lines = response.strip().split("\n")
        unique_lines = []
        seen = set()
        for line in lines:
            clean_line = line.strip()
            if clean_line and clean_line not in seen:
                unique_lines.append(line)
                seen.add(clean_line)

        cleaned_response = "\n".join(unique_lines)
        
        st.session_state.chat_history.append(("You", user_input))
        st.session_state.chat_history.append(("Assistant", cleaned_response))

        with st.chat_message("assistant"):
            st.write(cleaned_response)

    except Exception as e:
        st.error(f"❌ Error: {e}")
