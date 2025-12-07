import streamlit as st
from pprint import pprint, pformat
from scripts.generate_questionnaires import generate_tam_questions, generate_additional_tam_questions,ESSENTIAL_TAM_QUESTIONS, ADDITIONAL_TAM_QUESTIONS
from scripts import supabase_client 
from scripts.menu import menu
import uuid
import html, re
from datetime import datetime
from app import redirect_to_respond_page

current_page = "admin_page"

client = supabase_client.get_client()

additional_question_configs = [
    ("Technology support questions", "Technology Support"),
    ("User satisfaction questions", "User Satisfaction"),
    ("Computer anxiety questions", "Computer Anxiety"),
    ("Computer self-efficacy questions", "Computer Self-Efficacy"),
    ("Compatibility questions", "Compatibility"),
    ("Information quality questions", "Information Quality"),
    ("System quality questions", "System Quality"),
    ("Risk questions", "Risk"),
    ("Subjective norm questions", "Subjective Norm"),
    ("Behavioral control questions", "Behavioral Control"),
    ("Trust questions", "Trust"),
]

radio_options = ["Yes", "No"]

def init_questionnaire_ui_state():
    if "create_questionnaire" not in st.session_state:
        st.session_state.create_questionnaire = False

    if "add_questions" not in st.session_state:
        st.session_state.add_questions = False

    if "show_preview" not in st.session_state:
        st.session_state.show_preview = False

def restart_questionnaire_ui_state():
    if st.session_state.create_questionnaire:
        st.session_state.create_questionnaire = False

    if st.session_state.add_questions:
        st.session_state.add_questions = False

    if st.session_state.show_preview:
        st.session_state.show_preview = False
        

def preview_questionnaire():
    if st.session_state.get("app_name").strip() == "":
        st.warning("Please enter an app name.")
        return

    questions = generate_tam_questions(ESSENTIAL_TAM_QUESTIONS, st.session_state.app_name)

    if "add_questions" in st.session_state and st.session_state["add_questions"]:
        questions.update(generate_additional_tam_questions(ADDITIONAL_TAM_QUESTIONS, st.session_state.app_name))

    for category, questions in questions.items():
        st.markdown(f"### **{category}**" + "\n".join(f"\n{i+1} - {q}" for i, q in enumerate(questions)))

def delete_questionnaire(questionnaire_id: str):
    response = client.table("questionnaires").delete().eq("id", questionnaire_id).execute()

    if len(response.data) == 0:
        return f"Error deleting questionnaire"
    else:
        st.rerun()

def delete_profile(profile_id: str):
    response = client.table("profiles").delete().eq("id", profile_id).execute()

    if len(response.data) == 0:
        return f"Error deleting profile"
    else:
        st.rerun()

def submit_questionnaire():

    if st.session_state.get("app_name").strip() == "":
        st.warning("Please enter an app name.")
        return

    q_details = st.session_state.get("q_details", "")

    if q_details and q_details.strip():
        questionnaire_details = q_details.strip()
    else:
        questionnaire_details = None

    questionnaire_insert = client.table("questionnaires").insert({
        "title": f"TAM Questionnaire for {st.session_state.app_name}",
        "details": questionnaire_details,
        "created_by": st.session_state["user_id"]
    }).execute()

    if not questionnaire_insert.data:
        raise Exception("Failed to create questionnaire")

    questionnaire_id = questionnaire_insert.data[0]["id"]

    questions = generate_tam_questions(ESSENTIAL_TAM_QUESTIONS, st.session_state.app_name)

    if "add_questions" in st.session_state and st.session_state["add_questions"]:
        questions.update(generate_additional_tam_questions(ADDITIONAL_TAM_QUESTIONS, st.session_state.app_name))

    position = 1

    for category, qs in questions.items():
        for question_text in qs:
            question_insert = client.table("questions").insert({
                "questionnaire_id": questionnaire_id,
                "question_text": question_text,
                "position": position
            }).execute()

            position += 1

        if not question_insert.data:
            raise Exception("Failed to insert question.")

    st.success("Your questionnaire has been submitted!")
    
    
