# demo_i18n.py
"""
Script de demostración del sistema de internacionalización
"""

import sys
from pathlib import Path

# Agregar el directorio del proyecto al path
sys.path.insert(0, str(Path(__file__).parent))

from utils.i18n import tr, set_language, get_translation_manager

def demo_translations():
    """Demostrar el funcionamiento del sistema de traducciones"""
    
    print("🌍 DEMOSTRACIÓN DEL SISTEMA DE INTERNACIONALIZACIÓN")
    print("=" * 60)
    
    # Obtener manager
    manager = get_translation_manager()
    
    print(f"📁 Directorio de traducciones: {manager.translations_dir}")
    print(f"🗂️  Idiomas disponibles: {manager.get_available_languages()}")
    print()
    
    # Demostrar traducciones en español
    print("🇪🇸 ESPAÑOL (por defecto):")
    print("-" * 30)
    set_language("es")
    
    print(f"Título de la app: {tr('app_title', version='1.2')}")
    print(f"Menú archivo: {tr('menu_file')}")
    print(f"Pestaña F1: {tr('tab_f1')}")
    print(f"Título F1: {tr('f1_title')}")
    print(f"Botón actualizar: {tr('f1_refresh_button')}")
    print(f"Cargando datos: {tr('f1_data_updated', count=21)}")
    print()
    
    # Demostrar traducciones en inglés
    print("🇺🇸 ENGLISH:")
    print("-" * 30)
    set_language("en")
    
    print(f"App title: {tr('app_title', version='1.2')}")
    print(f"File menu: {tr('menu_file')}")
    print(f"F1 tab: {tr('tab_f1')}")
    print(f"F1 title: {tr('f1_title')}")
    print(f"Refresh button: {tr('f1_refresh_button')}")
    print(f"Data loaded: {tr('f1_data_updated', count=21)}")
    print()
    
    # Demostrar listas traducidas
    print("📋 LISTAS TRADUCIDAS:")
    print("-" * 30)
    
    print("🇪🇸 Características MotoGP (Español):")
    set_language("es")
    for feature in tr("motogp_features"):
        print(f"  • {feature}")
    
    print()
    print("🇺🇸 MotoGP Features (English):")
    set_language("en")
    for feature in tr("motogp_features"):
        print(f"  • {feature}")
    
    print()
    
    # Demostrar manejo de errores
    print("⚠️  MANEJO DE ERRORES:")
    print("-" * 30)
    
    # Clave inexistente
    missing_key = tr("clave_inexistente")
    print(f"Clave inexistente: {missing_key}")
    
    # Formateo con argumentos faltantes
    error_format = tr("f1_data_updated")  # Sin argumento 'count'
    print(f"Sin argumentos: {error_format}")
    
    print()
    
    # Información del estado actual
    print("📊 ESTADO ACTUAL:")
    print("-" * 30)
    print(f"Idioma actual: {manager.get_current_language()}")
    print(f"Idioma de respaldo: {manager.fallback_language}")
    print(f"Total de claves en español: {len(manager.translations.get('es', {}))}")
    print(f"Total de claves en inglés: {len(manager.translations.get('en', {}))}")
    
    print()
    print("✅ Demostración completada!")

def test_file_creation():
    """Probar la creación de archivos de traducción"""
    
    print("\n📁 VERIFICACIÓN DE ARCHIVOS:")
    print("-" * 30)
    
    translations_dir = Path("translations")
    
    print(f"Directorio de traducciones: {translations_dir.absolute()}")
    print(f"Existe: {translations_dir.exists()}")
    
    if translations_dir.exists():
        files = list(translations_dir.glob("*.json"))
        print(f"Archivos encontrados: {len(files)}")
        
        for file in files:
            print(f"  📄 {file.name} ({file.stat().st_size} bytes)")
            
            # Mostrar primeras líneas del archivo
            try:
                with open(file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    lines = content.split('\n')
                    print(f"    Primeras 3 líneas:")
                    for i, line in enumerate(lines[:3]):
                        print(f"      {i+1}: {line}")
                    print(f"    ... (total: {len(lines)} líneas)")
            except Exception as e:
                print(f"    Error leyendo archivo: {e}")
            print()

def interactive_demo():
    """Demo interactivo para probar traducciones"""
    
    print("\n🎮 MODO INTERACTIVO:")
    print("-" * 30)
    print("Comandos disponibles:")
    print("  es - Cambiar a español")
    print("  en - Cambiar a inglés")
    print("  keys - Mostrar claves disponibles")
    print("  test <clave> - Probar una clave específica")
    print("  quit - Salir")
    print()
    
    manager = get_translation_manager()
    
    while True:
        try:
            current_lang = manager.get_current_language()
            command = input(f"[{current_lang}] >>> ").strip().lower()
            
            if command == "quit":
                break
            elif command == "es":
                set_language("es")
                print("🇪🇸 Idioma cambiado a español")
            elif command == "en":
                set_language("en")
                print("🇺🇸 Language changed to English")
            elif command == "keys":
                lang = manager.get_current_language()
                keys = list(manager.translations.get(lang, {}).keys())
                print(f"Claves disponibles en {lang} ({len(keys)}):")
                for i, key in enumerate(sorted(keys)[:20]):  # Mostrar solo las primeras 20
                    print(f"  {i+1:2d}. {key}")
                if len(keys) > 20:
                    print(f"  ... y {len(keys) - 20} más")
            elif command.startswith("test "):
                key = command[5:].strip()
                if key:
                    translation = tr(key)
                    print(f"'{key}' -> '{translation}'")
                else:
                    print("Por favor proporciona una clave para probar")
            else:
                print("Comando no reconocido. Usa 'quit' para salir.")
                
        except KeyboardInterrupt:
            print("\n👋 ¡Hasta luego!")
            break
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    print("🚀 Iniciando demostración del sistema I18n...")
    
    try:
        # Ejecutar demostraciones
        demo_translations()
        test_file_creation()
        
        # Preguntar si quiere modo interactivo
        response = input("\n¿Quieres probar el modo interactivo? (s/n): ").lower().strip()
        if response in ['s', 'si', 'sí', 'y', 'yes']:
            interactive_demo()
        
        print("\n🎉 ¡Demostración finalizada!")
        print("\nPara usar el sistema I18n en tu aplicación:")
        print("1. from utils.i18n import tr, set_language")
        print("2. Usa tr('clave') para traducir")
        print("3. Usa set_language('en') para cambiar idioma")
        
    except Exception as e:
        print(f"❌ Error durante la demostración: {e}")
        import traceback
        traceback.print_exc()