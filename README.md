# ckanext-dge-ga

`ckanext-dge-ga` es una extensión para CKAN utilizada en la plataforma [datos.gob.es](https://datos.gob.es/) para la integración con Google Analytics.

> [!TIP]
> Guía base y contexto del proyecto: https://github.com/datosgobes/datos.gob.es

## Descripción

- Añade un plugin CKAN para habilitar la integración con Google Analytics.

## Requisitos

- Una instancia de CKAN.

### Compatibilidad

Compatibilidad con versiones de CKAN:

| Versión de CKAN | ¿Compatible?                                                              |
|--------------|-----------------------------------------------------------------------------|
| 2.8          | ❌ No (requiere Python 3+)                                                   |
| 2.9          | ✅ Sí                                                                        |
| 2.10         | ❓ Desconocido                                                               |
| 2.11         | ❓ Desconocido                                                               |

## Instalación

```sh
pip install -e .
```

## Configuración

Activa el plugin en tu configuración de CKAN:

```ini
ckan.plugins = … dge_ga
```

### Plugins

- `dge_ga`

## Licencia

Este proyecto se distribuye bajo licencia **GNU Affero General Public License (AGPL) v3.0 o posterior**. Consulta el fichero [LICENSE](LICENSE).

