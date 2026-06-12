### Inicializar

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### Limpiar
## pycache

# 1. Eliminar del sistema de archivos
# linux
```bash
find . -type d -name "__pycache__" -exec rm -r {} +
```

# windows
```bash
Get-ChildItem -Recurse -Directory -Filter "__pycache__" | Remove-Item -Recurse -Force
```

## venv
# linux
```bash
rm -rf venv
```

# windows
```bash
Remove-Item venv -Recurse -Force
```
