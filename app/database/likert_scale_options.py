class Likert_scale_options:
    def __init__(self, client):
        self.supabase_client = client

    def get_options_by_likert_scale_id(self, likert_scale_id:str):
        try:
            return (
                self.supabase_client.table("likert_scale_options").select("value, label").eq("likert_scale_id", likert_scale_id)
                .order("value").execute()
            )
        except Exception as e:
            raise RuntimeError(f"Failed to retrieve the likert scale's options: {e}")

    def create_likert_scale_options(self, likert_scale_options:dict):
        try:
            return (
                self.supabase_client.table("likert_scale_options").insert(likert_scale_options).execute()
            )
        except Exception as e:
            raise RuntimeError(f"Failed to insert the likert scale's options: {e}")