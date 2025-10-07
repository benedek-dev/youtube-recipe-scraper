import os
import json
from datetime import datetime
import requests

# Necesitarás instalar estas librerías:
# pip install yt-dlp pillow reportlab

try:
    import yt_dlp
    from PIL import Image
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image as RLImage, PageBreak
    from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
except ImportError:
    print("Por favor instala las dependencias necesarias:")
    print("pip install yt-dlp pillow reportlab")
    exit(1)

class YouTubeRecipeExtractor:
    def __init__(self, channel_url, output_folder="recetas_output"):
        self.channel_url = channel_url
        self.output_folder = output_folder
        self.recipes = []
        
        # Crear carpetas
        os.makedirs(output_folder, exist_ok=True)
        os.makedirs(f"{output_folder}/miniaturas", exist_ok=True)
        os.makedirs(f"{output_folder}/datos", exist_ok=True)
    
    def extraer_videos(self):
        """Extrae información de todos los videos del canal"""
        print(f"🔍 Extrayendo información del canal: {self.channel_url}\n")
        
        # Opciones para extraer solo la lista de videos
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': 'in_playlist',
            'skip_download': True,
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                print("📡 Obteniendo lista de videos...")
                info = ydl.extract_info(self.channel_url, download=False)
                
                # Encontrar todos los videos en las diferentes tabs
                all_videos = []
                
                if 'entries' in info:
                    for entry in info['entries']:
                        if entry is None:
                            continue
                        
                        # Si es una playlist (tab del canal)
                        if entry.get('_type') == 'playlist' and 'entries' in entry:
                            tab_name = entry.get('title', 'Unknown')
                            print(f"   📁 Procesando: {tab_name}")
                            
                            for video in entry['entries']:
                                if video and video.get('id'):
                                    # Solo añadir si no está ya en la lista
                                    if not any(v['id'] == video['id'] for v in all_videos):
                                        all_videos.append(video)
                        # Si es un video directo
                        elif entry.get('id'):
                            if not any(v['id'] == entry['id'] for v in all_videos):
                                all_videos.append(entry)
                
                print(f"\n✅ Se encontraron {len(all_videos)} videos únicos\n")
                
                if len(all_videos) == 0:
                    print("❌ No se encontraron videos en el canal")
                    return
                
                # Procesar cada video
                self.procesar_videos(all_videos)
                
        except Exception as e:
            print(f"❌ Error al extraer videos: {str(e)}")
            import traceback
            traceback.print_exc()
    
    def procesar_videos(self, videos):
        """Procesa cada video individualmente"""
        total = len(videos)
        
        for i, video in enumerate(videos, 1):
            try:
                video_id = video.get('id')
                video_url = f"https://www.youtube.com/watch?v={video_id}"
                
                print(f"📹 [{i}/{total}] Procesando video {video_id}...")
                
                # Opciones para obtener información detallada
                ydl_opts = {
                    'quiet': True,
                    'no_warnings': True,
                    'skip_download': True,
                }
                
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    video_info = ydl.extract_info(video_url, download=False)
                    
                    titulo = video_info.get('title', 'Sin título')
                    print(f"   ✓ {titulo[:60]}...")
                    
                    receta = {
                        'numero': i,
                        'titulo': titulo,
                        'descripcion': video_info.get('description', 'Sin descripción'),
                        'url': video_url,
                        'duracion': video_info.get('duration', 0),
                        'fecha_publicacion': video_info.get('upload_date', ''),
                        'miniatura_url': video_info.get('thumbnail', ''),
                        'miniatura_local': ''
                    }
                    
                    # Descargar miniatura
                    miniatura_path = self.descargar_miniatura(
                        receta['miniatura_url'], 
                        f"receta_{i:03d}.jpg"
                    )
                    receta['miniatura_local'] = miniatura_path
                    
                    self.recipes.append(receta)
                    
            except Exception as e:
                print(f"   ⚠️  Error procesando video: {str(e)}")
                continue
        
        # Guardar datos en JSON
        if self.recipes:
            self.guardar_json()
            print(f"\n✅ Extracción completada: {len(self.recipes)} recetas guardadas")
    
    def descargar_miniatura(self, url, filename):
        """Descarga la miniatura del video"""
        if not url:
            return ""
        
        try:
            response = requests.get(url, timeout=10)
            filepath = os.path.join(self.output_folder, "miniaturas", filename)
            
            with open(filepath, 'wb') as f:
                f.write(response.content)
            
            return filepath
        except Exception as e:
            print(f"   ⚠️  Error descargando miniatura: {str(e)}")
            return ""
    
    def guardar_json(self):
        """Guarda los datos en formato JSON"""
        json_path = os.path.join(self.output_folder, "datos", "recetas.json")
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(self.recipes, f, ensure_ascii=False, indent=2)
        print(f"\n💾 Datos guardados en: {json_path}")
    
    def crear_libro_pdf(self):
        """Crea un libro PDF bonito con todas las recetas"""
        if not self.recipes:
            print("\n❌ No hay recetas para crear el PDF")
            return
        
        print("\n📖 Generando libro de recetas PDF...")
        
        pdf_path = os.path.join(self.output_folder, f"Libro_Recetas_{datetime.now().strftime('%Y%m%d')}.pdf")
        doc = SimpleDocTemplate(pdf_path, pagesize=A4,
                                topMargin=0.75*inch, bottomMargin=0.75*inch,
                                leftMargin=0.75*inch, rightMargin=0.75*inch)
        
        # Estilos
        styles = getSampleStyleSheet()
        
        # Estilo para el título del libro
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=28,
            textColor='#8B4513',
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )
        
        # Estilo para títulos de recetas
        recipe_title_style = ParagraphStyle(
            'RecipeTitle',
            parent=styles['Heading2'],
            fontSize=16,
            textColor='#D2691E',
            spaceAfter=12,
            spaceBefore=12,
            fontName='Helvetica-Bold'
        )
        
        # Estilo para el contenido
        content_style = ParagraphStyle(
            'Content',
            parent=styles['Normal'],
            fontSize=10,
            alignment=TA_JUSTIFY,
            spaceAfter=12,
            leading=14
        )
        
        # Construir el documento
        story = []
        
        # Portada
        story.append(Spacer(1, 2*inch))
        story.append(Paragraph("🍳", title_style))
        story.append(Paragraph("Libro de Recetas", title_style))
        story.append(Paragraph("Colección Bebepiskóta", styles['Normal']))
        story.append(Spacer(1, 0.5*inch))
        story.append(Paragraph(f"Recopilado el {datetime.now().strftime('%d/%m/%Y')}", styles['Normal']))
        story.append(Paragraph(f"Total de recetas: {len(self.recipes)}", styles['Normal']))
        story.append(PageBreak())
        
        # Índice
        story.append(Paragraph("📑 Índice de Recetas", title_style))
        story.append(Spacer(1, 0.3*inch))
        
        for receta in self.recipes:
            indice_text = f"{receta['numero']}. {receta['titulo']}"
            story.append(Paragraph(indice_text, styles['Normal']))
            story.append(Spacer(1, 6))
        
        story.append(PageBreak())
        
        # Recetas
        for receta in self.recipes:
            # Título de la receta
            story.append(Paragraph(f"Receta #{receta['numero']}", styles['Normal']))
            story.append(Paragraph(receta['titulo'], recipe_title_style))
            story.append(Spacer(1, 0.2*inch))
            
            # Miniatura
            if receta['miniatura_local'] and os.path.exists(receta['miniatura_local']):
                try:
                    img = RLImage(receta['miniatura_local'], width=4*inch, height=3*inch)
                    story.append(img)
                    story.append(Spacer(1, 0.2*inch))
                except Exception as e:
                    pass
            
            # Descripción
            if receta['descripcion'] and len(receta['descripcion']) > 50:
                story.append(Paragraph("<b>Descripción:</b>", content_style))
                
                # Limpiar y formatear descripción
                descripcion = receta['descripcion'].replace('\n', '<br/>')
                # Limitar longitud si es muy larga
                if len(descripcion) > 2000:
                    descripcion = descripcion[:2000] + "..."
                
                story.append(Paragraph(descripcion, content_style))
                story.append(Spacer(1, 0.2*inch))
            
            # Link al video
            story.append(Paragraph(f"🔗 <b>Ver video completo:</b> {receta['url']}", styles['Normal']))
            
            story.append(PageBreak())
        
        # Generar PDF
        try:
            doc.build(story)
            print(f"✅ Libro PDF creado: {pdf_path}")
            return pdf_path
        except Exception as e:
            print(f"❌ Error creando PDF: {str(e)}")
            return None

def main():
    print("=" * 60)
    print("🍳 EXTRACTOR DE RECETAS DE YOUTUBE 🍳")
    print("=" * 60)
    print()
    
    # URL del canal
    canal_url = "https://youtube.com/@bebepiskota2913"
    
    # Crear extractor
    extractor = YouTubeRecipeExtractor(canal_url)
    
    # Extraer videos
    extractor.extraer_videos()
    
    # Crear libro PDF
    if extractor.recipes:
        extractor.crear_libro_pdf()
        
        print("\n" + "=" * 60)
        print("✅ ¡PROCESO COMPLETADO!")
        print("=" * 60)
        print(f"\n📁 Todos los archivos están en la carpeta: {extractor.output_folder}")
        print(f"   - Libro PDF con todas las recetas")
        print(f"   - Carpeta 'miniaturas' con todas las imágenes")
        print(f"   - Carpeta 'datos' con el archivo JSON")
        print("\n🎁 ¡Listo para regalar a tu madre!")
    else:
        print("\n❌ No se pudieron extraer recetas")

if __name__ == "__main__":
    main()