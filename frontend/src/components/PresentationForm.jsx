import { useState } from "react";
import axios from "axios";

const PresentationForm = () => {
  const [title, setTitle] = useState("");
  const [author, setAuthor] = useState("");
  const [numSlides, setNumSlides] = useState(5);
  const [description, setDescription] = useState("");
  const [useAI, setUseAI] = useState(true); // Default to AI
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    const requestData = {
      title: title.trim(),
      author: author.trim(),
      num_slides: Number(numSlides), // Ensure it's an integer
      description: useAI ? "" : description.trim(), // Empty string if AI is used
      useAI: useAI, // Boolean flag for AI
    };

    try {
      const response = await axios.post("https://smartpresentationgenerator-production.up.railway.app/api/generate_presentation", requestData, {
        responseType: "blob", // Important: Receive file as a Blob
      });

      // Create a URL for the downloaded file
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement("a");
      link.href = url;
      link.setAttribute("download", "presentation.pptx"); // Set download filename
      document.body.appendChild(link);
      link.click(); // Trigger download
      link.remove(); // Clean up

    } catch (error) {
      console.error("Error generating presentation:", error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-white p-6 rounded-lg shadow-md">
      <h2 className="text-xl font-semibold mb-4">Create Presentation</h2>
      <form onSubmit={handleSubmit} className="space-y-4">
        <input
          type="text"
          placeholder="Presentation Title"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          className="w-full p-2 border rounded"
          required
        />
        <input
          type="text"
          placeholder="Author Name"
          value={author}
          onChange={(e) => setAuthor(e.target.value)}
          className="w-full p-2 border rounded"
          required
        />
        <input
          type="number"
          placeholder="Number of Slides"
          value={numSlides}
          onChange={(e) => setNumSlides(e.target.value)}
          className="w-full p-2 border rounded"
          min="1"
          required
        />

        {/* Radio buttons for AI or Manual input */}
        <div className="flex space-x-4">
          <label className="flex items-center space-x-2">
            <input
              type="radio"
              checked={useAI}
              onChange={() => setUseAI(true)}
              className="w-4 h-4"
            />
            <span>Use AI to generate content</span>
          </label>
          <label className="flex items-center space-x-2">
            <input
              type="radio"
              checked={!useAI}
              onChange={() => setUseAI(false)}
              className="w-4 h-4"
            />
            <span>Enter content manually</span>
          </label>
        </div>

        {/* Show textarea only if manual input is selected */}
        {!useAI && (
          <textarea
            placeholder="Enter your presentation description"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            className="w-full p-2 border rounded"
            rows="4"
            required={!useAI}
          ></textarea>
        )}

        <button type="submit" className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700">
          {loading ? "Generating..." : "Generate & Download"}
        </button>
      </form>
    </div>
  );
};

export default PresentationForm;
