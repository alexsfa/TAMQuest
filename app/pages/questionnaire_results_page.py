import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

from database.questionnaires import Questionnaires
from database.likert_scales import Likert_scales
from database.likert_scale_options import Likert_scale_options
from database.questions import Questions
from database.responses import Responses
from database.answers import Answers

from utils import supabase_client 
from utils.menu import menu
from utils.questionnaire_scoring import mean_score

client = supabase_client.get_client()

questionnaires_repo = Questionnaires(client)
responses_repo = Responses(client)
questions_repo = Questions(client)
answers_repo = Answers(client)
likert_scales_repo = Likert_scales(client)
likert_scale_options_repo = Likert_scale_options(client)

if __name__ == "__main__":
    
    menu(client)

    questionnaire_info = questionnaires_repo.get_questionnaire_by_id(st.session_state["current_questionnaire_id"])

    likert_scale_info = likert_scales_repo.get_likert_scale_by_questionnaire_id(st.session_state["current_questionnaire_id"])

    likert_scale_options = likert_scale_options_repo.get_options_by_likert_scale_id(likert_scale_info.data[0]["id"])

    questions_info = questions_repo.get_questions_by_questionnaire_id(st.session_state["current_questionnaire_id"])

    responses_info = responses_repo.get_all_responses_by_questionnaire_id(st.session_state["current_questionnaire_id"])


    #############################

    st.write(f"## Results for {questionnaire_info.data[0]['title']}")

    unique_categories = list({item["category"] for item in questions_info.data})

    score = []

    answers = answers_repo.get_answers_by_questionnaire_id(st.session_state["current_questionnaire_id"])
    
    total_tam_score = mean_score(unique_categories, answers.data)

    st.write(f"### Total TAM score: {total_tam_score}")

    st.divider()




