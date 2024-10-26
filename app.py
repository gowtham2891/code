import os
import streamlit as st
from langchain_groq import ChatGroq
from langchain.prompts import ChatPromptTemplate
from langchain.chains import LLMChain
from datetime import datetime
import time
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()
GROQ_API_KEY = os.getenv('GROQ_API_KEY')

# Page configuration
st.set_page_config(
    page_title="✨ Code Wizard",
    page_icon="🪄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Enhanced CSS with modern styling
st.markdown("""
<style>
    /* Modern styling */
    .stApp {
        background-color: #f8fafc;
    }

    .welcome-container {
        text-align: center;
        padding: 2rem;
        background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
        border-radius: 1rem;
        margin-bottom: 2rem;
        animation: fadeIn 0.8s ease-out;
    }

    .welcome-title {
        font-size: 2.5rem;
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 1rem;
    }

    .stats-card {
        background: white;
        border-radius: 1rem;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        transition: transform 0.3s ease;
    }

    .stats-card:hover {
        transform: translateY(-5px);
    }

    .stat-item {
        display: inline-block;
        margin: 0 1rem;
        text-align: center;
    }

    /* Animations */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }

    /* Code area styling */
    .stTextArea textarea {
        font-family: 'Courier New', Courier, monospace;
        border-radius: 0.5rem;
        border: 1px solid #e2e8f0;
        padding: 1rem;
        font-size: 0.9rem;
        background-color: #f8fafc;
    }

    .stTextArea textarea:focus {
        border-color: #6366f1;
        box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.2);
    }

    /* Button styling */
    .stButton button {
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
        color: white;
        border: none;
        padding: 0.5rem 2rem;
        border-radius: 0.5rem;
        font-weight: bold;
        transition: all 0.3s ease;
    }

    .stButton button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 6px -1px rgba(99, 102, 241, 0.4);
    }

    /* Additional styling for chat interface */
    .chat-message {
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        animation: fadeIn 0.5s ease-out;
    }

    .user-message {
        background-color: #e0f2fe;
        margin-left: 2rem;
    }

    .assistant-message {
        background-color: #f0fdf4;
        margin-right: 2rem;
    }
</style>
""", unsafe_allow_html=True)

def init_session_state():
    """Initialize all session state variables"""
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    if 'code_submitted' not in st.session_state:
        st.session_state.code_submitted = False
    if 'current_code' not in st.session_state:
        st.session_state.current_code = ""
    if 'conversation_history' not in st.session_state:
        st.session_state.conversation_history = []
    if 'is_code_context' not in st.session_state:
        st.session_state.is_code_context = True
    if 'user_name' not in st.session_state:
        st.session_state.user_name = None
    if 'session_start' not in st.session_state:
        st.session_state.session_start = datetime.now()
    if 'questions_asked' not in st.session_state:
        st.session_state.questions_asked = 0
    if 'code_analyses' not in st.session_state:
        st.session_state.code_analyses = 0

def show_welcome_screen():
    """Display the welcome screen and handle user name input."""
    st.markdown("""
        <div class="welcome-container">
            <h1 class="welcome-title">🪄 Welcome to Code Wizard</h1>
            <p style="font-size: 1.2rem; color: #4b5563;">Your magical companion for code analysis and improvement</p>
        </div>
    """, unsafe_allow_html=True)
    
    with st.form("welcome_form"):
        name = st.text_input(
            "What's your name, fellow wizard? 🧙‍♂️",
            placeholder="Enter your name to begin...",
            label_visibility="visible"
        )
        submitted = st.form_submit_button("✨ Begin Your Coding Journey", use_container_width=True)
        
        if submitted and len(name.strip()) >= 2:
            st.session_state.user_name = name
            st.success(f"Welcome aboard, {name}! 🌟")
            time.sleep(1)
            st.rerun()
        elif submitted:
            st.warning("🪄 Please enter a valid name (at least 2 characters)")

def show_user_stats():
    """Display user session statistics."""
    session_duration = datetime.now() - st.session_state.session_start
    duration_mins = int(session_duration.total_seconds() / 60)
    
    st.markdown("""
        <div class="stats-card">
            <div class="stat-item">
                <h3>⏱️ Session Duration</h3>
                <p>{}</p>
            </div>
            <div class="stat-item">
                <h3>❓ Questions Asked</h3>
                <p>{}</p>
            </div>
            <div class="stat-item">
                <h3>🔍 Code Analyses</h3>
                <p>{}</p>
            </div>
        </div>
    """.format(duration_mins, st.session_state.questions_asked, st.session_state.code_analyses), 
    unsafe_allow_html=True)

def get_llm_response(prompt_template: str, **kwargs) -> str:
    """Get response from LLM using the new LangChain syntax"""
    if not GROQ_API_KEY:
        st.error("⚠️ GROQ_API_KEY not found. Please set it in your environment variables.")
        st.stop()
    
    try:
        llm = ChatGroq(
            groq_api_key=GROQ_API_KEY,
            model_name="mixtral-8x7b-32768",
            temperature=0.7
        )
        
        prompt = ChatPromptTemplate.from_template(prompt_template)
        chain = prompt | llm  # New syntax replacing LLMChain
        
        response = chain.invoke(kwargs)
        return response.content
    except Exception as e:
        st.error(f"Error in LLM processing: {str(e)}")
        return None

def analyze_code(code: str, query: str = None, is_initial_analysis: bool = True) -> str:
    """Analyze code using the Groq LLM."""
    if is_initial_analysis:
        prompt_template = """
        As a coding expert, analyze this code:
        
        ```
        {code}
        ```
        
        Provide a detailed yet engaging analysis including:
        1. 🎯 Overview of what the code does
        2. 🔍 Key components and their functionality
        3. 💡 Notable programming concepts used
        4. ⚡ Performance considerations
        5. 🛡️ Security considerations if applicable
        6. ✨ Potential improvements and best practices
        
        Make your explanation clear, engaging, and actionable, using emojis and formatting to enhance readability.
        """
        return get_llm_response(prompt_template, code=code)
    else:
        context = "\n".join([f"{msg['role']}: {msg['content']}" 
                           for msg in st.session_state.conversation_history[-3:]])
        
        prompt_template = """
        Question about the code:
        ```
        {code}
        ```
        
        Question: {query}
        
        Previous context:
        {context}
        
        Provide a focused, clear answer with relevant code references and examples where applicable.
        Use emojis and formatting to make the explanation more engaging.
        """
        return get_llm_response(prompt_template, code=code, query=query, context=context)

def render_code_analysis_section():
    """Render the code analysis section of the app"""
    st.markdown("### 📝 Let's analyze your code!")
    code_input = st.text_area(
        "Enter your code",
        height=300,
        placeholder="Paste your code here and let's make it better together! 🚀",
        label_visibility="collapsed"
    )
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🔍 Analyze Code", type="primary", use_container_width=True) and code_input.strip():
            st.session_state.current_code = code_input
            with st.spinner("🤖 Analyzing your code..."):
                explanation = analyze_code(code_input, is_initial_analysis=True)
                if explanation:
                    st.session_state.code_submitted = True
                    st.session_state.messages.extend([
                        {"role": "user", "content": "Please analyze this code."},
                        {"role": "assistant", "content": explanation}
                    ])
                    st.session_state.conversation_history.extend(st.session_state.messages[-2:])
                    st.session_state.code_analyses += 1
                    st.rerun()

def render_chat_interface():
    """Render the chat interface section"""
    with st.expander("📄 View Current Code", expanded=False):
        st.code(st.session_state.current_code, language="python")
        if st.button("📝 Submit New Code"):
            st.session_state.code_submitted = False
            st.rerun()
    
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    if prompt := st.chat_input("💭 Ask me anything about the code..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.session_state.questions_asked += 1
        
        with st.spinner("🤔 Thinking..."):
            response = analyze_code(
                st.session_state.current_code, 
                prompt, 
                is_initial_analysis=False
            ) if st.session_state.is_code_context else get_llm_response(
                "Answer this programming question:\nQuestion: {query}\n\n"
                "Provide a clear, comprehensive answer with examples where applicable.\n"
                "Use emojis and formatting to make the explanation engaging.",
                query=prompt
            )
            
            if response:
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": response
                })
                st.session_state.conversation_history.append({
                    "role": "assistant",
                    "content": response
                })
                st.rerun()

def render_sidebar():
    """Render the sidebar section"""
    with st.sidebar:
        st.markdown("### ⚙️ Settings")
        st.session_state.is_code_context = st.toggle(
            "Code-specific questions",
            value=st.session_state.is_code_context,
            help="Toggle between code-specific and general programming questions"
        )
        
        if st.button("🗑️ Clear Chat") and st.session_state.messages:
            st.session_state.messages = []
            st.session_state.code_submitted = False
            st.session_state.current_code = ""
            st.session_state.conversation_history = []
            st.success("✨ Chat cleared!")
            st.rerun()

def main():
    """Main application logic."""
    init_session_state()
    
    if not st.session_state.user_name:
        show_welcome_screen()
        return
    
    st.markdown(f"""
        <div style="text-align: center; margin-bottom: 2rem;">
            <h1 class="welcome-title">Hello, {st.session_state.user_name}! 🌟</h1>
            <p style="font-size: 1.2rem; color: #4b5563;">Ready to make some coding magic? ✨</p>
        </div>
    """, unsafe_allow_html=True)
    
    show_user_stats()
    
    if not st.session_state.code_submitted:
        render_code_analysis_section()
    else:
        render_chat_interface()
    
    render_sidebar()

if __name__ == "__main__":
    main()
