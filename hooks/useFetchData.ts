import { useEffect, useState } from "react";
import { fetchDetections } from "../utils/apiClient";

export const useFetchData = () => {
  const [data, setData] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const dummyData = [
      { id: "1", lat: 7.124, lon: 126.447, disease: "Northern Leaf Blight", confidence: 0.93 },
      { id: "2", lat: 7.125, lon: 126.448, disease: "Healthy", confidence: 1 },
    ];

    setData(dummyData);
    setLoading(false);
  }, []);

  return { data, loading };
};
