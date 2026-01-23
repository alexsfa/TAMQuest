class Likert_scale_options:
    def __init__(self, client):
        self.supabase_client = client

    '''
    The get_options_by_likert_scale_id function retrieves all the options
    of a questionnaire's likert scale by their likert scale id
    '''
    def get_options_by_likert_scale_id(self, likert_scale_id: str):
        try:
            return (
                self.supabase_client.
                table("likert_scale_options").
                select("id, value, label").
                eq("likert_scale_id", likert_scale_id).
                order("value").
                execute()
            )
        except Exception as e:
            raise RuntimeError(
                f"Failed to retrieve the likert scale's options: {e}"
            )

    '''
    The create_likert_scale_options function stores the likert scale options
    of a specific likert scale
    '''
    def create_likert_scale_options(self, likert_scale_options: dict):
        try:
            return (
                self.supabase_client.
                table("likert_scale_options").
                insert(likert_scale_options).
                execute()
            )
        except Exception as e:
            raise RuntimeError(
                f"Failed to insert the likert scale's options: {e}"
            )
