class Questions:

    def __init__(self, client):
        self.supabase_client = client

    """
    The get_questions_by_questionnaire_id function returns all the questions
    that correspond to a questionnaire's id (for users)
    """
    def get_questions_by_questionnaire_id(self, questionnaire_id: str):
        try:
            return (
                self.supabase_client
                .table("questions")
                .select("id, question_text, category")
                .eq("questionnaire_id", questionnaire_id)
                .execute()
            )
        except Exception as e:
            raise RuntimeError(
                f"Failed to retrieve questions: {e}"
            )

    '''
    The create_questions function stores the questions
    of a questionnaire in the database.
    '''
    def create_questions(self, questions: list[dict]):
        # inserts the questions list as rows for the question table
        try:
            return (
                 self.supabase_client
                 .table("questions")
                 .insert(questions)
                 .execute()
            )
        except Exception as e:
            raise RuntimeError(f"Failed to create the questions: {e}")
