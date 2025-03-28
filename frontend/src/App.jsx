import Navbar from "./components/Navbar";
import PresentationForm from "./components/PresentationForm";

function App() {
  return (
    <div className="min-h-screen bg-gray-100">
      <Navbar />
      <div className="container mx-auto p-4">
        <PresentationForm />
      </div>
    </div>
  );
}

export default App;
