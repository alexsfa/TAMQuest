
-- Definition of database tables

create table profiles (
    id uuid primary key references auth.users(id),
    full_name text not null,
    birthdate date,
    created_at default now(),
    updated_at default now(),
    city text,
    country text
);

create table questionnaires (
    id uuid primary key default gen_random_uuid(),
    title text not null,
    details text,
    created_at default now(),
    created_by uuid references public.profiles(id) ON DELETE CASCADE
);

create table questions (
    id uuid primary key default gen_random_uuid(),
    questionnaire_id uuid references public.questionnaires(id) ON DELETE CASCADE,
    question_text text,
    position integer,
    category text,
    is_custom bool default false,
    is_negative bool default false
);

create table likert_scales (
    id uuid primary key default gen_random_uuid(),
    questionnaire_id uuid references public.questionnaires(id) ON DELETE CASCADE
);

create table likert_scale_options (
    id uuid primary key default gen_random_uuid(),
    likert_scale_id uuid references public.likert_scales(id) ON DELETE CASCADE,
    value integer,
    label text
);

create table responses (
    id uuid primary key default gen_random_uuid(),
    user_id uuid references public.profiles(id) ON DELETE CASCADE,
    questionnaire_id uuid references public.questionnaires(id) ON DELETE CASCADE,
    submitted_at timestamptz,
    is_submitted bool default false
);

create table answers (
    id uuid primary key default gen_random_uuid(),
    response_id uuid references public.responses(id) ON DELETE CASCADE,
    question_id uuid references public.questions(id),
    selected_option uuid references public.likert_scale_options(id)
);

-- Activation of Row-Level Security for each table

ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.questionnaires ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.questions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.likert_scales ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.likert_scale_options ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.responses ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.answers ENABLE ROW LEVEL SECURITY;

-- Definition of RLS Policies

-- 'profiles' table RLS Policies

CREATE POLICY "Admins can view all profiles"
ON public.profiles
FOR SELECT
USING (auth.jwt() -> 'app_metadata' ->> 'role' = 'admin');

CREATE POLICY "Admins can delete all profiles"
ON public.profiles
FOR DELETE
USING (auth.jwt() -> 'app_metadata' ->> 'role' = 'admin');

CREATE POLICY "Users can view their own profile"
ON public.profiles
FOR SELECT 
USING (id = auth.uid());

CREATE POLICY "Users can create their own profile"
ON public.profiles
FOR INSERT 
WITH CHECK (id = auth.uid());

CREATE POLICY "Users can update their own profile"
ON public.profiles
FOR UPDATE
USING (id = auth.uid())
WITH CHECK (id = auth.uid());

CREATE POLICY "Users can delete their own profile"
ON public.profiles
FOR DELETE
USING (id = auth.uid());

-- 'questionnaires' table RLS Policies

CREATE POLICY "Admins can create questionnaires"
ON public.questionnaires
FOR INSERT 
WITH CHECK (auth.jwt() -> 'app_metadata' ->> 'role' = 'admin');

CREATE POLICY "Admins can delete questionnaires"
ON public.questionnaires
FOR DELETE
USING (auth.jwt() -> 'app_metadata' ->> 'role' = 'admin');

CREATE POLICY "Users can view questionnaires"
ON public.questionnaires
FOR SELECT 
USING (auth.uid() IS NOT NULL);

-- 'questions' table RLS Policies

CREATE POLICY "Admins can insert questions"
ON public.questions
FOR INSERT 
WITH CHECK (auth.jwt() -> 'app_metadata' ->> 'role' = 'admin');

CREATE POLICY "Users can view questions"
ON public.questions
FOR SELECT 
USING (auth.uid() IS NOT NULL);

-- 'likert_scales' table RLS Policies

CREATE POLICY "Admins can insert Likert scales"
ON public.likert_scales
FOR INSERT 
WITH CHECK (auth.jwt() -> 'app_metadata' ->> 'role' = 'admin');

