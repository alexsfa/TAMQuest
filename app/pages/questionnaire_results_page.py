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
from utils.questionnaire_scoring import (tam_score, count_category_answers_by_label, construct_scores, pivot_constructs, calc_spearman_correlation, 
plot_spearman_by_response, plot_pvalue_rows)

client = supabase_client.get_client()

questionnaires_repo = Questionnaires(client)
responses_repo = Responses(client)
questions_repo = Questions(client)
answers_repo = Answers(client)
likert_scales_repo = Likert_scales(client)
likert_scale_options_repo = Likert_scale_options(client)

basic_constructs = ["Perceived Usefulness", "Perceived Ease of Use", "Attitude", "Behavioral Intention"]

if __name__ == "__main__":
    
    menu(client)

    questionnaire_info = questionnaires_repo.get_questionnaire_by_id(st.session_state["current_questionnaire_id"])

    likert_scale_info = likert_scales_repo.get_likert_scale_by_questionnaire_id(st.session_state["current_questionnaire_id"])

    likert_scale_options = likert_scale_options_repo.get_options_by_likert_scale_id(likert_scale_info.data[0]["id"])

    questions_info = questions_repo.get_questions_by_questionnaire_id(st.session_state["current_questionnaire_id"])

    answers = answers_repo.get_submitted_answers_by_questionnaire_id(st.session_state["current_questionnaire_id"])

    unique_constructs = list({item["questions"]["category"] for item in answers.data})

    secondary_constructs = [construct for construct in unique_constructs if construct not in basic_constructs]

    unique_responses = {item["response_id"] for item in answers.data}
    count_of_responses = len(unique_responses)

    st.write(f"## Results for {questionnaire_info.data[0]['title']}")

    st.write(f"#### The TAM constructs which have been examined are the following:")
    construct_cols = st.columns(3)
    for i, construct in enumerate(unique_constructs):
        construct_cols[i % 3].write(f"##### {construct}")
    st.write("\n")
    st.write(f"#### There are {count_of_responses} responses for this questionnaire.")
    st.write(f"#### Total of answers submitted are {len(answers.data)}.")

    st.divider()

    for category in basic_constructs:

        automated_questions_answers, custom_questions_answers = [], []

        for item in answers.data:
            if item["questions"]["category"] == category:
                (custom_questions_answers if item["questions"]["is_custom"] else automated_questions_answers).append(item)

        has_custom = len(custom_questions_answers) > 0

        st.write(f"## {category}")
        st.write("### Automated questions")

        count_category_answers_by_label(automated_questions_answers, f"Questions score contribution for {category} automated questions", likert_scale_options.data)

        question_texts = list({item["questions"]["question_text"] for item in custom_questions_answers})
        
        if has_custom:
            st.write("### Custom questions")
            for question_text in question_texts:
                count_category_answers_by_label(custom_questions_answers, f"Score contribution for '{question_text}' question", likert_scale_options.data)


    st.write(f"# Total TAM score: {tam_score(unique_constructs, answers.data, likert_scale_options.data, basic_constructs):.3f}")

    st.divider()

    if len(secondary_constructs) != 0 :

        st.title("Secondary constructs analysis")
        
       
        for construct in secondary_constructs:
            automated_questions_answers, custom_questions_answers = [], []

            for item in answers.data:
                if item["questions"]["category"] == construct:
                    (custom_questions_answers if item["questions"]["is_custom"] else automated_questions_answers).append(item)

            has_custom = len(custom_questions_answers) > 0

            st.write(f"## {construct}")
            st.write("### Automated questions")

            count_category_answers_by_label(automated_questions_answers, f"Answers for {construct} automated questions", likert_scale_options.data)

            question_texts = list({item["questions"]["question_text"] for item in custom_questions_answers})
        
            if has_custom:
                st.write("### Custom questions")
                for question_text in question_texts:
                    count_category_answers_by_label(custom_questions_answers, f"Answers for '{question_text}' question", likert_scale_options.data)

        st.divider()

    unique_responses = {item["response_id"] for item in answers.data}
    count = len(unique_responses)

    if count_of_responses < 10:
        st.write("#### There are not enough responses for a valid spearman analysis.")
    else:

        st.write("### Spearman statistic analysis for TAM's basic constructs")
    
        responses_category_means = responses_repo.get_all_responses_category_means(st.session_state["current_questionnaire_id"])

        basic_category_means = pivot_constructs(responses_category_means.data)

        basic_constructs_spearman_results = []
        basic_constructs_spearman_results.append(calc_spearman_correlation(basic_category_means, "Attitude", "Behavioral Intention"))
        basic_constructs_spearman_results.append(calc_spearman_correlation(basic_category_means, "Perceived Usefulness", "Attitude"))
        basic_constructs_spearman_results.append(calc_spearman_correlation(basic_category_means, "Perceived Ease of Use", "Attitude"))

        final_df = pd.concat(basic_constructs_spearman_results, ignore_index=True)

        plot_spearman_by_response(final_df)

        plot_pvalue_rows(final_df)

        pu_constructs = ["Subjective Norm", "Information Quality", "Compatibility", "Trust", "Risk"]
        peou_constructs = ["Technology Support" ,"Computer Self-Efficacy", "Computer Anxiety", "User Satisfaction", "System Quality", "Behavioral Control"]

        available_pu_constructs = [construct for construct in unique_constructs if construct in pu_constructs]
        available_peou_constructs = [construct for construct in unique_constructs if construct in peou_constructs]

        if len(available_pu_constructs) != 0:   
            st.write("### Spearman statistic analysis between PU and secondary constructs")
            pu_spearman_results = []
            for construct in available_pu_constructs:
                pu_spearman_results.append(calc_spearman_correlation(basic_category_means, construct, "Perceived Usefulness"))

            pu_df = pd.concat(pu_spearman_results, ignore_index=True)

            plot_spearman_by_response(pu_df)
            plot_pvalue_rows(pu_df)

        if len(available_peou_constructs) != 0:
            st.write("### Spearman statistic analysis between PEOU and secondary constructs")
            peou_spearman_results = []
            for construct in available_peou_constructs:
                peou_spearman_results.append(calc_spearman_correlation(basic_category_means, construct, "Perceived Ease of Use"))

            peou_df = pd.concat(peou_spearman_results, ignore_index=True)

            plot_spearman_by_response(peou_df)
            plot_pvalue_rows(peou_df)


        

    








