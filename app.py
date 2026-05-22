import streamlit as st
import json
from contextlib import contextmanager, redirect_stdout
from io import StringIO
from main import wedding_crew, llm  # Import the crew and LLM from your backend

# ── Streamlit Page Configuration ────────────────────────────────────────────────

st.set_page_config(
    page_title="AwadhAI Wedding Concierge",
    page_icon="🏰",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("🏰 AwadhAI Wedding Concierge")
st.caption(f"Powered by CrewAI and Google's `{llm.model}` model.")


# ── Session State Management ──────────────────────────────────────────────────

# Initialize session state for the run, logs, and result
if "crew_run" not in st.session_state:
    st.session_state.crew_run = False
if "crew_logs" not in st.session_state:
    st.session_state.crew_logs = ""
if "crew_result" not in st.session_state:
    st.session_state.crew_result = None


# ── Custom Callback/Logger ────────────────────────────────────────────────────

# A simple context manager to capture stdout
@contextmanager
def st_capture_stdout():
    """Context manager to capture stdout and update Streamlit session state."""
    buffer = StringIO()
    with redirect_stdout(buffer):
        yield
    
    # After the block, update the logs in session state
    log_output = buffer.getvalue()
    st.session_state.crew_logs += log_output
    # Also print to console for debugging
    print(log_output)


# ── Sidebar for User Inputs ───────────────────────────────────────────────────

with st.sidebar:
    st.header("Step 1: Plan Your Dream Wedding")
    st.markdown(
        "Enter your budget and guest count, and our AI agents will craft the "
        "perfect Awadhi wedding plan for you in Lucknow."
    )

    # Input fields for user to specify their wedding details
    guest_count = st.number_input(
        "Guest Count", min_value=50, max_value=1000, value=150, step=10
    )
    total_budget = st.number_input(
        "Total Budget (INR)",
        min_value=100_000,
        max_value=5_000_000,
        value=500_000,
        step=25_000,
    )
    
    # The button that kicks off the agentic crew
    plan_button = st.button(
        "Plan My Wedding",
        type="primary",
        use_container_width=True,
        disabled=st.session_state.crew_run,
    )


# ── Main Panel for Agentic Workflow & Results ─────────────────────────────────

if plan_button:
    st.session_state.crew_run = True
    st.session_state.crew_logs = ""
    st.session_state.crew_result = None

    # Display a status spinner while the crew is running
    with st.status("🤖 The AI Concierge is planning your wedding...", expanded=True) as status:
        st.markdown("### Agentic Workflow Log")
        log_container = st.empty()

        # Prepare inputs for the crew
        inputs = {
            "guest_count": guest_count,
            "date": "2024-12-20",  # Static date for this example
            "total_budget": total_budget,
            "venue_cost": 200_000, # Placeholder, can be refined
        }

        # Use the custom context manager to capture logs
        with st_capture_stdout():
            # Kick off the crew's work
            result = wedding_crew.kickoff(inputs=inputs)
            st.session_state.crew_result = result
        
        # Update the log container with the final captured logs
        log_container.code(st.session_state.crew_logs, language="log")
        
        status.update(label="✅ Wedding Plan Complete!", state="complete", expanded=False)

import re

# ... existing code ...

# Display the final result if it exists in the session state
if st.session_state.crew_result:
    st.header("Step 2: Your Custom Wedding Plan")

    try:
        # The final result from the negotiator is often a JSON string wrapped in markdown.
        # We use a regex to extract the JSON part.
        json_match = re.search(r"```json\n({.*?})\n```", st.session_state.crew_result, re.DOTALL)
        if json_match:
            json_str = json_match.group(1)
        else:
            # If no markdown block is found, assume the whole string is the JSON
            json_str = st.session_state.crew_result

        final_plan = json.loads(json_str)

        col1, col2, col3 = st.columns(3)
        col1.metric(
            "Original Price",
            f"₹{final_plan.get('original_total_cost', 0):,.2f}",
            help="The initial estimated cost before negotiation.",
        )
        col2.metric(
            "Discount",
            f"{final_plan.get('discount_percent', 0)}%",
            f"- ₹{final_plan.get('discount_amount', 0):,.2f}",
            help="The discount secured by our AI Negotiator.",
        )
        col3.metric(
            "Final Price",
            f"₹{final_plan.get('final_price', 0):,.2f}",
            help="The final, negotiated price for your event.",
        )

        st.success("🎉 **Congratulations! Here is your negotiated wedding itinerary.**")

        # Display the detailed plan in an expander
        with st.expander("View Full Itinerary Details", expanded=True):
            st.markdown(
                f"""
                - **Chosen Venue**: `The Grand Palace, Gomti Nagar` (Based on guest count of {guest_count})
                - **Awadhi Menu**: `Standard Awadhi Menu` (Selected based on your budget)
                - **Original Combined Cost**: `₹{final_plan.get('original_total_cost', 0):,.2f}`
                - **Final Negotiated Price**: `₹{final_plan.get('final_price', 0):,.2f}`
                - **Total Savings**: `₹{final_plan.get('discount_amount', 0):,.2f}`
                """
            )
            st.info(
                "This plan has been tailored by our AI agents to provide the best "
                "value and experience for your special day in Lucknow."
            )

    except (json.JSONDecodeError, TypeError, AttributeError) as e:
        st.error(
            "Sorry, there was an error processing the final plan. "
            "Please try running the planner again."
        )
        st.code(st.session_state.crew_result, language="text")

# Display the logs in an expander if they exist
if st.session_state.crew_logs and not st.session_state.crew_result:
     with st.expander("Show Agent Logs", expanded=True):
        st.code(st.session_state.crew_logs, language="log")
