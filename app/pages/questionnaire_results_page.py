import streamlit as st
import pandas as pd

from app import (
    client,
    questionnaires_repo,
    responses_repo,
    questions_repo,
    answers_repo,
    likert_scales_repo,
    likert_scale_options_repo
)

from utils.menu import menu
from utils.questionnaire_scoring import (
    tam_score,
    count_category_answers_by_label,
    pivot_constructs,
    calc_spearman_correlation,
    plot_spearman_by_response,
    plot_pvalue_rows
)

basic_constructs = [
    "Perceived Usefulness",
    "Perceived Ease of Use",
    "Attitude",
    "Behavioral Intention"
]

if __name__ == "__main__":

    menu(client)

    questionnaire_info = (
        questionnaires_repo.
        get_questionnaire_by_id(
            st.session_state["current_questionnaire_id"]
        )
    )

    likert_scale_info = (
        likert_scales_repo.
        get_likert_scale_by_questionnaire_id(
            st.session_state["current_questionnaire_id"]
            )
    )

    likert_scale_options = (
        likert_scale_options_repo.
        get_options_by_likert_scale_id(
            likert_scale_info.data[0]["id"]
        )
    )

    questions_info = (
        questions_repo.
        get_questions_by_questionnaire_id(
            st.session_state["current_questionnaire_id"]
        )
    )

    answers = (
        answers_repo.
        get_submitted_answers_by_questionnaire_id(
            st.session_state["current_questionnaire_id"]
        )
    )

    unique_constructs = list(
        {
            item["questions"]["category"]
            for item in answers.data
        }
    )

    secondary_constructs = [
        construct
        for construct in unique_constructs
        if construct not in basic_constructs
    ]

    # Counting the number of responses based on the
    # different response_ids of the retrieved answers.
    unique_responses = {item["response_id"] for item in answers.data}
    count_of_responses = len(unique_responses)

    st.write(f"## Results for {questionnaire_info.data[0]['title']}")

    # Showcasing the basic and additional TAM constructs
    # that the specified questionnaire has examined.
    st.write(
        "#### The TAM constructs which have been"
        " examined are the following:"
    )
    construct_cols = st.columns(3)
    for i, construct in enumerate(unique_constructs):
        construct_cols[i % 3].write(f"##### {construct}")
    st.write("\n")
    st.write(
        f"#### There are {count_of_responses} responses "
        "for this questionnaire."
    )
    st.write(f"#### Total of answers submitted are {len(answers.data)}.")

    st.divider()

    # If there are no responses for the questionnaire,
    # the app does not proceed to a statistical analysis.
    if count_of_responses == 0:
        st.write(
            "The response rate did not meet the minimum threshold"
            "required for statistical analysis"
        )
        st.stop()

    # For each of the basic constructs, the number of times that an answer
    # has been selected gets showcased on a bar chart.
    # If there are custom questions, a bar chart shows the number of times that
    # an answer has been selected only for that question.
    for category in basic_constructs:

        automated_questions_answers, custom_questions_answers = [], []

        for item in answers.data:
            if item["questions"]["category"] == category:
                (
                    custom_questions_answers
                    if item["questions"]["is_custom"]
                    else automated_questions_answers
                ).append(item)

        has_custom = len(custom_questions_answers) > 0

        st.write(f"## {category}")
        st.write("### Automated questions")
        count_category_answers_by_label(
            automated_questions_answers,
            (
                f"Questions score contribution for {category}"
                "automated questions"
            ),
            likert_scale_options.data
        )

        question_texts = list(
            {
                item["questions"]["question_text"]
                for item in custom_questions_answers
            }
        )

        if has_custom:
            st.write("### Custom questions")
            for question_text in question_texts:
                count_category_answers_by_label(
                    custom_questions_answers,
                    f"Score contribution for '{question_text}' question",
                    likert_scale_options.data
                )

    # Total TAM score of the questionnaire gets calculated and printed
    final_tam_score = tam_score(
        unique_constructs,
        answers.data,
        likert_scale_options.data,
        basic_constructs
    )
    st.write(f"# Total TAM score:{final_tam_score}")

    st.divider()

    # If there are additional construct, the same statistic analysis
    # gets applied to them but the results do not contribute
    # on the final TAM score.
    if len(secondary_constructs) != 0:

        st.title("Secondary constructs analysis")

        for construct in secondary_constructs:
            automated_questions_answers, custom_questions_answers = [], []

            for item in answers.data:
                if item["questions"]["category"] == construct:
                    (
                        custom_questions_answers
                        if item["questions"]["is_custom"]
                        else automated_questions_answers
                    ).append(item)

            has_custom = len(custom_questions_answers) > 0

            st.write(f"## {construct}")
            st.write("### Automated questions")

            count_category_answers_by_label(
                automated_questions_answers,
                f"Answers for {construct} automated questions",
                likert_scale_options.data
            )

            question_texts = list(
                {
                    item["questions"]["question_text"]
                    for item in custom_questions_answers
                }
            )

            if has_custom:
                st.write("### Custom questions")
                for question_text in question_texts:
                    count_category_answers_by_label(
                        custom_questions_answers,
                        f"Answers for '{question_text}' question",
                        likert_scale_options.data
                    )

        st.divider()

    # If there are less than 10 responses for the questionnaire,
    # the app does not proceed on a spearman analysis
    if count_of_responses < 10:
        st.write(
            "#### There are not enough responses"
            "#### for a valid spearman analysis."
        )
    else:

        # Performing a spearman analysis between TAM's basic constructs
        st.write("### Spearman statistic analysis for TAM's basic constructs")

        responses_category_means = (
            responses_repo.get_all_responses_category_means(
                st.session_state["current_questionnaire_id"]
            )
        )

        basic_category_means = pivot_constructs(responses_category_means.data)

        basic_constructs_spearman_results = []
        basic_constructs_spearman_results.append(
            calc_spearman_correlation(
                basic_category_means,
                "Attitude",
                "Behavioral Intention"
            )
        )
        basic_constructs_spearman_results.append(
            calc_spearman_correlation(
                basic_category_means,
                "Perceived Usefulness",
                "Attitude"
            )
        )
        basic_constructs_spearman_results.append(
            calc_spearman_correlation(
                basic_category_means,
                "Perceived Ease of Use",
                "Attitude"
            )
        )

        final_df = pd.concat(
            basic_constructs_spearman_results,
            ignore_index=True
        )

        plot_spearman_by_response(final_df)

        plot_pvalue_rows(final_df)

        pu_constructs = [
            "Subjective Norm",
            "Information Quality",
            "Compatibility",
            "Trust",
            "Risk"
        ]

        peou_constructs = [
            "Technology Support",
            "Computer Self-Efficacy",
            "Computer Anxiety",
            "User Satisfaction",
            "System Quality",
            "Behavioral Control"
        ]

        available_pu_constructs = [
            construct
            for construct in unique_constructs
            if construct in pu_constructs
        ]

        available_peou_constructs = [
            construct
            for construct in unique_constructs
            if construct in peou_constructs
        ]

        # Performing a spearman analysis between Perceived Usefulness
        # and all the available dependent constructs.
        if len(available_pu_constructs) != 0:
            st.write(
                "### Spearman statistic analysis between"
                "### PU and secondary constructs"
            )
            pu_spearman_results = []
            for construct in available_pu_constructs:
                pu_spearman_results.append(
                    calc_spearman_correlation(
                        basic_category_means,
                        construct,
                        "Perceived Usefulness"
                    )
                )

            pu_df = pd.concat(pu_spearman_results, ignore_index=True)

            plot_spearman_by_response(pu_df)
            plot_pvalue_rows(pu_df)

        # Performing a spearman analysis between Perceived Ease of Use
        # and all the available dependent constructs.
        if len(available_peou_constructs) != 0:
            st.write(
                "### Spearman statistic analysis between"
                "### PEOU and secondary constructs"
            )
            peou_spearman_results = []
            for construct in available_peou_constructs:
                peou_spearman_results.append(
                    calc_spearman_correlation(
                        basic_category_means,
                        construct,
                        "Perceived Ease of Use"
                    )
                )

            peou_df = pd.concat(peou_spearman_results, ignore_index=True)

            plot_spearman_by_response(peou_df)
            plot_pvalue_rows(peou_df)
