#!/usr/bin/env python3
"""
Script pour convertir la documentation Markdown en HTML stylé
Compatible Windows sans dépendances système complexes
"""

import os
import sys
from pathlib import Path
import markdown2
from datetime import datetime

def create_css_style():
    """Créer le style CSS pour l'HTML"""
    return """
    <style>
    @media print {
        @page {
            size: A4;
            margin: 2cm;
        }
        body { font-size: 12pt; }
        h1 { page-break-before: always; }
        h1:first-of-type { page-break-before: avoid; }
        pre, .code-block { page-break-inside: avoid; }
        table { page-break-inside: avoid; }
    }
    
    body {
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        line-height: 1.6;
        color: #333;
        max-width: 210mm;
        margin: 0 auto;
        padding: 20px;
        background: white;
    }
    
    .header-info {
        text-align: center;
        margin-bottom: 30px;
        padding: 20px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
    }
    
    .header-info h1 {
        margin: 0;
        font-size: 28pt;
        margin-bottom: 10px;
    }
    
    .header-info p {
        margin: 5px 0;
        font-size: 14pt;
    }
    
    h1 {
        color: #2c3e50;
        border-bottom: 3px solid #3498db;
        padding-bottom: 10px;
        font-size: 24pt;
        margin-top: 40px;
        margin-bottom: 20px;
    }
    
    h2 {
        color: #34495e;
        border-left: 4px solid #3498db;
        padding-left: 15px;
        margin-top: 30px;
        font-size: 18pt;
        background-color: #f8f9fa;
        padding: 10px 15px;
    }
    
    h3 {
        color: #5a6c7d;
        font-size: 16pt;
        margin-top: 25px;
        border-bottom: 1px solid #eee;
        padding-bottom: 5px;
    }
    
    h4 {
        color: #7f8c8d;
        font-size: 14pt;
        margin-top: 20px;
    }
    
    pre {
        background-color: #f8f9fa;
        border: 1px solid #e9ecef;
        border-left: 4px solid #007bff;
        padding: 20px;
        font-family: 'Courier New', monospace;
        font-size: 11pt;
        overflow-x: auto;
        margin: 20px 0;
        border-radius: 5px;
    }
    
    code {
        background-color: #f1f3f4;
        padding: 3px 6px;
        border-radius: 3px;
        font-family: 'Courier New', monospace;
        font-size: 10pt;
        color: #c7254e;
    }
    
    table {
        width: 100%;
        border-collapse: collapse;
        margin: 20px 0;
        font-size: 11pt;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }
    
    th {
        background: linear-gradient(135deg, #3498db, #2980b9);
        color: white;
        padding: 12px;
        text-align: left;
        border: 1px solid #2980b9;
        font-weight: bold;
    }
    
    td {
        padding: 10px 12px;
        border: 1px solid #ddd;
        vertical-align: top;
    }
    
    tr:nth-child(even) {
        background-color: #f9f9f9;
    }
    
    tr:hover {
        background-color: #f0f8ff;
    }
    
    blockquote {
        border-left: 4px solid #17a2b8;
        margin: 20px 0;
        padding: 15px 25px;
        background-color: #f8f9fa;
        font-style: italic;
        border-radius: 0 5px 5px 0;
    }
    
    ul, ol {
        margin: 15px 0;
        padding-left: 30px;
    }
    
    li {
        margin: 8px 0;
        line-height: 1.5;
    }
    
    .toc {
        background: linear-gradient(135deg, #f8f9fa, #e9ecef);
        border: 2px solid #dee2e6;
        padding: 25px;
        margin: 30px 0;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    .toc h2 {
        margin-top: 0;
        color: #495057;
        border-left: none;
        padding-left: 0;
        background: none;
        text-align: center;
    }
    
    .architecture-diagram {
        text-align: center;
        font-family: 'Courier New', monospace;
        font-size: 10pt;
        background: linear-gradient(135deg, #f8f9fa, #ffffff);
        padding: 25px;
        border: 2px solid #dee2e6;
        margin: 25px 0;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .alert {
        padding: 15px;
        margin: 20px 0;
        border-radius: 5px;
        border-left: 4px solid;
    }
    
    .alert-warning {
        background-color: #fff3cd;
        border-left-color: #ffc107;
        color: #856404;
    }
    
    .alert-info {
        background-color: #d1ecf1;
        border-left-color: #17a2b8;
        color: #0c5460;
    }
    
    .alert-success {
        background-color: #d4edda;
        border-left-color: #28a745;
        color: #155724;
    }
    
    .footer-info {
        text-align: center;
        margin-top: 50px;
        padding: 20px;
        background-color: #f8f9fa;
        border-top: 2px solid #dee2e6;
        font-size: 10pt;
        color: #6c757d;
    }
    
    /* Améliorations visuelles */
    .btn {
        display: inline-block;
        padding: 8px 16px;
        background: linear-gradient(135deg, #007bff, #0056b3);
        color: white;
        text-decoration: none;
        border-radius: 5px;
        margin: 5px;
        font-size: 11pt;
    }
    
    .badge {
        display: inline-block;
        padding: 4px 8px;
        background: #28a745;
        color: white;
        border-radius: 3px;
        font-size: 9pt;
        margin: 2px;
    }
    
    /* Responsive design */
    @media screen and (max-width: 768px) {
        body {
            padding: 10px;
            font-size: 14px;
        }
        
        table {
            font-size: 10pt;
        }
        
        pre {
            font-size: 10pt;
            padding: 15px;
        }
    }
    
    /* Print optimizations */
    @media print {
        .no-print {
            display: none;
        }
        
        body {
            font-size: 10pt;
            color: black;
        }
        
        a {
            color: black;
            text-decoration: none;
        }
        
        h1, h2, h3 {
            color: black;
        }
        
        .header-info {
            background: none;
            color: black;
            border: 2px solid black;
        }
    }
    </style>
    """

