# Guía del Usuario: i18n Translation Automation

Este documento proporciona una guía detallada para configurar, ejecutar y extender la herramienta de CLI i18n Translation Automation.

---

## 1. Arquitectura y Operación Principal

La herramienta i18n Translation Automation está diseñada para integrarse en el flujo de desarrollo de aplicaciones web multilingües. El sistema asume que las cadenas de texto de la aplicación se redactan en un idioma principal (como el español) y deben replicarse y traducirse de forma automática en múltiples idiomas de destino.

Todas las claves y valores de traducción se almacenan en un único archivo JSON estructurado (por defecto: `data/messages.json`). Al añadir o importar una traducción, la herramienta realiza los siguientes pasos:
1. Carga la base de datos de traducciones existente.
2. Comprueba si hay conflictos (claves duplicadas) para evitar sobreescrituras accidentales.
3. Identifica qué idiomas de destino no tienen traducciones registradas para la clave proporcionada.
4. Realiza una petición a la API de traducción configurada (DeepL o Azure Translator) para traducir el texto original.
5. Guarda la estructura de datos actualizada de forma atómica en el disco para evitar corrupciones.
6. Genera una copia de seguridad con marca de tiempo en el directorio `backups/` antes de cada escritura.
7. Registra la transacción en el historial de cambios mensual (`changelog/`).

---

## 2. Modos de Operación y Características

La herramienta ofrece tres modos de operación independientes, adaptados a diferentes necesidades del flujo de desarrollo.

### 2.1. Modo de Comando Único
Diseñado para añadir entradas de traducción individuales de forma rápida durante el desarrollo activo.

*   **Estructura del Comando**:
    ```bash
    i18n add <clave> "<texto>"
    ```
*   **Comportamiento**: Traduce el texto proporcionado a todos los idiomas de destino configurados. Muestra las traducciones obtenidas en la consola y solicita una confirmación manual antes de escribir en el archivo de mensajes, a menos que se indiquen banderas de automatización.
*   **Parámetros Clave**:
    *   `--dry-run`: Realiza la llamada a la API y muestra los resultados en la terminal, pero no modifica el archivo JSON de mensajes ni genera copias de seguridad.
    *   `--force`: Omite la comprobación de claves duplicadas y la solicitud de confirmación manual, sobreescribiendo cualquier traducción previa registrada para la clave especificada.

### 2.2. Modo de Importación por Lotes
Diseñado para importar grandes volúmenes de traducciones, como en procesos de migración desde sistemas de traducción heredados o al integrar textos preparados por redactores externos.

*   **Estructura del Comando**:
    ```bash
    i18n import <ruta_archivo>
    ```
*   **Formatos Compatibles**:
    *   **Archivos CSV**: Deben contener dos columnas con una fila de cabecera. La primera columna debe llamarse estrictamente `key`. La segunda columna debe tener como cabecera el código del idioma de origen (por ejemplo, `es`), `text` o `value`.
        ```csv
        key,es
        auth.login.title,"Iniciar Sesión"
        auth.login.username,"Nombre de usuario"
        ```
    *   **Archivos JSON**: Un objeto JSON plano compuesto por pares clave-valor de tipo cadena.
        ```json
        {
          "auth.login.title": "Iniciar Sesión",
          "auth.login.username": "Nombre de usuario"
        }
        ```
*   **Comportamiento**: Lee cada entrada del archivo, valida que no existan claves duplicadas, traduce el texto a los idiomas configurados y actualiza el archivo de almacenamiento. Se muestra una barra de progreso durante la ejecución y un resumen detallado al finalizar (entradas añadidas, omitidas y errores detectados).
*   **Parámetros Clave**:
    *   `--dry-run`: Procesa e invoca las traducciones de la API para mostrar el resumen de las operaciones, pero no efectúa modificaciones en el sistema de archivos local.
    *   `--force`: Sobreescribe de manera automática las claves de la base de datos que coincidan con las del archivo importado.

### 2.3. Modo Interactivo
Diseñado para la incorporación continua de traducciones múltiples sin la necesidad de ejecutar comandos CLI individuales de forma repetida.

*   **Estructura del Comando**:
    ```bash
    i18n interactive
    ```
