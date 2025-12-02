import streamlit as st
import html
from datetime import datetime
from dotenv import load_dotenv
from scripts import supabase_client 
from scripts.menu import menu

# The environment vars are getting loaded for the whole process of the app
load_dotenv()

client = supabase_client.get_client()

current_page = "main_page"

# -----------------------------------------
# Below starts the UI of the app
# -----------------------------------------
def delete_questionnaire(questionnaire_id: str):
    response = client.table("questionnaires").delete().eq("id", questionnaire_id).execute()

    if len(response.data) == 0:
        st.write("Error deleting questionnaire:", response.data)  
    else:
        st.write("Questionnaire deleted successfully")

if __name__ == "__main__":
    client = supabase_client.get_client()
    menu(client)
    st.session_state.last_page = current_page

    st.title("Welcome to TAMQuest")

    st.write("## Available questionnaires")

    qs = client.table("questionnaires").select("*").execute()

    if len(qs.data) == 0:
        st.write("There are no questionnaires available for response")
    else:
        questionnire_list = qs.data

        for item in questionnire_list:
            title_safe = html.escape(item['title'])
            details_safe = html.escape(item['details'])

            dt = datetime.fromisoformat(item["created_at"])
            formatted_time = dt.strftime("%Y-%m-%d %H:%M:%S %Z")

            questionnaire_card = st.container()

            if st.session_state.role == 'admin':
        
                col1, col2, col3 = st.columns([5,1,1])
        
                with col1:
                    st.markdown(f"""
                        <article style='
                            border: 4px solid #000000; 
                            background-color: #E4EDA6;
                            padding:8px;
                            border-radius:8px;
                            margin-bottom:0px;
                            text-align: center;'>
                            <h3>{title_safe}</h3>
                            <p style='font-size:18px;'>{details_safe}</p>
                            <small>Created at: {formatted_time}</small><br>
                        </article>
                        """, unsafe_allow_html=True)
                with col2:
                    respond_key = f"respond_{item['id']}"
                    if st.button("Respond", key=respond_key):
                        pass
            
                with col3:
                    delete_key = f"delete_{item['id']}"
                    if st.button("Delete", key=delete_key):
                        delete_questionnaire(item['id'])
        
                st.write("\n")
            
            else:
                col1, col2 = st.columns([3,1])
        
                with col1:
                    st.markdown(f"""
                        <article style='
                            border: 4px solid #000000; 
                            background-color: #E4EDA6;
                            padding:8px;
                            border-radius:8px;
                            margin-bottom:0px;
                            text-align: center;'>
                            <h3>{title_safe}</h3>
                            <p style='font-size:18px;'>{details_safe}</p>
                            <small>Created at: {formatted_time}</small><br>
                        </article>
                        """, unsafe_allow_html=True)
                with col2:
                    respond_key = f"respond_{item['id']}"
                    if st.button("Respond", key=respond_key):
                        st.write("respond")
        
                st.write("\n")