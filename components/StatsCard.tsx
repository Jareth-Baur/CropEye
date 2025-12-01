interface StatsCardProps {
  title: string;
  value: number | string;
}

export const StatsCard = ({ title, value }: StatsCardProps) => (
  <div className="bg-white shadow rounded p-4">
    <div className="text-gray-500">{title}</div>
    <div className="text-2xl font-bold">{value}</div>
  </div>
);
