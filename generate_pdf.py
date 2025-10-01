#!/usr/bin/env python3
"""
Script pour convertir la documentation Markdown en PDF
Utilise markdown2 et weasyprint pour générer un PDF professionnel
"""

import os
import sys
from pathlib import Path
import markdown2
from weasyprint import HTML, CSS
from datetime import datetime

def install_dependencies():
    """Installer les dépendances nécessaires"""
    try:
        import markdown2
        import weasyprint
        print("✅ Dépendances déjà installées")
    except ImportError:
        print("📦 Installation des dépendances...")
        os.system("pip install markdown2 weasyprint")
        print("✅ Dépendances installées")

def create_css_style():
    """Créer le style CSS pour le PDF"""
    return """
    @page {
        size: A4;
        margin: 2cm;
        @top-center {
            content: "Système de Gestion de Bibliothèque - Architecture";
            font-size: 10pt;
            color: #666;
        }
        @bottom-center {
            content: "Page " counter(page) " sur " counter(pages);
            font-size: 10pt;
            color: #666;
        }
    }
    
    body {
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        line-height: 1.6;
        color: #333;
        font-size: 11pt;
    }
    
    h1 {
        color: #2c3e50;
        border-bottom: 3px solid #3498db;
        padding-bottom: 10px;
        page-break-before: always;
        font-size: 24pt;
        margin-top: 30px;
    }
    
    h1:first-of-type {
        page-break-before: avoid;
        text-align: center;
        font-size: 28pt;
        color: #2980b9;
        margin-bottom: 30px;
    }
    
    h2 {
        color: #34495e;
        border-left: 4px solid #3498db;
        padding-left: 15px;
        margin-top: 25px;
        font-size: 18pt;
    }
    
    h3 {
        color: #5a6c7d;
        font-size: 14pt;
        margin-top: 20px;
    }
    
    h4 {
        color: #7f8c8d;
        font-size: 12pt;
        margin-top: 15px;
    }
    
    pre {
        background-color: #f8f9fa;
        border: 1px solid #e9ecef;
        border-left: 4px solid #007bff;
        padding: 15px;
        font-family: 'Courier New', monospace;
        font-size: 9pt;
        overflow-x: auto;
        margin: 15px 0;
    }
    
    code {
        background-color: #f1f3f4;
        padding: 2px 4px;
        border-radius: 3px;
        font-family: 'Courier New', monospace;
        font-size: 9pt;
        color: #c7254e;
    }
    
    table {
        width: 100%;
        border-collapse: collapse;
        margin: 15px 0;
        font-size: 10pt;
    }
    
    th {
        background-color: #3498db;
        color: white;
        padding: 10px;
        text-align: left;
        border: 1px solid #2980b9;
    }
    
    td {
        padding: 8px;
        border: 1px solid #ddd;
    }
    
    tr:nth-child(even) {
        background-color: #f9f9f9;
    }
    
    blockquote {
        border-left: 4px solid #17a2b8;
        margin: 15px 0;
        padding: 10px 20px;
        background-color: #f8f9fa;
        font-style: italic;
    }
    
    ul, ol {
        margin: 10px 0;
        padding-left: 30px;
    }
    
    li {
        margin: 5px 0;
    }
    
    .toc {
        background-color: #f8f9fa;
        border: 1px solid #dee2e6;
        padding: 20px;
        margin: 20px 0;
        page-break-after: always;
    }
    
    .toc h2 {
        margin-top: 0;
        color: #495057;
        border-left: none;
        padding-left: 0;
    }
    
    .architecture-diagram {
        text-align: center;
        font-family: monospace;
        font-size: 9pt;
        background-color: #f8f9fa;
        padding: 20px;
        border: 1px solid #dee2e6;
        margin: 20px 0;
    }
    
    .warning {
        background-color: #fff3cd;
        border-left: 4px solid #ffc107;
        padding: 10px;
        margin: 15px 0;
    }
    
    .info {
        background-color: #d1ecf1;
        border-left: 4px solid #17a2b8;
        padding: 10px;
        margin: 15px 0;
    }
    
    .success {
        background-color: #d4edda;
        border-left: 4px solid #28a745;
        padding: 10px;
        margin: 15px 0;
    }
    
    /* Page breaks pour les sections importantes */
    .page-break {
        page-break-before: always;
    }
    
    /* Footer info */
    .footer-info {
        position: fixed;
        bottom: 0;
        width: 100%;
        text-align: center;
        font-size: 8pt;
        color: #999;
    }
    
    /* Code syntax highlighting */
    .codehilite {
        background-color: #f8f9fa;
    }
    
    .codehilite .k { color: #007020; font-weight: bold; } /* Keyword */
    .codehilite .s { color: #4070a0; } /* String */
    .codehilite .c { color: #408080; font-style: italic; } /* Comment */
    .codehilite .n { color: #000000; } /* Name */
    """

