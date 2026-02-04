// src/pages/Fraud.tsx
import React, { useEffect, useState } from "react";
import { fetchFraudData } from "@/api/api";
import { Pie } from "react-chartjs-2";
import ChartCard from "../components/ChartCard";
import {
  Chart as ChartJS,
  ArcElement,
  Tooltip,
  Legend,
} from "chart.js";

ChartJS.register(ArcElement, Tooltip, Legend);

const Fraud = () => {
  const [fraudData, setFraudData] = useState<any[]>([]);

  useEffect(() => {
    fetchFraudData().then((data) => setFraudData(data));
  }, []);

  const numFraud = fraudData.filter((d) => d.Meta_Prediction === 1).length;
  const numNoFraud = fraudData.length - numFraud;

  const pieData = {
    labels: ["Fraud", "Not Fraud"],
    datasets: [
      {
        data: [numFraud, numNoFraud],
        backgroundColor: ["#f87171", "#34d399"], // red/green
      },
    ],
  };

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
      <ChartCard title="Fraud Distribution">
        <Pie data={pieData} />
      </ChartCard>
    </div>
  );
};

export default Fraud;
