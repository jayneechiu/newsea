import { useState, useEffect } from "react";
import {
  Plus,
  X,
  Search,
  TrendingUp,
  Sparkles,
  MessageCircle,
} from "lucide-react";

interface Subreddit {
  name: string;
  subscribers: number;
  description: string;
  category: string;
}

interface DemoPost {
  id: string;
  title: string;
  author: string;
  score: number;
  comments: number;
  subreddit: string;
}

// Demo 热帖数据
const DEMO_POSTS: DemoPost[] = [
  {
    id: "1",
    title: "Building a Full-Stack App with React, TypeScript, and Tailwind CSS",
    author: "codingmaster",
    score: 2456,
    comments: 234,
    subreddit: "reactjs",
  },
  {
    id: "2",
    title: "Advanced Python Tips: 10 Hidden Features You Should Know",
    author: "pythonista",
    score: 3829,
    comments: 412,
    subreddit: "python",
  },
  {
    id: "3",
    title: "AI Breakthrough: New Model Surpasses GPT-4 in Reasoning Tasks",
    author: "ai_researcher",
    score: 5621,
    comments: 892,
    subreddit: "machinelearning",
  },
];

// 模拟数据
const CATEGORIES = [
  "Programming",
  "Tech news",
  "AI",
  "Data science",
  "Frontend",
  "Backend",
  "Game dev",
  "Other",
];

const POPULAR_SUBREDDITS: Subreddit[] = [
  {
    name: "python",
    subscribers: 1200000,
    description: "The Python language",
    category: "Programming",
  },
  {
    name: "javascript",
    subscribers: 980000,
    description: "All things JavaScript",
    category: "Frontend",
  },
  {
    name: "reactjs",
    subscribers: 650000,
    description: "The React framework",
    category: "Frontend",
  },
  {
    name: "webdev",
    subscribers: 870000,
    description: "Web development",
    category: "Frontend",
  },
  {
    name: "machinelearning",
    subscribers: 760000,
    description: "Machine learning",
    category: "AI",
  },
  {
    name: "datascience",
    subscribers: 540000,
    description: "Data science",
    category: "Data science",
  },
  {
    name: "programming",
    subscribers: 1500000,
    description: "Programming discussion",
    category: "Programming",
  },
  {
    name: "learnprogramming",
    subscribers: 890000,
    description: "Learning to code",
    category: "Programming",
  },
  {
    name: "technology",
    subscribers: 2100000,
    description: "Technology news",
    category: "Tech news",
  },
  {
    name: "artificial",
    subscribers: 420000,
    description: "AI technology",
    category: "AI",
  },
];

