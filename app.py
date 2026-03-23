import io

import gspread
import pandas as pd
import streamlit as st
from fpdf import FPDF
from geopy.geocoders import Nominatim
from langchain_core.messages import HumanMessage
from pypdf import PdfReader

from agent import get_agent

# 1. Page Configuration
st.set_page_config(page_title="Captain's Log", page_icon="🖖", layout="wide")

# --- CUSTOM STYLING (BACKGROUND & FONT) ---
page_style = """
<style>
# @import url('https://fonts.googleapis.com/css2?family=Bruno+Ace+SC&display=swap');

# * {
#     font-family: 'Bruno Ace SC', sans-serif !important;
# }

[data-testid="stAppViewContainer"] {
    background-color: #EBF7F3;
}

[data-testid="stHeader"] {
    background: rgba(0,0,0,0);
}
</style>
"""
st.markdown(page_style, unsafe_allow_html=True)
# ----------------------------------

# --- STATE MANAGEMENT ---
if "messages" not in st.session_state:
    st.session_state["messages"] = []
if "last_itinerary" not in st.session_state:
    st.session_state["last_itinerary"] = "Your trip details will appear here..."

# THE FIX: Separate the Base Data from the Live Data
if "base_expense_data" not in st.session_state:
    st.session_state.base_expense_data = pd.DataFrame(
        [
            {
                "Date": "",
                "Time": "",
                "Activity": "Sample Flight",
                "Cost": 150.00,
                "Link": "https://www.ryanair.com",
                "Notes": "Flight to Fuerteventura",
            }
        ]
    )
if "live_expense_data" not in st.session_state:
    st.session_state.live_expense_data = st.session_state.base_expense_data.copy()

# --- SIDEBAR (Settings & Preferences) ---
with st.sidebar:
    st.title("🖖 Captain's Log")
    st.caption("powered by Gemini 2.5 Flash")
    st.markdown("---")
    st.subheader("📄 Upload Documents")
    uploaded_file = st.file_uploader("Drop booking confirmation (PDF)", type=["pdf"])

    if uploaded_file is not None:
        try:
            reader = PdfReader(uploaded_file)
            extracted_text = ""
            for page in reader.pages:
                extracted_text += page.extract_text() + "\n"

            st.session_state["pdf_context"] = extracted_text
            st.success("Document loaded into Agent memory!")
        except Exception as e:
            st.error(f"Could not read PDF: {e}")
    else:
        st.session_state["pdf_context"] = ""

    st.subheader("⚙️ Preferences")
    currency = st.selectbox("Currency", ["EUR (€)", "USD ($)", "GBP (£)"])
    temp_scale = st.radio("Temperature", ["Celsius (°C)", "Fahrenheit (°F)"])

    st.markdown("---")
    st.subheader("🔌 Integrations")
    if st.button("Connect Google Sheets"):
        st.toast("Connecting to Google Drive... (Demo)")

    st.markdown("---")
    if st.button("Clear Chat & Reset"):
        st.session_state["messages"] = []
        st.session_state["last_itinerary"] = "Your trip details will appear here..."

        # Reset both data streams safely
        reset_df = pd.DataFrame(
            [
                {
                    "Date": "",
                    "Time": "",
                    "Activity": "Sample Flight",
                    "Cost": 150.00,
                    "Link": "https://www.ryanair.com",
                    "Notes": "Flight to Fuerteventura",
                }
            ]
        )
        st.session_state.base_expense_data = reset_df
        st.session_state.live_expense_data = reset_df

        # WIPE THE WIDGET MEMORY SO IT REDRAWS
        if "expense_editor" in st.session_state:
            del st.session_state["expense_editor"]

        st.rerun()

# --- MAIN LAYOUT (2 Columns) ---
st.title("🖖 Captain's Log Command Center")

col_chat, col_dashboard = st.columns([1, 1.5], gap="large")

