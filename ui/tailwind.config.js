/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        newsea: {
          primary: "#3a6ea5", // Newsletter 品牌蓝
          secondary: "#91a4bd", // 灰蓝色
          dark: "#0f172a", // 深蓝黑
          light: "#dfe9f3", // 浅蓝背景
          accent: "#eef3f9", // 罗经区浅蓝
          beige: "#f3efe7", // 米色背景
          border: "#e6dfd1", // 米色边框
        },
      },
    },
  },
  plugins: [],
};
