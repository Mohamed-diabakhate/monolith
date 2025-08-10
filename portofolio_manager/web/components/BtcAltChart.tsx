"use client";
import {
  PieChart,
  Pie,
  Cell,
  Legend,
  Tooltip,
  ResponsiveContainer,
} from "recharts";

export function BtcAltChart({ btc, alt }: { btc: number; alt: number }) {
  const data = [
    { name: "BTC", value: btc },
    { name: "Alts", value: alt },
  ];
  const COLORS = ["#f7931a", "#3b82f6"];
  return (
    <div className="h-64 w-full">
      <ResponsiveContainer>
        <PieChart>
          <Pie dataKey="value" data={data} outerRadius={90} label>
            {data.map((entry, index) => (
              <Cell
                key={`cell-${index}`}
                fill={COLORS[index % COLORS.length]}
              />
            ))}
          </Pie>
          <Tooltip />
          <Legend />
        </PieChart>
      </ResponsiveContainer>
    </div>
  );
}
