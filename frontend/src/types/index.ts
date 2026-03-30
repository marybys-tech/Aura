export type Category =
  | "intelligence"
  | "stamina"
  | "sociality"
  | "creativity"
  | "discipline"
  | "wellness";

export interface CategoryMeta {
  color: string;
  glow: string;
  label: string;
  icon: string;
}

export interface User {
  id: string;
  email: string;
  display_name: string;
  avatar_url: string | null;
  oauth_provider: string;
  timezone: string;
  created_at: string;
}

export interface CategoryScore {
  category: Category;
  score: number;
  streak_days: number;
  longest_streak: number;
}

export interface Habit {
  id: string;
  title: string;
  description: string | null;
  category: Category;
  schedule_type: "daily" | "specific_days" | "multiple_daily";
  schedule_days: number[] | null;
  times_per_day: number;
  is_active: boolean;
  created_at: string;
}

export interface HabitCompletion {
  id: string;
  habit_id: string;
  date: string;
  status: "completed" | "skipped";
  completion_count: number;
  points_delta: number;
}

export interface Quest {
  id: string;
  quest_type: "daily" | "weekly";
  title: string;
  description: string;
  target_category: Category;
  bonus_points: number;
  status: "active" | "completed" | "expired";
  issued_date: string;
  expires_at: string;
}

export interface Narration {
  id: string;
  trigger_type: string;
  content: string;
  created_at: string;
}

// API response types
export interface UserWithScores extends User {
  scores: Record<string, number>;
}

export interface DashboardHabit {
  id: string;
  title: string;
  category: Category;
  times_per_day: number;
  completions_today: number;
  status: "pending" | "completed" | "skipped";
}

export interface QuestSummary {
  id: string;
  title: string;
  description: string;
  target_category: Category;
  bonus_points: number;
  quest_type: string;
  status: string;
}

export interface TodayResponse {
  date: string;
  habits: DashboardHabit[];
  scores: Record<string, CategoryScore>;
  active_quests: QuestSummary[];
}

export interface WeekDayStatus {
  date: string;
  status: string | null;
}

export interface WeekHabitRow {
  habit_id: string;
  title: string;
  category: Category;
  days: WeekDayStatus[];
}

export interface WeekResponse {
  start_date: string;
  end_date: string;
  habits: WeekHabitRow[];
  scores: Record<string, CategoryScore>;
  active_quests: QuestSummary[];
}

export interface MonthDaySummary {
  date: string;
  completed: number;
  total: number;
}

export interface MonthResponse {
  month: number;
  year: number;
  days: MonthDaySummary[];
  scores: Record<string, CategoryScore>;
  active_quests: QuestSummary[];
}

export interface StatsResponse {
  scores: Record<string, CategoryScore>;
  total_aura: number;
}

export interface CompletionWithScore {
  completion: HabitCompletion;
  updated_score: CategoryScore;
  narration: Narration | null;
}

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
}
