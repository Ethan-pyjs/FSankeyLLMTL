# 🖥️ Local System Requirements - Financial Sankey Story-Teller

This document outlines the compute and software requirements to run the Financial Sankey Story-Teller locally.

---

## ✅ Recommended System Requirements

### Hardware

| Component      | Recommended Specs                                    |
| -------------- | ---------------------------------------------------- |
| **CPU**        | 6+ core processor (Intel i7 / AMD Ryzen 7 or better) |
| **RAM**        | 32–48 GB (for optimal performance)                   |
| **Disk Space** | 5–10 GB (includes models, cache, dependencies)       |
| **GPU**        | 6GB+ VRAM (NVIDIA recommended for local LLMs)        |

> Note: GPU is optional, but strongly recommended for faster LLM/vision model inference. Without GPU, expect slower performance.

---

## 🔽 Minimum System Requirements (for testing or non-GPU environments)

| Component      | Minimum Specs                                |
| -------------- | -------------------------------------------- |
| **CPU**        | Quad-core (Intel i5 / AMD Ryzen 5 or better) |
| **RAM**        | 16 GB                                        |
| **Disk Space** | 2–3 GB                                       |
| **GPU**        | Not required                                 |

---

## 🛠️ Software Requirements

### Frontend

* **Node.js**: v18 or newer
* **npm**: Comes with Node.js (used for package management)

### Backend

* **Python**: 3.10 or newer
* **Pip**: Installed with Python
* **FastAPI**: For backend API
* **PyMuPDF**: For PDF parsing
* **CORS Middleware**: For cross-origin requests

### LLM/Model Layer

* **Ollama** (or equivalent LLM host)

  * Models used:

    * `Granite 3.3` (for story generation)
    * `Granite 3.2-vision` (for parsing tables and visual content)

---

## ⚙️ Optional Tools

* **VS Code**: For code editing
* **Postman or Insomnia**: For API testing
* **Tesseract** (optional): If OCR is needed for scanned PDFs

---

## 📝 Notes

* Ensure Ollama is properly installed and that the necessary models are downloaded before running the backend.
* For lower-spec systems, run smaller LLMs or offload processing to cloud services.

---

This app is optimized for local single-user operation. Avoid deploying this setup in a high-concurrency environment without scaling adjustments.
