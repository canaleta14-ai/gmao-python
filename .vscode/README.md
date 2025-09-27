# Configuración del Proyecto GMAO

## 🛠️ Configuración de VS Code

Este proyecto incluye configuración específica de VS Code para asegurar consistencia en el desarrollo.

### Archivos de Configuración

- **`.vscode/settings.json`**: Configuración del workspace
- **`.vscode/tasks.json`**: Tareas disponibles (Run, Install, Test, etc.)
- **`.vscode/launch.json`**: Configuración de debugging
- **`.vscode/extensions.json`**: Extensiones recomendadas

### Configuración Importante

#### Codificación UTF-8
```json
{
    "files.encoding": "utf8",
    "files.autoGuessEncoding": false
}
```

Esta configuración asegura que todos los archivos se guarden en **UTF-8**, evitando problemas de codificación.

#### Formateo de Código
- **Python**: Usa Black como formateador
- **JavaScript/CSS**: Usa Prettier
- **Indentación**: 4 espacios, sin tabs

#### Entorno Python
- **Interpreter**: `./.venv/Scripts/python.exe`
- **Activación automática**: En terminal integrado

### Tareas Disponibles

1. **Run Flask App** (Ctrl+Shift+B): Ejecuta la aplicación Flask
2. **Install Dependencies**: Instala dependencias de `requirements.txt`
3. **Initialize Database**: Ejecuta `init_db.py`
4. **Run Tests**: Ejecuta tests con pytest
5. **Check Syntax**: Verifica sintaxis del código

### Debugging

Tres configuraciones de debug disponibles:
1. **Python: Flask**: Debug de la aplicación Flask completa
2. **Python: Current File**: Debug del archivo actual
3. **Python: Test File**: Debug de tests

### Extensiones Recomendadas

- **Python**: ms-python.python, ms-python.debugpy, ms-python.black-formatter
- **Web**: Prettier, Auto Rename Tag, Tailwind CSS
- **Utilidades**: Todo Tree, Path Intellisense, SQLite Viewer

### Configuración Global Recomendada

Para una experiencia óptima, configura también globalmente en VS Code:

```json
{
    "files.encoding": "utf8",
    "files.autoGuessEncoding": false,
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
        "source.organizeImports": true
    },
    "python.defaultInterpreterPath": "python3",
    "emmet.includeLanguages": {
        "jinja-html": "html"
    }
}
```

### Verificación

Para verificar que la configuración funciona correctamente:

1. Abre cualquier archivo Python
2. Ve a View → Command Palette → `Developer: Reload Window`
3. Verifica que el encoding en la barra inferior diga "UTF-8"
4. Ejecuta una tarea con Ctrl+Shift+P → "Tasks: Run Task"