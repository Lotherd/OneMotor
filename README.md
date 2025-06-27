# 🏎️ Motorsport Dashboard

A modern desktop application for following Formula 1 and MotoGP championships with real-time data, multilingual support, and a professional dark-themed interface.

## 🌟 Current Features

### ✅ **Implemented & Working**
- 🏎️ **F1 Real-time Standings** - Live driver championship standings with podium highlighting
- 📅 **F1 Race Calendar** - 2025 season calendar with race results and podium displays
- 🌍 **Multilingual Support** - Complete English/Spanish localization system
- 🎨 **Modern Dark UI** - Professional dark theme with F1 red accents
- 🖥️ **High-Quality Interface** - Responsive PyQt6 design with smooth animations
- 🔄 **Auto-refresh Data** - Background threading for non-blocking UI updates
- 🏆 **Podium Visualization** - Gold/silver/bronze highlighting for race winners
- 📊 **Interactive Tables** - Sortable, styled tables with hover effects
- 🎯 **Smart Navigation** - Card-based home screen with smooth transitions
- ⚡ **API Fallback System** - Multiple endpoint support for reliable data access
- 📱 **High-DPI Support** - Crisp rendering on all screen types
- 🔧 **Modular Architecture** - Clean MVC pattern with extensible design

### 🎨 **User Interface Highlights**
- **Home Screen**: Large interactive cards for F1/MotoGP selection
- **F1 Section**: Tabbed interface with standings and calendar
- **Dark Theme**: Professional motorsport-inspired color scheme
- **Responsive Design**: Adaptive layouts for different screen sizes
- **Smooth Animations**: Hover effects and transition animations
- **High-Quality Icons**: PNG icons with multiple resolution support

## 🚧 **In Development**

### 🔲 **MotoGP Integration** (Phase 3)
- MotoGP API integration
- MotoGP standings display
- MotoGP race calendar
- Real-time MotoGP data

### 🔲 **Enhanced F1 Features** (Phase 2)
- Historical race data analysis
- Driver/team detailed statistics
- Performance trending graphs
- Qualifying results display

### 🔲 **Advanced Features** (Phase 4)
- Live race updates during sessions
- Telemetry data visualization
- Predictive analytics with ML
- Real-time timing data
- Push notifications for race events

### 🔲 **Additional Improvements**
- More language support (French, German, Italian)
- Data export functionality (CSV, PDF)
- Offline mode with cached data
- Custom themes and color schemes
- User preferences and settings panel

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd motorsport-dashboard
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application:**
   ```bash
   python main.py
   ```

## 🛠️ Technology Stack

### **Core Technologies**
- **Framework:** PyQt6 (Modern Qt framework for Python)
- **Language:** Python 3.8+
- **Architecture:** MVC pattern with modular design
- **Threading:** QThread for background operations