if __name__ == "__main__":

    client = supabase_client.get_client()
    menu(client)

    init_questionnaire_ui_state()

    if st.session_state.last_page != current_page:
        restart_questionnaire_ui_state()
        st.session_state.last_page = current_page
    
    st.title("Welcome to the admin page") 

    if st.button("Create new questionnaire"):
        st.session_state.create_questionnaire = not st.session_state.create_questionnaire

    if st.session_state.create_questionnaire:
        st.text_input("The name of the app", key="app_name")

        st.text_area("Enter details about the questionnaire", height=150, key="q_details")

        if "add_questions" not in st.session_state:
            st.session_state.add_questions = False

        if "show_preview" not in st.session_state:
            st.session_state.show_preview = False

        button_1, button_2 = st.columns(2)
        with button_1:
            if st.button("Add additional questions"):
                st.session_state.add_questions = not st.session_state.add_questions

        with button_2:
            if st.button("Preview Questionnaire"):
                st.session_state.show_preview = not st.session_state.show_preview

        additional_questions_container = st.container()
 
        with additional_questions_container:
            if st.session_state.add_questions:
                cols = st.columns(2)

                for i, (label, key) in enumerate(additional_question_configs):
                    col = cols[i % 2]
                    col.checkbox(label, key=key)
            else:
                additional_questions_container.empty()

        questionnaire_preview_container = st.container()

        with questionnaire_preview_container:
            if st.session_state.show_preview:
                preview_questionnaire()

        if st.button("Submit Questionnaire"):
            try:
                submit_questionnaire()
                restart_questionnaire_ui_state()
            except Exception as e:
                st.error(f"Failed to create questionnaire: {e}")

    st.divider()
    st.write("## Available questionnaires")

    qs = client.table("questionnaires").select(
        f"""
        *,
        responses:responses!left(
            id,
            user_id,
            questionnaire_id
        )
        """
        + f"responses(user_id.eq.{st.session_state['user_id']})").order("created_at", desc=True).execute()

    if len(qs.data) == 0:
        st.write("There are no questionnaires available for response")
    else:
        questionnaire_list = qs.data

        for item in questionnaire_list:
            title_safe = html.escape(item['title'])

            if item['details'] is None:
                details_safe = "No details were provided."
            else: 
                details_safe = html.escape(item['details'])

            raw = item["created_at"]
            raw = re.sub(
                r"\.(\d+)(?=[+-])",
                lambda m: "." + (m.group(1) + "000000")[:6],
                raw
            )
            dt = datetime.fromisoformat(raw)
            formatted_time = dt.strftime("%Y-%m-%d %H:%M:%S %Z")

            questionnaire_card = st.container()

            col1, col2, col3 = st.columns([5,1,1])
        
            with col1:
                st.markdown(f"""
                    <article style='
                        border: 4px solid #000000; 
                        background-color: #E4EDA6;
                        padding:8px;
                        border-radius:8px;
                        margin-bottom:12px;
                        text-align: center;'>
                        <h3>{title_safe}</h3>
                        <p style='font-size:18px;'>{details_safe}</p>
                        <small>Created at: {formatted_time}</small><br>
                    </article>
                    """, unsafe_allow_html=True)

            if len(item["responses"]) == 0:
                with col2:
                    respond_key = f"respond_{item['id']}"
                    if st.button("Respond", key=respond_key):
                        redirect_to_respond_page(item['id'])

                message_box = st.empty()

                with col3:
                    delete_key = f"delete_{item['id']}"
                    if st.button("Delete", key=delete_key):
                        msg = delete_questionnaire(item['id'])
                        message_box.error(msg)
        
                    st.write("\n")
            else:
                message_box = st.empty()

                with col2:
                    delete_key = f"delete_{item['id']}"
                    if st.button("Delete", key=delete_key):
                        msg = delete_questionnaire(item['id'])
                        message_box.error(msg)
        
                st.write("\n")

    st.divider()
    st.write("## Profiles' list")

    profiles = client.table("profiles").select("*").execute()

    if len(profiles.data) == 0:
        st.write("There are not any users yet.")
    else:
        cols = st.columns(3)
        for i, profile in enumerate(profiles.data):
            user_name = html.escape(profile["full_name"])
            user_birthdate = html.escape(profile["birthdate"])
            user_city = html.escape(profile["city"])
            user_country = html.escape(profile["country"])

            col = cols[i % 3]
            with col:
                st.markdown(f"""
                    <article style='
                        border: 4px solid #000000; 
                        background-color: #B2FBE6;
                        border-radius:8px;
                        padding-top: 12px;
                        margin-bottom:12px;
                        text-align: center;'>
                        <p style='font-size:18px;'>{user_name}</p>
                        <p style='font-size:18px;'>{user_birthdate}</p>
                        <p style='font-size:18px;'>{user_country}, {user_city}</p>
                    </article>
                    """, unsafe_allow_html=True)

                delete_key = f"delete_{profile['id']}"
                if st.button("Delete", key=delete_key):
                    msg = delete_profile(profile['id'])
                    message_box.error(msg)

                st.markdown("</div>", unsafe_allow_html=True)

            message_box = st.empty()







