import streamlit as st
from groq import Groq
from langchain_groq import ChatGroq
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import (
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
    AIMessagePromptTemplate,
    ChatPromptTemplate
)
from prompt_template import SYSTEM_PROMPT_TEMPLATE
from dotenv import load_dotenv
import os
from duckduckgo_search import DDGS

load_dotenv()

GROQ_API = os.getenv("GROQ_API")

st.title("🌍 Sofia - Your AI Travel Planner")
st.caption("✈️ Personalized Travel Itineraries, Activity Suggestions, and Expert Guidance")

# Sidebar configuration
with st.sidebar:
    st.header("⚙️ Configuration")
    selected_model = st.selectbox(
        "Choose Model",
        ["gemma2-9b-it", "llama-3.3-70b-versatile","llama3-70b-8192","mixtral-8x7b-32768"],
        index=0
    )
    st.divider()
    st.markdown("### Model Capabilities")
    st.markdown("""
    ### ✈️ **AI Travel Planner**
    ---

    **Capabilities:**  
    - 🔍 **Input Refinement:** Gathers essential details — budget, duration, destination, preferences, and more.  
    - 🏖️ **Personalized Suggestions:** Curates top attractions, hidden gems, and activity ideas using web search tools.  
    - 🗓 **Day-by-Day Itinerary:** Generates coherent, practical travel plans tailored to user preferences.  
    - 🤝 **Conversational Flow:** Asks follow-up questions to clarify missing or vague details.  
    - 🏨 **Accommodation & Dining:** Recommends stays and food options aligned with user needs.  
    - ♿ **Accessibility:** Considers mobility concerns and accessibility requirements.  
    - 🔄 **Flexible & Engaging:** Offers optional activities and alternative plans.  

    ---
    """)
    st.divider()
    st.markdown("Built with [Groq](https://groq.com/) | [LangChain](https://python.langchain.com/)")

# Initialize the Groq client
groq_client = ChatGroq(
    groq_api_key=GROQ_API,
    model_name=selected_model,
    temperature=0.3
)

# System prompt configuration
system_prompt = SystemMessagePromptTemplate.from_template(
    SYSTEM_PROMPT_TEMPLATE
)

# Web search function
def perform_web_search(query, max_results=5):
    try:
        results = DDGS().text("python programming", max_results=max_results)
        if results:
            summarized_results = "\n".join(
                [f"- {res['title']}: {res['href']}" for res in results]
            )
            return summarized_results
        else:
            return "No relevant results found."
    except Exception as e:
        return f"Error during web search: {e}"

# Session state management
if "message_log" not in st.session_state:
    st.session_state.message_log = []

# Chat container
chat_container = st.container()

# Display chat messages
with chat_container:
    for message in st.session_state.message_log:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# Chat input and processing
user_query = st.chat_input("Ask your travel planning question here...")

# AI response generation
def generate_ai_response(prompt_chain):
    processing_pipeline = prompt_chain | groq_client | StrOutputParser()
    return processing_pipeline.invoke({})

# Build prompt chain with optional search context
def build_prompt_chain(search_results=None):
    prompt_sequence = [system_prompt]
    for msg in st.session_state.message_log:
        if msg["role"] == "user":
            prompt_sequence.append(HumanMessagePromptTemplate.from_template(msg["content"]))
        elif msg["role"] == "ai":
            prompt_sequence.append(AIMessagePromptTemplate.from_template(msg["content"]))
    if search_results:
        search_context = f"""
        Here are some recent web search findings related to the user's query:
        {search_results}

        Please analyze this information to find key insights, recommendations, or hidden gems that are relevant to the user's preferences.
        """
        prompt_sequence.append(SystemMessagePromptTemplate.from_template(search_context))
    return ChatPromptTemplate.from_messages(prompt_sequence)

# Main logic
if user_query:
    st.session_state.message_log.append({"role": "user", "content": user_query})

    search_results = None
    if any(keyword in user_query.lower() for keyword in ["attractions", "places to visit", "restaurants", "things to do"]):
        with st.spinner("🔍 Searching the web for relevant information..."):
            search_results = perform_web_search(user_query)

    with st.spinner("🤔 Generating response..."):
        prompt_chain = build_prompt_chain(search_results)
        ai_response = generate_ai_response(prompt_chain)

    st.session_state.message_log.append({"role": "ai", "content": ai_response})
    st.rerun()


