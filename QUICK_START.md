# ⚡ Quick Start — Bot WAC Oracle RMS

## Requisitos previos
- Python 3.11+
- Google Chrome instalado
- Acceso a Oracle RMS (credenciales de usuario)

---

## 1. Instala las dependencias

```bash
pip install -r requirements.txt
```

---

## 2. Configura las variables de entorno

```bash
cp .env.example .env
# Edita .env con tu URL de Oracle y credenciales
```

---

## 3. Crea el archivo Excel de entrada

```bash
python create_example_excel.py
```

Esto genera `data/wac_update.xlsx` con datos de ejemplo.  
Edita el archivo y reemplaza los datos por los registros reales que deseas actualizar.

| Columna | Descripción |
|---------|-------------|
| `SKU` | Código del producto |
| `LOCATION` | Código de almacén / tienda (ver tabla en `config.py`) |
| `NEW_WAC` | Nuevo costo unitario a registrar |
| `UNITS` | Cantidad de unidades |

---

## 4. Ejecuta el bot

```bash
python main.py
```

El bot abrirá Chrome y esperará **2 minutos** para que hagas login manualmente.  
Después, procesará cada fila automáticamente y escribirá el resultado en el Excel.

---

## Opciones de línea de comandos

```bash
# Usar un archivo Excel distinto
python main.py --excel data/mi_archivo.xlsx

# Modo headless (sin ventana de Chrome, requiere sesión pre-establecida)
python main.py --headless
```

---

## Archivos de log

Los logs se guardan en `logs/wac_bot.log` con rotación automática (5 MB × 3 archivos).

---

## Estructura de salida en Excel

Al finalizar cada fila, el bot escribe:

| Columna | Valor |
|---------|-------|
| `STATUS` | `EXITOSO` / `ERROR` / `OMITIDO` |
| `NOTES` | Detalle del resultado o mensaje de error |
| `CURRENT_WAC` | WAC leído de Oracle antes de la actualización |
| `TIMESTAMP` | Fecha y hora de procesamiento |
