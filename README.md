# i18n Translation Automation

A specialized Python CLI tool to automate i18n translation workflows for multilingual web application development. Write your source texts in a single language and translate them instantly to multiple languages using translation APIs of your choice (DeepL/Azure), while maintaining a structured messages.json file with automatic backups and monthly changelogs.

---

Una herramienta de CLI en Python especializada en automatizar flujos de traducción i18n para el desarrollo de aplicaciones web multilingües. Escribe tus textos fuente en un único idioma y tradúcelos instantáneamente a múltiples idiomas destino utilizando las APIs de traducción de tu elección (DeepL/Azure), manteniendo un archivo estructurado messages.json con copias de seguridad automáticas y registros mensuales de cambios.

---

## Choose your language / Elige tu idioma

Please select your language from the collapsible sections below to access the full documentation:

Por favor, selecciona tu idioma en las secciones desplegables a continuación para acceder a la documentación completa:

* [English Documentation](#english-documentation)
* [Documentación en Español](#documentación en español)

---

## English Documentation

<details open>
<summary><strong>Click to expand / collapse English Guide</strong></summary>

### Features

- **Multiple Translation Providers**: Built-in support for DeepL (default) and Azure Translator, with a clean interface for adding custom APIs.
- **Three Core Operational Modes**:
  1. **Single Command Mode** (i18n add): Add and translate a single key-value entry instantly.
  2. **Bulk Import Mode** (i18n import): Import and translate multiple keys from a flat JSON or a simple 2-column CSV file.
  3. **Interactive Mode** (i18n interactive): Enter multiple translation keys recursively in a dedicated prompt loop.
- **Bilingual and Clean Setup Wizard**: Configure your provider, source language, target languages, and file paths in minutes.
- **Automatic Backups**: Creates a timestamped backup copy of messages.json in backups/ before any write operation.
- **Operation Changelog**: Generates clean, monthly partition logs in changelog/YYYY-MM.log documenting all translations.
- **Dry-run Mode**: Test and preview translations directly in the CLI using --dry-run without modifying your files.
- **Overwrite Safety**: Aborts with warning if a key already exists, preventing accidental overrides unless the --force flag is specified.

---

### Requirements

- Python 3.9 or later
- A valid API key for your chosen translation provider (e.g., DeepL Free API key, Azure subscription key).

---

### Getting Started

#### 1. Clone & Set Up Directory
Clone this repository to your local system and enter the project folder:
```bash
git clone https://github.com/Daclapo/i18n-TranslationAutomation.git
cd i18n-TranslationAutomation
```

#### 2. Virtual Environment Setup
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

#### 3. Install Package (Editable Mode)
Install the project and its dependencies in development mode:
```bash
pip install -e ".[dev]"
```
This registers the global CLI command i18n in your current terminal environment.

#### 4. Configure API Keys
Copy the environment variables template and add your API credentials:
```bash
cp .env.example .env
```
Open .env and fill in your DeepL or Azure API key:
```env
DEEPL_API_KEY=your-actual-deepl-api-key-here
```
(Your .env file containing real keys is automatically ignored by Git and will not be shared publicly).

#### 5. Run the Setup Wizard
Initialize your project's configuration:
```bash
i18n setup
```
The wizard will guide you through the configuration parameters:
1. **Translation provider**: deepl or azure.
2. **API key**: Enter env:DEEPL_API_KEY to securely load the key from the environment/.env file without hardcoding it in the config file.
3. **Source language**: (e.g., ES for Spanish).
4. **Target languages**: Comma-separated list (e.g., EN, PT-BR).
5. **Messages file path**: Path to save your translation file (e.g., data/messages.json).

This generates a clean config.yaml file in the project root.

---

### Usage Guide

#### 1. Single Command Addition
Translate a Spanish source text to all configured target languages:
```bash
i18n add home.hero.title "Bienvenido a nuestra plataforma de automatización"
```
**Options:**
- `--dry-run`: View translations in the console without updating the JSON file.
- `--force`: Automatically overwrite the key if it already exists, skipping confirmation.

#### 2. Bulk Import
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

#### 3. Interactive CLI Loop
Enter interactive mode to recursively translate multiple keys without running individual CLI commands:
```bash
i18n interactive
```
*Leave the key input blank or press Ctrl+C to safely exit the interactive loop.*

---

### Output JSON Structure

All translations are compiled into a structured messages.json file in your data folder, formatted as follows:

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

### Development, Testing and Extensibility

#### Running Tests
Automated unit and integration tests are located in the tests/ directory and use mocked API providers. No internet connection or real API keys are required to run them:
```bash
pytest tests/ -v
```

#### Adding a Custom Provider
You can easily plug in a new translation service (e.g. OpenAI, Google Cloud, AWS Translate):
1. Create a new provider file in src/i18n_manager/providers/ (e.g., my_custom_provider.py).
2. Inherit from the abstract TranslationProvider base class and implement the translate method:
   ```python
   from i18n_manager.providers.base import TranslationProvider

   class MyCustomProvider(TranslationProvider):
       def __init__(self, api_key: str, **kwargs):
           self.api_key = api_key

       def translate(self, text: str, source_lang: str, target_lang: str) -> str:
           # Implement your API translation call here
           return translated_text
   ```
3. Register the new provider class in src/i18n_manager/providers/__init__.py:
   ```python
   from i18n_manager.providers.my_custom_provider import MyCustomProvider
   PROVIDER_REGISTRY["mycustom"] = MyCustomProvider
   ```
4. Run i18n setup and choose mycustom as your active provider.

---

### Project File Structure

```
i18n-TranslationAutomation/
├── pyproject.toml          # Project configuration, scripts, and dependencies
├── config.yaml             # Core tool settings (generated by setup)
├── .env                    # Stored API keys (ignored by git - template in .env.example)
├── .env.example            # Environment variables template for new clones
├── .gitignore              # Git exclusions (venv, .env, backups, caches)
├── CONTEXT.md              # Technical project overview and architecture decisions
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

</details>

---

## Documentación en Español

<details>
<summary><strong>Haz clic para expandir / contraer la Guía en Español</strong></summary>

### Características

- **Múltiples Proveedores de Traducción**: Soporte nativo incorporado para DeepL (por defecto) y Azure Translator, con una interfaz limpia para añadir APIs personalizadas de forma rápida.
- **Tres Modos de Operación Clave**:
  1. **Modo de Comando Único** (i18n add): Agrega y traduce de forma instantánea una única entrada clave-valor.
  2. **Modo de Importación por Lotes** (i18n import): Importa y traduce de forma masiva múltiples claves desde un JSON plano o un archivo CSV simple de 2 columnas.
  3. **Modo Interactivo** (i18n interactive): Introduce múltiples claves de traducción de forma recursiva en un bucle interactivo optimizado.
- **Asistente de Configuración Rápido y Sencillo**: Configura tu proveedor, idioma origen, idiomas destino y rutas de archivos en cuestión de minutos.
- **Copias de Seguridad Automáticas**: Crea una copia de seguridad con marca de tiempo de tu messages.json en la carpeta backups/ antes de cada operación de escritura.
- **Registro Mensual de Cambios**: Genera registros mensuales organizados en changelog/YYYY-MM.log que documentan cada una de las traducciones realizadas.
- **Modo Dry-run**: Prueba y previsualiza las traducciones directamente en la consola usando la bandera --dry-run sin modificar tus archivos locales.
- **Seguridad contra Sobreescrituras**: Aborta con una advertencia si la clave ya existe en el JSON, evitando sobreescrituras accidentales a menos que se especifique la bandera --force.

---

### Requisitos

- Python 3.9 o superior.
- Una clave API válida para tu proveedor de traducción elegido (por ejemplo, una clave de API Gratuita de DeepL o una suscripción de Azure Translator).

---

### Primeros Pasos

#### 1. Clonar el Repositorio
Clona este repositorio en tu sistema local e ingresa a la carpeta del proyecto:
```bash
git clone https://github.com/Daclapo/i18n-TranslationAutomation.git
cd i18n-TranslationAutomation
```

#### 2. Configurar el Entorno Virtual
Se recomienda utilizar un entorno virtual de Python:
```bash
# Crear entorno virtual
python3 -m venv venv

# Activar en macOS/Linux
source venv/bin/activate

# Activar en Windows (cmd)
venv\Scripts\activate.bat

# Activar en Windows (PowerShell)
.\venv\Scripts\Activate.ps1
```

#### 3. Instalar el Paquete (Modo Editable)
Instala el proyecto y sus dependencias de desarrollo localmente:
```bash
pip install -e ".[dev]"
```
Esto registrará el comando global i18n en tu terminal actual.

#### 4. Configurar las Claves de API
Copia la plantilla de variables de entorno y añade tus credenciales de API:
```bash
cp .env.example .env
```
Abre el archivo .env resultante y completa tus credenciales de DeepL o Azure:
```env
DEEPL_API_KEY=tu-clave-real-de-deepl-aqui
```
(El archivo .env que contiene tus claves reales está excluido de Git en .gitignore por seguridad y no se subirá al repositorio público).

#### 5. Ejecutar el Asistente de Configuración
Inicializa la configuración de tu herramienta:
```bash
i18n setup
```
El asistente te guiará de forma interactiva:
1. **Translation provider (Proveedor)**: Elige deepl o azure.
2. **API key (Clave)**: Escribe env:DEEPL_API_KEY para cargar la clave de forma segura desde las variables de entorno (.env) sin exponerla directamente en texto plano en el archivo de configuración.
3. **Source language (Idioma origen)**: Código del idioma base (ej., ES para Español).
4. **Target languages (Idiomas destino)**: Lista separada por comas (ej., EN, PT-BR).
5. **Messages file path (Ruta de salida)**: Dónde guardar el archivo JSON (ej., data/messages.json).

Esto generará el archivo config.yaml en la raíz del proyecto.

---

### Guía de Uso

#### 1. Añadir una única traducción
Traduce un texto base en Español a todos tus idiomas de destino configurados:
```bash
i18n add home.hero.title "Bienvenido a nuestra plataforma de automatización"
```
**Opciones disponibles:**
- `--dry-run`: Previsualiza las traducciones generadas por la API en la consola sin guardarlas en el archivo JSON.
- `--force`: Sobreescribe la clave de traducción automáticamente si ya existe, sin pedir confirmación manual.

#### 2. Importación masiva por lotes
Importa y traduce entradas completas desde un archivo externo:
```bash
i18n import nuevas_traducciones.csv
# o
i18n import nuevas_traducciones.json
```
- **Formato CSV**: Archivo de dos columnas con cabecera (columna 1: key, columna 2: el código de idioma base (ej., es), text o value):
  ```csv
  key,es
  nav.about,"Sobre Nosotros"
  nav.contact,"Contacta con nuestro equipo"
  ```
- **Formato JSON**: Un objeto JSON plano de tipo clave-valor:
  ```json
  {
    "button.submit": "Enviar solicitud",
    "button.cancel": "Cancelar operación"
  }
  ```

#### 3. Bucle interactivo por consola
Ingresa en un bucle interactivo que te permite añadir múltiples entradas sin tener que ejecutar comandos CLI repetidamente:
```bash
i18n interactive
```
*Deja la clave vacía o presiona Ctrl+C para salir del bucle interactivo de manera segura.*

---

### Estructura del JSON de Salida

Todas tus traducciones se compilan en un único archivo estructurado messages.json dentro de tu carpeta de datos:

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

### Desarrollo, Pruebas y Extensibilidad

#### Ejecutar Pruebas Unitarias
Las pruebas automatizadas residen en el directorio tests/ y utilizan mocks para simular las llamadas a las APIs de traducción. No requieren conexión a internet ni claves reales para ejecutarse:
```bash
pytest tests/ -v
```

#### Añadir un Proveedor Personalizado
Añadir soporte para un nuevo motor de traducción (ej., OpenAI, Google Cloud Translator, AWS Translate) es muy sencillo:
1. Crea un nuevo archivo dentro de src/i18n_manager/providers/ (ej., mi_proveedor.py).
2. Hereda de la clase base abstracta TranslationProvider e implementa el método translate:
   ```python
   from i18n_manager.providers.base import TranslationProvider

   class MiProveedor(TranslationProvider):
       def __init__(self, api_key: str, **kwargs):
           self.api_key = api_key

       def translate(self, text: str, source_lang: str, target_lang: str) -> str:
           # Implementa tu llamada HTTP/API de traducción aquí
           return texto_traducido
   ```
3. Registra tu nueva clase en src/i18n_manager/providers/__init__.py:
   ```python
   from i18n_manager.providers.mi_proveedor import MiProveedor
   PROVIDER_REGISTRY["miproveedor"] = MyCustomProvider
   ```
4. Ejecuta i18n setup y selecciona miproveedor como tu proveedor activo.

---

### Estructura de Archivos del Proyecto

```
i18n-TranslationAutomation/
├── pyproject.toml          # Metadatos del paquete, comandos de CLI y dependencias
├── config.yaml             # Configuración del usuario (generada por setup)
├── .env                    # Claves API locales (ignorado por git - ver plantilla .env.example)
├── .env.example            # Plantilla de variables de entorno para nuevas clonaciones
├── .gitignore              # Exclusiones de Git (venv, .env, backups, caches)
├── CONTEXT.md              # Resumen técnico de arquitectura y decisiones de diseño
├── data/
│   └── messages.json       # Archivo JSON principal de almacenamiento de traducciones
├── src/
│   └── i18n_manager/       # Raíz del código fuente
│       ├── cli.py          # Definición de comandos de la CLI (click)
│       ├── config.py       # Lector de configuraciones y variables de entorno
│       ├── storage.py      # Gestor atómico de JSON, copias de seguridad y logs de cambios
│       ├── translator.py   # Orquestador del flujo de traducción
│       └── providers/      # Proveedores de traducción
│           ├── __init__.py # Registro de proveedores
│           ├── base.py     # Clase base abstracta TranslationProvider
│           ├── deepl_provider.py
│           └── azure_provider.py
├── backups/                # Copias de seguridad automáticas con marcas de tiempo
├── changelog/              # Logs históricos mensuales (changelog/YYYY-MM.log)
└── tests/                  # Suite completa de pruebas unitarias simuladas (mocked)
```

</details>
