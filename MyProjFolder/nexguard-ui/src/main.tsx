// main.tsx (complete working version)
import React from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import "./index.css";
import Dashboard from "./pages/Dashboard";
import Fraud from "./pages/Fraud";
import Churn from "./pages/Churn";
import { Sidebar } from "./components/sidebar";

const Layout = ({ children }: { children: React.ReactNode }) => (
  <div className="flex h-screen bg-gray-900 text-white">
    <Sidebar />
    <main className="flex-1 overflow-auto p-6">{children}</main>
  </div>
);

const root = ReactDOM.createRoot(document.getElementById("root") as HTMLElement);

root.render(
  <React.StrictMode>
    <BrowserRouter future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
      <Layout>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/fraud" element={<Fraud />} />
          <Route path="/churn" element={<Churn />} />
        </Routes>
      </Layout>
    </BrowserRouter>
  </React.StrictMode>
);