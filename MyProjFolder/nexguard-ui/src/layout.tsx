import "./index.css";
import { Sidebar } from "@/components/sidebar";

export const metadata = {
  title: "CloudAI Dashboard",
  description: "Fraud & Churn Analytics Dashboard",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex h-screen bg-gray-900 text-white">
      <Sidebar />
      <main className="flex-1 overflow-auto p-6">{children}</main>
    </div>
  );
}