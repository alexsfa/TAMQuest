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

def total_score_bar_chart(scores_by_category: dict, basic_categories:list):

    fig, ax = plt.subplots(figsize=(10, 4), dpi=100)

    filtered_abbreviations = [abbr for abbr in mapped_categories if mapped_categories.get(abbr) in basic_categories]
    filtered_values = [ scores_by_category[mapped_categories[abbr]] for abbr in filtered_abbreviations ]

    bars = ax.bar(filtered_abbreviations, filtered_values)

    for bar, score in zip(bars, scores_by_category.values()):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2, height, f"{score}", ha="center", va="bottom" if height>=0 else "top")

    ax.set_title("TAM Score Contribution by Category")
    ax.set_ylim(0, max(scores_by_category.values()) + 10)
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

    bars = ax.bar(x_vals, y_vals)

    for bar, answer in zip(bars, answer_counts_dict.values()):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2, height, f"{answer}", ha="center", va="bottom" if height>=0 else "top")

    ax.set_title(title)
    ax.set_ylim(0, max(y_vals) + 5)
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

def calc_spearman_correlation(data: pd.DataFrame, dependent: str, response: str):

    dependent = next((k for k, v in mapped_categories.items() if v == dependent), None)
    response = next((k for k, v in mapped_categories.items() if v == response), None)

    x_axis = data[dependent]
    y_axis = data[response]

    st.write(data[dependent])
    
    x_labels = data[dependent].columns.tolist()

    r_values = []
    p_values = []

    for x in x_labels:
        r, p = spearmanr(x_axis[x], y_axis)
        r_values.append(r)
        p_values.append(p)

    results_df = pd.DataFrame({
        "Response variable": y_axis.columns.tolist(),
        'Dependent variable': x_labels,
        'Spearman r': r_values,
        'p-value': p_values
    })

    return results_df

def plot_spearman_by_response(df):
 
    df["label"] = df["Dependent variable"] + " → " + df["Response variable"]

    colors = []
    for r in df["Spearman r"]:
        if r < -0.5:
            colors.append("red")
        elif -0.5 <= r < 0:
            colors.append("pink")
        elif 0 <= r < 0.5:
            colors.append("lightgreen")
        else:
            colors.append("green")

    fig, ax = plt.subplots(figsize=(8, 3))
    bars = ax.bar(df["label"], df["Spearman r"], color=colors)

    ax.axhline(0, color="black", linewidth=0.8)

    ax.set_ylim(-1.1, 1.1)

    for bar, r in zip(bars, df["Spearman r"]):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2, height, f"{r:.2f}", ha="center", va="bottom" if height>=0 else "top")

    plt.ylabel("Spearman r")
    plt.title("Spearman correlations between predictors and responses")
    st.pyplot(fig)

def plot_pvalue_rows(df, title="Spearman p-value for each relationship"):

    df["label"] = df["Dependent variable"] + " → " + df["Response variable"]

    colors = ["green" if p < 0.05 else "red" for p in df["p-value"]]

    fig, ax = plt.subplots(figsize=(8, 3))
    bars = ax.bar(df["label"], df["p-value"], color=colors)

    ax.axhline(0, color="black", linewidth=0.8)
    
    max_p_decimal_part = str(max(df["p-value"])).split(".")[1] if "." in str(max(df["p-value"])) else ""

    if max_p_decimal_part.startswith("00"):
        padding = 0.001
    else:
        padding = 0.1  

    ax.set_ylim(0, max(df["p-value"]) + padding)

    for bar, p in zip(bars, df["p-value"]):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2, height, f"{p:.4f}", ha="center", va="bottom" if height>=0 else "top")

    plt.ylabel("p-value")
    plt.title("Spearman p-values for predictors and responses")
    st.pyplot(fig)



    