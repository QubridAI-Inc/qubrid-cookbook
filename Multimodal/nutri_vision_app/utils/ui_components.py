"""UI display components"""
import streamlit as st

def display_macro_row(data: dict):
    """Displays the horizontal nutrition bar with icons"""
    calories = data.get('calories', 0)
    protein = data.get('protein', 0)
    carbs = data.get('carbs', 0)
    fat = data.get('fat', 0)

    # Uses the CSS classes defined in styles.py for dynamic theming
    html_content = f"""
    <div class="glass-card">
        <div style="display: flex; align-items: center; gap: 1rem; margin-bottom: 0.5rem;">
            <span style="font-size: 1.2rem;">📊</span>
            <span style="font-weight: 700; font-size: 1.1rem;" class="macro-value">Nutrition (per 100g):</span>
        </div>
        <div class="macro-container">
            <div class="macro-item">
                <span style="font-size: 1.5rem;">🔥</span>
                <span class="macro-value">{calories}</span>
                <span class="macro-label">Kcal</span>
            </div>
            <div class="macro-divider"></div>
            <div class="macro-item">
                <span style="font-size: 1.5rem;">💪</span>
                <span class="macro-value">{protein}g</span>
                <span class="macro-label">Protein</span>
            </div>
            <div class="macro-divider"></div>
            <div class="macro-item">
                <span style="font-size: 1.5rem;">🌾</span>
                <span class="macro-value">{carbs}g</span>
                <span class="macro-label">Carbs</span>
            </div>
            <div class="macro-divider"></div>
            <div class="macro-item">
                <span style="font-size: 1.5rem;">🥑</span>
                <span class="macro-value">{fat}g</span>
                <span class="macro-label">Fat</span>
            </div>
        </div>
    </div>
    """
    st.markdown(html_content, unsafe_allow_html=True)

def display_health_bar(score: int):
    """Displays the health score progress bar"""
    if score is None: score = 0
    
    if score >= 80:
        color = "#10b981"
        text = "Excellent"
        icon = "🌟"
    elif score >= 60:
        color = "#f59e0b"
        text = "Good"
        icon = "👍"
    elif score >= 40:
        color = "#f97316"
        text = "Fair"
        icon = "⚠️"
    else:
        color = "#ef4444"
        text = "Poor"
        icon = "🛑"

    html_content = f"""
    <div class="glass-card">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.8rem;">
            <div style="display: flex; align-items: center; gap: 0.5rem;">
                <span style="font-size: 1.2rem;">🎯</span>
                <span style="font-weight: 700; font-size: 1.1rem;" class="macro-value">Health Score:</span>
            </div>
            <div style="display: flex; align-items: center; gap: 1rem;">
                <span style="font-size: 1.5rem; font-weight: 800; color: {color};">{score}/100</span>
                <span style="background: {color}; color: white; padding: 4px 12px; border-radius: 12px; font-weight: 600; font-size: 0.9rem;">{icon} {text}</span>
            </div>
        </div>
        <div style="width: 100%; background: rgba(128,128,128,0.1); height: 12px; border-radius: 6px; overflow: hidden;">
            <div style="width: {score}%; background: {color}; height: 100%; border-radius: 6px; transition: width 1s ease;"></div>
        </div>
    </div>
    """
    st.markdown(html_content, unsafe_allow_html=True)

def display_metrics_footer(tokens, time_sec, tps):
    """Displays the usage stats"""
    st.markdown(f"""
    <div style="display: flex; justify-content: center; gap: 2rem; padding: 1rem; margin-top: 3rem; opacity: 0.6; color: inherit;">
        <span style="font-size: 0.85rem;">⚡ <b>{tokens}</b> Tokens</span>
        <span style="font-size: 0.85rem;">⏱️ <b>{time_sec:.2f}s</b> Response</span>
    </div>
    """, unsafe_allow_html=True)

def format_analysis_report(data: dict) -> str:
    """Generates a clean markdown report from the structured JSON data"""
    if not data:
        return "No analysis data available."
        
    dish = data.get('dish_name', 'Unknown Dish')
    insights = data.get('health_insights', [])
    allergens = data.get('allergens', [])
    dietary = data.get('dietary', {})
    
    # Format lists
    dietary_list = [k.replace('_', ' ').title() for k, v in dietary.items() if v]
    dietary_str = ", ".join(dietary_list) if dietary_list else "Standard Diet"
    
    insights_str = ""
    for insight in insights:
        insights_str += f"- {insight}\n"
    
    allergens_str = ", ".join(allergens) if allergens else "None detected"

    return f"""
### 🍽️ {dish}

**🎯 Health Score:** {data.get('health_score', 0)}/100

**💡 Health Insights:**
{insights_str}

**⚠️ Allergens:**
{allergens_str}

**✅ Dietary Tags:**
{dietary_str}

**📊 Nutritional Values (per 100g):**
- **Calories:** {data.get('calories', 0)} kcal
- **Protein:** {data.get('protein', 0)}g
- **Carbs:** {data.get('carbs', 0)}g
- **Fat:** {data.get('fat', 0)}g
- **Fiber:** {data.get('fiber', 0)}g
- **Sugar:** {data.get('sugar', 0)}g
"""
