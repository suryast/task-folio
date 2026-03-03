import {
  pgTable,
  uuid,
  varchar,
  text,
  integer,
  timestamp,
  index,
} from 'drizzle-orm/pg-core'

export const users = pgTable('users', {
  id: uuid('id').primaryKey().defaultRandom(),
  email: varchar('email', { length: 255 }).unique().notNull(),
  createdAt: timestamp('created_at').defaultNow().notNull(),
})

export const jobProfiles = pgTable(
  'job_profiles',
  {
    id: uuid('id').primaryKey().defaultRandom(),
    userId: uuid('user_id').references(() => users.id, { onDelete: 'set null' }),
    jobTitle: varchar('job_title', { length: 255 }).notNull(),
    jobDescription: text('job_description'),
    onetSocCode: varchar('onet_soc_code', { length: 20 }),
    createdAt: timestamp('created_at').defaultNow().notNull(),
  },
  (table) => [index('job_profiles_user_id_idx').on(table.userId)]
)

export type TaskCategory = 'cognitive' | 'interpersonal' | 'physical' | 'administrative'
export type TaskFrequency = 'daily' | 'weekly' | 'monthly' | 'quarterly'
export type TaskSource = 'onet' | 'llm' | 'user'
export type AITimeframe = 'now' | '1-2y' | '3-5y' | 'unlikely'

export const tasks = pgTable(
  'tasks',
  {
    id: uuid('id').primaryKey().defaultRandom(),
    jobProfileId: uuid('job_profile_id')
      .references(() => jobProfiles.id, { onDelete: 'cascade' })
      .notNull(),
    name: varchar('name', { length: 255 }).notNull(),
    description: text('description'),
    category: varchar('category', { length: 50 }).$type<TaskCategory>().notNull(),
    frequency: varchar('frequency', { length: 20 }).$type<TaskFrequency>().notNull(),
    aiExposureScore: integer('ai_exposure_score'),
    aiReasoning: text('ai_reasoning'),
    aiTimeframe: varchar('ai_timeframe', { length: 10 }).$type<AITimeframe>(),
    source: varchar('source', { length: 10 }).$type<TaskSource>().notNull(),
    createdAt: timestamp('created_at').defaultNow().notNull(),
  },
  (table) => [index('tasks_job_profile_id_idx').on(table.jobProfileId)]
)

export type ValidationVote = 'agree' | 'disagree' | 'edit'

export const taskValidations = pgTable(
  'task_validations',
  {
    id: uuid('id').primaryKey().defaultRandom(),
    taskId: uuid('task_id')
      .references(() => tasks.id, { onDelete: 'cascade' })
      .notNull(),
    userId: uuid('user_id')
      .references(() => users.id, { onDelete: 'cascade' })
      .notNull(),
    vote: varchar('vote', { length: 10 }).$type<ValidationVote>().notNull(),
    editedName: varchar('edited_name', { length: 255 }),
    editedDescription: text('edited_description'),
    createdAt: timestamp('created_at').defaultNow().notNull(),
  },
  (table) => [index('task_validations_task_id_idx').on(table.taskId)]
)
