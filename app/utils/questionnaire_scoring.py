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

def mean_score(categories: list, answers: list):
    score = []

    df = pd.DataFrame([{
        "category": answer["questions"]["category"],
        "score": 6 - answer["likert_scale_options"]["value"] if answer["questions"]["is_negative"] else answer["likert_scale_options"]["value"]
    } for answer in answers ])
    scores_by_category = {cat: int(df[df["category"] == cat]["score"].sum())
                        for cat in categories}

    total_score_bar_chart(scores_by_category)

    total_score = sum(scores_by_category.values())
    
    total_tam_score = total_score/(len(answers)*5)

    return total_tam_score

    