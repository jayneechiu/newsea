import { useState } from "react";
import { Mail, Lock, LogIn } from "lucide-react";
import { useNavigate } from "react-router-dom";

function Login() {
  const navigate = useNavigate();
  const [isLogin, setIsLogin] = useState(true);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);

    // 模拟登录
    setTimeout(() => {
      localStorage.setItem("userEmail", email);
      localStorage.setItem("isLoggedIn", "true");
      setLoading(false);
      navigate("/feed");
    }, 1000);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-newsea-primary via-[#4d7fb3] to-newsea-secondary flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl shadow-2xl w-full max-w-md p-8">
        {/* Logo */}
        <div className="text-center mb-8">
          <Mail className="h-16 w-16 text-newsea-primary mx-auto mb-4" />
          <h1 className="text-3xl font-bold text-newsea-dark">
            Newsea Newsletter
          </h1>
          <p className="text-gray-600 mt-2">
            {isLogin ? "欢迎回来" : "创建您的账户"}
          </p>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              邮箱地址
            </label>
            <div className="relative">
              <Mail className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="your@email.com"
                className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-newsea-primary focus:border-transparent"
                required
              />
            </div>
          </div>

          {isLogin && (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                密码
              </label>
              <div className="relative">
                <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••"
                  className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-newsea-primary focus:border-transparent"
                  required
                />
              </div>
            </div>
          )}

          <button
            type="submit"
            disabled={loading}
            className="w-full btn-primary py-3 text-lg flex items-center justify-center space-x-2 disabled:opacity-50"
          >
            <LogIn className="h-5 w-5" />
            <span>{loading ? "处理中..." : isLogin ? "登录" : "注册"}</span>
          </button>
        </form>

        {/* Toggle */}
        <div className="mt-6 text-center">
          <button
            onClick={() => setIsLogin(!isLogin)}
            className="text-newsea-primary hover:text-blue-700 font-medium"
          >
            {isLogin ? "还没有账户？立即注册" : "已有账户？立即登录"}
          </button>
        </div>

        {/* Demo Hint */}
        <div className="mt-6 p-4 bg-orange-50 rounded-lg">
          <p className="text-sm text-gray-600 text-center">
            💡 演示模式：输入任意邮箱即可登录
          </p>
        </div>
      </div>
    </div>
  );
}

export default Login;
