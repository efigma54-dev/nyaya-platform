
CREATE TABLE IF NOT EXISTS rules (
    id SERIAL PRIMARY KEY,
    short_title VARCHAR(300) NOT NULL,
    full_title VARCHAR(500) NOT NULL,
    act_id INTEGER,
    year INTEGER,
    category lawcategory NOT NULL,
    state VARCHAR(100),
    source_url VARCHAR(500),
    full_text TEXT,
    qdrant_id VARCHAR(100) UNIQUE,
    embedding_model VARCHAR(100),
    is_active BOOLEAN NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    FOREIGN KEY (act_id) REFERENCES acts(id)
);

CREATE INDEX IF NOT EXISTS ix_rules_short_title ON rules(short_title);

CREATE TABLE IF NOT EXISTS rule_sections (
    id SERIAL PRIMARY KEY,
    rule_id INTEGER NOT NULL,
    section_id INTEGER NOT NULL,
    notes TEXT,
    FOREIGN KEY (rule_id) REFERENCES rules(id),
    FOREIGN KEY (section_id) REFERENCES sections(id)
);

CREATE UNIQUE INDEX IF NOT EXISTS ix_rule_section ON rule_sections(rule_id, section_id);

CREATE TABLE IF NOT EXISTS notifications (
    id SERIAL PRIMARY KEY,
    short_title VARCHAR(300) NOT NULL,
    full_title VARCHAR(500) NOT NULL,
    issuing_authority VARCHAR(200) NOT NULL,
    notification_date VARCHAR(50),
    category lawcategory NOT NULL,
    state VARCHAR(100),
    source_url VARCHAR(500),
    full_text TEXT,
    keywords VARCHAR[],
    qdrant_id VARCHAR(100) UNIQUE,
    embedding_model VARCHAR(100),
    is_active BOOLEAN NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT NOW() NOT NULL
);

CREATE INDEX IF NOT EXISTS ix_notifications_short_title ON notifications(short_title);

UPDATE alembic_version SET version_num = '4_add_rules_notifications_tables';
