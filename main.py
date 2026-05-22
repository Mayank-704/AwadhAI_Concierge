import os
import json
import random
from crewai import Agent, Task, Crew, Process, LLM
from crewai.tools import tool
from dotenv import load_dotenv

load_dotenv()

# ── LLM Setup ────────────────────────────────────────────────────────────────
# CrewAI v0.60+ requires its own LLM wrapper (backed by LiteLLM).
# LangChain ChatGoogleGenerativeAI objects are no longer accepted.
# The GEMINI_API_KEY env var is picked up automatically by LiteLLM;
# alternatively set GOOGLE_API_KEY — either name works.
llm = LLM(
    model="gemini-2.5-flash-lite",   # LiteLLM provider/model string
    temperature=0.1,
    api_key=os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY"),
)


# ── Tools (replaces bare lambda/action — the correct CrewAI pattern) ─────────

@tool("Venue Filter Tool")
def filter_venues(guest_count: int, date: str) -> str:
    """
    Reads lucknow_vendors.json and returns venues that can accommodate
    the given guest count. Falls back to all venues if no capacity field exists.
    """
    try:
        with open("lucknow_vendors.json", "r") as f:
            data = json.load(f)
    except FileNotFoundError:
        return "Error: lucknow_vendors.json not found. Please ensure the file exists."
    except json.JSONDecodeError:
        return "Error: lucknow_vendors.json is malformed and could not be parsed."

    venues = data.get("venues", [])
    # Filter by capacity when the field is present; otherwise keep all
    suitable = [v for v in venues if v.get("capacity", guest_count) >= guest_count]
    if not suitable:
        suitable = venues  # graceful fallback

    return json.dumps(suitable, indent=2, ensure_ascii=False)


@tool("Menu Selector Tool")
def select_menu(venue_cost: float, total_budget: float) -> str:
    """
    Calculates the remaining budget after the venue cost and returns
    the most suitable Awadhi menu tier with its estimated cost.
    """
    remaining_budget = total_budget - venue_cost

    if remaining_budget > 200_000:
        menu = {"menu": "Full Awadhi Menu",     "cost": 180_000}
    elif remaining_budget > 100_000:
        menu = {"menu": "Standard Awadhi Menu", "cost":  90_000}
    else:
        menu = {"menu": "Basic Awadhi Menu",    "cost":  45_000}

    menu["remaining_budget_after_venue"] = remaining_budget
    return json.dumps(menu, indent=2)


@tool("Price Negotiator Tool")
def negotiate_price(venue_cost: float, menu_cost: float) -> str:
    """
    Simulates price negotiation and returns the final discounted price,
    discount percentage, and total savings for venue + catering combined.
    """
    total_cost     = venue_cost + menu_cost
    discount_rate  = random.uniform(0.05, 0.20)   # 5 – 20 % discount
    discount_amount = total_cost * discount_rate
    final_price    = total_cost - discount_amount

    result = {
        "original_total_cost": round(total_cost, 2),
        "discount_percent":    round(discount_rate * 100, 2),
        "discount_amount":     round(discount_amount, 2),
        "final_price":         round(final_price, 2),
    }
    return json.dumps(result, indent=2)


# ── Agents ────────────────────────────────────────────────────────────────────

venue_scout = Agent(
    role="Venue Scout",
    goal="Find and filter suitable wedding venues in Lucknow based on user requirements.",
    backstory=(
        "An experienced event planner with deep knowledge of Lucknow's venues, "
        "dedicated to finding the perfect setting for your special day."
    ),
    llm=llm,
    tools=[filter_venues],
    allow_delegation=False,
    verbose=True,
)

culinary_expert = Agent(
    role="Culinary Expert",
    goal="Select an appropriate Awadhi menu based on the remaining budget after venue selection.",
    backstory=(
        "A renowned chef specialising in Awadhi cuisine, passionate about creating "
        "a memorable dining experience that perfectly fits your budget."
    ),
    llm=llm,
    tools=[select_menu],
    allow_delegation=False,
    verbose=True,
)

negotiator = Agent(
    role="Negotiator",
    goal="Negotiate a final discounted price with the selected venue and caterer.",
    backstory=(
        "A sharp, persuasive negotiator with a knack for getting the best deals, "
        "ensuring you receive maximum value for your money."
    ),
    llm=llm,
    tools=[negotiate_price],
    allow_delegation=False,
    verbose=True,
)


# ── Tasks ─────────────────────────────────────────────────────────────────────
# FIX: Removed the invalid `action` parameter that was present on all tasks.
# FIX: Removed the `culinary_task.output.raw` reference that raised AttributeError
#      at definition time (before the crew had even run).

venue_task = Task(
    description=(
        "Use the Venue Filter Tool to read lucknow_vendors.json and identify venues "
        "capable of hosting {guest_count} guests on {date}. "
        "List each suitable venue with its name, capacity, and pricing."
    ),
    agent=venue_scout,
    expected_output=(
        "A structured list of suitable venues, each with name, capacity, and price details."
    ),
)

culinary_task = Task(
    description=(
        "The confirmed venue costs {venue_cost} rupees from a total budget of {total_budget} rupees. "
        "Use the Menu Selector Tool (passing venue_cost={venue_cost} and total_budget={total_budget}) "
        "to choose the best Awadhi menu tier. Report the menu name, per-head description, and total cost."
    ),
    agent=culinary_expert,
    expected_output="The selected Awadhi menu name and its estimated total cost.",
    context=[venue_task],
)

negotiation_task = Task(
    description=(
        "The venue costs {venue_cost} rupees. Review the Culinary Expert's output above to obtain "
        "the menu cost, then call the Price Negotiator Tool with both figures. "
        "Present the original combined cost, the negotiated discount percentage, and the final price."
    ),
    agent=negotiator,
    expected_output=(
        "A summary showing the original total cost, discount percentage achieved, and the final price."
    ),
    context=[culinary_task],
)


# ── Crew ──────────────────────────────────────────────────────────────────────

wedding_crew = Crew(
    agents=[venue_scout, culinary_expert, negotiator],
    tasks=[venue_task, culinary_task, negotiation_task],
    process=Process.sequential,
    verbose=True,
)

# ── Run ───────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    result = wedding_crew.kickoff(
        inputs={
            "guest_count":  150,
            "date":         "2024-12-20",
            "total_budget": 500_000,
            "venue_cost":   200_000,
        }
    )
    print("\n" + "=" * 60)
    print("FINAL WEDDING PLAN SUMMARY")
    print("=" * 60)
    print(result)