import { Routes, Route, Navigate, useLocation } from "react-router-dom";
import Layout from "./components/Layout";
import Login from "./pages/Login";
import Subscriptions from "./pages/Subscriptions";
import Home from "./pages/Home";
import Newsletter from "./pages/Newsletter";
import NewsletterAdmin from "./pages/NewsletterAdmin";
import SignalDetail from "./pages/SignalDetail";
import { useI18n } from "./i18n";

// 简单的认证检查
const ProtectedRoute = ({ children }: { children: React.ReactNode }) => {
  const isLoggedIn = localStorage.getItem("isLoggedIn") === "true";
  return isLoggedIn ? <>{children}</> : <Navigate to="/login" replace />;
};

function App() {
  useLocation(); // re-render on navigation so login/logout state is re-read
  const { t } = useI18n();
  const isLoggedIn = localStorage.getItem("isLoggedIn") === "true";

  return (
    <>
      {import.meta.env.VITE_USE_MOCK_DATA === "true" && (
        <div className="bg-newsea-primary px-4 py-1.5 text-center text-xs font-semibold text-white sm:text-sm">
          {t("demoMode")}
        </div>
      )}
      <Routes>
        {/* 公开路由 */}
        <Route path="/login" element={<Login />} />
        <Route path="/newsletter" element={<Newsletter />} />
        <Route path="/newsletter/admin" element={<NewsletterAdmin />} />
        <Route path="/signals/:cardId" element={<SignalDetail />} />

        {/* 首页：未登录显示公共热帖，登录后显示订阅内容 */}
        <Route
          path="/"
          element={
            isLoggedIn ? (
              <Layout>
                <Home />
              </Layout>
            ) : (
              <Home />
            )
          }
        />

        {/* 需要登录的路由 */}
        <Route
          path="/subscriptions"
          element={
            <ProtectedRoute>
              <Layout>
                <Subscriptions />
              </Layout>
            </ProtectedRoute>
          }
        />
      </Routes>
    </>
  );
}

export default App;
