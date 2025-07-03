import streamlit as st
from datetime import datetime
import requests

# API configuration (now always points to the local Flask server)
API_URL = "http://localhost:5000"

def initialize_session():
    if 'history' not in st.session_state:
        st.session_state.history = []
    if 'initialized' not in st.session_state:
        st.session_state.initialized = False

def setup_sidebar():
    with st.sidebar:
        st.title("🔍 Research Agent Settings")
        
        gemini_key = st.text_input("Gemini API Key", type="password")
        google_key = st.text_input("Google API Key", type="password")
        google_cse = st.text_input("Google CSE ID", type="password")
        
        if st.button("Initialize Agent"):
            try:
                response = requests.post(
                    f"{API_URL}/initialize",
                    json={
                        "gemini_api_key": gemini_key,
                        "google_api_key": google_key,
                        "google_cse_id": google_cse
                    }
                )
                if response.status_code == 200:
                    st.session_state.initialized = True
                    st.success("Agent initialized!")
                else:
                    st.error(f"Initialization failed: {response.json().get('error', 'Unknown error')}")
            except requests.exceptions.ConnectionError:
                st.error("Could not connect to the research agent backend. Is it running?")
            except Exception as e:
                st.error(f"Error: {str(e)}")

def display_chat():
    st.title("🧠 Research Agent Chat")
    
    for msg in st.session_state.history:
        role = "user" if msg['type'] == 'query' else 'assistant'
        with st.chat_message(role):
            st.markdown(msg['content'])
            if role == 'assistant' and msg.get('sources'):
                with st.expander("📚 Sources"):
                    for src in msg['sources']:
                        st.markdown(f"[{src['title']}]({src['link']})")
    
    if prompt := st.chat_input("Enter your research question..."):
        if not st.session_state.initialized:
            st.error("Please initialize the agent first")
            return
        
        st.session_state.history.append({
            "type": "query",
            "content": prompt,
            "time": str(datetime.now())
        })
        
        with st.chat_message("user"):
            st.markdown(prompt)
        
        with st.chat_message("assistant"):
            with st.spinner("Researching..."):
                try:
                    response = requests.post(
                        f"{API_URL}/research",
                        json={"query": prompt}
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        st.markdown(data['response'])
                        
                        st.session_state.history.append({
                            "type": "response",
                            "content": data['response'],
                            "sources": [{'title': r['title'], 'link': r['link']} for r in data['sources']],
                            "time": str(datetime.now())
                        })
                    else:
                        st.error(f"Research failed: {response.json().get('error', 'Unknown error')}")
                except requests.exceptions.ConnectionError:
                    st.error("Backend service unavailable. Please try again.")
                except Exception as e:
                    st.error(f"Error: {str(e)}")

def main():
    st.set_page_config(
        page_title="Research Agent Chat", 
        page_icon="🔍",
        layout="wide"
    )
    initialize_session()
    setup_sidebar()
    display_chat()

if __name__ == '__main__':
    main()
