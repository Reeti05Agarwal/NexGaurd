import express from "express";
import mysql from "mysql2/promise";
import cors from "cors";
import dotenv from "dotenv";

dotenv.config();
const app = express();
app.use(cors());

const db = mysql.createPool({
  host: process.env.DB_HOST,
  user: process.env.DB_USER,
  password: process.env.DB_PASS,
  database: process.env.DB_NAME,
});

app.get("/fraud/stats", async (req, res) => {
  const [rows] = await db.query(`
    SELECT 
      COUNT(*) AS total,
      SUM(Meta_Prediction = 1) AS frauds
    FROM FraudTable
  `);
  res.json(rows[0]);
});

app.listen(3000, () => console.log("API running on 3000"));
