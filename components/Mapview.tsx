import { MapContainer, TileLayer, Marker, Popup } from "react-leaflet";
import "leaflet/dist/leaflet.css";

interface Detection {
  id: string;
  lat: number;
  lon: number;
  disease: string;
  confidence: number;
}

interface MapViewProps {
  data: Detection[];
}

export const MapView = ({ data }: MapViewProps) => (
  <MapContainer center={[0, 0]} zoom={2} className="w-full h-[500px] rounded shadow">
    <TileLayer
      url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      attribution="&copy; OpenStreetMap contributors"
    />
    {data.map((d) => (
      <Marker key={d.id} position={[d.lat, d.lon]}>
        <Popup>
          <div>
            <strong>{d.disease}</strong>
            <p>Confidence: {Math.round(d.confidence * 100)}%</p>
          </div>
        </Popup>
      </Marker>
    ))}
  </MapContainer>
);