# i18n Translation Automation

[Leer este manual en español](README.es.md)

A specialized Python CLI tool to automate i18n translation workflows for multilingual web application development. Write your source texts in a single language and translate them instantly to multiple languages using translation APIs of your choice (DeepL/Azure), while maintaining a structured `messages.json` file with automatic backups and monthly changelogs.

---

## Features

- **Multiple Translation Providers**: Built-in support for DeepL (default) and Azure Translator, with a clean interface for adding custom APIs.
- **Three Core Operational Modes**:
  1. **Single Command Mode** (`i18n add`): Add and translate a single key-value entry instantly.
  2. **Bulk Import Mode** (`i18n import`): Import and translate multiple keys from a flat JSON or a simple 2-column CSV file.
  3. **Interactive Mode** (`i18n interactive`): Enter multiple translation keys recursively in a dedicated prompt loop.
- **Bilingual and Clean Setup Wizard**: Configure your provider, source language, target languages, and file paths in minutes.
- **Automatic Backups**: Creates a timestamped backup copy of `messages.json` in `backups/` before any write operation.
- **Operation Changelog**: Generates clean, monthly partition logs in `changelog/YYYY-MM.log` documenting all translations.
- **Dry-run Mode**: Test and preview translations directly in the CLI using `--dry-run` without modifying your files.
- **Overwrite Safety**: Aborts with warning if a key already exists, preventing accidental overrides unless the `--force` flag is specified.

---

## Detailed Guides

For extensive guides, step-by-step instructions on obtaining API keys, provider comparisons, and custom configurations, please refer to the documentation directory:
- [English User Guide](docs/guide.md)
- [Guía de Usuario en Español](docs/guia.md)

---

## Requirements

- Python 3.9 or later
- A valid API key for your chosen translation provider (e.g., DeepL Free API key, Azure subscription key).

---

## Getting Started

### 1. Clone & Set Up Directory
Clone this repository to your local system and enter the project folder:
```bash
git clone https://github.com/Daclapo/i18n-TranslationAutomation.git
cd i18n-TranslationAutomation
```

### 2. Virtual Environment Setup
It is recommended to run the tool inside a Python virtual environment:
```bash
# Create virtual environment
python3 -m venv venv

# Activate on macOS/Linux
source venv/bin/activate

# Activate on Windows (cmd)
venv\Scripts\activate.bat

# Activate on Windows (PowerShell)
.\venv\Scripts\Activate.ps1
```

### 3. Install Package (Editable Mode)
Install the project and its dependencies in development mode:
```bash
pip install -e ".[dev]"
```
This registers the global CLI command `i18n` in your current terminal environment.

### 4. Configure API Keys
Copy the environment variables template and add your API credentials:
```bash
cp .env.example .env
```
Open `.env` and fill in your DeepL or Azure API key:
```env
DEEPL_API_KEY=your-actual-deepl-api-key-here
```
*(Your `.env` file containing real keys is automatically ignored by Git and will not be shared publicly)*.

### 5. Run the Setup Wizard
Initialize your project's configuration:
```bash
i18n setup
```
The wizard will guide you through the configuration parameters:
1. **Translation provider**: `deepl` or `azure`.
2. **API key**: Enter `env:DEEPL_API_KEY` to securely load the key from the environment/`.env` file without hardcoding it in the config file.
3. **Source language**: (e.g., `ES` for Spanish).
4. **Target languages**: Comma-separated list (e.g., `EN, PT-BR`).
5. **Messages file path**: Path to save your translation file (e.g., `data/messages.json`).

This generates a clean `config.yaml` file in the project root.

---

## Usage Guide

### 1. Single Command Addition
Translate a Spanish source text to all configured target languages:
```bash
i18n add home.hero.title "Bienvenido a nuestra plataforma de automatización"
```
**Options:**
- `--dry-run`: View translations in the console without updating the JSON file.
- `--force`: Automatically overwrite the key if it already exists, skipping confirmation.

