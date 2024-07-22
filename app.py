from langchain_community.llms import OpenAI
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os
from langchain.schema import(
    HumanMessage,
    SystemMessage
)

load_dotenv()

llm = ChatOpenAI(openai_api_key = os.getenv("OPENAI_API_KEY"), temperature=0.9,model_name="gpt-3.5-turbo",max_tokens=150)

response = llm([HumanMessage(content="Qual é o melhor rpg do super nintendo, segundo o metacritic?")])

print(response)