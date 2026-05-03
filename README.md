<img src="Assets\Images\qubrid_banner.png" width="100%"/>

<!-- Links -->
<p align="center">
  <a href="https://qubrid.com/">🔗 Website</a> •
  <a href="https://docs.platform.qubrid.com/">📖 Docs</a> •
  <a href="https://platform.qubrid.com/playground">🧪 Playground</a> •
  <a href="https://platform.qubrid.com/api-keys">🗝️ Get Model API Key </a> •
  <a href="https://platform.qubrid.com/">🚀 Platform</a> •
  <a href="https://www.qubrid.com/blog-news">📚 Blog</a>
</p>

# Qubrid Cookbook

The Qubrid Cookbook is a comprehensive collection of code examples, guides, and tutorials designed to help developers build production-ready AI applications using [Qubrid AI](https://qubrid.com/). Whether you're deploying models, building agents, or fine-tuning for your specific use case, these recipes provide ready-to-use code you can integrate directly into your projects.

## 🎯 About Qubrid AI

Qubrid AI is a **full-stack AI platform** that eliminates infrastructure complexity, enabling you to:

- ⚡ Access high-performance **GPU Virtual Machines**
- 🤗 **Deploy models** from Hugging Face or use latest open-source models
- 🧠 Run **reliable, scalable inference** with enterprise-grade performance
- 🔧 **Fine-tune models** on your proprietary data
- 📚 Build **custom RAG pipelines** and AI agents
- ☁️ Deploy to **cloud and edge** environments seamlessly

**No setup. No infra headaches. Just build and ship AI.**

## 🚀 Getting Started

### Prerequisites

To use the examples in this cookbook, you'll need:

- A Qubrid AI API key - **[Sign up for free](https://platform.qubrid.com/)** ⚡
- Python 3.8+
- Basic understanding of AI/ML concepts

### Get Your API Key

1. Visit [platform.qubrid.com](https://platform.qubrid.com/) and create a free account
2. Navigate to your dashboard
3. Go to **Settings → API Keys**
4. Generate your API key and you're ready to go! 🎉

## 📚 Cookbooks

| Cookbook                                                                                                                              | Description                                                                                                                                                                 |
| :------------------------------------------------------------------------------------------------------------------------------------ | :-------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **🤖 Agents**                                                                                                                         |                                                                                                                                                                             |
| [Claude Sonnet 4.6 Gmail Outlook Newsletter Agent](./Agents/Claude_Sonnet_4.6_API_Gmail_Outlook_Newsletter_Agent_Multi-agent_Example) | Multi-agent example for managing emails and newsletters.                                                                                                                    |
| [GLM-5 Content Writer Agent](./Agents/GLM-5_API_Content_Writer_Agent_Example)                                                         | AI agent for content writing using GLM-5 API.                                                                                                                               |
| [Hunyan OCR Multilingual Translation Agent](./Agents/Hunyan_OCR_API_Multilingual_Translation_Agent_Example)                           | Specializes in extracting text from images through advanced OCR and translating it to 48+ languages using intelligent AI agents.                                            |
| [Image Restoration Agent](./Deprecated/Image_Restoration_Agent)                                                                           | AI agent for image restoration and enhancement.                                                                                                                             |
| [MiniMax-M2.5 Long Context Agent](./Agents/MiniMax-M2.5_API_Long_Context_Agent_Example)                                               | Long context agent example using MiniMax API.                                                                                                                               |
| [Mistral-7B Resume Optimizer Agentic App](./Agents/Mistral-7B-Instruct-v0.3_API_Resume_Optimizer_Agentic_App_Example)                 | Agentic application for resume optimization using Mistral-7B.                                                                                                               |
| **🧠 LLM Applications**                                                                                                               |                                                                                                                                                                             |
| [GPT-OSS-120B Reasoning Chatbot](./LLMs/GPT-OSS-120B_API_Reasoning_Chatbot_Example)                                                   | Build conversational AI with advanced reasoning capabilities.                                                                                                               |
| [Kimi-K2-Thinking Think Trace AI](./LLMs/Kimi-K2-Thinking_API_Think_Trace_AI_Example)                                                 | Think trace AI example using Kimi-K2-Thinking API.                                                                                                                          |
| [Kimi-K2.5 Landing Page Creator](./LLMs/Kimi-K2.5_API_Landing_Page_Creator_Example)                                                   | AI landing page creator application using Kimi API.                                                                                                                         |
| [Pro AI Image Creator](./Deprecated/pro_ai_image_creator)                                                                                   | Professional AI image generation application.                                                                                                                               |
| **👁️ Multimodal AI**                                                                                                                  |                                                                                                                                                                             |
| [Qwen3-VL Medical Prescription Chatbot](./Multimodal/Qwen3-VL-30B-A3B-Instruct_API_Medical_Prescription_Chatbot_Example)              | Analyzes medical prescriptions (handwritten or digital) through a multi-step vision reasoning pipeline, extracting structured data, and providing focused medical insights. |
| [Qwen3-VL Nutritional Vision App](./Multimodal/Qwen3-VL-30B-A3B-Instruct_API_Nutri_Vision_App_Example)                                | Multimodal vision language model to provide comprehensive nutritional analysis from a single food image.                                                                    |
| [Qwen3-VL Smart Inspection Chatbot](./Multimodal/Qwen3-VL-30B-A3B-Instruct_API_Smart_Inspection_Chatbot_Example)                      | Vision based quality control assistant that transforms how industrial teams inspect and diagnose equipment.                                                                 |
| [Qwen3-VL Vision Chatbot](./Multimodal/Qwen3-VL-30B-A3B-Instruct_API_Vision_Chatbot_Example)                                          | General-purpose multimodal conversation assistant.                                                                                                                          |
| [Whisper Large GPT OSS](./Deprecated/whisper_large_gpt_oss)                                                                           | Audio processing and transcription using Whisper Large.                                                                                                                     |
| **📓 Notebooks**                                                                                                                      |                                                                                                                                                                             |
| [GPT-OSS-120B Confidence Aware RAG](./Notebooks/GPT_OSS_120B_API_Confidence_Aware_RAG_Example.ipynb)                                  | Jupyter notebook example for confidence aware RAG.                                                                                                                          |
| [GPT-OSS-120B Email Agent with HITL](./Notebooks/GPT_OSS_120B_API_Email_Agent_with_HITL_Example.ipynb)                                | Human-in-the-loop email agent example.                                                                                                                                      |
| [GPT-OSS-120B Langgraph Conditional Workflows](./Notebooks/GPT_OSS_120B_API_Langgraph_Conditional_Workflows_Example.ipynb)            | Building conditional workflows with Langgraph.                                                                                                                              |
| [GPT-OSS-120B Langgraph Youtube Agent](./Notebooks/GPT_OSS_120B_API_Langgraph_Youtube_Agent_Example.ipynb)                            | Langgraph agent example for interacting with Youtube.                                                                                                                       |
| [GPT-OSS-20B Tool using Agent](./Notebooks/GPT_OSS_20B_API_Tool_using_Agent_Example.ipynb)                                            | Example showing a 20B model using tools.                                                                                                                                    |

## 📺 Video Tutorials

Learn by watching! Check out our comprehensive video tutorials on YouTube:

- [Qubrid AI YouTube Channel](https://www.youtube.com/@QubridAI) - Complete tutorials and guides
- [Cookbook Series Playlist](https://www.youtube.com/playlist?list=PLoaE-lmLecgPoYuSa2BsmlJ8isKB5KFtq) - Step-by-step cookbook walkthroughs

Subscribe to stay updated with the latest tutorials and product demos!

## 🤝 Contributing

We welcome contributions from the community! To add your cookbook or improve existing ones:

1. Fork this repository
2. Create your cookbook following our structure guidelines
3. Submit a pull request

## 📖 Explore Further

### Official Resources

- [🌐 Qubrid Website](https://qubrid.com/) - Learn about our platform and services
- [🚀 Qubrid Platform](https://platform.qubrid.com/) - Access your dashboard and projects
- [📖 Documentation](https://docs.platform.qubrid.com/) - Complete API and platform docs
- [🧪 Playground](https://platform.qubrid.com/playground) - Test models interactively
- [🗝️ Model API](https://platform.qubrid.com/api-keys) - Get Model API Key
- [📚 Blog](https://www.qubrid.com/blog-news) - Latest updates and technical articles

### Community & Learning

- [📺 YouTube Channel](https://www.youtube.com/@QubridAI) - Video tutorials and demos
- [🎬 Cookbook Playlist](https://www.youtube.com/playlist?list=PLoaE-lmLecgPoYuSa2BsmlJ8isKB5KFtq) - Step-by-step guides
- [💼 LinkedIn](https://www.linkedin.com/company/qubrid) - Professional updates and insights

---

<p align="center">
  <strong>Made with ❤️ by <a href="https://qubrid.com">Qubrid AI</a></strong>
</p>
