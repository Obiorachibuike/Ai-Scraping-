import os
from pathlib import Path
from typing import List, Dict, Optional
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains.history_aware_retriever import create_history_aware_retriever
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough

class ResearchAgent:
    """Core research agent with Gemini and Google Search"""
    
    def __init__(self, gemini_api_key: str, google_api_key: str, google_cse_id: str):
        # Initialize Gemini
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-pro",
            temperature=0.4,
            google_api_key=gemini_api_key
        )
        self.embeddings = GoogleGenerativeAIEmbeddings(
            model="models/embedding-001",
            google_api_key=gemini_api_key
        )
        
        # Initialize Google Search
        from research_agent.web_search import GoogleSearch
        self.search = GoogleSearch(google_api_key, google_cse_id)
        
        # Knowledge base setup
        self.vectorstore = None
        self.retriever = None
        self.session_history = []
        self._initialize_knowledge_base()
    
    def _initialize_knowledge_base(self):
        """Load or initialize vector knowledge base"""
        kb_path = Path("knowledge_base/gemini_index")
        if kb_path.exists():
            self.vectorstore = FAISS.load_local(
                str(kb_path), self.embeddings, allow_dangerous_deserialization=True
            )
            self.retriever = self.vectorstore.as_retriever()
    
    def add_sources(self, urls: List[str]):
        """Add web sources to knowledge base"""
        from langchain_community.document_loaders import WebBaseLoader
        from langchain_text_splitters import RecursiveCharacterTextSplitter
        
        loader = WebBaseLoader(urls)
        docs = loader.load()
        
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1500,
            chunk_overlap=300
        )
        splits = text_splitter.split_documents(docs)
        
        if self.vectorstore is None:
            self.vectorstore = FAISS.from_documents(splits, self.embeddings)
        else:
            self.vectorstore.add_documents(splits)
        
        self.retriever = self.vectorstore.as_retriever()
    
    def research(self, query: str) -> Dict[str, str]:
        """Perform research including web search and analysis"""
        # First perform Google search
        search_results = self.search.search(query)
        urls = [r.link for r in search_results]
        self.add_sources(urls)
        
        # Then get research response from LLM
        if not self.retriever:
            return {
                "response": self.llm.invoke(query).content,
                "sources": search_results
            }
        
        retriever_chain = create_history_aware_retriever(
            self.llm, self.retriever, self._create_retriever_prompt()
        )
        document_chain = create_stuff_documents_chain(self.llm, self._create_research_prompt())
        
        retrieval_chain = (
            RunnablePassthrough.assign(
                context=lambda x: retriever_chain.invoke({
                    "input": x["input"],
                    "chat_history": x["chat_history"]
                })
            )
            | document_chain
        )
        
        response = retrieval_chain.invoke({
            "input": query,
            "chat_history": self.session_history
        })
        
        self.session_history.append((query, response))
        return {
            "response": response,
            "sources": search_results
        }
    
    def _create_retriever_prompt(self):
        return ChatPromptTemplate.from_messages([
            ("system", "Rephrase this question considering conversation history:"),
            ("user", "{input}")
        ])
    
    def _create_research_prompt(self):
        return ChatPromptTemplate.from_messages([
            ("system", """Analyze this research context and answer thoroughly:
            
            Context: {context}
            
            - Highlight key insights
            - Identify any contradictions
            - Suggest follow-up questions
            - Cite sources when possible"""),
            ("user", "{input}")
        ])
