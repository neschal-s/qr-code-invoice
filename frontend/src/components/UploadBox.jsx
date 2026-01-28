import React from "react";

const UploadBox = ({ onUpload, loading }) => {
  const handleChange = (e) => {
    const file = e.target.files[0];
    if (!file) return;

    if (file.type !== "application/pdf") {
      alert("Please upload a PDF file");
      return;
    }

    onUpload(file);
  };

  return (
    <div className="border-2 border-dashed rounded-lg p-8 text-center bg-white">
      <input
        type="file"
        accept="application/pdf"
        onChange={handleChange}
        disabled={loading}
      />
      <p className="text-sm text-gray-500 mt-3">
        Upload invoice PDF
      </p>
      {loading && (
        <p className="mt-3 text-blue-600 font-medium">
          Processing invoice…
        </p>
      )}
    </div>
  );
};

export default UploadBox;
