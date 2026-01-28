import React from "react";

const PdfPreview = ({ pdfUrl }) => {
  if (!pdfUrl) return null;

  return (
    <div className="mt-6">
      <h2 className="text-lg font-semibold mb-2">
        Preview
      </h2>
      <iframe
        src={pdfUrl}
        title="Invoice Preview"
        className="w-full h-[500px] border rounded"
      />
    </div>
  );
};

export default PdfPreview;
