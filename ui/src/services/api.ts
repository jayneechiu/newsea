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
  timeFilter: string = "day"
) => {
  return apiClient.post("/newsletter/send", {
    subreddit,
    limit,
    time_filter: timeFilter,
  });
};

// Stats
export const getStats = async () => {
  return apiClient.get("/stats");
};

// Subscribe
export const subscribe = async (email: string, subreddits: string[]) => {
  return apiClient.post("/subscribe", {
    email,
    subreddits,
  });
};

export default apiClient;
