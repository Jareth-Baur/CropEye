import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from "recharts";

interface ChartViewProps {
  data: { disease: string; count: number }[];
}

export const ChartView = ({ data }: ChartViewProps) => (
  <ResponsiveContainer width="100%" height={300}>
    <BarChart data={data}>
      <XAxis dataKey="disease" />
      <YAxis />
      <Tooltip />
      <Bar dataKey="count" fill="#16a34a" />
    </BarChart>
  </ResponsiveContainer>
);
