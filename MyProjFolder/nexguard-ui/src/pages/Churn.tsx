import React, { useEffect, useState } from "react";
import { fetchChurnData } from "@/api/api";
import ChartCard from "../components/ChartCard";
import {
  Chart as ChartJS,
  ArcElement,
  Tooltip,
  Legend,
  CategoryScale,
  LinearScale,
  BarElement,
  PointElement,
  LineElement,
} from "chart.js";
import { Pie, Bar, Line } from "react-chartjs-2";

ChartJS.register(
  ArcElement,
  Tooltip,
  Legend,
  CategoryScale,
  LinearScale,
  BarElement,
  PointElement,
  LineElement
);

interface ChurnRecord {
  PredictedChurn: number;
  Processed: number;
  churn_reason?: string;
  satisfactionscore?: number;
  tenure_months?: number;
  amount?: number;
  cltv?: number;
}

const Churn = () => {
  const [churnData, setChurnData] = useState<ChurnRecord[]>([]);

  useEffect(() => {
    fetchChurnData().then((data) => setChurnData(data));
  }, []);

  if (churnData.length === 0) return <p>Loading...</p>;

  // === Pie Chart: Churn vs Retain ===
  const processed = churnData.reduce((sum, rec) => sum + (rec.Processed || 0), 0);
  const numChurn = churnData.reduce((sum, rec) => sum + rec.PredictedChurn, 0);
  const numRetain = processed - numChurn;

  const churnPieData = {
    labels: ["Churn", "Retain"],
    datasets: [
      {
        data: [numChurn, numRetain],
        backgroundColor: ["#f87171", "#34d399"], // red/green
      },
    ],
  };

  // === Bar Chart: Churn Reasons ===
  const churnReasonsCounts: { [key: string]: number } = {};
  churnData.forEach((rec) => {
    if (rec.churn_reason) {
      churnReasonsCounts[rec.churn_reason] = (churnReasonsCounts[rec.churn_reason] || 0) + 1;
    }
  });

  const churnReasonsData = {
    labels: Object.keys(churnReasonsCounts),
    datasets: [
      {
        label: "Churn Reasons",
        data: Object.values(churnReasonsCounts),
        backgroundColor: "#8b5cf6", // purple
      },
    ],
  };

  // === Line Chart: Customer Satisfaction / Sentiment Trends ===
  const satisfactionBuckets: { [key: number]: number[] } = {};
  churnData.forEach((rec, idx) => {
    const bucket = Math.floor(idx / 20) * 20;
    if (!satisfactionBuckets[bucket]) satisfactionBuckets[bucket] = [];
    if (rec.satisfactionscore !== undefined) satisfactionBuckets[bucket].push(rec.satisfactionscore);
  });

  const sentimentData = {
    labels: Object.keys(satisfactionBuckets),
    datasets: [
      {
        label: "Avg Satisfaction Score",
        data: Object.values(satisfactionBuckets).map(
          (arr) => arr.reduce((a, b) => a + b, 0) / arr.length
        ),
        borderColor: "#3b82f6",
        backgroundColor: "#3b82f6",
        fill: false,
        tension: 0.4,
      },
    ],
  };

  // === Line Chart: Churn vs Tenure ===
  const tenureMap: { [key: number]: number[] } = {};
  churnData.forEach((rec) => {
    if (rec.tenure_months !== undefined) {
      if (!tenureMap[rec.tenure_months]) tenureMap[rec.tenure_months] = [];
      tenureMap[rec.tenure_months].push(rec.PredictedChurn);
    }
  });

  const churnOverTenureData = {
    labels: Object.keys(tenureMap),
    datasets: [
      {
        label: "Churn Rate",
        data: Object.values(tenureMap).map(
          (arr) => arr.reduce((a, b) => a + b, 0) / arr.length
        ),
        borderColor: "#f472b6",
        backgroundColor: "#f472b6",
        fill: false,
        tension: 0.4,
      },
    ],
  };

  // === Bar Chart: CLTV Distribution ===
  const cltvBins = 10;
  const cltvValues = churnData.map((rec) => rec.cltv).filter((v) => v !== undefined) as number[];
  const cltvMin = Math.min(...cltvValues);
  const cltvMax = Math.max(...cltvValues);
  const binSize = (cltvMax - cltvMin) / cltvBins;
  const cltvCounts = Array(cltvBins).fill(0);

  cltvValues.forEach((v) => {
    const bin = Math.min(Math.floor((v - cltvMin) / binSize), cltvBins - 1);
    cltvCounts[bin]++;
  });

  const cltvData = {
    labels: Array.from({ length: cltvBins }, (_, i) => `${(cltvMin + i * binSize).toFixed(1)}-${(cltvMin + (i + 1) * binSize).toFixed(1)}`),
    datasets: [
      {
        label: "Customer Count",
        data: cltvCounts,
        backgroundColor: "#10b981",
      },
    ],
  };

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
      <ChartCard title="Churn vs Retain">{<Pie data={churnPieData} />}</ChartCard>
      <ChartCard title="Churn Reasons">{<Bar data={churnReasonsData} />}</ChartCard>
      <ChartCard title="Customer Satisfaction">{<Line data={sentimentData} />}</ChartCard>
      <ChartCard title="Churn vs Tenure">{<Line data={churnOverTenureData} />}</ChartCard>
      <ChartCard title="CLTV Distribution">{<Bar data={cltvData} />}</ChartCard>
    </div>
  );
};

export default Churn;
