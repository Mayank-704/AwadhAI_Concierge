# 👑 AwadhAI Concierge: The Agentic Wedding Planner

> "End-to-end wedding negotiation and booking for the Lucknow market, powered by multi-agent AI." 
> 
> 

---

## 🚀 The Problem (PS-21)

Lucknow hosts thousands of weddings annually across banquet halls and farmhouses, all planned manually. Planning a Gomti Nagar wedding manually is chaotic, and manual negotiation is a massive pain point for B2C consumers.

## 🧠 Our Agentic Solution

Our solution utilizes the CrewAI architecture to orchestrate a seamless planning experience. We bypassed a traditional database entirely to build a high-impact, multi-agent orchestrator tailored for a flawless demo. It features three distinct AI personas collaborating autonomously to discover, negotiate, and book:

* 
**The Venue Scout:** Parses local data based on the user's guest count and preferred date.


* 
**The Culinary Expert:** Selects an Awadhi menu that fits the remaining budget after the venue is chosen.


* 
**The Negotiator:** Takes the selected venue and caterer, applies a randomized negotiation success rate, and calculates a final discounted price for the B2C consumer.



## 📍 Local Intelligence

Our AI is grounded in specific Lucknow data to prove it is a targeted solution, not a generic wrapper.

* It reads from a highly specific `lucknow_vendors.json` knowledge base.


* It references specific Gomti Nagar venues, such as "The Awadh Grand Banquet".


* It integrates authentic Awadhi catering styles, specifically mentioning items like Galouti Kebabs and Dum Biryani.



## 🛠 Tech Stack

To execute this flawlessly under extreme time constraints, we made ruthless engineering trade-offs:

* 
**Frontend:** Streamlit version 1.57.0 instantly gives us a clean, interactive UI.


* 
**Agent Framework:** CrewAI and CrewAI-Tools version 1.14.4 ensures the multi-agent backend does not stall.


* 
**LLM Provider:** Gemini via `google-genai` version 2.2.0. As of late 2025, `google-generativeai` was officially deprecated, so we utilized the correct, actively maintained package for Gemini 1.5 Flash to guarantee fast and reliable API calls.



## 💻 How to Run Locally

Use these exactly 3 copy-paste commands to run the project:

```bash
git clone <your-repository-link>
pip install streamlit==1.57.0 crewai==1.14.4 crewai-tools==1.14.4 google-genai==2.2.0
streamlit run app.py

```

## 🎥 3-Minute Demo Video

[Placeholder: Insert YouTube/Drive link for your final submission here] 

---
