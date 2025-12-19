import streamlit as st

ESSENTIAL_TAM_QUESTIONS = {
    "Perceived Usefulness": [
        "Using {app_name} improves my work performance.",
        "{app_name} improves the results of my work.",
        "I found {app_name} useful.",
        "Using {app_name} allows me to complete my tasks faster.",
    ],
    "Perceived Ease of Use": [
        "{app_name} is easy to use.",
        "The training provided for using {app_name} is easy to follow.",
        "My interaction with {app_name} is understandable and clear.",
        "It is easy to use {app_name} to complete related tasks.",
    ],
    "Attitude": [
        "Using {app_name} is a good idea for me.",
        "I like to use {app_name}.",
        "Using {app_name} is fun.",
        "{app_name} is an attractive way to complete related tasks.",
    ],
    "Behavioral Intention": [
        "I predict I will use {app_name} in the distant future.",
        "I will often use {app_name} in the future, if I can.",
        "I intend to continue using {app_name}.",
        "I will recommend the {app_name} to others.",
    ],
}

ADDITIONAL_TAM_QUESTIONS = {
    "Technology Support": [ 
        "{app_name} technical problem hotline is available at any time.",
        "{app_name} technical team offers good technical support.",
    ],
    "User Satisfaction": [
        "The use of {app_name} makes me completely satisfied.",
        "I feel very confident in using {app_name}.",
    ],
    "Computer Anxiety": [
        "I feel apprehensive about using {app_name}.",
        "I am afraid of making a mistake using {app_name} that I cannot correct.",
    ],
    "Computer Self-Efficacy": [
        "I expect to become proficient in using {app_name}.",
        "I would feel confident that I can use {app_name}.",
    ],
    "Compatibility": [
        "Using {app_name} is appropriate for my lifestyle.",
        "Using {app_name} is appropriate for the completion of my related tasks.",
    ],
    "Information Quality": [
        "Information of {app_name} is accurate and relevant.",
        "Information of {app_name} is rich in detail.",
    ],
    "System Quality": [
        "{app_name} allows information to be readily accessible to you.",
        "{app_name} is easy to use at the first time I access it.",
    ],
    "Risk": [
        "I believe the use of {app_name} comes with too many risks.",
        "I believe the use of {app_name} is time consuming.",
    ],
    "Subjective Norm": [
        "People who are important to me would think that I should use {app_name}.",
        "Using {app_name} would make me prestigious among my peers.",
    ],
    "Behavioral Control": [
        "I have absolute control while using {app_name}.",
        "I am capable of using {app_name}.",
    ],
    "Trust": [
        "I have serious doubts about using {app_name}.",
        "I do not trust {app_name}.",
    ],
}

CUSTOM_QUESTIONS = {}

def generate_tam_questions(questions: dict, app_name: str):
    formatted_questions = {}
    for category, questions in ESSENTIAL_TAM_QUESTIONS.items():
        formatted_questions[category] = [
            q.format(app_name=app_name) for q in questions
        ]

    return formatted_questions

def generate_additional_tam_questions(questions: dict, app_name: str):
    formatted_questions = {}
    for category, questions in ADDITIONAL_TAM_QUESTIONS.items():
        if st.session_state[category]:
            formatted_questions[category] = [
                q.format(app_name=app_name) for q in questions
            ]

    return formatted_questions

def add_custom_questions_categories():
    additional_custom_questions_categories = []
    for category in ADDITIONAL_TAM_QUESTIONS.keys():
        if category in st.session_state and st.session_state[category]:
            additional_custom_questions_categories.append(category)
    
    return additional_custom_questions_categories

def add_custom_questions(custom_question: str, selected_category: str):

    if custom_question.strip() == "":
        st.warning("Please enter an app name.")
        return

    if selected_category in CUSTOM_QUESTIONS:
        CUSTOM_QUESTIONS[selected_category].append(custom_question)
    else:
        CUSTOM_QUESTIONS[selected_category] = [custom_question]




