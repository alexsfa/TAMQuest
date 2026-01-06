import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from scipy.stats import spearmanr

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

def total_score_bar_chart(scores_by_category: pd.DataFrame, basic_categories:list):
    
    fig, ax = plt.subplots(figsize=(10, 4), dpi=100)
    filtered_abbreviations = [abbr for abbr in mapped_categories if mapped_categories.get(abbr) in basic_categories]
    filtered_values = [ scores_by_category[mapped_categories[abbr]] for abbr in filtered_abbreviations ]
    ax.bar(filtered_abbreviations, filtered_values)
    ax.set_title("TAM Score Contribution by Category")
    ax.set_ylim(0, max(scores_by_category.values()) + 1)
    ax.yaxis.get_major_locator().set_params(integer=True)

    st.pyplot(fig)

def category_answers_bar_chart(answer_counts: pd.DataFrame, title:str, likert_scale_options: list):
    likert_labels = [option["label"] for option in likert_scale_options]

    full_answer_counts = {str(label): 0 for label in likert_labels}
    
    answer_counts_dict = answer_counts.set_index("Label")["count"].to_dict()
    full_answer_counts.update(answer_counts_dict)

    x_vals = list(full_answer_counts.keys())  
    y_vals = list(full_answer_counts.values()) 


    fig, ax = plt.subplots(figsize=(10, 2), dpi=100)
    ax.bar(x_vals, y_vals)
    ax.set_title(title)
    ax.set_ylim(0, max(y_vals) + 1)
    ax.yaxis.get_major_locator().set_params(integer=True)

    st.pyplot(fig)


def count_category_answers_by_label(answers:list, title:str, likert_scale_options: list):

    df = pd.DataFrame(answers)

    count_df = (
        df["likert_scale_options"]
        .apply(lambda x: x["label"])   
        .value_counts()               
        .reset_index()
    )

    count_df.columns = ["Label", "count"]
    
    category_answers_bar_chart(count_df, title, likert_scale_options)

    return None
    
def tam_score(categories: list, answers: list, likert_scale_options: list, basic_categories: list):

    basic_categories_answers = [
        a for a in answers
        if a["questions"]["category"] in basic_categories
    ]

    df = pd.DataFrame([{
        "category": answer["questions"]["category"],
        "score": (len(likert_scale_options) + 1) - answer["likert_scale_options"]["value"] if answer["questions"]["is_negative"] else answer["likert_scale_options"]["value"]
    } for answer in basic_categories_answers ])
    scores_by_category = {cat: int(df[df["category"] == cat]["score"].sum())
                        for cat in categories}

    len(df)

    st.write("## Categories distribution on TAM score")
    total_score_bar_chart(scores_by_category, basic_categories)

    total_score = sum(scores_by_category.values())
    
    total_tam_score = total_score/(len(df)*len(likert_scale_options))

    return total_tam_score

def construct_scores(answers:list, likert_scale_options: list, categories: list):

    answers = [a for a in answers if a["questions"]["category"] in categories]

    answer_df = pd.DataFrame([{
        "category": answer["questions"]["category"],
        "score": (len(likert_scale_options) + 1) - answer["likert_scale_options"]["value"]
                 if answer["questions"]["is_negative"] else answer["likert_scale_options"]["value"]
    } for answer in answers])

    result = {}
    for category in categories:
        cat_df = answer_df[answer_df["category"] == category]
        result[category] = {
            "total_score": int(cat_df["score"].sum()),
            "count_answers": len(cat_df)
        }

    return result

def pivot_constructs(data: dict):
    
    construct_means_df = pd.DataFrame(data)

    resulted_df = construct_means_df.pivot(index="response_id", columns="category", values="mean_score").reset_index()

    rename_map = {v: k for k, v in mapped_categories.items() if v in resulted_df.columns}

    resulted_df = resulted_df.rename(columns=rename_map)

    return resulted_df

def calc_spearman_correlation(x_axis: pd.DataFrame, y_axis: pd.DataFrame):
    
    x_labels = x_axis.columns.tolist()

    r_values = []
    p_values = []

    for x in x_labels:
        r, p = spearmanr(x_axis[x], y_axis)
        r_values.append(r)
        p_values.append(p)
        st.write(x, r, p)

    results_df = pd.DataFrame({
        'Category': x_labels,
        'Spearman r': r_values,
        'p-value': p_values
    })

    plt.figure(figsize=(10, 3))
    sns.barplot(x='Category', y='Spearman r', data=results_df, palette='viridis')
    plt.title('Spearman Correlation Coefficients')
    plt.ylabel('Spearman r')
    plt.xticks(rotation=45)
    st.pyplot(plt)
    
    # Προαιρετικά: Δημιουργία bar chart για να οπτικοποιήσεις τα p-values
    plt.figure(figsize=(10, 3))
    sns.barplot(x='Category', y='p-value', data=results_df, palette='coolwarm')
    plt.title('p-values for Spearman Correlation')
    plt.ylabel('p-value')
    plt.xticks(rotation=45)
    st.pyplot(plt)


    