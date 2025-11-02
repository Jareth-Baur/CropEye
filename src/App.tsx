import './App.css'
import ImageUploader from "./components/ImageUploader";

function App() {
  return (
    <div className="min-h-screen bg-green-50 flex flex-col items-center justify-center">
      <h1 className="text-3xl font-bold mb-6 text-green-700">🌽 MaizeScan</h1>
      <ImageUploader />
    </div>
  );
}

export default App
