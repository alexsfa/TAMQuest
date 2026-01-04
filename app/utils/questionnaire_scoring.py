import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

mapped_categories = {
    "PU": "Perceived Usefulness",
    "PEOU": "Perceived Ease of Use",
    "AT": "Attitude",
    "BI": "Behavioral Intention",
    "TS": "Technology Support",
    "US": "User Satisfaction",
    "CA": "Computer Anxiety",
    "CSE": "Computer Self-Efficacy",
    "COMP": "Compatibility",
    "IQ": "Information Quality",
    "SQ": "System Quality",
    "R": "Risk",
    "SN": "Subjective Norm",
    "BC": "Behavioral Control",
    "T": "Trust"
}

def total_score_bar_chart(scores_by_category: dict):
    
    fig, ax = plt.subplots(figsize=(10, 4), dpi=100)
    filtered_abbreviations = [abbr for abbr in mapped_categories if mapped_categories.get(abbr) in scores_by_category.keys()]
    filtered_values = [ scores_by_category[mapped_categories[abbr]] for abbr in filtered_abbreviations ]
    ax.bar(filtered_abbreviations, filtered_values)
    ax.set_title("TAM Score Contribution by Category")
    ax.set_ylim(0, max(scores_by_category.values()) + 1)

    st.pyplot(fig)

def category_answers_bar_chart(answer_counts: dict, category:str):
    fig, ax = plt.subplots(figsize=(10, 2), dpi=100)
    ax.bar(answer_counts.keys(), answer_counts.values())
    ax.set_title(f"Answer Distribution for {category}")
    ax.set_ylim(0, max(answer_counts.values()) + 1)

    st.pyplot(fig)

def count_category_answers_by_label(df: pd.DataFrame, category:str, likert_scale_options: list):
    
    filtered_df = df[df["category"] == category]

    counts = filtered_df["score"].value_counts().reindex(range(1, 6), fill_value=0)

    result = {}
    for option in likert_scale_options:
        option_value = option["value"]
        result[option["label"]] = counts.get(option_value, 0)

    category_answers_bar_chart(result, category)

    return result


def mean_score(categories: list, answers: list, likert_scale_options: list):

    df = pd.DataFrame([{
        "category": answer["questions"]["category"],
        "score": (len(likert_scale_options) + 1) - answer["likert_scale_options"]["value"] if answer["questions"]["is_negative"] else answer["likert_scale_options"]["value"]
    } for answer in answers ])
    scores_by_category = {cat: int(df[df["category"] == cat]["score"].sum())
                        for cat in categories}

    for category in categories:
        st.write(f"## {category}")
        result = count_category_answers_by_label(df, category, likert_scale_options)

    st.write("## Categories distribution on TAM score")
    total_score_bar_chart(scores_by_category)

    total_score = sum(scores_by_category.values())
    
    total_tam_score = total_score/(len(answers)*len(likert_scale_options))

    return total_tam_score

    