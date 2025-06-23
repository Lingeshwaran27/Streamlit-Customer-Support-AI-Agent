# 🛒 AI Customer Support Agent with Memory

An AI-powered customer support assistant built with **Streamlit**, **OpenAI (via OpenRouter)**, and **Mem0 (Qdrant vector memory)** — capable of remembering past interactions for highly personalized support experiences.

> 💬 _“Hi again, Lingesh! I remember your last order of a MacBook Pro. Would you like help with tracking that or something else?”_

---

## 🚀 Features

- 🧠 **Persistent Memory** using Qdrant via Mem0 to recall previous conversations and context
- 🤖 **OpenAI Chat API** via OpenRouter for fast, powerful responses
- 🧾 **Synthetic Data Generation** of customer history & profiles for realistic support scenarios
- 💻 **Streamlit UI** for clean, interactive support chat experience
- 🔐 Uses `.env` to securely manage API keys

---

## ⚙️ Tech Stack

| Tool        | Purpose                           |
|-------------|------------------------------------|
| `Streamlit` | Frontend UI for chat               |
| `OpenAI`    | GPT-4 / GPT-3.5 responses          |
| `Mem0`      | Memory abstraction over Qdrant     |
| `Qdrant Cloud` | Vector database for memory         |
| `dotenv`    | Load `.env` secrets securely       |

---

## 📸 Demo Screenshot

> _(Optional - add an `assets/chat_demo.png` and uncomment below)_

<!-- ![Chat Demo](assets/chat_demo.png) -->

---

## 🧪 How It Works

1. **User logs in with Customer ID**
2. System recalls previous chat & profile data from Qdrant
3. User chats with support assistant (powered by GPT)
4. Assistant generates helpful replies based on memory + prompt
5. All new chats are stored as new memory chunks for future reference
6. Optionally, generate realistic synthetic customer history for demo use

---

## 📦 Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/your-username/streamlit-customer-support-ai.git
cd streamlit-customer-support-ai
