import streamlit as st
import html
import re
from datetime import date, datetime

from database.responses import Responses

from utils.generate_questionnaires import (
    generate_tam_questions,
    generate_additional_tam_questions
)
from utils.logger_config import logger
from utils import supabase_client

client = supabase_client.get_client()
responses_repo = Responses(client)

DEFAULT_LIKERT_SCALE = [
    "Strongly disagree",
    "Disagree",
    "Neutral",
    "Agree",
    "Strongly agree"
]


'''
The format_time function normalizes and
formats a ISO-8601 timestamp into
a readable date/time string
'''


def format_time(timestamp: str):
    timestamp = re.sub(
            r"\.(\d+)(?=[+-])",
            lambda m: "." + (m.group(1) + "000000")[:6],
            timestamp
    )
    dt = datetime.fromisoformat(timestamp)
    return dt.strftime("%Y-%m-%d %H:%M:%S %Z")


'''
The create_questionnaire_card function retrieves a questionnaire's
data as an argument and presents it in a card that has been
styled by HTML/CSS.

The card is being rendered directly into the app's UI.
'''


def create_questionnaire_card(questionnaire: dict):

    title_safe = html.escape(questionnaire['title'])

    if questionnaire["details"] is None:
        details_safe = html.escape("No details were provided.")
    else:
        details_safe = html.escape(questionnaire['details'])

    formatted_time = format_time(questionnaire["created_at"])

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


'''
The create_response_card function retrieves the data
of a response and its respondent and presents it in a card
that has been styled by HTML/CSS.

The card is being rendered directly into the app's UI.
'''


def create_response_card(
        response: dict,
        response_profile_name: str | None = None
):

    title_safe = html.escape(response['questionnaires']['title'])

    formatted_time = format_time(response["questionnaires"]["created_at"])

    response_owner = None

    if "profiles" in response and response["profiles"]:
        response_owner = response["profiles"]["full_name"]
    else:
        response_owner = response_profile_name or "Unknown"

    st.markdown(
        f"""
        <article style="
            border: 4px solid #000000;
            background-color: #E4EDA6;
            padding: 8px;
            border-radius: 8px;
            margin-bottom: 12px;
            text-align: center;
        ">
            <p style="font-size:18px; margin-top:4px; margin-bottom:0px;">
                Response for
            </p>
            <h3 style="margin-bottom:0px;">{title_safe}</h3>
            <small>Submitted at: {formatted_time}</small><br>
            <small>By: {response_owner}</small><br>
        </article>
        """,
        unsafe_allow_html=True,
    )


'''
The create_profile_card function retrieves a profile's data as an argument
and presents it in a card that has been styled by HTML/CSS.

The card is being rendered directly into the app's UI.
'''


def create_profile_card(profile: dict):
    user_name = html.escape(profile["full_name"])
    user_birthdate = html.escape(profile["birthdate"])
    user_city = html.escape(profile["city"])
    user_country = html.escape(profile["country"])

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


'''
The set_naswer_layout renders a response answer layout
directly into the app's UI by displaying the number
and the text of its corresponding question and the selected
likert scale answer's label.
'''


def set_answer_layout(answer: dict):
    st.markdown("</br></br>", unsafe_allow_html=True)
    st.markdown(
        (
            "<h5 style='margin-bottom:2px'>"
            f"{answer['questions']['position']}."
            f"{answer['questions']['question_text']}"
            "</h5>"
        ),
        unsafe_allow_html=True
    )
    st.markdown(
        (
            "<h5 style='margin-bottom:'>"
            f"Answer: {answer['likert_scale_options']['label']}"
            "</h5"
        ),
        unsafe_allow_html=True
    )


'''
The set_response_ui function sets the UI form that
a user can respond to the questions of a questionnaire.

If there is a draft of a user's response, a list of the
draft's answers gets inserted so the corresponding
radio buttons will be already selected.
'''


def set_response_ui(
    questions,
    likert_scale_options: list,
    draft_answers: list | None = None
):

    if draft_answers is None:
        for question_index, question in enumerate(questions.data, start=1):
            question_key = f"q{question_index}_answer"

            st.markdown("</br></br>", unsafe_allow_html=True)
            st.markdown(
                (
                    "<h5 style='margin-bottom:-10px'>"
                    f"{question_index}. {question['question_text']}"
                    "</h5>"
                ),
                unsafe_allow_html=True
            )

            st.radio(
                label=question['question_text'],
                options=[
                    option["label"]
                    for option in likert_scale_options.data
                ],
                key=question_key,
                horizontal=True,
                index=None,
                label_visibility="collapsed",
            )
        st.markdown("</br></br>", unsafe_allow_html=True)

    else:
        # check which selected_option_value field of draft_answers
        # matches a scale of LIKERT SCALE list
        indexes = [
            next(
                (
                    item["value"] - 1
                    for item in likert_scale_options.data
                    if item["id"] == ans["selected_option"]
                ),
                None
            )
            for ans in draft_answers.data
        ]
        for question_index, question in enumerate(questions.data, start=1):
            question_key = f"q{question_index}_answer"
            st.markdown("</br></br>", unsafe_allow_html=True)
            st.markdown(
                (
                    "<h5 style='margin-bottom:-10px'>"
                    f"{question_index}. {question['question_text']}"
                    "</h5>"
                ),
                unsafe_allow_html=True
            )
            st.radio(
                label=question['question_text'],
                options=[
                    option["label"]
                    for option in likert_scale_options.data
                ],
                key=question_key,
                horizontal=True,
                index=indexes[question_index - 1],
                label_visibility="collapsed"
            )
        st.markdown("</br></br>", unsafe_allow_html=True)


