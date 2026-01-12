import { Link, useLocation, useNavigate } from "react-router-dom";
import { Home, Heart, LogOut, User } from "lucide-react";

interface LayoutProps {
  children: React.ReactNode;
}

function Layout({ children }: LayoutProps) {
  const location = useLocation();
  const navigate = useNavigate();
  const userEmail = localStorage.getItem("userEmail") || "user@example.com";

  const isActive = (path: string) => location.pathname === path;

  const handleLogout = () => {
    localStorage.removeItem("isLoggedIn");
    localStorage.removeItem("userEmail");
    navigate("/login");
  };

  return (
    <div className="min-h-screen flex flex-col">
      {/* Header */}
      <header className="bg-white shadow-sm sticky top-0 z-50">
        <nav className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <Link to="/" className="flex items-center space-x-2">
              <img
                src="/newseaLogo.png"
                alt="Newsea Logo"
                className="h-10 w-10 rounded-full"
              />
              <span className="text-xl font-bold text-newsea-dark">Newsea</span>
            </Link>

            <div className="flex items-center space-x-6">
              <Link
                to="/"
                className={`flex items-center space-x-1 px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                  isActive("/")
                    ? "text-newsea-primary bg-newsea-light"
                    : "text-gray-700 hover:text-newsea-primary hover:bg-gray-50"
                }`}
              >
                <Home className="h-4 w-4" />
                <span>首页</span>
              </Link>
              <Link
                to="/subscriptions"
                className={`flex items-center space-x-1 px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                  isActive("/subscriptions")
                    ? "text-newsea-primary bg-newsea-light"
                    : "text-gray-700 hover:text-newsea-primary hover:bg-gray-50"
                }`}
              >
                <Heart className="h-4 w-4" />
                <span>我的订阅</span>
              </Link>

              {/* User Menu */}
              <div className="flex items-center space-x-3 border-l pl-6">
                <div className="flex items-center space-x-2">
                  <User className="h-5 w-5 text-gray-600" />
                  <span className="text-sm text-gray-700">{userEmail}</span>
                </div>
                <button
                  onClick={handleLogout}
                  className="flex items-center space-x-1 text-gray-600 hover:text-newsea-primary transition-colors"
                >
                  <LogOut className="h-4 w-4" />
                  <span className="text-sm">退出</span>
                </button>
              </div>
            </div>
          </div>
        </nav>
      </header>

      {/* Main Content */}
      <main className="flex-1">{children}</main>

      {/* Footer */}
      <footer className="bg-white border-t border-newsea-border mt-auto">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="text-center">
            <p className="text-gray-500 text-sm">
              © 2026 Newsea · Powered by Reddit API & OpenAI
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
}

export default Layout;
