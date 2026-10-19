# Proyecto

## Componentes

- `app` aplicación con login.

## Base de Datos y Administrador 

* Se levantan con: 

```bash
docker-compose up
```

Queda
- postgresql: Atiende en su puerto por defecto: 5432 credenciales: user/pass
- pgadmin: se encuentra en: http://localhost:5050 credenciales: admin@admin.com/pass

## Instalar Proyecto

# Python

```bash
asdf plugin add python
asdf install python 3.12.3
asdf set python 3.12.3
```
# Poety + dependencias

```bash
asdf plugin add poetry
asdf install poetry 2.1.4
asdf set poetry 2.1.4
asdf exec poetry install
```

# Iniciar la app (crea las tablas de la DB)

Primero se debe crear la base: "proyecto" en el Pgadmin

```bash
asdf exec poetry run flask run
```
- Se debería ver el sitio en: http://localhost:5000 


# Seeds de datos 

Abrir la shell de flask:
```bash
asdf exec poetry run flask shell
```

Ejecutar las seeds para popular la base:
```bash
from src.core.seeds import run
run()
```