class Likert_scale_options:
    def __init__(self, client):
        self.supabase_client = client


    def create_likert_scale_options(self, likert_scale_options:dict):
        try:
            return (
                self.supabase_client.table("likert_scale_options").insert(likert_scale_options).execute()
            )
        except Exception as e:
            raise RuntimeError(f"Failed to insert the likert scale's options: {e}")