import os
import openai
import streamlit
from dotenv import find_dotenv, load_dotenv
from langchain.agents import AgentExecutor, ZeroShotAgent
from langchain.chains import LLMChain

from prompts import PREFIX, SUFFIX
from tools import get_tools

_ = load_dotenv(find_dotenv())  # read local .env file
openai.api_key = os.environ["OPENAI_API_KEY"]



def get_agent():
    """
    The get_agent function is a helper function that creates an AgentExecutor object.
    
    :return: The agent_chain
    :doc-author: Yusuf
    """
    agent_prompt = ZeroShotAgent.create_prompt(
        tools=get_tools(),
        prefix=PREFIX,
        suffix=SUFFIX,
        input_variables=["input", "chat_history", "agent_scratchpad"],
    )
    llm_chain = LLMChain(llm=streamlit.session_state["llm"], prompt=agent_prompt)
    agent = ZeroShotAgent(llm_chain=llm_chain, tools=get_tools())
    agent_chain = AgentExecutor.from_agent_and_tools(
        agent=agent,
        tools=get_tools(),
        memory=streamlit.session_state["memory"],
        verbose=True,
    )
    return agent_chain
