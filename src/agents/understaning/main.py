# Importing Libraries.
import os
import json
import uuid
from typing import List, Dict
from pydantic import BaseModel, Field
# Importing LangChain Libraries.
from langchain_core.prompts import ChatPromptTemplate

from tools.database import create
from tools.llm import open_ai_chat_model

from utils.prompt import get_system_prompt

# Construct the absolute path to the config.json file.
config_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../config/config.json"))
# Load JSON data
with open(config_path, "r") as file:
    config = json.load(file)



class UpdateUnderstanding(BaseModel):
    """Update the current understanding of the user's input"""
    current_understanding: str = Field(description="Updated understanding of the user's input")

class UnderstandingAgent:
    """Agent responsible for updating the current understanding of the user's input"""

    def __init__(self, client_id):
        # Initialize the Agent.
        __agent = config["Agents"]["understanding"]


        # Getting the system prompt.
        __system_prompt = get_system_prompt(agent_name = __agent["Name"], client_id = client_id)

        self.understanding_prompt = ChatPromptTemplate.from_messages([
                                        ("system", __system_prompt),
                                        ("human", "{question}"), 
                                        ("human", "{context}")
                                    ])


        # Getting the LLM Model.
        __llm = __agent["LLM"]
        __model = __agent["LLM Model"]
        __temperature = __agent["Temperature"]

        __llm_chat_model = f"{__llm}_chat_model"
        __llm_model = globals()[__llm_chat_model](model=__model, temperature=__temperature)

        self.chat_model = __llm_model.with_structured_output(UpdateUnderstanding)


        # Defining the understanding agent.
        run_id = str(uuid.uuid4())
        self.__trace(client_id = client_id, run_id = run_id, agent_id = __agent["ID"])
        # Creating the chain.
        self.chain = (self.understanding_prompt | self.chat_model).with_config({"run_id": run_id})


    def update_understanding(self, question, messages: list = None) -> str:
        """Updates the current understanding of the user's input"""
        context = str()

        if messages:
            context += "\n".join([
                f"{'User previous question' if i == 0 else 'Assistant previous output'}: {msg[i]}"
                for msg in messages  # Iterate over all tuples in messages
                for i in range(len(msg))  # Iterate over elements within each tuple
            ])
            context += "\n"

        context += "\n".join([
            f"{'User'}: {question}"
        ])

        return self.chain.invoke(
            input={
                "question": question,
                "context": context
            }
        )


    def __trace(self, client_id: int, run_id: str, agent_id: int):
        """Trace the understanding agent"""

        try:
            # Create a new trace in the database
            insert_query = f'''
                INSERT INTO public.agent_run_history(client_id, run_id, agent_id)
                VALUES ({client_id}, '{run_id}', {agent_id})
            '''

            create(insert_query = insert_query)
        except Exception as exception:
            raise exception