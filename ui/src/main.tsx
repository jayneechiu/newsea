import React from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter } from "react-router-dom";
import App from "./App";
import "./index.css";

// Restore the deep link that the GitHub Pages 404 page (demo-404.html) redirected from.
const pagesRedirect = sessionStorage.getItem("newsea:redirect");
if (pagesRedirect) {
  sessionStorage.removeItem("newsea:redirect");
  window.history.replaceState(null, "", pagesRedirect);
}

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <BrowserRouter basename={import.meta.env.BASE_URL.replace(/\/$/, "")}>
      <App />
    </BrowserRouter>
  </React.StrictMode>
);
