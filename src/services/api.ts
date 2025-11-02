import axios from "axios";

const api = axios.create({
  baseURL: "http://localhost:5000/api", // backend API
});

export const classifyImage = async (imageFile: File) => {
  const formData = new FormData();
  formData.append("image", imageFile);
  const response = await api.post("/classify", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return response.data;
};
