# Company Research Assistant (Account Plan Generator)

## Overview
This is an AI-powered agent designed to assist users in researching companies and generating comprehensive account plans. It uses natural conversation to gather requirements, performs research using external tools, and synthesizes findings into a structured plan.

## Features
- **Interactive Research**: The agent converses with the user to understand research goals and provides updates during the process.
- **Multi-source Information Gathering**: Uses search tools to gather data about target companies.
- **Account Plan Generation**: Generates structured account plans including Company Overview, Key Stakeholders, Pain Points, and Strategic Opportunities.
- **Iterative Refinement**: Allows users to update specific sections of the plan through conversation.

## Architecture
- **Frontend**: Streamlit (for chat interface and plan display).
- **Orchestration**: LangGraph (for stateful agentic workflow).
- **LLM**: OpenAI GPT-4 (configurable).
- **Tools**: DuckDuckGo Search (for web research).

## Setup Instructions

1. **Clone the repository**
2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
3. **Set up Environment Variables**:
   Create a `.env` file and add your Google API key:
   ```
   GOOGLE_API_KEY=...
   ```
4. **Run the application**:
   ```bash
   streamlit run main.py
   ```

## Design Decisions
- **LangGraph**: Chosen for its ability to handle cyclic graphs and state, which is crucial for the "human-in-the-loop" aspect where the agent asks for clarification or confirmation during research.
- **Streamlit**: Selected for rapid prototyping and built-in chat components.