function Subscriptions() {
  const [subscribedSubs, setSubscribedSubs] = useState<string[]>([
    "python",
    "javascript",
    "reactjs",
  ]);
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedCategory, setSelectedCategory] = useState("All");
  const [suggestions, setSuggestions] = useState<Subreddit[]>([]);

  useEffect(() => {
    // 根据搜索和分类过滤推荐
    let filtered = POPULAR_SUBREDDITS.filter(
      (sub) => !subscribedSubs.includes(sub.name)
    );

    if (searchQuery) {
      filtered = filtered.filter(
        (sub) =>
          sub.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
          sub.description.toLowerCase().includes(searchQuery.toLowerCase())
      );
    }

    if (selectedCategory !== "All") {
      filtered = filtered.filter((sub) => sub.category === selectedCategory);
    }

    setSuggestions(filtered);
  }, [searchQuery, selectedCategory, subscribedSubs]);

  const handleSubscribe = (subName: string) => {
    setSubscribedSubs((prev) => [...prev, subName]);
  };

  const handleUnsubscribe = (subName: string) => {
    setSubscribedSubs((prev) => prev.filter((s) => s !== subName));
  };

  const formatNumber = (num: number) => {
    if (num >= 1000000) return `${(num / 1000000).toFixed(1)}M`;
    if (num >= 1000) return `${(num / 1000).toFixed(0)}K`;
    return num.toString();
  };

  return (
    <div className="min-h-screen bg-newsea-beige py-6">
      <div className="max-w-6xl mx-auto px-4">
        <h1 className="text-3xl font-bold mb-6">Manage subscriptions</h1>

        {/* 我的订阅 */}
        <section className="mb-8">
          <h2 className="text-xl font-semibold mb-4 flex items-center">
            <Sparkles className="h-5 w-5 mr-2 text-newsea-primary" />
            My subscriptions ({subscribedSubs.length})
          </h2>
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3">
            {subscribedSubs.map((sub) => (
              <div
                key={sub}
                className="bg-white rounded-lg p-4 shadow-sm flex items-center justify-between group hover:shadow-md transition-shadow"
              >
                <div>
                  <h3 className="font-semibold text-gray-900">r/{sub}</h3>
                </div>
                <button
                  onClick={() => handleUnsubscribe(sub)}
                  className="opacity-0 group-hover:opacity-100 transition-opacity text-red-500 hover:text-red-700"
                >
                  <X className="h-5 w-5" />
                </button>
              </div>
            ))}
          </div>
        </section>

        {/* 搜索和分类 */}
        <section className="mb-6">
          <div className="bg-white rounded-lg shadow-sm p-4">
            <div className="flex flex-col md:flex-row gap-4">
              {/* 搜索框 */}
              <div className="flex-1 relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
                <input
                  type="text"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  placeholder="Search subreddits..."
                  className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-newsea-primary focus:border-transparent"
                />
              </div>

              {/* 分类选择 */}
              <div className="flex gap-2 overflow-x-auto pb-2 md:pb-0">
                <button
                  onClick={() => setSelectedCategory("All")}
                  className={`px-4 py-2 rounded-lg whitespace-nowrap transition-colors ${
                    selectedCategory === "All"
                      ? "bg-newsea-primary text-white"
                      : "bg-gray-100 text-gray-700 hover:bg-gray-200"
                  }`}
                >
                  All
                </button>
                {CATEGORIES.map((cat) => (
                  <button
                    key={cat}
                    onClick={() => setSelectedCategory(cat)}
                    className={`px-4 py-2 rounded-lg whitespace-nowrap transition-colors ${
                      selectedCategory === cat
                        ? "bg-newsea-primary text-white"
                        : "bg-gray-100 text-gray-700 hover:bg-gray-200"
                    }`}
                  >
                    {cat}
                  </button>
                ))}
              </div>
            </div>
          </div>
        </section>

        {/* Demo 热帖卡片 */}
        <section className="mb-8">
          <h2 className="text-xl font-semibold mb-4 flex items-center">
            <TrendingUp className="h-5 w-5 mr-2 text-newsea-accent" />
            Trending posts preview
          </h2>
          <div className="grid md:grid-cols-2 gap-4">
            {DEMO_POSTS.map((post) => (
              <div
                key={post.id}
                className="bg-white rounded-xl shadow-sm hover:shadow-md transition-shadow overflow-hidden border border-gray-100"
              >
                <div className="p-4">
                  {/* Subreddit Tag */}
                  <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-newsea-primary bg-opacity-10 text-newsea-primary mb-3">
                    r/{post.subreddit}
                  </span>

                  {/* Title */}
                  <h3 className="text-base font-semibold text-gray-900 mb-3 line-clamp-2">
                    {post.title}
                  </h3>

                  {/* Meta */}
                  <div className="flex items-center justify-between text-sm text-gray-600">
                    <div className="flex items-center space-x-3">
                      <div className="flex items-center space-x-1">
                        <TrendingUp className="h-3.5 w-3.5 text-newsea-accent" />
                        <span className="font-semibold">{post.score}</span>
                      </div>
                      <div className="flex items-center space-x-1">
                        <MessageCircle className="h-3.5 w-3.5" />
                        <span>{post.comments}</span>
                      </div>
                    </div>
                    <span className="text-gray-500 text-xs">
                      u/{post.author}
                    </span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </section>

        {/* 推荐订阅 */}
        <section>
          <h2 className="text-xl font-semibold mb-4 flex items-center">
            <Search className="h-5 w-5 mr-2 text-newsea-primary" />
            Discover more
          </h2>
          <div className="grid md:grid-cols-2 gap-4">
            {suggestions.map((sub) => (
              <div
                key={sub.name}
                className="bg-white rounded-lg p-4 shadow-sm hover:shadow-md transition-shadow"
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <h3 className="font-semibold text-lg text-gray-900">
                      r/{sub.name}
                    </h3>
                    <p className="text-sm text-gray-600 mt-1">
                      {sub.description}
                    </p>
                    <div className="flex items-center space-x-4 mt-2 text-sm text-gray-500">
                      <span className="flex items-center">
                        <TrendingUp className="h-4 w-4 mr-1" />
                        {formatNumber(sub.subscribers)} subscribers
                      </span>
                      <span className="px-2 py-0.5 bg-gray-100 rounded-full text-xs">
                        {sub.category}
                      </span>
                    </div>
                  </div>
                  <button
                    onClick={() => handleSubscribe(sub.name)}
                    className="ml-4 flex items-center space-x-1 bg-newsea-primary text-white px-4 py-2 rounded-lg hover:bg-[#2d5783] transition-colors shadow-sm hover:shadow-md"
                  >
                    <Plus className="h-4 w-4" />
                    <span>Subscribe</span>
                  </button>
                </div>
              </div>
            ))}
          </div>

          {suggestions.length === 0 && (
            <div className="text-center py-12 text-gray-500">
              No matching subreddits found
            </div>
          )}
        </section>
      </div>
    </div>
  );
}

export default Subscriptions;
