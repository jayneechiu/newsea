import axios from "axios";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "/api";

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    "Content-Type": "application/json",
  },
});

// Response interceptor
apiClient.interceptors.response.use(
  (response) => response.data,
  (error) => {
    console.error("API Error:", error);
    return Promise.reject(error);
  }
);

// Health check
export const getHealth = async () => {
  return apiClient.get("/health");
};

// Posts
export const getPosts = async (
  subreddit: string,
  limit: number = 10,
  timeFilter: string = "day"
): Promise<any> => {
  return apiClient.get(`/posts/${subreddit}`, {
    params: { limit, time_filter: timeFilter },
  });
};

// Get recent posts from database
export const getRecentPostsFromDB = async (
  days: number = 7,
  limit: number = 50
): Promise<any> => {
  return apiClient.get("/posts/db/recent", {
    params: { days, limit },
  });
};

// Get posts with GPT summaries
export const getPostsWithSummaries = async (limit: number = 20): Promise<any> => {
  return apiClient.get("/posts/db/with-summaries", {
    params: { limit },
  });
};

// Newsletter
export const sendNewsletter = async (
  subreddit: string,
  limit: number = 10,
  timeFilter: string = "day",
  adminKey?: string
) => {
  return apiClient.post("/newsletter/send", {
    subreddit,
    limit,
    time_filter: timeFilter,
  }, {
    headers: adminKey ? { "X-Newsea-Admin-Key": adminKey } : undefined,
  });
};

export type NewsletterPost = {
  id: string;
  title: string;
  subreddit: string;
  permalink: string;
  newsletter_teaser?: string;
  gpt_summary?: string;
  selftext?: string;
  trend_label?: string;
};

export type NewsletterDraft = {
  id: string;
  subreddit: string;
  time_filter: string;
  posts: NewsletterPost[];
  editor_words: string;
  uses_ai: boolean;
  generation_mode?: "ai" | "mixed" | "fallback";
  status: "draft" | "sending" | "sent" | "failed";
  created_at: string;
  sent_at?: string | null;
};

export const getLatestNewsletter = async (): Promise<{
  id: string;
  subreddit: string;
  posts: NewsletterPost[];
  editor_words: string;
  published_at: string;
}> => {
  return apiClient.get("/newsletter/latest") as unknown as Promise<{
    id: string;
    subreddit: string;
    posts: NewsletterPost[];
    editor_words: string;
    published_at: string;
  }>;
};

export const createNewsletterDraft = async (
  subreddit: string,
  adminKey: string,
  limit: number = 4,
  timeFilter: string = "week"
): Promise<{ status: string; draft: NewsletterDraft }> => {
  return apiClient.post("/admin/newsletter/drafts", {
    subreddit,
    limit,
    time_filter: timeFilter,
  }, {
    headers: { "X-Newsea-Admin-Key": adminKey },
    timeout: 90000,
  }) as unknown as Promise<{ status: string; draft: NewsletterDraft }>;
};

export const sendNewsletterDraft = async (draftId: string, adminKey: string) => {
  return apiClient.post(`/admin/newsletter/drafts/${draftId}/send`, {}, {
    headers: { "X-Newsea-Admin-Key": adminKey },
  });
};

// Stats
export const getStats = async () => {
  return apiClient.get("/stats");
};

// Subscribe
export const subscribe = async (email: string, subreddits: string[], name?: string) => {
  return apiClient.post("/newsletter/subscriptions", {
    email,
    subreddits,
    name,
  });
};

export type NewsletterSubscription = {
  id: number;
  email: string;
  name?: string | null;
  subreddits: string[];
  status: "pending" | "approved" | "rejected";
  requested_at: string;
};

export const getNewsletterSubscriptions = async (
  adminKey: string,
  status: NewsletterSubscription["status"] = "pending"
): Promise<{ count: number; subscriptions: NewsletterSubscription[] }> => {
  return apiClient.get("/admin/newsletter/subscriptions", {
    params: { status },
    headers: { "X-Newsea-Admin-Key": adminKey },
  }) as unknown as Promise<{ count: number; subscriptions: NewsletterSubscription[] }>;
};

export const reviewNewsletterSubscription = async (
  id: number,
  action: "approve" | "reject",
  adminKey: string
) => {
  return apiClient.post(`/admin/newsletter/subscriptions/${id}/${action}`, {}, {
    headers: { "X-Newsea-Admin-Key": adminKey },
  });
};

export default apiClient;
