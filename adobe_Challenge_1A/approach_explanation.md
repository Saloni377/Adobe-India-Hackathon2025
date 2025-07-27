Approach for Document Structure Extraction (Challenge 1A)

Our solution tackles the challenge of converting unstructured PDF content into a clean, hierarchical outline consisting of the Title, and heading levels: H1, H2, and H3. Since PDFs lack inherent structural tags, our goal was to infer document hierarchy accurately using a combination of layout cues and text styling.

Core Problem with PDF Structure Extraction
PDFs are designed for visual presentation, not semantic understanding. Unlike HTML or Word documents, they don’t contain native tags for headings or titles. Therefore, we can’t simply rely on parsing — we must intelligently infer structure based on font styles, sizes, layout, and content heuristics.

Our Smart Heuristic-Based Extraction Pipeline
We designed a lightweight, multi-step pipeline using PyMuPDF (fitz) to parse layout-rich PDF elements and apply rules for heading classification:

Step 1: Font & Style-Based Block Extraction
We first extract text blocks from each page, along with metadata:

Font size

Font family

Bold/italic style flags

Bounding box position

Page number

These attributes form the foundation for identifying prominent, structured elements like headings and titles.

Step 2: Heading Classification Using Heuristics
We then classify text spans into one of the four heading levels using the following logic:

Title: First large, bold, and centered line near the top of the document

H1: Bold and centered text blocks that appear section-wise

H2: Bold headings that end with colons or use semantic words (like “Overview”)

H3: Numbered subpoints (e.g., 2.3, 1.1.1) that typically appear indented or inline

We also account for heading patterns like "Unit 1", "Chapter IV", etc., using regex.

Step 3: Noise & Bullet Filtering
To reduce false positives, we exclude:

Page numbers, version info, dates

Bullet points or short phrases

Decorative or repetitive lines

This ensures that the final outline only includes structurally relevant content.

Step 4: Output as Clean JSON Format
We return the extracted structure in a hierarchical JSON format as required:
{
  "title": "Understanding AI",
  "outline": [
    { "level": "H1", "text": "Introduction", "page": 1 },
    { "level": "H2", "text": "What is AI?", "page": 2 },
    { "level": "H3", "text": "History of AI", "page": 3 }
  ]
}
If no clear title is found, the document filename is used as a fallback.