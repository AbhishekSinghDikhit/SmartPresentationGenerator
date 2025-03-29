import { useState } from "react";
import axios from "axios";

const PresentationForm = () => {
  const [title, setTitle] = useState("");
  const [author, setAuthor] = useState("");
  const [numSlides, setNumSlides] = useState(5);
  const [description, setDescription] = useState("");
  const [useAI, setUseAI] = useState(true);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    const requestData = {
      title: title.trim(),
      author: author.trim(),
      num_slides: Number(numSlides),
      description: useAI ? "" : description.trim(),
      useAI: useAI,
    };

    try {
      const response = await axios.post(
        "https://smartpresentationgenerator-production.up.railway.app/api/generate_presentation",
        requestData,
        { responseType: "blob" }
      );

      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement("a");
      link.href = url;
      link.setAttribute("download", "presentation.pptx");
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (error) {
      console.error("Error generating presentation:", error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex items-center justify-center min-h-screen bg-gradient-to-r from-blue-50 to-blue-100 p-4">
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
              "Generate & Download"
            )}
          </button>
        </form>
      </div>
    </div>
  );
};

export default PresentationForm;
