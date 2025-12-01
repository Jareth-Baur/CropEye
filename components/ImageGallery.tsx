interface ImageGalleryProps {
  images: { id: string; url: string; disease: string }[];
}

export const ImageGallery = ({ images }: ImageGalleryProps) => (
  <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4 p-4">
    {images.map((img) => (
      <div key={img.id} className="bg-white shadow rounded overflow-hidden">
        <img src={img.url} alt={img.disease} className="w-full h-48 object-cover" />
        <div className="p-2">
          <p className="font-bold">{img.disease}</p>
        </div>
      </div>
    ))}
  </div>
);
