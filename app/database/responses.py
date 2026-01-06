class Responses:
    def __init__(self, client):
        self.supabase_client = client
    
    """
    The get_all_responses() function gets all the responses including their corresponding questionnaire's info
    and the name of the profile which has submitted it. (for admins)
    """
    def get_all_responses(self):
        try:
            return (
                self.supabase_client.table("responses").select("questionnaires(*), profiles(full_name), id, submitted_at, is_submitted")
                .eq("is_submitted", True).order("submitted_at", desc=True).execute()
            )
        except Exception as e:
            raise RuntimeError(f"Failed to retrieve responses: {e}")

    def get_all_responses_by_questionnaire_id(self, questionnaire_id: str):
        try:
            return (
                self.supabase_client.table("responses").select("questionnaires(*), profiles(*), id, submitted_at, is_submitted")
                .eq("questionnaire_id", questionnaire_id).eq("is_submitted", True).execute()
            )
        except Exception as e:
            raise RuntimeError(f"Failed to retrieve responses: {e}")   

    """
    The get_response_by_id function gets the response that matches with the response_id parameter (for users)
    """
    def get_response_by_id(self, response_id: str):
        try:
            return (
                self.supabase_client.table("responses")
                .select("questionnaires(id, title, details, created_at), profiles(full_name), submitted_at")
                .eq("id", response_id).execute()
            )
        except Exception as e:
            raise RuntimeError(f"Failed to retrieve response: {e}")

    """
    The get_response_by_user_id function gets all the responses that their user_id 
    matches the parameter user_id (for users)
    """
    def get_response_by_user_id(self, user_id: str):
        try:
            return (
                self.supabase_client.table("responses").select("questionnaires(*), id, submitted_at, is_submitted")
                .eq("user_id", user_id).order("is_submitted", desc=True).execute()
            )
        except Exception as e:
            raise RuntimeError(f"Failed to retrieve response: {e}")

    """
    The get_draft_by_questionnaire_id function gets the user's response by its questionnaire_id.
    For only the drafts' retrieval, set is_submitted to False (for users)
    """
    def get_responses_by_questionnaire_id(self, user_id: str, questionnaire_id: str, is_submitted: bool | None = None):
        try:
            query = (
                self.supabase_client.table("responses").select("id").eq("user_id", user_id)
                .eq("questionnaire_id", questionnaire_id)
            )

            if is_submitted is None:
                query = query.eq("is_submitted", is_submitted)
            
            return query.execute()
        except Exception as e:
            raise RuntimeError(f"Failed to retrieve the specified draft: {e}")

    def  get_all_responses_category_means(self, questionnaire_id: str):
        try:
            return self.supabase_client.rpc("get_response_category_means", {"q_id": questionnaire_id}).execute()
        except Exception as e:
            raise RuntimeError(f"Failed to retrieve the specified draft: {e}")

    """
    The create_response function inserts a new row in the responses' table (for users)
    """
    def create_response(self, user_id: str, questionnaire_id: str, is_submitted: bool):
        try: 
            return (
                    self.supabase_client.table("responses").insert({
                    "user_id": user_id,
                    "questionnaire_id": questionnaire_id,
                    "is_submitted": is_submitted
                }).execute()
            )
        except Exception as e:
            raise RuntimeError(f"Failed to create response: {e}")

    """
    The update_response_on_submitted function updates the response of response_id on its is_submitted field.
    This function is used for users so they can submit their drafts.
    """
    def update_response_on_submitted(self, user_id: str, is_submitted: bool):
        try:
            return (
                self.supabase_client.table("responses").update({"is_submitted": is_submitted})
                .eq("user_id", user_id).execute()
            )
        except Exception as e:
            raise RuntimeError(f"Failed to update response: {e}")

    """
    The delete_response_by_id function deletes the response with the corresponding response_ids
    """
    def delete_response_by_id(self, response_id: str):
        try:
            return self.supabase_client.table("responses").delete().eq("id", response_id).execute()
        except Exception as e:
            raise RuntimeError(f"Failed to delete responses: {e}")

        
        