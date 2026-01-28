import React from "react";

const ResultCard = ({ result }) => {
  if (!result) return null;

  const { parsed_data, qr_payload, qr_url, pdf_url } = result;

  return (
    <div className="mt-6 p-6 bg-white rounded-lg shadow">
      <h2 className="text-lg font-semibold mb-4">
        Invoice Details
      </h2>

      <div className="grid grid-cols-2 gap-3 text-sm">
        <div><b>Invoice No:</b> {parsed_data.invoice_no}</div>
        <div><b>Invoice Date:</b> {parsed_data.invoice_date}</div>
        <div><b>PO Number:</b> {parsed_data.po_number}</div>
        <div><b>Quantity:</b> {parsed_data.quantity}</div>
        <div><b>HSN:</b> {parsed_data.hsn}</div>
        <div><b>Total:</b> ₹{parsed_data.total_value}</div>
      </div>

      <div className="mt-4">
        <p className="text-xs break-all text-gray-500">
          <b>QR Payload:</b> {qr_payload}
        </p>
      </div>

      {/* QR Preview */}
      {qr_url && (
        <div className="mt-6">
          <p className="text-sm font-medium mb-2">QR Code Preview</p>
          <img
            src={qr_url}
            alt="Invoice QR"
            className="w-[200px] h-[200px] border"
          />
        </div>
      )}

      {/* Actions */}
      <div className="flex gap-4 mt-6">
        {pdf_url && (
          <a
            href={result.pdf_url}
            download
            target="_blank"
            rel="noreferrer"
            >
            <button>Download PDF with QR</button>
            </a>
        )}

        {qr_url && (
          <a
            href={qr_url}
            target="_blank"
            rel="noreferrer"
            className="px-4 py-2 bg-gray-200 rounded"
          >
            Open QR in New Tab
          </a>
        )}
      </div>
    </div>
  );
};

export default ResultCard;
