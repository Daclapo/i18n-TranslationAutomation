# User Guide: i18n Translation Automation

This document provides a comprehensive guide for configuring, running, and extending the i18n Translation Automation CLI tool.

---

## 1. Core Architecture and Operation

The i18n Translation Automation CLI tool is designed to integrate into the development workflow of multilingual web applications. The tool assumes that application source strings are authored in a primary language (such as Spanish) and need to be replicated and translated across multiple target languages.

All translation keys and values are stored in a single structured JSON file (default: `data/messages.json`). When a translation is added or imported, the tool performs the following steps:
1. Loads the existing translation database.
2. Checks for conflicts (duplicate keys) to prevent accidental overwrites.
3. Identifies missing target languages for the given key.
4. Contacts the configured translation API (DeepL or Azure Translator) to translate the source text.
5. Saves the updated data structure atomically to prevent corruption.
6. Generates a timestamped backup before writing.
7. Logs the transaction in the monthly changelog.

---

## 2. Operational Modes and Features

The tool offers three distinct operational modes, each tailored to different development scenarios.

### 2.1. Single Command Mode
Designed for adding individual translation entries during active coding.

*   **Command Structure**:
    ```bash
    i18n add <key> "<text>"
    ```
*   **Behavior**: Translates the provided text into all configured target languages. It will display the translations in the console and prompt for write confirmation unless automated flags are set.
*   **Key Parameters**:
    *   `--dry-run`: Performs the translation via the API and displays the results in the terminal, but does not write to the messages file or create backups.
    *   `--force`: Bypasses the duplicate key check and confirmation prompt, overwriting any existing translations for the specified key.

### 2.2. Bulk Import Mode
Designed for importing large batches of translations, such as when migrating from an legacy translation system or importing keys prepared by copywriters.

*   **Command Structure**:
    ```bash
    i18n import <file_path>
    ```
*   **Supported Formats**:
    *   **CSV Files**: Must contain two columns with a header row. The first column header must be named `key`. The second column header must represent the source language code (e.g., `es`), `text`, or `value`.
        ```csv
        key,es
        auth.login.title,"Iniciar Sesión"
        auth.login.username,"Nombre de usuario"
        ```
    *   **JSON Files**: A flat key-value object containing string mappings.
        ```json
        {
          "auth.login.title": "Iniciar Sesión",
          "auth.login.username": "Nombre de usuario"
        }
        ```
*   **Behavior**: Reads each entry, checks for existing keys, translates them to target languages, and updates the translation file. A progress bar and a final summary (added, skipped, errors) are displayed.
*   **Key Parameters**:
    *   `--dry-run`: Parses and translates the file contents, showing the summary of operations without performing any filesystem writes.
    *   `--force`: Overwrites any keys in the database that match keys in the imported file.

### 2.3. Interactive Mode
Designed for continuous addition of multiple translations without the overhead of executing individual CLI commands repeatedly.

*   **Command Structure**:
    ```bash
    i18n interactive
    ```
*   **Behavior**: Enters a loop prompting for the translation key and the corresponding source text. Each entry is validated, translated, and committed immediately before prompting for the next entry.
*   **Termination**: Exit the loop by submitting an empty key or by pressing `Ctrl+C`.

---

## 3. Configuration File Options

Configuration is stored in `config.yaml` in the project root. The file uses the YAML standard and contains the following parameters:

*   **`provider`** (string): The active translation service. Supported values are `deepl` or `azure`.
*   **`api_key`** (string): The authentication credentials. Can be a literal key or a reference to an environment variable using the `env:VARIABLE_NAME` prefix.
*   **`source_language`** (string): The ISO language code representing the input text (e.g., `ES`).
*   **`target_languages`** (list of strings): The ISO language codes for the desired translations (e.g., `EN`, `PT-BR`).
*   **`messages_file`** (string): Relative or absolute path to the main JSON translation file.
*   **`azure_region`** (string, optional): Required only when using the Azure Translator provider to specify the subscription region.

Example `config.yaml`:
```yaml
provider: deepl
api_key: env:DEEPL_API_KEY
source_language: ES
target_languages:
  - EN
  - PT-BR
messages_file: data/messages.json
```

---

## 4. How to Obtain API Keys

### 4.1. DeepL API Key
1. Navigate to the DeepL Developer Portal at [https://www.deepl.com/pro-api](https://www.deepl.com/pro-api).
2. Select a subscription plan. The **DeepL API Free** plan allows translating up to 500,000 characters per month free of charge.
3. Complete the registration process (credit card verification is required for security, but no charges are made on the free tier).
4. Go to your Account Account settings page and locate the **API Account Key** section.
5. Copy the generated key. It typically ends with `:fx` for the free tier.

### 4.2. Azure Translator Key
1. Sign in to the Azure Portal at [https://portal.azure.com](https://portal.azure.com).
2. Click **Create a resource** and search for **Translator**.
3. Select **Translator** and click **Create**.
4. Configure the subscription, resource group, region, and pricing tier (the free tier `F0` supports up to 2 million characters per month).
5. Once the deployment is complete, navigate to the resource's **Keys and Endpoint** section.
6. Copy either of the two generated subscription keys and note the region name (e.g., `westeurope`).

---

## 5. Translation Providers Comparison

To help you decide which provider is best suited for your workflow, review the comparison below:

| Feature | DeepL API | Azure Translator |
| :--- | :--- | :--- |
| **Translation Quality** | Renowned for highly natural, context-aware translations, particularly for European languages. | Strong, consistent quality across a broader range of global languages. |
| **Free Tier Limit** | 500,000 characters per month. | 2,000,000 characters per month. |
| **Setup Complexity** | Simple registration, single API key needed. | Requires an active Microsoft Azure account, subscription setup, key, and region name. |
| **Formality Control** | Supported (can adjust formal/informal language dynamically). | Not supported natively through basic translation endpoint. |
| **Regional Keys** | Global key structure. | Tied to specific Azure regions (e.g., global, eastus, westeurope). |

For general web applications written in Spanish and translating to English or Portuguese, DeepL is recommended due to its high contextual translation quality. If your project exceeds the 500,000 character limit or targets less common languages, Azure Translator is a highly reliable alternative.