*   **Comportamiento**: Inicia un bucle continuo en la consola que solicita de forma sucesiva la clave de traducción y su correspondiente texto en el idioma origen. Cada entrada se valida, se traduce y se escribe en el archivo JSON inmediatamente antes de proceder con la siguiente clave.
*   **Salida**: Es posible finalizar el modo interactivo enviando una clave vacía o pulsando la combinación de teclas `Ctrl+C`.

---

## 3. Parámetros del Archivo de Configuración

La configuración se almacena en el archivo `config.yaml` en la raíz del proyecto. Este archivo emplea el formato estándar YAML y consta de los siguientes parámetros:

*   **`provider`** (cadena): El servicio de traducción activo. Los valores admitidos son `deepl` o `azure`.
*   **`api_key`** (cadena): Credencial de autenticación de la API. Puede especificarse la clave de forma literal o hacer referencia a una variable de entorno utilizando el prefijo `env:NOMBRE_VARIABLE`.
*   **`source_language`** (cadena): Código ISO de idioma correspondiente al texto de origen (ej., `ES`).
*   **`target_languages`** (lista de cadenas): Códigos ISO de idioma correspondientes a las traducciones requeridas (ej., `EN`, `PT-BR`).
*   **`messages_file`** (cadena): Ruta relativa o absoluta que apunta al archivo JSON principal donde se almacenan las traducciones.
*   **`azure_region`** (cadena, opcional): Requerida únicamente cuando se utiliza el proveedor `azure` para especificar la región de suscripción del servicio.

Ejemplo de `config.yaml`:
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

## 4. Instrucciones para Obtener Claves de API

### 4.1. Clave de API de DeepL
1. Acceda al portal de desarrolladores de DeepL en la dirección [https://www.deepl.com/pro-api](https://www.deepl.com/pro-api).
2. Seleccione un plan de suscripción. El plan **DeepL API Free** permite traducir hasta 500,000 caracteres al mes sin coste alguno.
3. Siga los pasos de registro del portal (es necesario introducir una tarjeta de crédito como método de verificación de identidad, pero no se realizarán cargos en el plan gratuito).
4. Diríjase a los ajustes de su cuenta de usuario y localice la sección **Claves de la API**.
5. Copie la clave generada. En los planes gratuitos, esta suele concluir con el sufijo `:fx`.

### 4.2. Clave de Azure Translator
1. Inicie sesión en el portal de Microsoft Azure en [https://portal.azure.com](https://portal.azure.com).
2. Seleccione la opción **Crear un recurso** y busque **Translator** (o Traductor).
3. Seleccione el servicio de traducción y haga clic en **Crear**.
4. Configure la suscripción de Azure, el grupo de recursos, la ubicación (región) y el plan de precios (el plan gratuito `F0` permite procesar hasta 2 millones de caracteres mensuales).
5. Una vez completado el despliegue del recurso, acceda a la sección **Claves y punto de conexión** dentro de la pestaña de administración.
6. Copie cualquiera de las dos claves de suscripción proporcionadas e identifique el nombre de la región seleccionada (por ejemplo, `westeurope` o `eastus`).

---

## 5. Comparativa de Proveedores de Traducción

La siguiente tabla presenta una comparativa técnica para ayudarle a seleccionar el proveedor idóneo para su flujo de trabajo:

| Característica | DeepL API | Azure Translator |
| :--- | :--- | :--- |
| **Calidad de Traducción** | Destaca por ofrecer traducciones con un lenguaje muy natural y preciso, especialmente en lenguas europeas. | Calidad robusta y uniforme en una cobertura más amplia de idiomas internacionales. |
| **Límite Mensual Gratuito** | 500,000 caracteres mensuales. | 2,000,000 caracteres mensuales. |
| **Complejidad de Configuración** | Registro sencillo, requiere únicamente una clave API. | Requiere cuenta activa de Microsoft Azure, configurar un recurso de traducción, clave de API y región. |
| **Control de Formalidad** | Soportado (permite alternar entre tono formal e informal de forma dinámica). | No disponible de manera nativa en el endpoint básico de traducción. |
| **Uso de Regiones** | Estructura de clave de ámbito global. | Vinculado a la región configurada en el recurso de Azure. |

Para proyectos cuyo idioma de origen sea el español y tengan como destino el inglés o portugués, se recomienda el uso de DeepL por la naturalidad de su motor. Si su aplicación requiere traducir volúmenes superiores a los 500,000 caracteres mensuales o necesita idiomas de menor difusión, Azure Translator constituye una alternativa altamente eficiente.
