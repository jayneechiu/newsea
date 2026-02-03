import { useEffect, useState } from "react";
import {
  TrendingUp,
  MessageCircle,
  ExternalLink,
  RefreshCw,
  LogIn,
} from "lucide-react";
import { Link } from "react-router-dom";
import { getPosts, getRecentPostsFromDB, getPostsWithSummaries } from "@/services/api";

interface Post {
  id: string;
  title: string;
  author: string;
  score: number;
  num_comments: number;
  permalink: string;
  subreddit: string;
  thumbnail?: string;
  gpt_summary?: string;
}

// 公共热门 subreddits（未登录用户看到的）
const PUBLIC_SUBS = [
  "programming",
  "technology",
  "python",
  "javascript",
  "artificial",
];



function Home() {
  const isLoggedIn = localStorage.getItem("isLoggedIn") === "true";
  const [posts, setPosts] = useState<Post[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchPublicFeed = async () => {
    setLoading(true);
    try {
      // 优先从数据库获取最近的帖子
      const dbData = await getRecentPostsFromDB(30, 50);
      if (dbData && dbData.posts && dbData.posts.length > 0) {
        const dbPosts = dbData.posts.map((p: any) => ({
          id: p.id,
          title: p.title,
          author: p.author || 'unknown',
          score: p.score || 0,
          num_comments: p.num_comments || 0,
          permalink: p.url || '',
          subreddit: p.subreddit || 'unknown',
          gpt_summary: p.gpt_summary,
        }));
        setPosts(dbPosts.slice(0, 12));
        setLoading(false);
        return;
      }
      
      // 数据库没有数据，从Reddit API实时获取
      const allPosts: Post[] = [];
      for (const sub of PUBLIC_SUBS) {
        const data = await getPosts(sub, 3, "day");
        if (data && data.posts) {
          allPosts.push(
            ...data.posts.map((p: any) => ({ ...p, subreddit: sub }))
          );
        }
      }
      allPosts.sort((a, b) => b.score - a.score);
      setPosts(allPosts.slice(0, 12));
    } catch (err) {
      console.error("Failed to fetch public feed:", err);
      setPosts([]);
    } finally {
      setLoading(false);
    }
  };

  const fetchSubscribedFeed = async () => {
    setLoading(true);
    try {
      // 优先从数据库获取有GPT摘要的帖子
      const summaryData = await getPostsWithSummaries(20);
      if (summaryData && summaryData.posts && summaryData.posts.length > 0) {
        const dbPosts = summaryData.posts.map((p: any) => ({
          id: p.id,
          title: p.title,
          author: p.author || 'unknown',
          score: p.score || 0,
          num_comments: p.num_comments || 0,
          permalink: p.url || '',
          subreddit: p.subreddit || 'unknown',
          gpt_summary: p.gpt_summary,
        }));
        setPosts(dbPosts);
        setLoading(false);
        return;
      }
      
      // 如果数据库没有GPT摘要的帖子，尝试获取最近的帖子
      const recentData = await getRecentPostsFromDB(30, 20);
      if (recentData && recentData.posts && recentData.posts.length > 0) {
        const dbPosts = recentData.posts.map((p: any) => ({
          id: p.id,
          title: p.title,
          author: p.author || 'unknown',
          score: p.score || 0,
          num_comments: p.num_comments || 0,
          permalink: p.url || '',
          subreddit: p.subreddit || 'unknown',
          gpt_summary: p.gpt_summary,
        }));
        setPosts(dbPosts);
        setLoading(false);
        return;
      }
      
      // 数据库没有数据，显示空状态
      setPosts([]);
    } catch (err) {
      console.error("Failed to fetch subscribed feed:", err);
      setPosts([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (isLoggedIn) {
      fetchSubscribedFeed();
    } else {
      fetchPublicFeed();
    }
  }, [isLoggedIn]);

  return (
    <div className="min-h-screen bg-newsea-beige">
      {!isLoggedIn && (
        <header className="bg-white shadow-sm sticky top-0 z-50">
          <nav className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between items-center h-16">
              <div className="flex items-center space-x-2">
                <img
                  src="/newseaLogo.png"
                  alt="Newsea Logo"
                  className="h-10 w-10 rounded-full"
                />
                <span className="text-xl font-bold text-newsea-dark">
                  Newsea
                </span>
              </div>
              <Link
                to="/login"
                className="flex items-center space-x-2 bg-newsea-primary text-white px-6 py-2 rounded-lg hover:bg-[#2d5783] transition-colors font-semibold"
              >
                <LogIn className="h-5 w-5" />
                <span>登录 / 注册</span>
              </Link>
            </div>
          </nav>
        </header>
      )}

      <main
        className={
          isLoggedIn
            ? "max-w-6xl mx-auto px-4 py-6"
            : "max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8"
        }
      >
        {!isLoggedIn && (
          <div className="bg-gradient-to-r from-newsea-primary via-[#4d7fb3] to-newsea-secondary text-white rounded-2xl p-8 mb-8 text-center">
            <h1 className="text-4xl font-bold mb-3">Newsea · 每日精选热帖</h1>
            <p className="text-lg text-blue-100 mb-6">
              发现来自 Reddit 的热门内容 · 登录后可订阅感兴趣的话题
            </p>
            <Link
              to="/login"
              className="inline-flex items-center space-x-2 bg-white text-newsea-primary font-bold py-3 px-8 rounded-lg hover:bg-gray-100 transition-colors"
            >
              <LogIn className="h-5 w-5" />
              <span>登录以订阅更多</span>
            </Link>
          </div>
        )}

        {loading && (
          <div className="flex items-center justify-center py-20">
            <RefreshCw className="h-12 w-12 text-newsea-primary animate-spin" />
          </div>
        )}

        {!loading && (
          <div>
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-2xl font-bold text-newsea-dark flex items-center">
                <TrendingUp className="h-6 w-6 mr-2 text-newsea-primary" />
                {isLoggedIn ? "我的订阅" : "今日热门"}
              </h2>
              <button
                onClick={isLoggedIn ? fetchSubscribedFeed : fetchPublicFeed}
                className="flex items-center space-x-2 text-newsea-primary hover:text-[#2d5783] transition-colors"
              >
                <RefreshCw className="h-5 w-5" />
                <span>刷新</span>
              </button>
            </div>

            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
              {posts.map((post) => (
                <article
                  key={post.id}
                  className="bg-white rounded-xl shadow-sm hover:shadow-md transition-shadow overflow-hidden border border-newsea-border"
                >
                  <div className="px-4 pt-4">
                    <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-newsea-primary bg-opacity-10 text-newsea-primary">
                      r/{post.subreddit}
                    </span>
                  </div>

                  <div className="p-4">
                    <h3 className="text-base font-semibold text-gray-900 mb-3 line-clamp-3">
                      {post.title}
                    </h3>

                    {post.gpt_summary && (
                      <p className="text-sm text-gray-600 mb-3 line-clamp-5">
                        {post.gpt_summary}
                      </p>
                    )}

                    <div className="flex items-center justify-between text-sm text-gray-600">
                      <div className="flex items-center space-x-4">
                        <div className="flex items-center space-x-1">
                          <TrendingUp className="h-4 w-4 text-orange-500" />
                          <span className="font-semibold">{post.score}</span>
                        </div>
                        <div className="flex items-center space-x-1">
                          <MessageCircle className="h-4 w-4 text-gray-500" />
                          <span>{post.num_comments}</span>
                        </div>
                      </div>
                      <span className="text-gray-500 text-xs">
                        u/{post.author}
                      </span>
                    </div>

                    <a
                      href={post.permalink.startsWith('http') ? post.permalink : `https://reddit.com${post.permalink}`}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="mt-3 inline-flex items-center space-x-1 text-newsea-primary hover:text-[#2d5783] font-medium transition-colors text-sm"
                    >
                      <span>查看详情</span>
                      <ExternalLink className="h-3.5 w-3.5" />
                    </a>
                  </div>
                </article>
              ))}
            </div>

            {posts.length === 0 && !loading && (
              <div className="text-center py-12">
                <p className="text-gray-500">暂无内容</p>
              </div>
            )}
          </div>
        )}
      </main>

      {!isLoggedIn && (
        <footer className="bg-white border-t border-newsea-border mt-12">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
            <div className="text-center">
              <p className="text-gray-500 text-sm">
                © 2026 Newsea · Powered by Reddit API & OpenAI
              </p>
            </div>
          </div>
        </footer>
      )}
    </div>
  );
}

export default Home;
