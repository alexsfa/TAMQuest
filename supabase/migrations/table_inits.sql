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
CREATE TABLE IF NOT EXISTS public.question_options (
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
    submitted_at TIMESTAMPTZ DEFAULT now(),
    answer_text TEXT,
    UNIQUE (id, questionnaire_id)
);

-- adding policies about the permissions that a user has on the responses table
ALTER TABLE public.responses ENABLE ROW LEVEL SECURITY;

-- POLICIES
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_policies
    WHERE policyname = 'Users can insert their responses'
      AND schemaname = 'public'
      AND tablename = 'responses'
  ) THEN
    EXECUTE 'CREATE POLICY "Users can insert their responses"
      ON public.responses
      FOR INSERT
      WITH CHECK (auth.uid() = user_id)';
  END IF;
END
$$;

DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_policies
    WHERE policyname = 'Users can view their responses'
      AND schemaname = 'public'
      AND tablename = 'responses'
  ) THEN
    EXECUTE 'CREATE POLICY "Users can view their responses"
      ON public.responses
      FOR SELECT
      USING (auth.uid() = user_id)';
  END IF;
END
$$;

-- ANSWERS 
CREATE TABLE IF NOT EXISTS public.answers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    response_id UUID NOT NULL REFERENCES public.responses(id) ON DELETE CASCADE, -- the answer corresponds to a full user submission (response)
    question_id UUID NOT NULL REFERENCES public.questions(id) ON DELETE CASCADE, -- the answer corresponds to a question
    selected_option_id UUID NOT NULL REFERENCES public.question_options(id) ON DELETE CASCADE, -- the answer corresponds to a question's option
    UNIQUE (response_id, question_id)
); 
