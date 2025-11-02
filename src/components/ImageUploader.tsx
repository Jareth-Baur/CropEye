import { useState } from "react";
import { classifyImage } from "../services/api";

export default function ImageUploader() {
  const [image, setImage] = useState<File | null>(null);
  const [result, setResult] = useState<any>(null);

  const handleUpload = async () => {
    if (!image) return;
    const data = await classifyImage(image);
    setResult(data);
  };

  return (
    <div className="p-6 bg-white rounded-xl shadow">
      <input
        type="file"
        accept="image/*"
        onChange={(e) => setImage(e.target.files?.[0] || null)}
      />
      <button
        onClick={handleUpload}
        className="mt-3 bg-green-600 text-white px-4 py-2 rounded"
      >
        Classify Image
      </button>

      {result && (
        <div className="mt-4">
          <p><strong>Disease:</strong> {result.disease}</p>
          <p><strong>Confidence:</strong> {(result.confidence * 100).toFixed(2)}%</p>
        </div>
      )}
    </div>
  );
}
