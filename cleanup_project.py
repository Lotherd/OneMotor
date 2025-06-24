# cleanup_project.py
"""
Project cleanup script - removes unnecessary files and converts comments to English
"""

import os
import shutil
from pathlib import Path
from datetime import datetime

def backup_before_cleanup():
    """Create backup before cleanup"""
    backup_name = f"backup_before_cleanup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    backup_dir = Path(backup_name)
    
    print(f"🔄 Creating backup: {backup_dir}")
    
    # Copy entire project except __pycache__ and .git
    shutil.copytree(".", backup_dir, ignore=shutil.ignore_patterns(
        '__pycache__', '*.pyc', '.git', 'venv', 'env', '.env',
        'backup_*', '*.log'
    ))
    
    print(f"✅ Backup created: {backup_dir}")
    return backup_dir

def remove_unnecessary_files():
    """Remove unnecessary files"""
    
    files_to_remove = [
        "test_api_connection.py",
        "demo_i18n.py", 
        "quick_fix.py",
        "update_app.py",
        "import sys.py"
    ]
    
    dirs_to_remove = [
        "backup_20250624_113340"
    ]
    
    print("\n🗑️  Removing unnecessary files...")
    
    # Remove files
    for file_name in files_to_remove:
        file_path = Path(file_name)
        if file_path.exists():
            file_path.unlink()
            print(f"   ❌ Removed: {file_name}")
        else:
            print(f"   ℹ️  Not found: {file_name}")
    
    # Remove directories
    for dir_name in dirs_to_remove:
        dir_path = Path(dir_name)
        if dir_path.exists():
            shutil.rmtree(dir_path)
            print(f"   ❌ Removed directory: {dir_name}")
        else:
            print(f"   ℹ️  Directory not found: {dir_name}")

def update_default_language():
    """Update default language to English in settings"""
    
    settings_file = Path("config/settings.py")
    if settings_file.exists():
        content = settings_file.read_text(encoding='utf-8')
        
        # Change default language from "es" to "en"
        content = content.replace(
            'DEFAULT_LANGUAGE = "es"',
            'DEFAULT_LANGUAGE = "en"'
        )
        
        settings_file.write_text(content, encoding='utf-8')
        print("✅ Updated default language to English")

def show_project_structure():
    """Show clean project structure"""
    
    print("\n📁 CLEAN PROJECT STRUCTURE:")
    print("=" * 50)
    
    essential_files = [
        "main.py",                    # ⭐ Entry point
        "settings.json",              # 💾 User settings
        "config/",
        "├── __init__.py",
        "├── settings.py",            # ⚙️ App configuration
        "services/",
        "├── __init__.py", 
        "├── api_client.py",          # 🌐 API services
        "├── data_service.py",        # 📊 Data processing
        "models/",
        "├── __init__.py",
        "├── driver.py",              # 🏎️ Data models
        "ui/",
        "├── __init__.py",
        "├── main_window.py",         # 🖥️ Main interface
        "├── styles/",
        "│   ├── __init__.py",
        "│   └── app_styles.py",      # 🎨 UI styles
        "├── widgets/",
        "│   ├── __init__.py",
        "│   ├── f1_tab.py",          # 🏁 F1 interface
        "│   └── motogp_tab.py",      # 🏍️ MotoGP interface
        "utils/",
        "├── __init__.py",
        "├── i18n.py",                # 🌍 Internationalization
        "translations/",
        "├── en.json",                # 🇺🇸 English translations
        "├── es.json",                # 🇪🇸 Spanish translations
        "logs/",                      # 📋 Auto-generated logs
        "└── app.log"
    ]
    
    for item in essential_files:
        if item.endswith("/"):
            print(f"📁 {item}")
        elif item.startswith("├── ") or item.startswith("│   ") or item.startswith("└── "):
            print(f"   {item}")
        else:
            path = Path(item)
            if path.exists():
                print(f"✅ {item}")
            else:
                print(f"❌ {item} (missing)")

