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
            "reasoning": True,
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

                            # Handle reasoning content
                            reasoning = delta.get("reasoning_content", "")
                            if reasoning:
                                chunk = ChatGenerationChunk(
                                    message=AIMessageChunk(
                                        content="",
                                        additional_kwargs={
                                            "reasoning_content": reasoning
                                        },
                                    )
                                )
                                yield chunk

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


def run_cli():
    try:
        from rich.console import Console, Group
        from rich.markdown import Markdown
        from rich.panel import Panel
        from rich.prompt import Prompt
        from rich.live import Live
    except ImportError:
        print("Please install 'rich' to use the CLI: pip install rich")
        return

    console = Console()

    # Initialize Chat Model
    chat = ChatQubrid(api_key=qubrid_api_key)

    # Store conversation history
    messages = []

    console.print(
        Panel.fit(
            "[bold blue]Qubrid AI Chatbot[/bold blue]\n[italic]Powered by GPT-OSS-120B[/italic]",
            border_style="blue",
        )
    )
    console.print("[dim]Type 'quit' or 'exit' to end the conversation.[/dim]\n")

    while True:
        try:
            user_input = Prompt.ask("[bold green]You[/bold green]")
            if user_input.lower() in ["quit", "exit"]:
                console.print("[yellow]Goodbye![/yellow]")
                break

            messages.append(HumanMessage(content=user_input))

            console.print("[bold purple]Bot[/bold purple]: ", end="")

            # Create a Live display for streaming
            with Live(console=console, refresh_per_second=10) as live:
                reasoning_buffer = ""
                response_buffer = ""

                for chunk in chat.stream(messages):
                    reasoning = chunk.additional_kwargs.get("reasoning_content", "")
                    content = chunk.content

                    if reasoning:
                        reasoning_buffer += reasoning

                    if content:
                        response_buffer += content

                    renderables = []
                    if reasoning_buffer:
                        renderables.append(
                            Panel(
                                Markdown(reasoning_buffer),
                                title="Thinking",
                                border_style="yellow",
                                title_align="left",
                            )
                        )
                    if response_buffer:
                        renderables.append(Markdown(response_buffer))

                    live.update(Group(*renderables))

            # Print a newline after streaming finishes to separate from next prompt
            console.print("")

            messages.append(AIMessage(content=response_buffer))

        except KeyboardInterrupt:
            console.print("\n[yellow]Exiting...[/yellow]")
            break
        except Exception as e:
            console.print(f"\n[red]Error: {e}[/red]")


if __name__ == "__main__":
    run_cli()