# ==============================
# LEFT COLUMN: Chat Interface
# ==============================
with col_chat:
    chat_container = st.container(height=500)

    with chat_container:
        for msg in st.session_state.messages:
            if msg["role"] == "user":
                st.chat_message("user").write(msg["content"])
            else:
                st.chat_message("assistant").write(msg["content"])

    if prompt := st.chat_input("Ex: What time is my flight?"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with chat_container:
            st.chat_message("user").write(prompt)

        with st.spinner("Thinking..."):
            try:
                agent = get_agent()
                system_instructions = f"\n\n[System note: The user prefers prices in {currency} and weather in {temp_scale}. Please format your response accordingly.]"

                if st.session_state.get("pdf_context"):
                    system_instructions += f"\n\n[System note: The user uploaded a booking document. Here is the text from it:\n{st.session_state['pdf_context']}\nUse this exact data to answer questions about their current trip, flights, or expenses.]"

                enhanced_prompt = prompt + system_instructions
                response = agent.invoke(
                    {"messages": [HumanMessage(content=enhanced_prompt)]}
                )
                result = response["messages"][-1].content

                st.session_state.messages.append(
                    {"role": "assistant", "content": result}
                )
                st.session_state["last_itinerary"] = result
                st.rerun()
            except Exception as e:
                st.error(f"Error: {e}")

# ==============================
# RIGHT COLUMN: The Dashboard
# ==============================
with col_dashboard:
    st.subheader("📋 Live Trip Dashboard")

    cur_sym = currency.split("(")[1].replace(")", "")
    tmp_sym = "°C" if "Celsius" in temp_scale else "°F"

    m1, m2, m3 = st.columns(3)
    m1.metric("Est. Flight", f"{cur_sym}0", "-12%")
    m2.metric("Avg. Temp", f"24{tmp_sym}", "Sunny")
    m3.metric("Daily Budget", f"{cur_sym}120", "Moderate")

    st.markdown("---")

    tab1, tab2, tab3 = st.tabs(["📝 Itinerary", "💰 Expenses", "🗺️ Map"])

    with tab1:
        st.info("Latest Agent Response:")
        st.markdown(st.session_state["last_itinerary"])

        if (
            st.session_state["last_itinerary"]
            != "Your trip details will appear here..."
        ):
            pdf = FPDF()
            pdf.add_page()

            # --- HEADER ---
            pdf.set_font("helvetica", style="B", size=16)
            pdf.cell(
                0,
                10,
                text="CaptainsLog: Mission Briefing",
                new_x="LMARGIN",
                new_y="NEXT",
                align="C",
            )
            pdf.ln(10)

            # --- ITINERARY ---
            pdf.set_font("helvetica", style="B", size=14)
            pdf.cell(
                0, 10, text="1. AI Itinerary & Notes", new_x="LMARGIN", new_y="NEXT"
            )
            pdf.set_font("helvetica", size=12)

            raw_text = st.session_state["last_itinerary"]
            if isinstance(raw_text, list):
                clean_text = ""
                for item in raw_text:
                    if isinstance(item, dict) and "text" in item:
                        clean_text += item["text"] + "\n"
                    elif isinstance(item, str):
                        clean_text += item + "\n"
                raw_text = clean_text
            else:
                raw_text = str(raw_text)

            raw_text = raw_text.replace("€", "EUR")
            safe_text = raw_text.encode("latin-1", "replace").decode("latin-1")
            pdf.multi_cell(0, 7, text=safe_text)
            pdf.ln(10)

            # --- BUDGET ---
            pdf.set_font("helvetica", style="B", size=14)
            pdf.cell(0, 10, text="2. Approved Budget", new_x="LMARGIN", new_y="NEXT")
            pdf.set_font("helvetica", size=12)

            df = st.session_state.live_expense_data
            if not df.empty:
                for index, row in df.iterrows():
                    date_time = f"{row.get('Date', '')} {row.get('Time', '')}".strip()
                    row_text = f"- {date_time} | {row.get('Activity', 'Unknown')} - {cur_sym}{row.get('Cost', '0')}"
                    row_text = row_text.replace("€", "EUR").replace("£", "GBP")
                    safe_row_text = row_text.encode("latin-1", "replace").decode(
                        "latin-1"
                    )

                    pdf.cell(0, 8, text=safe_row_text, new_x="LMARGIN", new_y="NEXT")
            else:
                pdf.cell(
                    0, 10, text="No expenses logged yet.", new_x="LMARGIN", new_y="NEXT"
                )

            # --- FINALIZE PDF ---
            pdf_bytes = bytes(pdf.output())

            st.markdown("---")
            st.download_button(
                label="📄 Download Mission Briefing (PDF)",
                data=pdf_bytes,
                file_name="CaptainsLog_Mission_Briefing.pdf",
                mime="application/pdf",
                type="primary",
            )

    with tab2:
        st.write("### 📝 Daily Expense Log")
        st.write("Log your expenses below. Add new rows at the bottom!")

        # Added the specific 'key' so we can force it to reset!
        edited_expenses = st.data_editor(
            st.session_state.base_expense_data,
            key="expense_editor",
            num_rows="dynamic",
            width="stretch",
            column_config={
                "Link": st.column_config.LinkColumn("Link"),
                "Cost": st.column_config.NumberColumn(
                    f"Cost ({cur_sym})", min_value=0.0, format="%.2f"
                ),
            },
        )

        st.session_state.live_expense_data = edited_expenses

        st.markdown("---")
        st.write("### 📊 Budget Summary")

        df_for_summary = st.session_state.live_expense_data.copy()

        if not df_for_summary.empty:
            df_for_summary["Activity"] = (
                df_for_summary["Activity"]
                .replace("", "Unnamed Activity")
                .fillna("Unnamed Activity")
            )
            df_for_summary["Cost"] = pd.to_numeric(
                df_for_summary["Cost"], errors="coerce"
            ).fillna(0)
            summary_df = df_for_summary.groupby("Activity")["Cost"].sum().reset_index()
            grand_total = summary_df["Cost"].sum()
        else:
            summary_df = pd.DataFrame({"Activity": ["No Data"], "Cost": [0.0]})
            grand_total = 0.0

        col_table, col_chart = st.columns([1, 1.5])

        with col_table:
            st.dataframe(
                summary_df,
                hide_index=True,
                width="stretch",
                column_config={
                    "Cost": st.column_config.NumberColumn(
                        f"Total ({cur_sym})", format="%.2f"
                    )
                },
            )
            st.markdown(f"**Grand Total: {cur_sym}{grand_total:.2f}**")

        with col_chart:
            st.bar_chart(summary_df.set_index("Activity"), y="Cost")

        # --- TWO-WAY GOOGLE SHEETS SYNC ---
        st.markdown("---")
        st.write("### ☁️ Cloud Sync")

        col_load, col_sync = st.columns(2)

        with col_load:
            if st.button("📥 Load from Google Sheets", use_container_width=True):
                try:
                    gc = gspread.service_account(filename="credentials.json")
                    sh = gc.open("MyTrip_Budget_2026")
                    worksheet = sh.sheet1

                    cloud_data = worksheet.get_all_records()

                    if cloud_data:
                        df = pd.DataFrame(cloud_data)

                        # THE DATA CLEANER: Force Gspread strings into safe numbers
                        if "Cost" in df.columns:
                            df["Cost"] = pd.to_numeric(
                                df["Cost"], errors="coerce"
                            ).fillna(0.0)

                        st.session_state.base_expense_data = df
                        st.session_state.live_expense_data = df.copy()

                        # THE CACHE WIPE: Force Streamlit to redraw the table visually
                        if "expense_editor" in st.session_state:
                            del st.session_state["expense_editor"]

                        st.success("Data successfully loaded from the cloud!")
                        st.rerun()
                    else:
                        st.info("The Google Sheet is currently empty.")
                except Exception as e:
                    st.error(f"Failed to load data. Error details: {e}")

        with col_sync:
            num_rows = len(st.session_state.live_expense_data)
            if st.button(
                "💾 Push to Google Sheets", type="primary", use_container_width=True
            ):
                try:
                    gc = gspread.service_account(filename="credentials.json")
                    sh = gc.open("MyTrip_Budget_2026")
                    worksheet = sh.sheet1

                    data_to_upload = [
                        st.session_state.live_expense_data.columns.values.tolist()
                    ] + st.session_state.live_expense_data.values.tolist()

                    worksheet.clear()
                    worksheet.update(values=data_to_upload, range_name="A1")

                    st.success(f"Successfully pushed {num_rows} rows to the cloud!")
                    st.balloons()
                except Exception as e:
                    st.error(f"Sync failed. Error details: {e}")

    with tab3:
        st.write("### 🗺️ Destination Map")

        default_dest = st.session_state.get("destination", "Paris")
        dest = st.text_input("Enter destination to map:", value=default_dest)

        if dest:
            st.session_state["destination"] = dest

            try:
                geolocator = Nominatim(user_agent="travel_genie_app")
                location = geolocator.geocode(dest)

                if location:
                    st.success(f"Found: {location.address}")
                    map_data = pd.DataFrame(
                        {"lat": [location.latitude], "lon": [location.longitude]}
                    )
                    st.map(map_data, zoom=10)
                else:
                    st.error("Could not find that location. Try a different name.")
            except Exception as e:
                st.warning("Map service is currently busy. Try again in a moment.")
