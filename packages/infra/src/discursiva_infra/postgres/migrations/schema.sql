DO $$ BEGIN
    CREATE TYPE submission_status AS ENUM ('PENDING', 'PROCESSING', 'DONE', 'ERROR');
EXCEPTION
    WHEN duplicate_object THEN NULL;
END $$;

CREATE TABLE IF NOT EXISTS submissions (
    id          UUID              PRIMARY KEY,
    student_id  TEXT              NOT NULL,
    s3_key      TEXT              NOT NULL,
    status      submission_status NOT NULL DEFAULT 'PENDING',
    score       NUMERIC(4, 2)     CHECK (score BETWEEN 0 AND 10),
    created_at  TIMESTAMPTZ       NOT NULL DEFAULT now(),
    updated_at  TIMESTAMPTZ       NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_submissions_student_id
    ON submissions (student_id);

CREATE INDEX IF NOT EXISTS idx_submissions_student_created
    ON submissions (student_id, created_at DESC);

CREATE OR REPLACE FUNCTION set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DO $$ BEGIN
    CREATE TRIGGER trg_submissions_updated_at
    BEFORE UPDATE ON submissions
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();
EXCEPTION
    WHEN duplicate_object THEN NULL;
END $$;