CREATE POLICY "Users can view Likert scales"
ON public.likert_scales
FOR SELECT 
USING (auth.uid() IS NOT NULL);

-- 'likert_scale_options' table RLS Policies

CREATE POLICY "Admins can insert Likert scale options"
ON public.likert_scale_options
FOR INSERT 
WITH CHECK (auth.jwt() -> 'app_metadata' ->> 'role' = 'admin');

CREATE POLICY "Users can view Likert scales' options"
ON public.likert_scale_options
FOR SELECT 
USING (auth.uid() IS NOT NULL);

-- 'responses' table RLS Policies

CREATE POLICY "Admins can view all responses"
ON public.responses
FOR SELECT
USING (auth.jwt() -> 'app_metadata' ->> 'role' = 'admin');

CREATE POLICY "Admins can delete all responses"
ON public.responses
FOR DELETE
USING (auth.jwt() -> 'app_metadata' ->> 'role' = 'admin');

CREATE POLICY "Users can view their own responses"
ON public.responses
FOR SELECT 
USING (user_id = auth.uid());

CREATE POLICY "Users can submit their own responses"
ON public.responses
FOR INSERT 
WITH CHECK (user_id = auth.uid());

CREATE POLICY "Users can update their own drafts"
ON public.responses
FOR UPDATE
USING (user_id = auth.uid() AND is_submitted = false)
WITH CHECK (user_id = auth.uid());

CREATE POLICY "Users can delete their own responses"
ON public.responses
FOR DELETE
USING (user_id = auth.uid());

-- 'answers' table RLS Policies

CREATE POLICY "Admins can view all answers"
ON public.answers
FOR SELECT
USING (auth.jwt() -> 'app_metadata' ->> 'role' = 'admin');

CREATE POLICY "Users can view their own answers"
ON public.answers FOR SELECT
USING (
    EXISTS (
        SELECT 1 FROM public.responses r
        WHERE r.id = public.answers.response_id
        AND r.user_id = auth.uid()
    )
);

CREATE POLICY "Users can insert their own answers"
ON public.answers
FOR INSERT 
WITH CHECK (
    EXISTS (
        SELECT 1
        FROM public.responses r
        WHERE r.id = answers.response_id
          AND r.user_id = auth.uid()
    )
);

CREATE POLICY "Users can update their own answers"
ON public.answers
FOR UPDATE
USING  (
    EXISTS (
        SELECT 1
        FROM public.responses r
        WHERE r.id = answers.response_id
          AND r.user_id = auth.uid()
          AND r.is_submitted = false
    )
)
WITH CHECK (
    EXISTS (
    SELECT 1
    FROM public.responses r
    WHERE r.id = answers.response_id
        AND r.user_id = auth.uid()
        AND r.is_submitted = false
    )
);

CREATE OR REPLACE FUNCTION get_all_response_category_means(q_id_param UUID)
RETURNS TABLE (
    response_id UUID,
    category TEXT,
    mean_score NUMERIC
) 
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
BEGIN
    RETURN QUERY
    SELECT 
        a.response_id, 
        q.category, 
        AVG(
            CASE 
                WHEN q.is_negative THEN 6 - lso.value 
                ELSE lso.value 
            END
        )::NUMERIC AS mean_score 
    FROM public.answers a 
    JOIN public.questions q ON a.question_id = q.id 
    JOIN public.likert_scale_options lso ON a.selected_option = lso.id 
    JOIN public.responses r ON a.response_id = r.id 
    WHERE q.questionnaire_id = q_id_param 
      AND r.is_submitted = TRUE 
    GROUP BY a.response_id, q.category;
END;
$$;

CREATE OR REPLACE FUNCTION get_questionnaires_without_user_response(user_id_param UUID)
RETURNS SETOF public.questionnaires
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
BEGIN
    RETURN QUERY
    SELECT q.*
    FROM public.questionnaires q
    WHERE NOT EXISTS (
        SELECT 1
        FROM public.responses r
        WHERE r.questionnaire_id = q.id
          AND r.user_id = user_id_param
    );
END;
$$;








