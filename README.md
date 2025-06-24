# F1 & MotoGP Dashboard

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
