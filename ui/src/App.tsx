import { Routes, Route, Navigate } from "react-router-dom";
import Layout from "./components/Layout";
import Login from "./pages/Login";
import Subscriptions from "./pages/Subscriptions";
import Home from "./pages/Home";

// 简单的认证检查
const ProtectedRoute = ({ children }: { children: React.ReactNode }) => {
  const isLoggedIn = localStorage.getItem("isLoggedIn") === "true";
  return isLoggedIn ? <>{children}</> : <Navigate to="/login" replace />;
};

function App() {
  const isLoggedIn = localStorage.getItem("isLoggedIn") === "true";

  return (
    <Routes>
      {/* 公开路由 */}
      <Route path="/login" element={<Login />} />

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
  );
}

export default App;
