const SlidePreview = ({ previewImages }) => {
  if (!previewImages || previewImages.length === 0) return null;

  return (
    <div className="mt-6 w-full max-w-3xl">
      <h3 className="text-lg font-semibold text-gray-700 mb-4 text-center">Slide Previews</h3>
      <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
        {previewImages.map((img, index) => (
          <img
            key={index}
            src={img}
            alt={`Slide ${index + 1}`}
            className="w-full h-32 object-cover rounded-md shadow-md"
          />
        ))}
      </div>
    </div>
  );
};

export default SlidePreview;
