# oracle-wac-automation

Bot de automatización de actualización de **Costo Promedio Ponderado (WAC)** en Oracle RMS mediante Selenium y Excel.

---

## ✨ Características

- 🔐 Login manual interactivo (ventana de 2 minutos)
- 🔄 Sincronización con Oracle ADF (AJAX)
- ✅ Validaciones de negocio antes de escribir en Oracle
- 🧮 Cálculo automático del WAC ponderado con precisión decimal
- 📊 Actualización del Excel en tiempo real con colores de estado
- 📋 Logging completo a consola y archivo rotativo
- 🔁 2 reintentos automáticos con 5 segundos de espera
- 🌐 Mantiene el navegador abierto al finalizar

---

## 🗂️ Estructura del proyecto

```
oracle-wac-automation/
├── main.py                    # Script principal
├── config.py                  # Configuración centralizada y tabla de ubicaciones
├── create_example_excel.py    # Genera un Excel de ejemplo
├── requirements.txt           # Dependencias Python
├── .env.example               # Variables de entorno de ejemplo
├── QUICK_START.md             # Guía de inicio rápido
├── data/
│   └── wac_update.xlsx        # Archivo Excel de entrada/salida
├── logs/
│   └── wac_bot.log            # Log rotativo
└── src/
    ├── __init__.py
    ├── logger_setup.py        # Configuración de logging
    ├── driver_setup.py        # Inicialización de Chrome WebDriver
    ├── adf_synchronizer.py    # Sincronización Oracle ADF/AJAX
    ├── excel_handler.py       # Lectura y escritura de Excel
    ├── location_resolver.py   # Validación de códigos de ubicación
    ├── calculator.py          # Cálculos financieros WAC
    ├── oracle_navigator.py    # Interacciones con Oracle RMS
    └── sku_processor.py       # Procesamiento de registros SKU
```

---

## 🚀 Inicio rápido

Consulta [QUICK_START.md](QUICK_START.md) para instrucciones detalladas.

```bash
pip install -r requirements.txt
cp .env.example .env          # Edita con tu URL y credenciales
python create_example_excel.py
python main.py
```

---

## ⚙️ Configuración

Edita `.env` para ajustar los parámetros del bot:

| Variable | Descripción | Default |
|----------|-------------|---------|
| `ORACLE_URL` | URL de Oracle RMS | — |
| `ORACLE_USERNAME` | Usuario Oracle | — |
| `ORACLE_PASSWORD` | Contraseña Oracle | — |
| `LOGIN_WAIT_SECONDS` | Tiempo de espera login manual | `120` |
| `ADF_SYNC_TIMEOUT` | Timeout sincronización ADF | `30` |
| `MAX_RETRIES` | Reintentos por SKU | `2` |
| `RETRY_WAIT_SECONDS` | Espera entre reintentos | `5` |
| `EXCEL_INPUT_FILE` | Ruta al archivo Excel | `data/wac_update.xlsx` |

Los selectores de Oracle RMS (XPath) se configuran en `config.SELECTORS` dentro de `config.py`.

---

## 📦 Dependencias

| Paquete | Propósito |
|---------|-----------|
| `selenium` | Automatización de Chrome |
| `webdriver-manager` | Gestión automática de ChromeDriver |
| `openpyxl` | Lectura/escritura de Excel |
| `python-dotenv` | Variables de entorno |

---

## 📋 Formato del Excel

El archivo Excel debe tener las siguientes columnas (se crean automáticamente con `create_example_excel.py`):

| Columna | Tipo | Descripción |
|---------|------|-------------|
| `SKU` | Texto | Código del producto (**requerido**) |
| `LOCATION` | Texto | Código de ubicación (**requerido**) |
| `NEW_WAC` | Número | Nuevo costo unitario (**requerido**) |
| `UNITS` | Número | Cantidad de unidades (**requerido**) |
| `CURRENT_WAC` | Número | WAC actual (escrito por el bot) |
| `STATUS` | Texto | Estado del proceso (escrito por el bot) |
| `NOTES` | Texto | Notas / detalle de error (escrito por el bot) |
| `TIMESTAMP` | Texto | Fecha/hora de procesamiento (escrito por el bot) |

---

## 📍 Tabla de ubicaciones

La tabla de ubicaciones se define en `config.LOCATION_TABLE`. Incluye almacenes centrales, tiendas y centros de distribución. Modifica este diccionario para adaptarlo a tu organización.

---

## 🔒 Seguridad

- Las credenciales se almacenan en `.env` (no incluido en el repositorio, ver `.gitignore`).
- No hardcodees contraseñas en el código.

---

## 📄 Licencia

[MIT](LICENSE)

