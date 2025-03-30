import { useState } from "react";
import axios from "axios";
import SlidePreview from "./SlidePreview"; // Import the new component

const PresentationForm = () => {
  const [title, setTitle] = useState("");
  const [author, setAuthor] = useState("");
  const [numSlides, setNumSlides] = useState(5);
  const [description, setDescription] = useState("");
  const [useAI, setUseAI] = useState(true);
  const [imageStyle, setImageStyle] = useState("realistic"); // Default style
  const [loading, setLoading] = useState(false);
  const [previewImages, setPreviewImages] = useState([]);
  const [pptBlob, setPptBlob] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setPreviewImages([]);
    setPptBlob(null);

    const requestData = {
      title: title.trim(),
      author: author.trim(),
      num_slides: Number(numSlides),
      description: useAI ? "" : description.trim(),
      useAI: useAI,
      image_style: imageStyle, // Include image style in the request
    };

    try {
      const response = await axios.post(
        "http://127.0.0.1:8080/api/generate_presentation",
        requestData,
        { responseType: "blob" }
      );

      // Convert the response blob into a URL
      const blobUrl = window.URL.createObjectURL(new Blob([response.data]));
      setPptBlob(blobUrl);

      // Fetch slide previews (Assuming API provides slide preview URLs)
      const previewResponse = await axios.post(
        "http://127.0.0.1:8080/api/preview_slides",
        requestData
      );
      setPreviewImages(previewResponse.data.slide_previews);

    } catch (error) {
      console.error("Error generating presentation:", error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-gradient-to-r from-blue-50 to-blue-100 p-4">
      <div className="bg-white p-8 rounded-lg shadow-lg w-full max-w-md">
        <h2 className="text-2xl font-bold text-gray-700 mb-6 text-center">Create Presentation</h2>
        
        <form onSubmit={handleSubmit} className="space-y-4">
          <input
            type="text"
            placeholder="Presentation Title"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            className="w-full p-3 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-400"
            required
          />
          <input
            type="text"
            placeholder="Author Name"
            value={author}
            onChange={(e) => setAuthor(e.target.value)}
            className="w-full p-3 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-400"
            required
          />
          <input
            type="number"
            placeholder="Number of Slides"
            value={numSlides}
            onChange={(e) => setNumSlides(e.target.value)}
            className="w-full p-3 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-400"
            min="1"
            required
          />

          {/* Radio buttons */}
          <div className="flex justify-between items-center bg-gray-100 p-3 rounded-lg">
            <label className="flex items-center space-x-2">
              <input
                type="radio"
                checked={useAI}
                onChange={() => setUseAI(true)}
                className="w-5 h-5 text-blue-600"
              />
              <span className="text-gray-700">Use AI</span>
            </label>
            <label className="flex items-center space-x-2">
              <input
                type="radio"
                checked={!useAI}
                onChange={() => setUseAI(false)}
                className="w-5 h-5 text-blue-600"
              />
              <span className="text-gray-700">Enter Content Manually</span>
            </label>
          </div>

          {!useAI && (
            <textarea
              placeholder="Enter your presentation description"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              className="w-full p-3 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-400"
              rows="4"
              required
            ></textarea>
          )}

          {/* Dropdown for Image Style Selection */}
          <div className="flex flex-col">
            <label className="text-gray-700 mb-1 font-semibold">Select Image Style:</label>
            <select
              value={imageStyle}
              onChange={(e) => setImageStyle(e.target.value)}
              className="w-full p-3 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-400"
            >
              <option value="realistic">Realistic</option>
              <option value="anime">Anime</option>
              <option value="ghibli">Ghibli Studio</option>
            </select>
          </div>

          <button
            type="submit"
            className="w-full flex justify-center items-center bg-blue-600 text-white px-4 py-3 rounded-lg hover:bg-blue-700 transition-all"
          >
            {loading ? (
              <>
                <svg className="animate-spin h-5 w-5 mr-2 border-t-2 border-white rounded-full" viewBox="0 0 24 24"></svg>
                Generating...
              </>
            ) : (
              "Generate Presentation"
            )}
          </button>
        </form>
      </div>

      {/* Slide Preview Section */}
      <SlidePreview previewImages={previewImages} />

      {/* Download Button */}
      {pptBlob && (
        <div className="mt-6">
          <a
            href={pptBlob}
            download="presentation.pptx"
            className="bg-green-800 text-white px-6 py-3 rounded-lg hover:bg-green-700 transition-all"
          >
            Download Presentation
          </a>
        </div>
      )}
    </div>
  );
};

export default PresentationForm;