### **APIs & Data Sources**
- **Primary:** [Jolpica F1 API](https://github.com/jolpica/jolpica-f1) (Ergast replacement)
- **Backup:** OpenF1 API (alternative endpoint)
- **Rate Limit:** 200 requests/hour (unauthenticated)

### **Key Libraries**
- `PyQt6` - GUI framework
- `requests` - HTTP client for API calls
- `pathlib` - Modern path handling
- `logging` - Comprehensive logging system
- `json` - Settings and translation management

## 📁 Project Structure

```
motorsport-dashboard/
├── main.py                 # 🚀 Application entry point
├── config/                 # ⚙️ Configuration management
│   ├── __init__.py
│   └── settings.py         # App settings and API configuration
├── models/                 # 📊 Data models
│   ├── __init__.py
│   ├── driver.py          # Driver, Constructor, DriverStanding models
│   └── race.py            # Race and calendar models
├── services/               # 🌐 API and data services
│   ├── __init__.py
│   ├── api_client.py      # HTTP client with fallback endpoints
│   └── data_service.py    # Data processing and threading
├── ui/                     # 🖥️ User interface components
│   ├── __init__.py
│   ├── main_window.py     # Main application window
│   ├── styles/            # 🎨 CSS styling
│   │   ├── __init__.py
│   │   └── app_styles.py  # Centralized styling system
│   └── widgets/           # 🧩 UI components
│       ├── __init__.py
│       ├── f1_tab.py      # F1 interface with dark theme
│       └── motogp_tab.py  # MotoGP development preview
├── utils/                  # 🔧 Utility functions
│   ├── __init__.py
│   ├── i18n.py            # Internationalization system
│   └── image_utils.py     # High-quality image processing
├── translations/           # 🌍 Language files
│   ├── en.json            # English translations
│   └── es.json            # Spanish translations
├── logo/                   # 🖼️ Application assets
│   ├── f1_logo.png        # F1 branding (optional)
│   ├── motogp_logo.png    # MotoGP branding (optional)
│   ├── home.png           # Navigation icons
│   ├── refresh.png
│   ├── standing.png
│   └── calendar.png
├── logs/                   # 📋 Application logs (auto-generated)
├── settings.json          # 💾 User preferences (auto-generated)
└── requirements.txt       # 📦 Python dependencies
```

## 🌍 Language Support

### **Currently Supported**
- 🇺🇸 **English** (default)
- 🇪🇸 **Spanish** (complete translation)

### **Planned Languages**
- 🇫🇷 French
- 🇩🇪 German
- 🇮🇹 Italian
- 🇵🇹 Portuguese

**Change language:** Menu → Language → Select your preference

## 📊 Data Features

### **F1 Championship Standings**
- Real-time driver positions and points
- Constructor/team standings
- Win counts and statistics
- Podium position highlighting (Gold/Silver/Bronze)
- Driver nationality and team information

### **F1 Race Calendar**
- Complete 2025 season schedule
- Race dates and circuit information
- Podium results for completed races
- Grand Prix names and locations

### **Data Reliability**
- Multiple API endpoint fallback
- Automatic retry on failures
- Background data loading
- Cached data for offline viewing
- Error handling and user feedback

## 🔧 Development

### **Adding New Languages**

1. **Create translation file:**
   ```bash
   touch translations/fr.json  # For French
   ```

2. **Add language to i18n.py:**
   ```python
   # In utils/i18n.py
   def get_available_languages(self) -> Dict[str, str]:
       return {
           "en": "English",
           "es": "Español", 
           "fr": "Français"  # Add new language
       }
   ```

3. **Add menu option:**
   ```python
   # In ui/main_window.py setup_menu()
   fr_action = QAction("🇫🇷 Français", self)
   fr_action.triggered.connect(lambda: self.change_language("fr"))
   lang_menu.addAction(fr_action)
   ```

### **Adding New Data Sources**

1. **Create API client:**
   ```python
   # In services/api_client.py
   class NewAPIClient(APIClient):
       def __init__(self):
           super().__init__("https://api.example.com")
   ```

2. **Add data models:**
   ```python
   # In models/
   @dataclass
   class NewDataModel:
       # Define your data structure
   ```

3. **Integrate with UI:**
   ```python
   # In ui/widgets/
   class NewTabWidget(QWidget):
       # Create UI components
   ```

### **Code Quality Standards**

- **Documentation:** All functions have detailed docstrings
- **Type Hints:** Complete type annotations throughout
- **Error Handling:** Comprehensive exception management
- **Logging:** Detailed logging for debugging
- **Testing:** Unit tests for core functionality (planned)
- **Code Style:** PEP 8 compliant with consistent formatting

## 🎯 Roadmap

### **📅 Phase 1 (Completed)** ✅
- ✅ Application base structure
- ✅ F1 API integration (Jolpica/Ergast)
- ✅ Real-time F1 standings
- ✅ Dark theme UI design
- ✅ Multilingual support (EN/ES)
- ✅ High-quality interface components

### **📅 Phase 2 (Next - Q1 2025)** 🔄
- 🔲 Enhanced F1 race calendar features
- 🔲 Historical F1 race results
- 🔲 Motorsport news integration
- 🔲 Data export functionality
- 🔲 Performance improvements

### **📅 Phase 3 (Future - Q2 2025)** 🔲
- 🔲 MotoGP API integration
- 🔲 MotoGP standings and calendar
- 🔲 Real-time MotoGP data
- 🔲 Unified motorsport dashboard

### **📅 Phase 4 (Advanced - Q3 2025)** 🔲
- 🔲 Live race timing data
- 🔲 Detailed telemetry analysis
- 🔲 Performance analytics
- 🔲 Machine learning predictions
- 🔲 Mobile companion app

## 🔧 Configuration

### **API Settings**
```python
# config/settings.py
F1_API_ENDPOINTS = [
    "http://api.jolpi.ca/ergast/f1",      # Primary
    "https://api.jolpi.ca/ergast/f1",     # HTTPS backup
    "https://openf1.org/v1"               # Alternative
]
REQUEST_TIMEOUT = 15  # seconds
```

### **UI Customization**
```python
# config/settings.py
COLORS = {
    'f1_red': '#e10600',
    'motogp_blue': '#0066cc',
    'background': '#f8f9fa'
}
```

## 🤝 Contributing

We welcome contributions to improve the Motorsport Dashboard!

### **How to Contribute**

1. **Fork the repository**
2. **Create a feature branch:**
   ```bash
   git checkout -b feature/amazing-feature
   ```
3. **Make your changes with proper documentation**
4. **Test thoroughly**
5. **Commit with descriptive messages:**
   ```bash
   git commit -m "Add amazing feature for MotoGP integration"
   ```
6. **Push to your branch:**
   ```bash
   git push origin feature/amazing-feature
   ```
7. **Submit a Pull Request**

### **Development Setup**

```bash
# Clone your fork
git clone https://github.com/yourusername/motorsport-dashboard.git
cd motorsport-dashboard

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -r requirements.txt

# Run the application
python main.py
```

### **Code Contribution Guidelines**

- Follow existing code style and documentation format
- Add comprehensive docstrings to all functions
- Include type hints for parameters and return values
- Write unit tests for new functionality
- Update translations if adding user-facing text
- Test on multiple platforms if possible

## 📝 License

This project is open source and available under the **MIT License**.

```
MIT License - Feel free to use, modify, and distribute
```

## 🏁 About

### **Project Goals**
- Provide real-time motorsport data in a beautiful interface
- Support multiple racing series (F1, MotoGP, and more)
- Offer a professional-quality desktop application
- Maintain high code quality and extensibility
- Support the global motorsport community

### **Technical Excellence**
- **Clean Architecture:** Modular MVC design
- **High Performance:** Background threading and caching
- **User Experience:** Intuitive navigation and visual feedback
- **Reliability:** Multiple API endpoints and error handling
- **Accessibility:** High-DPI support and clear typography
- **Internationalization:** Complete multi-language support

---

**Made with ❤️ for motorsport fans worldwide**

*Experience the thrill of motorsport data like never before!*

---

## 📞 Support & Contact

- **Issues:** Report bugs or request features via GitHub Issues
- **Documentation:** Check the code comments for detailed implementation info  
- **Community:** Join discussions in GitHub Discussions

**Happy Racing! 🏁**