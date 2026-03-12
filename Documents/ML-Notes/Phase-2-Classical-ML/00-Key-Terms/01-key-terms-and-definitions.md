# Key Terms & Definitions in AI and Machine Learning

> This document provides foundational definitions for the most important terms you'll encounter in the world of AI and Machine Learning. Bookmark this as your quick-reference glossary.

---

## Table of Contents

- [Machine Learning (ML)](#machine-learning-ml)
- [Data Science](#data-science)
- [Artificial Intelligence (AI)](#artificial-intelligence-ai)
- [Deep Learning](#deep-learning)
- [Large Language Models (LLMs)](#large-language-models-llms)
- [Generative AI](#generative-ai)
- [Agentic AI](#agentic-ai)
- [How They All Relate](#how-they-all-relate)

---

## Machine Learning (ML)

**Definition:** Machine Learning is a subset of Artificial Intelligence that gives computers the ability to **learn from data** and make predictions or decisions **without being explicitly programmed** for every scenario.

Instead of writing rules like "if email contains 'free money' then mark as spam", you feed the algorithm thousands of emails that are already labeled as spam or not-spam, and the algorithm **learns the patterns** by itself.

### Types of Machine Learning

| Type | Description | Example |
|------|-------------|---------|
| **Supervised Learning** | Model learns from **labeled** data (input + correct output) | Predicting house prices, spam detection |
| **Unsupervised Learning** | Model finds patterns in **unlabeled** data | Customer segmentation, anomaly detection |
| **Reinforcement Learning** | Model learns by **trial and error**, receiving rewards or penalties | Game-playing AI, self-driving cars |

### Real-World Examples

- **Netflix Recommendations:** ML models analyze your watch history and predict what you might enjoy next.
- **Email Spam Filters:** Gmail uses ML to classify incoming emails as spam or legitimate.
- **Voice Assistants:** Siri and Alexa use ML to understand and respond to voice commands.
- **Fraud Detection:** Banks use ML to detect unusual credit card transactions in real-time.

---

## Data Science

**Definition:** Data Science is a **broad, interdisciplinary field** that uses scientific methods, statistics, algorithms, and systems to **extract knowledge and insights from structured and unstructured data**.

Think of Data Science as the umbrella that covers everything from collecting and cleaning data to analyzing it, visualizing it, and building ML models on top of it.

### How Data Science Differs from ML

| Aspect | Data Science | Machine Learning |
|--------|-------------|-----------------|
| **Scope** | Broader — includes data collection, cleaning, analysis, visualization, and storytelling | Narrower — focused on building predictive models |
| **Goal** | Extract insights and drive decisions | Make accurate predictions or automate decisions |
| **Tools** | SQL, Excel, Tableau, Python, R, Statistics | Scikit-learn, TensorFlow, PyTorch |

### Example

A Data Scientist at an e-commerce company might:
1. **Collect** data from website logs, purchase history, and customer surveys
2. **Clean** messy data (handle missing values, fix formats)
3. **Analyze** trends — "Which products sell best in December?"
4. **Visualize** sales dashboards for stakeholders
5. **Build an ML model** to predict which customers are likely to churn

Steps 1–4 are classic Data Science work. Step 5 is where Machine Learning comes in.

---

## Artificial Intelligence (AI)

**Definition:** Artificial Intelligence is the **broadest concept** — it refers to any technique that enables machines to **mimic human intelligence**. This includes reasoning, learning, problem-solving, perception, and language understanding.

### The AI Hierarchy

```
┌─────────────────────────────────────────────┐
│           Artificial Intelligence            │
│  ┌───────────────────────────────────────┐   │
│  │         Machine Learning              │   │
│  │  ┌───────────────────────────────┐    │   │
│  │  │       Deep Learning           │    │   │
│  │  │  ┌───────────────────────┐    │    │   │
│  │  │  │   LLMs / Gen AI       │    │    │   │
│  │  │  └───────────────────────┘    │    │   │
│  │  └───────────────────────────────┘    │   │
│  └───────────────────────────────────────┘   │
└─────────────────────────────────────────────┘
```

- **AI** is the big picture (any "smart" machine behavior)
- **ML** is a subset (learning from data)
- **Deep Learning** is a subset of ML (using neural networks with many layers)
- **LLMs and Generative AI** are subsets of Deep Learning

---

## Deep Learning

**Definition:** Deep Learning is a **subset of Machine Learning** that uses **artificial neural networks with multiple layers** (hence "deep") to learn representations of data. These networks are inspired by the structure of the human brain.

### Why "Deep"?

The word "deep" refers to the number of layers in the neural network. A network with 2–3 layers is "shallow." A network with dozens or hundreds of layers is "deep."

### When to Use Deep Learning vs Traditional ML

| Use Deep Learning When... | Use Traditional ML When... |
|--------------------------|---------------------------|
| You have **large amounts** of data | You have **smaller** datasets |
| The problem involves **images, audio, or text** | The data is **structured/tabular** (spreadsheets) |
| You need to learn **complex patterns** | Simpler patterns suffice |
| You have **GPU compute** available | Limited compute resources |

### Real-World Examples

- **Image Recognition:** Identifying objects in photos (e.g., self-driving car cameras)
- **Natural Language Processing:** Language translation (Google Translate)
- **Speech Recognition:** Converting speech to text
- **Medical Imaging:** Detecting tumors in X-rays or MRIs

---

## Large Language Models (LLMs)

**Definition:** Large Language Models are a type of **deep learning model** trained on **massive amounts of text data** to understand and generate human language. They learn the statistical patterns of language — which words and phrases tend to follow others.

### Key Characteristics

- **"Large"** refers to the number of parameters (billions or even trillions)
- **"Language"** means they specialize in text/language tasks
- **"Model"** means they are trained neural networks

### Examples of LLMs

| Model | Creator | Notable For |
|-------|---------|-------------|
| **GPT-4** | OpenAI | Powers ChatGPT; general-purpose language tasks |
| **Claude** | Anthropic | Focus on safety and helpfulness |
| **Gemini** | Google | Multimodal capabilities (text + images) |
| **LLaMA** | Meta | Open-source family of models |

### What Can LLMs Do?

- Answer questions in natural language
- Write code, essays, poems, emails
- Summarize long documents
- Translate between languages
- Reason through multi-step problems

### Important Limitation

LLMs **predict the next most likely token (word/piece of a word)** — they don't truly "understand" things the way humans do. They are incredibly powerful pattern matchers over language.

---

## Generative AI

**Definition:** Generative AI refers to AI systems that can **create new content** — text, images, audio, video, or code — that didn't exist before. It "generates" rather than just "classifies" or "predicts."

### How It Differs from Traditional AI

| Traditional AI (Discriminative) | Generative AI |
|-------------------------------|---------------|
| Classifies or predicts from existing data | **Creates new** data/content |
| "Is this email spam?" | "Write me a professional email" |
| "Is this image a cat?" | "Generate an image of a cat wearing a hat" |

### Types of Generative AI

| Type | What It Generates | Example Tools |
|------|-------------------|---------------|
| **Text Generation** | Articles, code, conversations | ChatGPT, Claude |
| **Image Generation** | Photos, art, designs | DALL-E, Midjourney, Stable Diffusion |
| **Audio Generation** | Music, speech, sound effects | Suno, ElevenLabs |
| **Video Generation** | Video clips, animations | Sora, Runway |
| **Code Generation** | Software code | GitHub Copilot, Cursor |

---

## Agentic AI

**Definition:** Agentic AI refers to AI systems that can **autonomously take actions**, make decisions, and complete multi-step tasks **with minimal human intervention**. Rather than just answering a question, an agent can plan, use tools, and execute a workflow.

### What Makes AI "Agentic"?

Traditional AI (like a chatbot) responds to a single prompt and gives a single answer. Agentic AI goes further:

1. **Planning** — It breaks a complex goal into sub-tasks
2. **Tool Use** — It can call APIs, search the web, run code, read files
3. **Memory** — It remembers context across steps
4. **Self-Correction** — It can evaluate its own output and retry if something fails
5. **Autonomy** — It operates with minimal human hand-holding

### Example: Traditional AI vs Agentic AI

**Task:** "Book me the cheapest flight from Delhi to London next Friday"

| Traditional AI (Chatbot) | Agentic AI |
|--------------------------|------------|
| "Here are some tips for finding cheap flights. You can check MakeMyTrip or Google Flights." | 1. Searches flight APIs for Delhi→London on that date |
| (Gives information, **you** do the work) | 2. Compares prices across airlines |
| | 3. Selects the cheapest option |
| | 4. Books the flight using your saved payment method |
| | 5. Sends you confirmation |

### Real-World Examples

- **Coding Agents:** AI that reads your codebase, writes code, runs tests, and fixes bugs autonomously
- **Research Agents:** AI that searches multiple sources, synthesizes findings, and writes a report
- **Customer Service Agents:** AI that handles support tickets end-to-end, including issuing refunds

---

## How They All Relate

```
AI (Broadest concept — machines mimicking human intelligence)
 └── Machine Learning (Learning from data)
      ├── Traditional ML (Linear Regression, Decision Trees, SVMs, etc.)
      └── Deep Learning (Neural Networks with many layers)
           ├── Computer Vision (CNNs — image recognition)
           ├── NLP (Understanding language)
           │    └── Large Language Models (GPT, Claude, Gemini)
           └── Generative AI (Creating new content)
                └── Agentic AI (Autonomous action-taking AI systems)

Data Science (Overlapping field that uses ML + statistics + domain knowledge)
```

### Quick Summary Table

| Term | One-Liner |
|------|-----------|
| **AI** | Machines that mimic human intelligence |
| **ML** | Algorithms that learn patterns from data |
| **Deep Learning** | ML using multi-layered neural networks |
| **Data Science** | Extracting insights from data using statistics, ML, and visualization |
| **LLM** | Deep learning models trained on massive text to understand/generate language |
| **Generative AI** | AI that creates new content (text, images, code, audio, video) |
| **Agentic AI** | AI that autonomously plans, uses tools, and completes multi-step tasks |

---

> **Next up:** [What is Supervised Learning?](../01-Supervised-Learning/01-what-is-supervised-learning.md)
