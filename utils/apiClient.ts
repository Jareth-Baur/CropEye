import axios from "axios";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:5000";

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
});

export const fetchDetections = async () => {
  try {
    const res = await apiClient.get("/detections");
    return res.data;
  } catch (err) {
    console.error("Error fetching detections:", err);
    return [];
  }
};
