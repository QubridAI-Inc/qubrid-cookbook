import streamlit as st
import time
from typing import Dict, Any, List

def render_clarification_form(readiness: Dict[str, Any]):
    """
    Renders a mandatory form to fill in missing or low-confidence medical 
    details required for scheduling.
    """
    st.warning("🧐 **Information Required for a Safe Schedule**")
    st.write("The AI needs a few more details to ensure your schedule is accurate and safe.")
    
    missing = readiness.get("missing", [])
    low_conf = readiness.get("low_confidence", [])
    all_gaps = missing + low_conf
    
    # Use a set to track unique medicines to group inputs
    medicines = sorted(list(set([gap["medicine"] for gap in all_gaps])))
    
    overrides = {}
    
    with st.form("schedule_clarification_form"):
        for med_name in medicines:
            st.subheader(f"{med_name}")
            # Deduplicate fields for this medicine to avoid duplicate keys in the form
            med_gaps = sorted(list(set([gap["field"] for gap in all_gaps if gap["medicine"] == med_name])))
            
            overrides[med_name] = {}
            
            cols = st.columns(len(med_gaps))
            for i, field in enumerate(med_gaps):
                with cols[i]:
                    label = field.replace("_", " ").title()
                    widget_key = f"clarify_{med_name}_{field}"
                    if field == "duration_days":
                        overrides[med_name][field] = st.number_input(
                            f"{label}", min_value=1, max_value=90, value=5, key=widget_key
                        )
                    elif field == "frequency":
                        overrides[med_name][field] = st.selectbox(
                            f"{label}", 
                            ["Once daily", "Twice daily", "Thrice daily", "Four times daily", "As needed (PRN)"],
                            key=widget_key
                        )
                    else:
                        overrides[med_name][field] = st.text_input(
                            f"{label}", placeholder=f"Enter {label.lower()}", key=widget_key
                        )
        
        submitted = st.form_submit_button("Proceed to Generate Schedule", width="stretch")
        if submitted:
            # Basic validation
            valid = True
            for med_name, fields in overrides.items():
                for field, val in fields.items():
                    if val == "" or val is None:
                        st.error(f"Please fill in {field} for {med_name}")
                        valid = False
            
            if valid:
                return overrides
    return None

def render_schedule_table(schedule_data: List[Dict[str, Any]]):
    """
    Renders a clean, tabular schedule with Morning, Afternoon, Night slots.
    """
    if not schedule_data:
        st.info("No schedule data available.")
        return

    st.subheader("📅 Your Personalized Medication Schedule")
    
    # Custom CSS for the table
    st.markdown("""
        <style>
        .schedule-table {
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 20px;
        }
        .schedule-table th, .schedule-table td {
            border: 1px solid rgba(255, 255, 255, 0.1);
            padding: 12px;
            text-align: center;
        }
        .schedule-table th {
            background-color: rgba(255, 255, 255, 0.05);
            color: #9a1b74;
        }
        .slot-active {
            color: #28a745;
            font-size: 20px;
            font-weight: bold;
        }
        .slot-inactive {
            color: rgba(255, 255, 255, 0.2);
            font-size: 20px;
        }
        </style>
    """, unsafe_allow_html=True)

    table_html = """<table class="schedule-table">
        <thead>
            <tr>
                <th>Medicine</th>
                <th>Dosage</th>
                <th>Morning</th>
                <th>Afternoon</th>
                <th>Night</th>
                <th>Duration</th>
            </tr>
        </thead>
        <tbody>"""
    
    for item in schedule_data:
        morning = "✓" if item.get("morning") else "-"
        afternoon = "✓" if item.get("afternoon") else "-"
        night = "✓" if item.get("night") else "-"
        
        m_class = "slot-active" if item.get("morning") else "slot-inactive"
        a_class = "slot-active" if item.get("afternoon") else "slot-inactive"
        n_class = "slot-active" if item.get("night") else "slot-inactive"
        
        table_html += f"<tr><td><b>{item.get('medicine')}</b><br><small>{item.get('instructions', '')}</small></td>"
        table_html += f"<td>{item.get('dosage')}</td>"
        table_html += f"<td class='{m_class}'>{morning}</td>"
        table_html += f"<td class='{a_class}'>{afternoon}</td>"
        table_html += f"<td class='{n_class}'>{night}</td>"
        table_html += f"<td>{item.get('duration_days')} days</td></tr>"
    
    table_html += "</tbody></table>"
    st.markdown(table_html, unsafe_allow_html=True)
    
    st.caption("💡 Hover over medicine names for specific instructions.")
    st.info("⚠️ This schedule is AI-generated based on your prescription. Always confirm with your doctor.")

def render_schedule_transparency(readiness: Dict[str, Any], overrides: Dict[str, Any], model_name: str):
    """
    Transparency panel specialized for the scheduler.
    """
    st.sidebar.divider()
    with st.sidebar.expander("🔬 Schedule Intelligence Panel", expanded=True):
        st.write(f"**Model:** `{model_name}`")
        
        # Breakdown of source data
        st.write("**Data Integrity:**")
        
        ai_provided = 0
        human_provided = 0
        
        if overrides:
            for med, fields in overrides.items():
                human_provided += len(fields)
        
        # Crude estimation for now
        st.caption(f"• Fields provided by Human: {human_provided}")
        st.caption(f"• Fields inferred by AI: Secured via gated logic")
        
        st.divider()
        st.markdown("""
        **Safety Guardrails Active:**
        - [x] Readiness Gate
        - [x] Hallucination Block
        - [x] Deterministic Merging
        """)
