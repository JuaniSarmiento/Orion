# Guía de Contribución - ORION

¡Gracias por tu interés en contribuir a ORION! 🎉

## 📋 Tabla de Contenidos

- [Código de Conducta](#código-de-conducta)
- [¿Cómo puedo contribuir?](#cómo-puedo-contribuir)
- [Configuración del Entorno](#configuración-del-entorno)
- [Proceso de Pull Request](#proceso-de-pull-request)
- [Guía de Estilo](#guía-de-estilo)
- [Reportar Bugs](#reportar-bugs)
- [Sugerir Features](#sugerir-features)

---

## Código de Conducta

Este proyecto adhiere a un Código de Conducta. Al participar, se espera que mantengas este código. Por favor reporta comportamientos inaceptables a soporte@orion.com.

### Nuestros Estándares

- ✅ Usar lenguaje acogedor e inclusivo
- ✅ Respetar diferentes puntos de vista y experiencias
- ✅ Aceptar críticas constructivas con gracia
- ✅ Enfocarse en lo que es mejor para la comunidad
- ❌ Uso de lenguaje o imágenes sexualizadas
- ❌ Trolling, comentarios insultantes o ataques personales
- ❌ Acoso público o privado

---

## ¿Cómo puedo contribuir?

### 🐛 Reportar Bugs

Si encuentras un bug, por favor:

1. **Busca** primero en los [issues existentes](https://github.com/tu-usuario/orion/issues)
2. Si no existe, **crea un nuevo issue** con:
   - Título descriptivo
   - Pasos para reproducir el problema
   - Comportamiento esperado vs actual
   - Logs relevantes
   - Versión de Python, Docker, etc.

**Ejemplo:**

```markdown
**Descripción:** El NLU no clasifica correctamente mensajes con emojis

**Pasos para reproducir:**
1. Enviar mensaje: "Hola 😊 donde esta mi pedido 12345?"
2. Ver respuesta

**Esperado:** Intent = trackear_pedido
**Actual:** Intent = intencion_desconocida

**Logs:**
[Incluir logs relevantes]

**Entorno:**
- Python: 3.11
- Docker: 20.10.21
- OS: Ubuntu 22.04
```

### ✨ Sugerir Features

Para sugerir nuevas características:

1. **Abre un issue** con el tag `enhancement`
2. Describe:
   - El problema que resuelve
   - Cómo lo imaginas funcionando
   - Beneficios para los usuarios
   - Posible implementación

### 💻 Contribuir Código

1. **Fork** el repositorio
2. **Clona** tu fork: `git clone https://github.com/tu-usuario/orion.git`
3. **Crea una rama**: `git checkout -b feature/mi-feature`
4. **Haz tus cambios**
5. **Agrega tests**
6. **Commit**: `git commit -m 'feat: agregar nueva funcionalidad'`
7. **Push**: `git push origin feature/mi-feature`
8. **Abre un Pull Request**

---

## Configuración del Entorno

### 1. Prerrequisitos

- Python 3.11+
- Docker 20.10+
- Git

### 2. Clonar y Configurar

```bash
# Clonar repositorio
git clone https://github.com/tu-usuario/orion.git
cd orion

# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# Instalar dependencias de desarrollo
pip install -r requirements-dev.txt

# Configurar pre-commit hooks
pre-commit install
```

### 3. Levantar Servicios

```bash
docker-compose up --build
```

### 4. Ejecutar Tests

```bash
# Tests unitarios
pytest tests/ -v

# Tests de integración
python test_nlu_enhanced.py

# Stress tests
python stress_test.py

# Coverage
pytest tests/ --cov=app --cov-report=html
```

---

## Proceso de Pull Request

### Antes de Enviar

- [ ] Los tests pasan (`pytest tests/`)
- [ ] El código sigue la guía de estilo (PEP 8)
- [ ] Agregaste tests para nuevas funcionalidades
- [ ] Actualizaste la documentación si es necesario
- [ ] Los commits siguen [Conventional Commits](#convención-de-commits)

### Conventional Commits

Usamos [Conventional Commits](https://www.conventionalcommits.org/) para mensajes:

```
<tipo>(<scope>): <descripción>

[cuerpo opcional]

[footer opcional]
```

**Tipos:**
- `feat`: Nueva funcionalidad
- `fix`: Corrección de bug
- `docs`: Cambios en documentación
- `style`: Formateo, punto y coma faltantes, etc.
- `refactor`: Refactorización de código
- `test`: Agregar o modificar tests
- `chore`: Mantenimiento, dependencias, etc.

**Ejemplos:**

```bash
git commit -m "feat(nlu): agregar soporte para emojis"
git commit -m "fix(api): corregir timeout en webhook"
git commit -m "docs(readme): actualizar instrucciones de instalación"
git commit -m "test(nlu): agregar tests para normalización"
```

### Revisión de Código

Tu PR será revisado por al menos un mantenedor. Pueden solicitar cambios. Por favor:

- Responde a los comentarios
- Haz los cambios solicitados
- Marca conversaciones como resueltas

---

## Guía de Estilo

### Python

Seguimos **PEP 8** con algunas excepciones:

- Longitud máxima de línea: **100 caracteres**
- Usar **type hints** siempre que sea posible
- Docstrings en **Google Style**

**Ejemplo:**

```python
from typing import Dict, List

def procesar_mensaje(texto: str, user_id: str) -> Dict[str, any]:
    """
    Procesa un mensaje de usuario y retorna la respuesta.
    
    Args:
        texto: El mensaje del usuario
        user_id: ID único del usuario
        
    Returns:
        Dict con la respuesta y metadatos
        
    Raises:
        ValueError: Si el texto está vacío
        
    Examples:
        >>> procesar_mensaje("Hola", "user123")
        {"response": "Hola!", "intent": "saludo"}
    """
    if not texto:
        raise ValueError("El texto no puede estar vacío")
    
    # Tu código aquí
    return {"response": "...", "intent": "..."}
```

### Formato Automático

Usamos herramientas de auto-formato:

```bash
# Black para formateo
black .

# isort para ordenar imports
isort .

# flake8 para linting
flake8 .

# mypy para type checking
mypy app/
```

### Estructura de Archivos

```python
# 1. Imports estándar
import os
import sys
from datetime import datetime

# 2. Imports de terceros
import httpx
from fastapi import FastAPI
from pydantic import BaseModel

# 3. Imports locales
from app.utils import normalize_text
from app.models import UserMessage

# 4. Constantes
API_VERSION = "1.0.0"
MAX_RETRIES = 3

# 5. Código
class MyClass:
    pass

def my_function():
    pass
```

### Nombres

- **Variables**: `snake_case`
- **Funciones**: `snake_case`
- **Clases**: `PascalCase`
- **Constantes**: `UPPER_SNAKE_CASE`
- **Privados**: `_prefijo_con_guion_bajo`

---

## Testing

### Escribir Tests

```python
import pytest
from app.main import procesar_mensaje

class TestProcesarMensaje:
    """Tests para la función procesar_mensaje."""
    
    def test_mensaje_simple(self):
        """Debe procesar un mensaje simple correctamente."""
        resultado = procesar_mensaje("Hola", "user123")
        
        assert resultado["intent"] == "saludo"
        assert resultado["confidence"] > 0.8
    
    def test_mensaje_vacio(self):
        """Debe lanzar error con mensaje vacío."""
        with pytest.raises(ValueError):
            procesar_mensaje("", "user123")
    
    @pytest.mark.parametrize("texto,intent_esperado", [
        ("donde esta mi pedido", "trackear_pedido"),
        ("tienen stock", "consultar_stock"),
        ("cuanto cuesta", "consultar_precio"),
    ])
    def test_multiples_intents(self, texto, intent_esperado):
        """Debe clasificar correctamente múltiples intents."""
        resultado = procesar_mensaje(texto, "user123")
        assert resultado["intent"] == intent_esperado
```

### Cobertura de Tests

Mantenemos **>80%** de cobertura:

```bash
pytest tests/ --cov=app --cov-report=term-missing
```

---

## Documentación

### Actualizar Documentación

Si tu cambio afecta:

- **README.md**: Actualiza instrucciones de uso
- **API docs**: Actualiza ejemplos de endpoints
- **Código**: Agrega/actualiza docstrings

### Escribir Docstrings

Usamos **Google Style**:

```python
def mi_funcion(param1: str, param2: int) -> bool:
    """
    Resumen de una línea de lo que hace la función.
    
    Descripción más detallada si es necesario.
    Puede ser de múltiples líneas.
    
    Args:
        param1: Descripción del primer parámetro
        param2: Descripción del segundo parámetro
        
    Returns:
        Descripción de lo que retorna
        
    Raises:
        ValueError: Cuando param2 es negativo
        TypeError: Cuando param1 no es string
        
    Examples:
        >>> mi_funcion("test", 5)
        True
    """
    pass
```

---

## Herramientas Útiles

### Pre-commit Hooks

Instala hooks para validar antes de commit:

```bash
pip install pre-commit
pre-commit install
```

Crea `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: https://github.com/psf/black
    rev: 23.1.0
    hooks:
      - id: black
  
  - repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
      - id: isort
  
  - repo: https://github.com/pycqa/flake8
    rev: 6.0.0
    hooks:
      - id: flake8
```

### VS Code Settings

`.vscode/settings.json`:

```json
{
  "python.formatting.provider": "black",
  "python.linting.enabled": true,
  "python.linting.flake8Enabled": true,
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "source.organizeImports": true
  }
}
```

---

## Preguntas Frecuentes

### ¿Cómo ejecuto un solo test?

```bash
pytest tests/test_nlu.py::test_clasificacion_simple -v
```

### ¿Cómo debugging en Docker?

Agrega `pdb` en tu código:

```python
import pdb; pdb.set_trace()
```

Luego ejecuta con:

```bash
docker-compose run --service-ports nlu python -m pdb app/main.py
```

### ¿Cómo actualizo dependencias?

```bash
# Ver outdated
pip list --outdated

# Actualizar
pip install --upgrade package-name

# Actualizar requirements
pip freeze > requirements.txt
```

---

## Reconocimientos

Todos los contribuidores son listados en el [Contributors](https://github.com/tu-usuario/orion/graphs/contributors).

**Top Contributors:**

- [@usuario1](https://github.com/usuario1) - 150 commits
- [@usuario2](https://github.com/usuario2) - 89 commits
- [@usuario3](https://github.com/usuario3) - 67 commits

---

## Contacto

¿Preguntas? Contacta a:

- **Email**: dev@orion.com
- **Discord**: https://discord.gg/orion
- **Twitter**: [@OrionProject](https://twitter.com/OrionProject)

---

¡Gracias por contribuir a ORION! 🚀
