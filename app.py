import streamlit as st
from openai import OpenAI
from mem0 import Memory
import os
import json
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Set up the Streamlit App
st.title("AI Customer Support Agent with Memory 🛒")
st.caption("Chat with a customer support assistant who remembers your past interactions.")

# Set the OpenAI API key manually
openai_api_key = st.text_input("Enter OpenAI API Key", type="password")

if openai_api_key:
    os.environ['OPENAI_API_KEY'] = openai_api_key

    class CustomerSupportAIAgent:
        def __init__(self):
            # Configure Qdrant Cloud
            config = {
                "vector_store": {
                    "provider": "qdrant",
                    "config": {
                        "url": "https://972793ba-2973-4b5f-927f-216570f6e487.us-east-1-0.aws.cloud.qdrant.io",
                        "api_key": os.getenv("QDRANT_API_KEY")                    }
                }
            }

            try:
                self.memory = Memory.from_config(config)
            except Exception as e:
                st.error(f"Failed to initialize memory: {e}")
                st.stop()

            self.client = OpenAI(
                api_key=os.getenv("OPENAI_API_KEY"),
                base_url="https://openrouter.ai/api/v1"
            )
            self.app_id = "customer-support"

        def handle_query(self, query, user_id=None):
            try:
                relevant_memories = self.memory.search(query=query, user_id=user_id)
                context = "Relevant past information:\n"
                if relevant_memories and "results" in relevant_memories:
                    for memory in relevant_memories["results"]:
                        if "memory" in memory:
                            context += f"- {memory['memory']}\n"

                full_prompt = f"{context}\nCustomer: {query}\nSupport Agent:"
                response = self.client.chat.completions.create(
                    model="openrouter/openai/gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are a customer support AI agent for TechGadgets.com, an online electronics store."},
                        {"role": "user", "content": full_prompt}
                    ],
                    max_tokens=500
                )
                answer = response.choices[0].message.content

                self.memory.add(query, user_id=user_id, metadata={"app_id": self.app_id, "role": "user"})
                self.memory.add(answer, user_id=user_id, metadata={"app_id": self.app_id, "role": "assistant"})

                return answer
            except Exception as e:
                st.error(f"An error occurred while handling the query: {e}")
                return "Sorry, I encountered an error. Please try again later."

        def get_memories(self, user_id=None):
            try:
                return self.memory.get_all(user_id=user_id)
            except Exception as e:
                st.error(f"Failed to retrieve memories: {e}")
                return None

        def generate_synthetic_data(self, user_id: str) -> dict | None:
            try:
                today = datetime.now()
                order_date = (today - timedelta(days=10)).strftime("%B %d, %Y")
                expected_delivery = (today + timedelta(days=2)).strftime("%B %d, %Y")

                prompt = f"""Generate a short customer profile for TechGadgets.com with:
1. Name
2. One recent order with product & price
3. One previous order
4. One customer support interaction

Return only the JSON."""


                response = self.client.chat.completions.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": "You are a data generation AI that creates realistic customer profiles and order histories. Always respond with valid JSON."},
                        {"role": "user", "content": prompt}
                    ]
                )

                customer_data = json.loads(response.choices[0].message.content)

                for key, value in customer_data.items():
                    if isinstance(value, list):
                        for item in value:
                            self.memory.add(json.dumps(item), user_id=user_id, metadata={"app_id": self.app_id, "role": "system"})
                    else:
                        self.memory.add(f"{key}: {json.dumps(value)}", user_id=user_id, metadata={"app_id": self.app_id, "role": "system"})

                return customer_data
            except Exception as e:
                st.error(f"Failed to generate synthetic data: {e}")
                return None

    # Initialize the CustomerSupportAIAgent
    support_agent = CustomerSupportAIAgent()

    # Sidebar for customer ID and memory view
    st.sidebar.title("Enter your Customer ID:")
    previous_customer_id = st.session_state.get("previous_customer_id", None)
    customer_id = st.sidebar.text_input("Enter your Customer ID")

    if customer_id != previous_customer_id:
        st.session_state.messages = []
        st.session_state.previous_customer_id = customer_id
        st.session_state.customer_data = None

    if st.sidebar.button("Generate Synthetic Data"):
        if customer_id:
            with st.spinner("Generating customer data..."):
                st.session_state.customer_data = support_agent.generate_synthetic_data(customer_id)
            if st.session_state.customer_data:
                st.sidebar.success("Synthetic data generated successfully!")
            else:
                st.sidebar.error("Failed to generate synthetic data.")
        else:
            st.sidebar.error("Please enter a customer ID first.")

    if st.sidebar.button("View Customer Profile"):
        if st.session_state.customer_data:
            st.sidebar.json(st.session_state.customer_data)
        else:
            st.sidebar.info("No customer data generated yet. Click 'Generate Synthetic Data' first.")

    if st.sidebar.button("View Memory Info"):
        if customer_id:
            memories = support_agent.get_memories(user_id=customer_id)
            if memories and "results" in memories:
                st.sidebar.write(f"Memory for customer **{customer_id}**:")
                for memory in memories["results"]:
                    if "memory" in memory:
                        st.write(f"- {memory['memory']}")
            else:
                st.sidebar.info("No memory found for this customer ID.")
        else:
            st.sidebar.error("Please enter a customer ID to view memory info.")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    query = st.chat_input("How can I assist you today?")

    if query and customer_id:
        st.session_state.messages.append({"role": "user", "content": query})
        with st.chat_message("user"):
            st.markdown(query)

        with st.spinner("Generating response..."):
            answer = support_agent.handle_query(query, user_id=customer_id)

        st.session_state.messages.append({"role": "assistant", "content": answer})
        with st.chat_message("assistant"):
            st.markdown(answer)

    elif not customer_id:
        st.error("Please enter a customer ID to start the chat.")

else:
    st.warning("Please enter your OpenAI API key to use the customer support agent.")
