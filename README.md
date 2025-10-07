🍰 Project Context — Bebepiskóta Recipe Collector & Cookbook PDF Generator
🧩 Overview

This project automatically collects all recipes (videos) from the YouTube channel @bebepiskota2913
 and generates a structured recipe dataset and a beautiful PDF recipe book.

It uses yt-dlp to extract video metadata, thumbnails, and descriptions, then organizes everything locally in a folder structure, ready to be browsed or exported.

Optionally, it can generate a formatted PDF cookbook with cover, index, and recipes (including images and video links).

⚙️ Main Features

✅ Automatic channel scraping

Fetches all videos (titles, descriptions, URLs, and thumbnails)

Handles large channels (400+ videos)

Skips unavailable/private videos

✅ Local data organization

Saves all metadata in recetas.json

Downloads and renames thumbnails automatically

Creates clean folder structure for recipes

✅ PDF book generation

Generates a full cookbook with:

Cover page (title, date, total recipes)

Index page (list of all recipe titles)

Recipe pages (title, description, thumbnail, and YouTube link)

Automatically paginated and stylized (ReportLab)

✅ Offline compatible

Once recipes are fetched, you can generate the book or process data without internet.

📂 Project Structure
receptkonyv/
├── main.py                # Main script — collects video data
├── libro_recetas.py       # PDF generator module
├── recetas_bebepiskota/
│   ├── recetas.json       # Saved metadata of all recipes
│   └── miniaturas/        # Folder for all downloaded thumbnails
├── requirements.txt       # Dependencies
└── README.md              # Documentation and project info

🧠 Workflow
1️⃣ Data Collection (main.py)

Uses yt-dlp to get all videos from the channel.

For each video:

Extracts title, description, thumbnail, and URL.

Downloads the thumbnail.

Saves everything in recetas_bebepiskota/recetas.json.

2️⃣ PDF Generation (libro_recetas.py)

Uses ReportLab to create a well-formatted PDF:

Cover page with summary.

Index listing all recipe titles.

One page per recipe, with its image and description.

Output example:

Libro_Recetas_20251007.pdf

🧱 Technologies
Purpose	Tool / Library
Video metadata	yt-dlp
Data structure	json, os, pathlib
PDF generation	reportlab
Utilities	datetime, argparse
🔧 Dependencies (requirements.txt)
yt-dlp
reportlab

💡 Example Output Preview
PDF Cover Page
🍳
LIBRO DE RECETAS
Colección Bebepiskóta
Recopilado el 07/10/2025
Total de recetas: 441

Index
📑 Índice de Recetas
1. Bizcocho de yogur
2. Galletas de avena
3. Pan sin levadura
...

Recipe Page
Receta #1
Bizcocho de yogur

[image]

Descripción:
Un bizcocho suave y esponjoso...

🔗 Ver video completo:
https://www.youtube.com/watch?v=abcd1234

🕒 Estimated Run Time

Initial data download: 20–40 minutes (depending on your internet speed)

PDF generation: < 1 minute for all recipes

🚀 Future Improvements

Add CLI interface for selecting channel or output folder.

Option to export as HTML or EPUB.

Include YouTube Shorts and playlists.

Generate bilingual cookbook (HU/ES).
