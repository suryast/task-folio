-- TaskFolio D1 Schema

-- Occupations table (361 ANZSCO occupations)
CREATE TABLE IF NOT EXISTS occupations (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  anzsco_code TEXT UNIQUE NOT NULL,
  title TEXT NOT NULL,
  employment INTEGER,
  median_pay_aud INTEGER,
  outlook TEXT,
  education TEXT,
  ai_exposure_baseline REAL,
  ai_exposure_weighted REAL,
  onet_code TEXT,
  mapping_confidence REAL,
  source TEXT,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_anzsco ON occupations(anzsco_code);
CREATE INDEX IF NOT EXISTS idx_employment ON occupations(employment DESC);

-- Tasks table (~4,500 tasks with economic primitives)
CREATE TABLE IF NOT EXISTS tasks (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  occupation_id INTEGER NOT NULL,
  onet_task_id TEXT,
  description TEXT NOT NULL,

  -- Anthropic Economic Index data
  automation_pct REAL,
  augmentation_pct REAL,
  human_time_without_ai REAL,
  human_time_with_ai REAL,
  speedup_factor REAL,
  human_education_years REAL,
  ai_education_years REAL,
  use_case TEXT,
  ai_autonomy INTEGER,
  success_rate REAL,
  usage_frequency REAL,

  -- TaskFolio additions
  frequency TEXT,
  frequency_weight REAL,
  timeframe TEXT,
  au_success_adjustment REAL,
  taskfolio_score INTEGER,

  source TEXT,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,

  FOREIGN KEY (occupation_id) REFERENCES occupations(id)
);

CREATE INDEX IF NOT EXISTS idx_occupation_tasks ON tasks(occupation_id);
CREATE INDEX IF NOT EXISTS idx_taskfolio_score ON tasks(taskfolio_score DESC);
CREATE INDEX IF NOT EXISTS idx_timeframe ON tasks(timeframe);

-- User analyses (custom job breakdowns)
CREATE TABLE IF NOT EXISTS user_analyses (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  job_title TEXT NOT NULL,
  job_description TEXT,
  analysis_json TEXT NOT NULL,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_job_title ON user_analyses(job_title);
