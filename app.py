import os
import streamlit as st
from hindsight_client import Hindsight
from groq import Groq

st.set_page_config(page_title="Memory-Powered Code Reviewer", layout="wide")
st.title("🤖 Memory-Powered AI Code Review Agent")
st.caption("Powered by Hindsight Memory & Groq LLM")

HINDSIGHT_KEY = os.environ.get("HINDSIGHT_API_KEY") or st.sidebar.text_input("Hindsight API Key", type="password")
GROQ_KEY = os.environ.get("GROQ_API_KEY") or st.sidebar.text_input("Groq API Key", type="password")

BANK_ID = "team-code-review-rules"

if HINDSIGHT_KEY and GROQ_KEY:
    # Set a timeout so requests don't hang indefinitely
    hindsight = Hindsight(
        base_url="https://api.hindsight.vectorize.io", 
        api_key=HINDSIGHT_KEY,
        timeout=30.0  # 30 seconds timeout
    )
    groq_client = Groq(api_key=GROQ_KEY)

    col1, col2 = st.columns(2)

    # Column 1: Teach Team Standards
    with col1:
        st.subheader("1. Teach Team Standards (Memory)")
        new_rule = st.text_area("Add a new coding standard / team rule:", placeholder="e.g., Never use print() in production. Always use logging.info().")
        
        # Guarded inside button click
        if st.button("Save Rule to Hindsight Memory"):
            if new_rule:
                with st.spinner("Saving to Hindsight Cloud..."):
                    try:
                        hindsight.retain(
                            bank_id=BANK_ID, 
                            content=new_rule, 
                            context="team_coding_standards"
                        )
                        st.success("Successfully saved rule to Hindsight memory bank!")
                    except Exception as e:
                        st.error(f"Hindsight connection error: {e}")
            else:
                st.warning("Please enter a rule first.")

    # Column 2: Review Code
    with col2:
        st.subheader("2. Review Code Diff")
        code_diff = st.text_area("Paste Code Diff / PR Snippet:", height=200, value="def process():\n    print('Starting process')")
        
        # Guarded inside button click
        if st.button("Run Code Review"):
            if code_diff:
                with st.spinner("Recalling memory & analyzing code..."):
                    try:
                        # 1. Recall memory from Hindsight
                        recalled_memories = hindsight.recall(
                            bank_id=BANK_ID, 
                            query="What are our team rules and coding guidelines?"
                        )
                        
                        # 2. Build LLM Prompt
                        prompt = f"""
                        You are an expert AI Code Review Agent.
                        
                        RECALLED TEAM MEMORY & RULES:
                        {recalled_memories}
                        
                        CODE TO REVIEW:
                        {code_diff}
                        
                        Please review the code according to our team's recalled rules.
                        """
                        
                        # 3. Call Groq
                        response = groq_client.chat.completions.create(
                            model="qwen/qwen3.8-27b",
                            messages=[{"role": "user", "content": prompt}],
                        )
                        
                        st.subheader("Agent Feedback:")
                        st.markdown(response.choices[0].message.content)
                    except Exception as e:
                        st.error(f"Error during code review: {e}")

else:
    st.warning("Please provide both API keys in the sidebar or `.env` file to start.")