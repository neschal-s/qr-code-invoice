import axios from "axios";

const API_BASE = "http://127.0.0.1:8000"; // change later for prod

export const uploadInvoice = async (file) => {
  const formData = new FormData();
  formData.append("file", file);

  const response = await axios.post(
    `${API_BASE}/upload-invoice`,
    formData,
    {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    }
  );

  return response.data;
};
