import json
import os
import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, PageBreak
from reportlab.lib.units import inch

# --- Konstansok a Stílushoz ---
PAGE_WIDTH, PAGE_HEIGHT = A4
MARGIN = 0.8 * inch
THUMBNAIL_WIDTH = 3 * inch
THUMBNAIL_HEIGHT = 1.8 * inch # Igazítás az arányhoz

# --- Elérési útvonalak (JAVÍTVA az Ön 'recetas_output' struktúrájához) ---
DATA_ROOT_DIR = 'recetas_output'
METADATA_FILE = os.path.join(DATA_ROOT_DIR, 'datos', 'recetas.json')
THUMBNAIL_DIR = os.path.join(DATA_ROOT_DIR, 'miniaturas')

OUTPUT_FILENAME_BASE = 'Libro_Recetas'
CHANNEL_NAME = '@bebepiskota2913' # A borítólaphoz

class RecipeCookbookGenerator:
    """
    Professzionális PDF szakácskönyvet generál az összegyűjtött recept metaadatokból.
    """
    def __init__(self, metadata_path=METADATA_FILE, thumbnail_dir=THUMBNAIL_DIR):
        self.metadata_path = metadata_path
        self.thumbnail_dir = thumbnail_dir
        self.styles = getSampleStyleSheet()
        self.recipes = self._load_recipes()
        
        # --- Egyéni Stílusok ---
        self.styles.add(ParagraphStyle(name='TitleStyle', fontSize=24, spaceAfter=20, alignment=1, textColor=colors.HexColor('#4A90E2'), fontName='Helvetica-Bold'))
        self.styles.add(ParagraphStyle(name='CoverTitle', fontSize=36, spaceAfter=20, alignment=1, textColor=colors.HexColor('#8B572A'), fontName='Helvetica-Bold'))
        self.styles.add(ParagraphStyle(name='CoverSubtitle', fontSize=16, spaceAfter=60, alignment=1, textColor=colors.HexColor('#4A4A4A')))
        self.styles.add(ParagraphStyle(name='IndexTitle', fontSize=20, spaceAfter=15, alignment=0, textColor=colors.HexColor('#000000'), fontName='Helvetica-Bold'))
        self.styles.add(ParagraphStyle(name='IndexEntry', fontSize=12, leading=16, spaceAfter=2, textColor=colors.HexColor('#333333')))
        self.styles.add(ParagraphStyle(name='RecipeTitle', fontSize=18, spaceAfter=10, alignment=0, textColor=colors.HexColor('#8B572A'), fontName='Helvetica-Bold'))
        self.styles.add(ParagraphStyle(name='Description', fontSize=10, leading=14, spaceAfter=15, textColor=colors.HexColor('#333333')))
        self.styles.add(ParagraphStyle(name='Link', fontSize=9, spaceAfter=5, textColor=colors.HexColor('#4A90E2')))
        self.styles.add(ParagraphStyle(name='SmallHeader', fontSize=12, spaceAfter=5, textColor=colors.HexColor('#4A4A4A'), fontName='Helvetica-Bold'))


    def _load_recipes(self):
        """Betölti és rendezi a recept adatokat a JSON fájlból."""
        if not os.path.exists(self.metadata_path):
            print(f"ERROR: Metadata file not found at {self.metadata_path}")
            return []
        try:
            with open(self.metadata_path, 'r', encoding='utf-8') as f:
                recipes = json.load(f)
            # Rendezés cím szerint
            return sorted(recipes, key=lambda r: r.get('titulo', ''))
        except Exception as e:
            print(f"ERROR: Could not load or parse recipes.json. {e}")
            return []

    def _get_output_filename(self):
        """Létrehozza a dátummal ellátott kimeneti fájlnevet."""
        date_str = datetime.date.today().strftime("%Y%m%d")
        return f"{OUTPUT_FILENAME_BASE}_{date_str}.pdf"

    def _create_cover_page(self, story):
        """Hozzáadja a professzionális borítólapot."""
        story.append(Spacer(1, PAGE_HEIGHT / 4)) # Középre igazítás függőlegesen
        story.append(Paragraph("✨ A Bebepiskóta Szakácskönyv ✨", self.styles['CoverTitle']))
        story.append(Paragraph(f"Receptek a YouTube {CHANNEL_NAME} csatornáról", self.styles['CoverSubtitle']))
        
        # Összefoglaló információk
        summary_data = [
            ['Receptek száma:', len(self.recipes)],
            ['Generálás dátuma:', datetime.date.today().strftime("%Y. %B %d.")],
        ]
        
        table_style = TableStyle([
            ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
            ('FONTSIZE', (0,0), (-1,-1), 14),
            ('ALIGN', (0,0), (0,-1), 'RIGHT'),
            ('ALIGN', (1,0), (1,-1), 'LEFT'),
            ('TOPPADDING', (0,0), (-1,-1), 8),
            ('BOTTOMPADDING', (0,0), (-1,-1), 8),
            ('TEXTCOLOR', (0,0), (-1,-1), colors.HexColor('#4A4A4A')),
        ])
        
        summary_table = Table(summary_data, colWidths=[3*inch, 3*inch])
        summary_table.setStyle(table_style)
        
        story.append(summary_table)
        story.append(PageBreak())

    def _create_index_page(self, story):
        """Hozzáadja a tartalomjegyzék oldalt."""
        story.append(Paragraph("📋 Recept Index", self.styles['IndexTitle']))
        story.append(Spacer(1, 0.25 * inch))

        # Két oszlopos index a jobb megjelenés érdekében
        num_recipes = len(self.recipes)
        mid_point = (num_recipes + 1) // 2

        # ITT HASZNÁLJUK A HELYES KULCSOT: 'titulo'
        col1_titles = [recipe.get('titulo', f"Névtelen Recept {i+1}") for i, recipe in enumerate(self.recipes[:mid_point])]
        col2_titles = [recipe.get('titulo', f"Névtelen Recept {i+mid_point+1}") for i, recipe in enumerate(self.recipes[mid_point:])]
        
        # Oszlopok kiegyenlítése
        if len(col1_titles) > len(col2_titles):
            col2_titles.extend([''] * (len(col1_titles) - len(col2_titles)))
        elif len(col2_titles) > len(col1_titles):
            col1_titles.extend([''] * (len(col2_titles) - len(col1_titles)))

        index_rows = [[
            Paragraph(f"• {col1_titles[i]}", self.styles['IndexEntry']),
            Paragraph(f"• {col2_titles[i]}" if col2_titles[i] else "", self.styles['IndexEntry'])
        ] for i in range(len(col1_titles))]
        
        index_table = Table(index_rows, colWidths=[PAGE_WIDTH/2 - MARGIN - 0.1*inch, PAGE_WIDTH/2 - MARGIN - 0.1*inch])
        index_table.setStyle(TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('LEFTPADDING', (1,0), (1,-1), 20),
            ('LINEBELOW', (0,0), (-1,-1), 0, colors.white),
        ]))
        
        story.append(index_table)
        story.append(PageBreak())

    def _create_recipe_page(self, story, recipe):
        """Hozzáad egy receptet, egy oldalonként."""
        
        # A KULCSOK JAVÍTVA A JSON-HOZ IGAZÍTVA:
        title = recipe.get('titulo', 'Névtelen Recept')
        description = recipe.get('descripcion', 'Nincs leírás megadva.')
        video_url = recipe.get('url', '#')
        thumbnail_name = recipe.get('miniatura_local', None) # <<< JAVÍTVA miniatura_local-ra
        
        story.append(Paragraph(title, self.styles['RecipeTitle']))
        story.append(Spacer(1, 0.1 * inch))

        # --- Kép és Link Szekció ---
        elements_for_table = []
        
        # 1. Miniatűr Kép
        # A miniatura_local tartalmazza a teljes elérési utat: recetas_output\miniaturas\receta_001.jpg
        image_path = thumbnail_name
        
        if image_path and os.path.exists(image_path):
            img = Image(image_path, width=THUMBNAIL_WIDTH, height=THUMBNAIL_HEIGHT)
            elements_for_table.append([img])
        else:
            # Placeholder, ha a kép hiányzik vagy hibás
            elements_for_table.append([Paragraph("<i>[A kép nem érhető el]</i>", self.styles['SmallHeader'])])

        # 2. Videó Link
        link_text = f'<b>Nézze meg a videót:</b> <a href="{video_url}">{video_url}</a>'
        elements_for_table.append([Paragraph(link_text, self.styles['Link'])])

        # Tábla létrehozása a tartalom igazításához
        info_table = Table(elements_for_table, colWidths=[PAGE_WIDTH - 2*MARGIN])
        info_table.setStyle(TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('BOTTOMPADDING', (0,0), (-1,-1), 12),
        ]))
        story.append(info_table)

        # --- Leírás/Összetevők Szekció ---
        story.append(Paragraph("<b>Recept részletek/összetevők:</b>", self.styles['SmallHeader']))
        
        # Leírás előfeldolgozása a ReportLab számára
        clean_description = description.replace('\n\n', '<br/><br/>').replace('\n', '<br/>')

        # ITT HASZNÁLJUK A HELYES KULCSOT: 'descripcion'
        story.append(Paragraph(clean_description, self.styles['Description']))
        
        # Oldaltörés minden recept után
        story.append(PageBreak())


    def generate(self):
        """Fő metódus a PDF generálásának koordinálására."""
        if not self.recipes:
            print("PDF generation skipped. No valid recipes found.")
            return

        output_filename = self._get_output_filename()
        
        # PDF dokumentum konfigurálása
        doc = SimpleDocTemplate(
            output_filename,
            pagesize=A4,
            leftMargin=MARGIN,
            rightMargin=MARGIN,
            topMargin=MARGIN,
            bottomMargin=MARGIN
        )
        
        story = []
        
        print("Borítólap hozzáadása...")
        self._create_cover_page(story)
        
        print("Recept index hozzáadása...")
        self._create_index_page(story)
        
        print(f"{len(self.recipes)} recept oldal hozzáadása...")
        for recipe in self.recipes:
            self._create_recipe_page(story, recipe)
            
        # PDF elkészítése
        print(f"PDF építése: {output_filename}...")
        try:
            doc.build(story)
            print(f"✅ Kész! A szakácskönyv mentve mint {output_filename}")
        except Exception as e:
            print(f"❌ HIBA: Nem sikerült elkészíteni a PDF-et. {e}")
            

# --- Futtatási Blokk ---
if __name__ == '__main__':
    generator = RecipeCookbookGenerator()
    generator.generate()