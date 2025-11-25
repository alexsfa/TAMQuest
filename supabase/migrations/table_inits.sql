-- APPLICATION TABLES

-- QUESTIONNAIRES
CREATE TABLE IF NOT EXISTS public.questionnaires (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title TEXT NOT NULL,
    details TEXT,
    created_by UUID REFERENCES auth.users(id),
    created_at TIMESTAMPTZ DEFAULT now()
);

-- QUESTIONS
CREATE TABLE IF NOT EXISTS public.questions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    questionnaire_id UUID NOT NULL REFERENCES public.questionnaires(id) ON DELETE CASCADE, -- a questionnaire has multiple questions
    question_text TEXT NOT NULL,
    position INT DEFAULT 0
);

-- QUESTION OPTIONS
CREATE TABLE IF NOT EXISTS public.answer_options (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    question_id UUID NOT NULL REFERENCES public.questions(id) ON DELETE CASCADE, -- a question has multiple possible answers (options)
    option_text TEXT NOT NULL,
    position INT DEFAULT 0
);

-- RESPONSES
CREATE TABLE IF NOT EXISTS public.responses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id),
    questionnaire_id UUID NOT NULL REFERENCES public.questionnaires(id) ON DELETE CASCADE, -- a user responses to a questionnaire
    submitted_at TIMESTAMPTZ,
    is_submitted BOOLEAN DEFAULT FALSE,
    answer_text TEXT,
    UNIQUE (user_id, questionnaire_id) -- a user can submit only one response
);

-- ANSWERS 
CREATE TABLE IF NOT EXISTS public.answers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    response_id UUID NOT NULL REFERENCES public.responses(id) ON DELETE CASCADE, -- the answer corresponds to a full user submission (response)
    question_id UUID NOT NULL REFERENCES public.questions(id) ON DELETE CASCADE, -- the answer corresponds to a question
    selected_option_id UUID REFERENCES public.answer_options(id) ON DELETE CASCADE, -- the answer corresponds to a question's option (it can be null for a draft response)
    UNIQUE (response_id, question_id)
); 

-- RLS prevents anyone from reading, inserting, updating, deleting rows until a policy explicitly allows it
ALTER TABLE public.responses ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.questionnaires ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.questions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.answer_options ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.answers ENABLE ROW LEVEL SECURITY;

-- POLICIES

-- Only logged in users can SELECT(view) the questionnaires
-- auth.role() is a built-in Supabase function that checks if JWT is authenticated

DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_policies
    WHERE policyname = 'All authenticated users can view questionnaires'
      AND schemaname = 'public'
      AND tablename = 'questionnaires'
  ) THEN
    EXECUTE 'CREATE POLICY "All authenticated users can view questionnaires"
      ON public.questionnaires
      FOR SELECT
      USING (auth.role() = ''authenticated''); '
  END IF;
END
$$;

-- Only logged in users can SELECT(view) the questions

DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_policies
    WHERE policyname = 'All authenticated users can view questions'
      AND schemaname = 'public'
      AND tablename = 'questions'
  ) THEN
    EXECUTE 'CREATE POLICY "All authenticated users can view questions"
      ON public.questions
      FOR SELECT
      USING (auth.role() = ''authenticated'');'
  END IF;
END
$$;

-- Only logged in users can SELECT(view) the the answer options of a question.

DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_policies
    WHERE policyname = 'All authenticated users can view the answer options'
      AND schemaname = 'public'
      AND tablename = 'answer_options'
  ) THEN
    EXECUTE 'CREATE POLICY "All authenticated users can view the answer options"
      ON public.answer_options
      FOR SELECT
      USING (auth.role() = ''authenticated'');'
  END IF;
END
$$;

-- Admins can INSERT or DELETE questionnaires
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_policies
    WHERE policyname = 'Questionnaires can be submitted by admins'
      AND schemaname = 'public'
      AND tablename = 'questionnaires'
  ) THEN
    EXECUTE 'CREATE POLICY "Questionnaires can be submitted by admins"
      ON public.questionnaires
      FOR INSERT
      WITH CHECK (auth.jwt() -> ''app_metadata'' ->> ''role'' = ''admin'');'
  END IF;
END
$$;

DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_policies
    WHERE policyname = 'Questionnaires can be deleted by admins'
      AND schemaname = 'public'
      AND tablename = 'questionnaires'
  ) THEN
    EXECUTE 'CREATE POLICY "Questionnaires can be deleted by admins"
      ON public.questionnaires
      FOR DELETE
      USING (auth.jwt() -> ''app_metadata'' ->> ''role'' = ''admin'');'
  END IF;
END
$$;

-- Admins can INSERT or DELETE questions

DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_policies
    WHERE policyname = 'Questions of the questionnaires can be submitted by admins'
      AND schemaname = 'public'
      AND tablename = 'questions'
  ) THEN
    EXECUTE 'CREATE POLICY "Questions of the questionnaires can be submitted by admins"
      ON public.questions
      FOR INSERT
      WITH CHECK (auth.jwt() -> ''app_metadata'' ->> ''role'' = ''admin'');'
  END IF;
END
$$;

DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_policies
    WHERE policyname = 'Questions of the questionnaires can be deleted by admins'
      AND schemaname = 'public'
      AND tablename = 'questions'
  ) THEN
    EXECUTE 'CREATE POLICY "Questions of the questionnaires can be deleted admins"
      ON public.questions
      FOR DELETE
      USING (auth.jwt() -> ''app_metadata'' ->> ''role'' = ''admin'');'
  END IF;
END
$$;