def update_readme():
    """Update README with English content"""
    
    readme_content = """# F1 & MotoGP Dashboard

A modern desktop application for following Formula 1 and MotoGP championships with real-time data and multilingual support.

## ✨ Features

- 🏎️ **Real-time F1 standings** - Current season driver and constructor standings
- 🌍 **Multilingual support** - English and Spanish interface
- 📊 **Clean data visualization** - Modern PyQt6 interface
- 🔄 **Auto-refresh** - Automatic data updates
- 🎨 **Modern UI** - Responsive design with F1/MotoGP theming
- 🏍️ **MotoGP support** - Coming soon

## 🚀 Quick Start

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the application:**
   ```bash
   python main.py
   ```

## 🛠️ Technology Stack

- **Framework:** PyQt6
- **Language:** Python 3.8+
- **API:** Jolpica F1 API (Ergast replacement)
- **Architecture:** MVC pattern with modular design

## 📁 Project Structure

```
OneMotor/
├── main.py              # Application entry point
├── config/              # Configuration
│   └── settings.py      # App settings
├── services/            # API and data services
├── models/              # Data models
├── ui/                  # User interface
│   ├── main_window.py   # Main window
│   ├── widgets/         # UI components
│   └── styles/          # CSS styles
├── utils/               # Utilities
│   └── i18n.py          # Internationalization
└── translations/        # Language files
    ├── en.json          # English
    └── es.json          # Spanish
```

## 🌍 Supported Languages

- 🇺🇸 **English** (default)
- 🇪🇸 **Spanish**

Change language from: **View → Language**

## 📊 Data Sources

- **F1 Data:** [Jolpica F1 API](https://github.com/jolpica/jolpica-f1) (Ergast replacement)
- **Rate Limit:** 200 requests/hour (unauthenticated)

## 🔧 Development

### Adding New Languages

1. Create new translation file: `translations/{lang_code}.json`
2. Update `utils/i18n.py` to include the new language
3. Add menu option in `ui/main_window.py`

### Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature-name`
3. Commit changes: `git commit -am 'Add feature'`
4. Push to branch: `git push origin feature-name`
5. Submit pull request

## 📝 License

This project is open source and available under the MIT License.

## 🏁 Roadmap

- ✅ F1 real-time standings
- ✅ Multilingual support
- 🔲 F1 race calendar
- 🔲 Historical race results
- 🔲 MotoGP integration
- 🔲 Live race updates
- 🔲 Telemetry analysis

---

Made with ❤️ for motorsport fans
"""
    
    readme_path = Path("README.md")
    readme_path.write_text(readme_content, encoding='utf-8')
    print("✅ Updated README.md with English content")

def create_requirements_file():
    """Create requirements.txt file"""
    
    requirements = """PyQt6>=6.4.0
requests>=2.28.0
pathlib>=1.0.0
"""
    
    req_path = Path("requirements.txt")
    req_path.write_text(requirements, encoding='utf-8')
    print("✅ Created requirements.txt")

def main():
    """Main cleanup function"""
    
    print("🧹 PROJECT CLEANUP & ENGLISH CONVERSION")
    print("=" * 50)
    print("This script will:")
    print("• Remove unnecessary files")
    print("• Set English as default language")
    print("• Update documentation")
    print("• Show clean project structure")
    
    confirm = input("\nContinue? (y/n): ").lower().strip()
    if confirm not in ['y', 'yes', 'si', 'sí']:
        print("❌ Cleanup cancelled")
        return
    
    # Create backup
    backup_dir = backup_before_cleanup()
    
    try:
        # Remove unnecessary files
        remove_unnecessary_files()
        
        # Update settings
        update_default_language()
        
        # Update documentation
        update_readme()
        create_requirements_file()
        
        # Show final structure
        show_project_structure()
        
        print("\n🎉 CLEANUP COMPLETED SUCCESSFULLY!")
        print("=" * 50)
        print("✅ Removed unnecessary files")
        print("✅ Set English as default language") 
        print("✅ Updated README.md")
        print("✅ Created requirements.txt")
        print(f"✅ Backup available at: {backup_dir}")
        
        print("\n📋 NEXT STEPS:")
        print("1. Review the updated files")
        print("2. Test the application: python main.py")
        print("3. Commit the cleaned project to git")
        print("4. Delete old backup folders if everything works")
        
        print("\n🚀 Your project is now clean and ready for international collaboration!")
        
    except Exception as e:
        print(f"\n❌ Error during cleanup: {e}")
        print(f"You can restore from backup: {backup_dir}")

if __name__ == "__main__":
    main()