import React, { useState } from "react";
import UploadBox from "../components/UploadBox";
import ResultCard from "../components/ResultCard";
import PdfPreview from "../components/PdfPreview";
import { uploadInvoice } from "../api/uploadInvoice";

const Home = () => {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);

  const handleUpload = async (file) => {
    try {
      setLoading(true);
      setResult(null);

      const data = await uploadInvoice(file);
      setResult(data);
    } catch (err) {
      console.error(err);
      alert("Failed to process invoice");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto py-10 px-4">
      <h1 className="text-2xl font-bold mb-6 text-center">
        Invoice QR Generator
      </h1>

      <UploadBox onUpload={handleUpload} loading={loading} />

      <ResultCard result={result} />
      <PdfPreview pdfUrl={result?.output_pdf} />
    </div>
  );
};

export default Home;
