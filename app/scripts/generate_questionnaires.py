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
    ]
}

TECHNICAL_SUPPORT_QUESTIONS = {
    "Technical Support": [
        "{app_name} technical problem hotline is available at any time.",
        "{app_name} technical team offers good technical support.",
    ]
}

USER_SATISFACTION_QUESTIONS = {
    "User Satisfaction": [
        "The use of {app_name} makes me completely satisfied.",
        "I feel very confident in using {app_name}.",
    ]
}

COMPUTER_ANXIETY_QUESTIONS = {
    "Computer Anxiety": [
        "I feel apprehensive about using {app_name}.",
        "I am afraid of making a mistake using {app_name} that I cannot correct.",
    ]
}

COMPUTER_SELF_EFFICACY_QUESTIONS = {
    "Computer Self-Efficacy": [
        "I expect to become proficient in using {app_name}.",
        "I would feel confident that I can use {app_name}.",
    ]
}

COMPATIBILITY_QUESTIONS = {
    "Compatibility": [
        "Using {app_name} is appropriate for my lifestyle.",
        "Using {app_name} is appropriate for the completion of my related tasks.",
    ]
}

INFORMATION_QUALITY_QUESTIONS = {
    "Information Quality": [
        "Information of {app_name} is accurate and relevant.",
        "Information of {app_name} is rich in detail.",
    ]
}

SYSTEM_QUALITY_QUESTIONS = {
    "System Quality": [
        "{app_name} allows information to be readily accessible to you.",
        "{app_name} is easy to use at the first time I access it.",
    ]
}

RISK_QUESTIONS = {
    "Risk": [
        "I believe the use of {app_name} comes with too many risks.",
        "I believe the use of {app_name} is time consuming.",
    ]
}

SUBJECTIVE_NORM_QUESTIONS = {
    "Subjective Norm": [
        "People who are important to me would think that I should use {app_name}.",
        "Using {app_name} would make me prestigious among my peers.",
    ]
}

BEHAVIORAL_CONTROL_QUESTIONS = {
    "Behavioral Control": [
        "I have absolute control while using {app_name}.",
        "I am capable of using {app_name}.",
    ]
}

TRUST_QUESTIONS = {
    "Trust": [
        "I have serious doubts about using {app_name}.",
        "I do not trust {app_name}.",
    ]
}

def generate_tam_questions(question_dict: dict, app_name: str):
    formatted_questions = {}

    for category, questions in question_dict.items():
        formatted_questions[category] = [
            q.format(app_name=app_name) for q in questions
        ]

    return formatted_questions