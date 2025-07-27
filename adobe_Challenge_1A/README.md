# Adobe Hackathon Round 1A – PDF Outline Extractor

## 🔧 Tech Stack
- Python 3
- PyMuPDF
- Docker

## 📁 Folder Structure
- `/app/input/`: Place PDF files here
- `/app/output/`: JSON outline will be saved here

## 💡 Features
- Extracts the **Title**, **H1**, **H2**, **H3** headings with **page numbers**
- Works offline, inside a Docker container
- No internet or GPU required

## 🚀 How to Build & Run

### 1. Build Docker Image
```bash
docker build --platform linux/amd64 -t pdf_outliner .