def convert_markdown_to_html(markdown_file, output_html):
    """Convertir le fichier Markdown en HTML stylé"""
    
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
            'task_list',
            'break-on-newline'
        ]
    )
    
    # Créer le CSS
    css_content = create_css_style()
    
    # Ajouter le wrapper HTML complet
    full_html = f"""
    <!DOCTYPE html>
    <html lang="fr">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Architecture Système de Gestion de Bibliothèque</title>
        {css_content}
    </head>
    <body>
        <div class="header-info">
            <h1>📚 Architecture du Système de Gestion de Bibliothèque</h1>
            <p><strong>Version:</strong> 1.0 | <strong>Généré le:</strong> {datetime.now().strftime('%d/%m/%Y à %H:%M')}</p>
            <p><strong>Technologies:</strong> 
                <span class="badge">React</span>
                <span class="badge">FastAPI</span>
                <span class="badge">PostgreSQL</span>
                <span class="badge">Docker</span>
                <span class="badge">Kubernetes</span>
            </p>
        </div>
        
        <div class="no-print" style="text-align: center; margin: 20px 0;">
            <button onclick="window.print()" class="btn">🖨️ Imprimer en PDF</button>
            <a href="#" onclick="window.history.back()" class="btn">⬅️ Retour</a>
        </div>
        
        {html_content}
        
        <div class="footer-info">
            <p><strong>© 2025 - Système de Gestion de Bibliothèque</strong></p>
            <p>Documentation Technique - Générée automatiquement</p>
            <p>🌐 <strong>URLs du système:</strong></p>
            <p>Frontend: <code>http://localhost</code> | API: <code>http://localhost/api</code> | Docs: <code>http://localhost:8000/docs</code></p>
        </div>
        
        <script>
            // Auto-scroll vers le sommaire au chargement
            document.addEventListener('DOMContentLoaded', function() {{
                // Améliorer la navigation
                const links = document.querySelectorAll('a[href^="#"]');
                links.forEach(link => {{
                    link.addEventListener('click', function(e) {{
                        e.preventDefault();
                        const target = document.querySelector(this.getAttribute('href'));
                        if (target) {{
                            target.scrollIntoView({{ behavior: 'smooth' }});
                        }}
                    }});
                }});
                
                // Ajouter un indicateur de lecture
                console.log('📋 Documentation chargée avec succès !');
            }});
        </script>
    </body>
    </html>
    """
    
    print("💾 Sauvegarde du fichier HTML...")
    
    # Sauvegarder le fichier HTML
    with open(output_html, 'w', encoding='utf-8') as f:
        f.write(full_html)
    
    print(f"✅ HTML généré avec succès : {output_html}")
    return True

def main():
    """Fonction principale"""
    print("🚀 Générateur de Documentation HTML")
    print("=" * 50)
    
    # Chemins des fichiers
    current_dir = Path(__file__).parent
    markdown_file = current_dir / "docs" / "Architecture_Document.md"
    output_dir = current_dir / "docs"
    output_html = output_dir / "Architecture_Systeme_Bibliotheque.html"
    
    # Créer le répertoire de sortie si nécessaire
    output_dir.mkdir(exist_ok=True)
    
    # Vérifier que le fichier Markdown existe
    if not markdown_file.exists():
        print(f"❌ Fichier Markdown non trouvé : {markdown_file}")
        sys.exit(1)
    
    # Convertir
    success = convert_markdown_to_html(markdown_file, output_html)
    
    if success:
        print("\n" + "=" * 50)
        print("🎉 Documentation HTML générée avec succès !")
        print(f"📁 Fichier : {output_html}")
        print(f"📊 Taille : {output_html.stat().st_size / 1024:.1f} KB")
        print("\n📋 Pour convertir en PDF :")
        print("   1. Ouvrez le fichier HTML dans votre navigateur")
        print("   2. Utilisez Ctrl+P (Imprimer)")
        print("   3. Choisissez 'Enregistrer au format PDF'")
        print("   4. Ajustez les marges si nécessaire")
        
        print("\n📋 Contenu de la documentation :")
        print("   • Vue d'ensemble du projet")
        print("   • Architecture technique détaillée")
        print("   • Documentation des composants")
        print("   • Guide d'installation")
        print("   • Procédures de maintenance")
        print("   • Diagrammes et schémas")
        
        # Ouvrir le fichier HTML automatiquement
        try:
            import subprocess
            subprocess.run(f'start "" "{output_html}"', shell=True, check=False)
            print(f"\n🌐 HTML ouvert automatiquement dans le navigateur")
        except:
            print(f"\n💡 Ouvrez manuellement : {output_html}")
    else:
        print("❌ Échec de la génération du HTML")
        sys.exit(1)

if __name__ == "__main__":
    main()