-- Admins can INSERT or DELETE answer options
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_policies
    WHERE policyname = 'Options as answers can be submitted by admins'
      AND schemaname = 'public'
      AND tablename = 'answer_options'
  ) THEN
    EXECUTE 'CREATE POLICY "Options as answers can be submitted by admins"
      ON public.answer_options
      FOR INSERT
      WITH CHECK (auth.jwt() -> ''app_metadata'' ->> ''role'' = ''admin'');'
  END IF;
END
$$;

DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_policies
    WHERE policyname = 'Options as answers can be deleted by admins'
      AND schemaname = 'public'
      AND tablename = 'answer_options'
  ) THEN
    EXECUTE 'CREATE POLICY "Options as answers can be deleted by admins"
      ON public.answer_options
      FOR DELETE
      USING (auth.jwt() -> ''app_metadata'' ->> ''role'' = ''admin'');'
  END IF;
END
$$;

-- Admins can SELECT or DELETE all responses

DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_policies
    WHERE policyname = 'Admins can view all responses'
      AND schemaname = 'public'
      AND tablename = 'responses'
  ) THEN
    EXECUTE 'CREATE POLICY "Admins can view all responses"
      ON public.responses
      FOR SELECT
      USING (auth.jwt() -> ''app_metadata'' ->> ''role'' = ''admin'');'
  END IF;
END
$$;

DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_policies
    WHERE policyname = 'Admins can delete all responses'
      AND schemaname = 'public'
      AND tablename = 'responses'
  ) THEN
    EXECUTE 'CREATE POLICY "Admins can delete all responses"
      ON public.responses
      FOR DELETE
      USING (auth.jwt() -> ''app_metadata'' ->> ''role'' = ''admin'');'
  END IF;
END
$$;

-- Authenticated users can only SELECT,INSERT, DELETE and submit their own responses.

-- current logged-in user's UUID must match the user_id of the response
-- first, the response is created as draft.
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_policies
    WHERE policyname = 'Users can insert their own responses'
      AND schemaname = 'public'
      AND tablename = 'responses'
  ) THEN
    EXECUTE 'CREATE POLICY "Users can insert their own responses"
      ON public.responses
      FOR INSERT
      WITH CHECK (
        auth.uid() = user_id
        AND is_submitted = FALSE
      )'; 
  END IF;
END
$$;

DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_policies
    WHERE policyname = 'Users can view their own responses'
      AND schemaname = 'public'
      AND tablename = 'responses'
  ) THEN
    EXECUTE 'CREATE POLICY "Users can view their own responses"
      ON public.responses
      FOR SELECT
      USING (auth.uid() = user_id)';
  END IF;
END
$$;

-- The user is allowed to submit his draft response by changing only 'is_submitted' 's field value
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_policies
    WHERE policyname = 'Users can submit their draft response'
      AND schemaname = 'public'
      AND tablename = 'responses'
  ) THEN
    EXECUTE 'CREATE POLICY "Users can submit their draft response"
      ON public.responses
      FOR UPDATE
      USING (
        auth.uid() = user_id
        AND is_submitted = FALSE
      ) 
      WITH CHECK(
        auth.uid() = user_id
        AND is_submitted = TRUE
        AND submitted_at IS NOT NULL
      )';
  END IF;
END
$$;

DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_policies
    WHERE policyname = 'Users can delete their own responses'
      AND schemaname = 'public'
      AND tablename = 'responses'
  ) THEN
    EXECUTE 'CREATE POLICY "Users can delete their own responses"
      ON public.responses
      FOR DELETE
      USING (auth.uid() = user_id)'; 
  END IF;
END
$$;

-- Admins can see everybody's responses.

DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_policies
    WHERE policyname = 'Admins can view all answers'
      AND schemaname = 'public'
      AND tablename = 'answers'
  ) THEN EXECUTE 'CREATE POLICY "Admins can view all answers"
      ON public.answers
      FOR SELECT
      USING (auth.jwt() -> ''app_metadata'' ->> ''role'' = ''admin'');';
  END IF;
END
$$;


-- Users can choose and insert their answer for each question, filling in their response

DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_policies
    WHERE policyname = 'Users can insert answers for their own draft response'
      AND schemaname = 'public'
      AND tablename = 'answers'
  ) THEN EXECUTE 'CREATE POLICY "Users can insert answers for their own draft response"
      ON public.answers
      FOR INSERT
      WITH CHECK (
        EXISTS (
          SELECT 1 FROM public.responses r
          WHERE r.id = response_id 
            AND r.user_id = auth.uid()
        )
      )';
  END IF;
END
$$;

-- Users can view their own set of answers which they form their response

DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_policies
    WHERE policyname = 'Users can view only their own answers'
      AND schemaname = 'public'
      AND tablename = 'answers'
  ) THEN EXECUTE 'CREATE POLICY "Users can view only their own answers"
      ON public.answers
      FOR SELECT
      USING (
        EXISTS (
          SELECT 1 FROM public.responses r
          WHERE r.id = response_id 
            AND r.user_id = auth.uid()
        )
      )';
  END IF;
END
$$;

-- Users can change their answers on a response, if the response is not yet submitted.

DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_policies
    WHERE policyname = 'Users can update answers for their own draft response'
      AND schemaname = 'public'
      AND tablename = 'answers'
  ) THEN EXECUTE 'CREATE POLICY "Users can update answers for their own draft response"
      ON public.answers
      FOR UPDATE
      USING (
        EXISTS (
          SELECT 1 FROM public.responses r
          WHERE r.id = response_id 
            AND r.user_id = auth.uid()
            AND r.is_submitted = FALSE
        )
      )';
  END IF;
END
$$;