'''
The function preview_questionnaire prints into the app's UI
all the TAM essential questions, all the additional questions
of the selected by the user categories and the user's custom questions
for the questionnaire.
'''


def preview_questionnaire(app_name: str, custom_questions: dict):
    if app_name.strip() == "":
        st.warning("Please enter the app's name.")
        return

    questions = generate_tam_questions(app_name)

    if (
        "add_questions" in st.session_state
        and st.session_state["add_questions"]
    ):
        questions.update(generate_additional_tam_questions(app_name))

    for category, question in custom_questions.items():
        if category in questions.keys():
            for q in question:
                questions[category].append(q[0])

    for category, questions in questions.items():
        st.markdown(f"#### **{category}**" + "\n".join(
            f"\n{i+1} - {q}"
            for i, q in enumerate(questions)
        ))


'''
The create_profile_form function renders the form with the profile fields
so the user can create his own profile or update it.
'''


def create_profile_form(mode: str):
    username = st.text_input("Your name", key=f"{mode}_username")
    birthdate = st.date_input(
        "Birthdate",
        key=f"{mode}_birthdate",
        max_value=date.today(),
        min_value=date(1900, 1, 1))
    city = st.text_input("Your city", key=f"{mode}_user_city")
    country = st.text_input("Your country", key=f"{mode}_user_country")
    return [username, birthdate.isoformat(), city, country]


'''
The create_responses_management_ui function render the response card
and the interaction keys for the response argument.
'''


def create_responses_management_ui(
    response: dict,
    redirection_button: str,
    callback,
    response_profile_name: str | None = None
):

    col1, col2, col3 = st.columns([3, 0.4, 0.5])

    with col1:
        create_response_card(response, response_profile_name)

    with col2:
        respond_key = f"{redirection_button}_{response['id']}"
        if st.button(redirection_button, key=respond_key):
            callback(response["id"])

    with col3:
        delete_key = f"delete_{response['id']}"
        if st.button("Delete", key=delete_key):
            delete_response = None
            try:
                delete_response = (
                    responses_repo.delete_response_by_id(
                        response['id']
                        )
                    )
                st.rerun()
            except RuntimeError as e:
                logger.error(f"Database error: {e}")

            if delete_response is None:
                st.error("Error during the response's deletion")
            else:
                st.rerun()


'''
The likert_scale_customization_ui renders a form which allows
the user to customize the likert scale that will be used for
the questionnaire that he creates.

The form allows the user to increase or decrease the number of
the likert scale's levels and also provides the choice of a
default likert scale usage.
'''


def likert_scale_customization_ui():
    ls_customization_container = st.container(border=True)

    with ls_customization_container:
        col_1, col_2, col_3, col_4 = st.columns([1, 1, 1, 1])

        with col_1:
            st.markdown(
                """
                <h3 style='margin-bottom:-30px; padding-top:2px;
                vertical-align:top; display:block;'>
                    Likert scale
                </h3>
                """,
                unsafe_allow_html=True,
            )

        with col_2:
            if st.button("Increment levels"):
                if st.session_state["questionnaire_likert_scale_levels"] == 7:
                    pass
                else:
                    st.session_state["questionnaire_likert_scale_levels"] += 1

        with col_3:
            if st.button("Decrement levels"):
                if st.session_state["questionnaire_likert_scale_levels"] == 2:
                    pass
                else:
                    st.session_state["questionnaire_likert_scale_levels"] -= 1

        with col_4:
            if st.button("Use default scale"):
                st.session_state["questionnaire_likert_scale_levels"] = 5

                for i in range(
                    st.session_state["questionnaire_likert_scale_levels"]
                ):
                    st.session_state[
                        f"likert_scale_lvl_{i+1}"
                    ] = DEFAULT_LIKERT_SCALE[i]

        for i in range(st.session_state["questionnaire_likert_scale_levels"]):
            st.text_input(f"Level {i+1}", key=f"likert_scale_lvl_{i+1}")