### 2. Bulk Import
Import and translate entries from an external file:
```bash
i18n import new_translations.csv
# or
i18n import new_translations.json
```
- **CSV Format**: A 2-column file with headers (column 1: key, column 2: source language code, text, or value):
  ```csv
  key,es
  nav.about,"Sobre Nosotros"
  nav.contact,"Contacta con nuestro equipo"
  ```
- **JSON Format**: A flat key-value map:
  ```json
  {
    "button.submit": "Enviar solicitud",
    "button.cancel": "Cancelar operación"
  }
  ```

### 3. Interactive CLI Loop
Enter interactive mode to recursively translate multiple keys without running individual CLI commands:
```bash
i18n interactive
```
*Leave the key input blank or press `Ctrl+C` to safely exit the interactive loop.*

---

## Output JSON Structure

All translations are compiled into a structured `messages.json` file in your data folder, formatted as follows:

```json
{
  "es": {
    "home.hero.title": "Bienvenido a nuestra plataforma de automatización",
    "nav.about": "Sobre Nosotros"
  },
  "en": {
    "home.hero.title": "Welcome to our automation platform",
    "nav.about": "About Us"
  },
  "pt-br": {
    "home.hero.title": "Bem-vindo à nossa plataforma de automação",
    "nav.about": "Sobre Nós"
  }
}
```

---

## Development, Testing and Extensibility

### Running Tests
Automated unit and integration tests are located in the `tests/` directory and use mocked API providers. No internet connection or real API keys are required to run them:
```bash
pytest tests/ -v
```

### Adding a Custom Provider
You can easily plug in a new translation service (e.g. OpenAI, Google Cloud, AWS Translate):
1. Create a new provider file in `src/i18n_manager/providers/` (e.g., `my_custom_provider.py`).
2. Inherit from the abstract `TranslationProvider` base class and implement the `translate` method:
   ```python
   from i18n_manager.providers.base import TranslationProvider

   class MyCustomProvider(TranslationProvider):
       def __init__(self, api_key: str, **kwargs):
           self.api_key = api_key

       def translate(self, text: str, source_lang: str, target_lang: str) -> str:
           # Implement your API translation call here
           return translated_text
   ```
3. Register the new provider class in `src/i18n_manager/providers/__init__.py`:
   ```python
   from i18n_manager.providers.my_custom_provider import MyCustomProvider
   PROVIDER_REGISTRY["mycustom"] = MyCustomProvider
   ```
4. Run `i18n setup` and choose `mycustom` as your active provider.

---

## Project File Structure

```
i18n-TranslationAutomation/
├── pyproject.toml          # Project configuration, scripts, and dependencies
├── config.yaml             # Core tool settings (generated by setup)
├── .env                    # Stored API keys (ignored by git - template in .env.example)
├── .env.example            # Environment variables template for new clones
├── .gitignore              # Git exclusions (venv, .env, backups, caches)
├── CONTEXT.md              # Technical project overview and architecture decisions
├── docs/                   # Exhaustive user guides
│   ├── guide.md            # Detailed English User Guide
│   └── guia.md             # Detailed Spanish User Guide
├── data/
│   └── messages.json       # Main multi-language translation output file
├── src/
│   └── i18n_manager/       # Source code root
│       ├── cli.py          # Command Line Interface (click) definitions
│       ├── config.py       # Configuration parser and env loader
│       ├── storage.py      # Safe atomic JSON writers, backups, changelogs
│       ├── translator.py   # Translation orchestrator
│       └── providers/      # API Translation Providers
│           ├── __init__.py # Provider Registry
│           ├── base.py     # Base abstract TranslationProvider class
│           ├── deepl_provider.py
│           └── azure_provider.py
├── backups/                # Automatically generated timestamped backups
├── changelog/              # Monthly operation logs (changelog/YYYY-MM.log)
└── tests/                  # Fully mocked automated test suite
```
