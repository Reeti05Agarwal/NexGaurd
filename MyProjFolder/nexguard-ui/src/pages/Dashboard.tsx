import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import ChartCard from "../components/ChartCard";
import { fetchFraudData, fetchChurnData } from "@/api/api";
import { Pie } from "react-chartjs-2";
import {
  Chart as ChartJS,
  ArcElement,
  Tooltip,
  Legend,
} from "chart.js";

ChartJS.register(ArcElement, Tooltip, Legend);

interface FraudRecord {
  Meta_Prediction: number;
  TransactionAmt?: number;
}

interface ChurnRecord {
  PredictedChurn: number;
  Processed: number;
}

const Dashboard = () => {
  const [fraudData, setFraudData] = useState<FraudRecord[]>([]);
  const [churnData, setChurnData] = useState<ChurnRecord[]>([]);

  useEffect(() => {
    fetchFraudData().then((data) => setFraudData(data));
    fetchChurnData().then((data) => setChurnData(data));
  }, []);

  if (!fraudData.length || !churnData.length) return <p>Loading...</p>;

  // === Fraud Summary ===
  const totalFraud = fraudData.length;
  const numFraud = fraudData.reduce((sum, rec) => sum + rec.Meta_Prediction, 0);
  const numNotFraud = totalFraud - numFraud;

  const fraudPieData = {
    labels: ["Fraud", "Not Fraud"],
    datasets: [
      {
        data: [numFraud, numNotFraud],
        backgroundColor: ["#f87171", "#34d399"],
      },
    ],
  };

  // === Churn Summary ===
  const processed = churnData.reduce((sum, rec) => sum + (rec.Processed || 0), 0);
  const numChurn = churnData.reduce((sum, rec) => sum + rec.PredictedChurn, 0);
  const numRetain = processed - numChurn;

  const churnPieData = {
    labels: ["Churn", "Retain"],
    datasets: [
      {
        data: [numChurn, numRetain],
        backgroundColor: ["#f87171", "#34d399"],
      },
    ],
  };

  return (
    <div className="p-6 grid grid-cols-1 md:grid-cols-2 gap-6">
      {/* Fraud Card */}
      <Link to="/fraud">
        <ChartCard title="Fraud Summary">
          <p className="text-white font-bold mb-2">
            Total Transactions: {totalFraud} <br />
            Fraud: {numFraud} <br />
            Not Fraud: {numNotFraud}
          </p>
          <Pie data={fraudPieData} />
        </ChartCard>
      </Link>

      {/* Churn Card */}
      <Link to="/churn">
        <ChartCard title="Churn Summary">
          <p className="text-white font-bold mb-2">
            Total Records: {processed} <br />
            Churned: {numChurn} <br />
            Retained: {numRetain}
          </p>
          <Pie data={churnPieData} />
        </ChartCard>
      </Link>
    </div>
  );
};

export default Dashboard;


// 'use client'

// import { useEffect, useState } from 'react'
// import { Bar } from 'react-chartjs-2'

// export default function Dashboard() {
//   const [fraudStats, setFraudStats] = useState<{ total: number; frauds: number } | null>(null)

//   useEffect(() => {
//     fetch('http://localhost:3000/fraud/stats') // your Express API
//       .then((res) => res.json())
//       .then((data) => setFraudStats(data))
//   }, [])

//   if (!fraudStats) return <p>Loading...</p>

//   const data = {
//     labels: ['Fraud', 'Non-Fraud'],
//     datasets: [
//       {
//         label: 'Transactions',
//         data: [fraudStats.frauds, fraudStats.total - fraudStats.frauds],
//         backgroundColor: ['#f87171', '#34d399'],
//       },
//     ],
//   }

//   return <Bar data={data} />
// }
