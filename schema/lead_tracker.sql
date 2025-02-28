-- Table: public.tracker_email

-- DROP TABLE IF EXISTS public.tracker_email;

CREATE TABLE IF NOT EXISTS public.tracker_email
(
    id integer NOT NULL DEFAULT nextval('tracker_email_id_seq'::regclass),
    headers jsonb NOT NULL,
    body jsonb DEFAULT '{}'::jsonb,
    CONSTRAINT tracker_email_pkey PRIMARY KEY (id)
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.tracker_email
    OWNER to airflow_user;

-- Index: idx_tracker_email_body

-- DROP INDEX IF EXISTS public.idx_tracker_email_body;

CREATE INDEX IF NOT EXISTS idx_tracker_email_body
    ON public.tracker_email USING gin
    (body jsonb_path_ops)
    TABLESPACE pg_default;

-- Index: idx_tracker_email_headers

-- DROP INDEX IF EXISTS public.idx_tracker_email_headers;

CREATE INDEX IF NOT EXISTS idx_tracker_email_headers
    ON public.tracker_email USING gin
    (headers jsonb_path_ops)
    TABLESPACE pg_default;