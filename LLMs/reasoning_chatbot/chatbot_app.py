import streamlit as st
from langchain_core.messages import HumanMessage, AIMessage
from chatbot import ChatQubrid, qubrid_api_key

# Page Configuration
st.set_page_config(page_title="Qubrid AI Chatbot", page_icon="🤖", layout="wide")

# Custom CSS for better UI
st.markdown(
    """
<style>
    .stChatMessage {
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    .stChatMessage[data-testid="stChatMessageUser"] {
        background-color: #f0f2f6;
    }
    .stChatMessage[data-testid="stChatMessageAssistant"] {
        background-color: #e8f0fe;
    }
</style>
""",
    unsafe_allow_html=True,
)

# Sidebar for Parameters
with st.sidebar:
    st.title("⚙️ Configuration")
    st.markdown("Adjust the model parameters below:")

    temperature = st.slider(
        "Temperature",
        min_value=0.0,
        max_value=1.0,
        value=0.7,
        step=0.1,
        help="Controls randomness: higher values make output more random, lower values make it more deterministic.",
    )

    max_tokens = st.number_input(
        "Max Tokens",
        min_value=1,
        max_value=65536,
        value=4096,
        step=256,
        help="The maximum number of tokens to generate.",
    )

    top_p = st.slider(
        "Top P",
        min_value=0.0,
        max_value=1.0,
        value=0.8,
        step=0.1,
        help="Controls diversity via nucleus sampling.",
    )

    if st.button("Clear Chat History", type="primary"):
        st.session_state.messages = []
        st.rerun()

# Initialize Session State
if "messages" not in st.session_state:
    st.session_state.messages = []

# Main Chat Interface
st.title("🤖 Qubrid AI Chatbot")
st.caption("Powered by GPT-OSS-120B")

# Display Chat History
for msg in st.session_state.messages:
    if isinstance(msg, HumanMessage):
        with st.chat_message("user"):
            st.markdown(msg.content)
    elif isinstance(msg, AIMessage):
        with st.chat_message("assistant"):
            st.markdown(msg.content)

# Chat Input
if prompt := st.chat_input("Type your message here..."):
    # Add user message to state and display
    st.session_state.messages.append(HumanMessage(content=prompt))
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate Response
    with st.chat_message("assistant"):
        # Container for reasoning
        reasoning_status = st.status("Thinking...", expanded=True)
        with reasoning_status:
            reasoning_placeholder = st.empty()

        message_placeholder = st.empty()

        full_response = ""
        full_reasoning = ""

        # Initialize Chat Model with current params
        chat = ChatQubrid(
            api_key=qubrid_api_key,
            temperature=temperature,
            max_tokens=max_tokens,
            top_p=top_p,
        )

        try:
            # Stream the response
            for chunk in chat.stream(st.session_state.messages):
                # Handle reasoning
                reasoning_chunk = chunk.additional_kwargs.get("reasoning_content", "")
                if reasoning_chunk:
                    full_reasoning += reasoning_chunk
                    reasoning_placeholder.markdown(full_reasoning)

                # Handle content
                content = chunk.content
                if content:
                    full_response += content
                    message_placeholder.markdown(full_response + "▌")

            # Final updates
            reasoning_status.update(
                label="Thinking Complete", state="complete", expanded=False
            )
            message_placeholder.markdown(full_response)

            # Add assistant message to state
            st.session_state.messages.append(AIMessage(content=full_response))

        except Exception as e:
            st.error(f"An error occurred: {e}")
