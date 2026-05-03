from langchain_core.messages import (
    HumanMessage,
    AIMessage,
    BaseMessage,
    SystemMessage,
    AIMessageChunk,
)
from langchain_core.language_models import BaseChatModel
from langchain_core.outputs import ChatResult, ChatGeneration, ChatGenerationChunk
from typing import Any, List, Optional, Iterator, Dict
import requests
import json

# API Key
qubrid_api_key = "your_qubrid_api_key_here"


class ChatQubrid(BaseChatModel):
    api_key: str
    base_url: str = "https://platform.qubrid.com/api/v1/qubridai/chat/completions"
    model: str = "openai/gpt-oss-120b"
    temperature: float = 0.7
    max_tokens: int = 65536
    top_p: float = 0.8

    @property
    def _llm_type(self) -> str:
        return "qubrid-chat"

    def _convert_messages(self, messages: List[BaseMessage]) -> List[Dict[str, Any]]:
        formatted_messages = []
        for message in messages:
            if isinstance(message, HumanMessage):
                role = "user"
            elif isinstance(message, AIMessage):
                role = "assistant"
            elif isinstance(message, SystemMessage):
                role = "system"
            else:
                role = "user"

            formatted_messages.append({"role": role, "content": message.content})
        return formatted_messages

    def _generate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[Any] = None,
        **kwargs: Any,
    ) -> ChatResult:
        content = ""
        for chunk in self._stream(messages, stop, run_manager, **kwargs):
            content += chunk.message.content
        return ChatResult(
            generations=[ChatGeneration(message=AIMessage(content=content))]
        )

    def _stream(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[Any] = None,
        **kwargs: Any,
    ) -> Iterator[ChatGenerationChunk]:

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": self.model,
            "messages": self._convert_messages(messages),
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "top_p": self.top_p,
            "stream": True,
        }

        # Use requests like in main.py which is known to work
        response = requests.post(
            self.base_url, headers=headers, json=payload, stream=True
        )

        for line in response.iter_lines():
            if line:
                decoded_line = line.decode("utf-8")
                if decoded_line.startswith("data: "):
                    json_str = decoded_line[6:]
                    if json_str.strip() == "[DONE]":
                        break
                    try:
                        json_data = json.loads(json_str)
                        if "choices" in json_data and len(json_data["choices"]) > 0:
                            delta = json_data["choices"][0].get("delta", {})
                            content = delta.get("content", "")

                            if content:
                                chunk = ChatGenerationChunk(
                                    message=AIMessageChunk(content=content)
                                )
                                if run_manager:
                                    run_manager.on_llm_new_token(content)
                                yield chunk
                    except Exception:
                        continue


# Initialize Chat Model
chat = ChatQubrid(api_key=qubrid_api_key)

# Store conversation history
messages = []

print("Start chatting with the bot (type 'quit' to exit):")

while True:
    try:
        user_input = input("\nYou: ")
        if user_input.lower() in ["quit", "exit"]:
            break

        messages.append(HumanMessage(content=user_input))

        print("Bot: ", end="", flush=True)
        response_content = ""

        # Stream the response
        for chunk in chat.stream(messages):
            content = chunk.content
            print(content, end="", flush=True)
            response_content += content

        messages.append(AIMessage(content=response_content))

    except KeyboardInterrupt:
        print("\nExiting...")
        break
    except Exception as e:
        print(f"\nError: {e}")
