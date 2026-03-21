export type Bindings = {
  DB: D1Database
  CACHE: KVNamespace
  BUCKET?: R2Bucket
  ANTHROPIC_API_KEY: string
}

export type TaskCategory = 'cognitive' | 'interpersonal' | 'physical' | 'administrative'
export type TaskFrequency = 'daily' | 'weekly' | 'monthly' | 'quarterly'
export type AITimeframe = 'now' | '1-2y' | '3-5y' | '5-10y' | '10y+' | 'unlikely'

export interface DecomposedTask {
  name: string
  description: string
  category: TaskCategory
  frequency: TaskFrequency
}

export interface TaskExposureScore {
  taskName: string
  exposureScore: number
  reasoning: string
  timeframe: AITimeframe
}
