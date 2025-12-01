"use client"; // <--- Add this at the very top

import { NavBar } from "../components/NavBar";
import { StatsCard } from "../components/StatsCard";
import { MapView } from "../components/Mapview";
import { useFetchData } from "../hooks/useFetchData";

export default function Dashboard() {
  const { data, loading } = useFetchData();

  if (loading) return <div className="p-4">Loading...</div>;

  const totalDetections = data.length;
  const healthyCount = data.filter((d) => d.disease === "Healthy").length;

  return (
    <div className="min-h-screen bg-gray-100">
      <NavBar />
      <div className="p-4 grid grid-cols-1 md:grid-cols-3 gap-4">
        <StatsCard title="Total Detections" value={totalDetections} />
        <StatsCard title="Healthy Plants" value={healthyCount} />
        <StatsCard title="Diseased Plants" value={totalDetections - healthyCount} />
      </div>
      <div className="p-4">
        <MapView data={data} />
      </div>
    </div>
  );
}
