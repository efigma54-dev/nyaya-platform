
CREATE TABLE IF NOT EXISTS chapters (
    id SERIAL PRIMARY KEY,
    act_id INTEGER NOT NULL,
    chapter_number VARCHAR(50) NOT NULL,
    chapter_title VARCHAR(500) NOT NULL,
    sort_order INTEGER,
    created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    FOREIGN KEY (act_id) REFERENCES acts(id)
);

ALTER TABLE sections ADD COLUMN IF NOT EXISTS chapter_id INTEGER;
ALTER TABLE sections ADD COLUMN IF NOT EXISTS sort_order INTEGER;
ALTER TABLE sections ADD COLUMN IF NOT EXISTS keywords VARCHAR[];
ALTER TABLE sections ADD COLUMN IF NOT EXISTS related_section_ids INTEGER[];
ALTER TABLE sections ADD COLUMN IF NOT EXISTS effective_date VARCHAR(50);

DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 
        FROM information_schema.table_constraints 
        WHERE constraint_name = 'sections_chapter_id_fkey'
    ) THEN
        ALTER TABLE sections 
        ADD CONSTRAINT sections_chapter_id_fkey 
        FOREIGN KEY (chapter_id) REFERENCES chapters(id);
    END IF;
END $$;

UPDATE alembic_version SET version_num = '5_add_missing_sections_columns_and_chapters_table';