def convert_markdown_to_pdf(markdown_file, output_pdf):
    """Convertir le fichier Markdown en PDF"""
    
    print(f"📖 Lecture du fichier Markdown : {markdown_file}")
    
    # Lire le fichier Markdown
    with open(markdown_file, 'r', encoding='utf-8') as f:
        markdown_content = f.read()
    
    print("🔄 Conversion Markdown vers HTML...")
    
    # Convertir Markdown en HTML avec extensions
    html_content = markdown2.markdown(
        markdown_content,
        extras=[
            'fenced-code-blocks',
            'tables', 
            'code-friendly',
            'toc',
            'header-ids',
            'footnotes',
            'strike',
            'task_list'
        ]
    )
    
    # Ajouter le wrapper HTML complet
    full_html = f"""
    <!DOCTYPE html>
    <html lang="fr">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Architecture Système de Gestion de Bibliothèque</title>
    </head>
    <body>
        <div class="header-info">
            <p><strong>Généré le :</strong> {datetime.now().strftime('%d/%m/%Y à %H:%M')}</p>
            <hr>
        </div>
        {html_content}
        <div class="footer-info">
            <p>© 2025 - Système de Gestion de Bibliothèque - Documentation Technique</p>
        </div>
    </body>
    </html>
    """
    
    print("🎨 Application du style CSS...")
    
    # Créer le CSS
    css_content = create_css_style()
    
    print("📄 Génération du PDF...")
    
    # Convertir HTML en PDF
    try:
        html_doc = HTML(string=full_html)
        css_doc = CSS(string=css_content)
        
        html_doc.write_pdf(
            output_pdf,
            stylesheets=[css_doc],
            optimize_images=True
        )
        
        print(f"✅ PDF généré avec succès : {output_pdf}")
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de la génération du PDF : {e}")
        return False

def main():
    """Fonction principale"""
    print("🚀 Générateur de Documentation PDF")
    print("=" * 50)
    
    # Vérifier et installer les dépendances
    install_dependencies()
    
    # Chemins des fichiers
    current_dir = Path(__file__).parent
    markdown_file = current_dir / "docs" / "Architecture_Document.md"
    output_dir = current_dir / "docs"
    output_pdf = output_dir / "Architecture_Systeme_Bibliotheque.pdf"
    
    # Créer le répertoire de sortie si nécessaire
    output_dir.mkdir(exist_ok=True)
    
    # Vérifier que le fichier Markdown existe
    if not markdown_file.exists():
        print(f"❌ Fichier Markdown non trouvé : {markdown_file}")
        print("📝 Utilisation du fichier dans le répertoire courant...")
        markdown_file = current_dir / "Architecture_Document.md"
        
        if not markdown_file.exists():
            print(f"❌ Fichier non trouvé : {markdown_file}")
            sys.exit(1)
    
    # Convertir
    success = convert_markdown_to_pdf(markdown_file, output_pdf)
    
    if success:
        print("\n" + "=" * 50)
        print("🎉 Documentation PDF générée avec succès !")
        print(f"📁 Fichier : {output_pdf}")
        print(f"📊 Taille : {output_pdf.stat().st_size / 1024:.1f} KB")
        print("\n📋 Contenu du PDF :")
        print("   • Vue d'ensemble du projet")
        print("   • Architecture technique détaillée")
        print("   • Documentation des composants")
        print("   • Guide d'installation")
        print("   • Procédures de maintenance")
        print("   • Diagrammes et schémas")
        
        # Ouvrir le PDF automatiquement (Windows)
        try:
            import subprocess
            subprocess.run(f'start "" "{output_pdf}"', shell=True, check=False)
            print(f"\n🔍 PDF ouvert automatiquement")
        except:
            print(f"\n💡 Ouvrez manuellement : {output_pdf}")
    else:
        print("❌ Échec de la génération du PDF")
        sys.exit(1)

if __name__ == "__main__":
    main()