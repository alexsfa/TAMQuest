class Answers:
    def __init__(self, client):
        self.supabase_client = client

    '''
    The get_answers_by_response_id function gets all the answers that have the corresponding response_id (for users)
    '''
    def get_answers_by_response_id(self, response_id: str):
        try:
            return (
                self.supabase_client.table("answers").select("*, questions(question_text, position)")
                .eq("response_id", response_id).order("questions(position)").execute()
            )
        except Exception as e:
            raise RuntimeError(f"Failed to retrieve answers: {e}")

    '''
    The create_answers function inserts a new row on the answers' table (for users)
    '''
    def create_answers(self, answers: list[dict]):
        try:
            return (
                self.supabase_client.table("answers").insert(answers).execute()
            )
        except Exception as e:
            raise RuntimeError(f"Failed to insert the answers: {e}")

    '''
    The update_answers function updates the answers of a specific resposnse (for users)
    '''
    def update_answers(self, answers: list[dict]):
        try:
            return (
                self.supabase_client.table("answers").upsert(answers, on_conflict=["response_id,question_id"]).execute()
            )
        except Exception as e:
            raise RuntimeError(f"Failed to update the answers: {e}")
