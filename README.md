# MNDWI
Indice satelital combinado para detectar agua en superficie

Script para calcular en Earth Engin el índice MNDWI y almacenarlo en una cuenta de Drive.
El índice se calcula en agregados de 8 días y por provincia.

**Satélites**: Sentinel 2, Landsat 8, MODIS Terra

Donde faltan datos de Sentinel se completan con Landsat y donde tampoco hay de este se agrega MODIS.

**Resolución mínima**: 500 mts
**Resolución máxima**: 30 mts
**Resolución temporal: 8 días**

**Scripts**:
  - funciones.py - Set de funciones, algunas de las cuales son utilizadas por la presente aplicación
  - watch_mndwi.py - script encargado de controlar la ejecución de main_mnwdi.py. Por el momento ejecuta instancias particulares. Se generalizará para toda fecha.
  - watch_drive.py - script encargado de controlar la ejecución de main_drive.py. Por el momento ejecuta instancias particulares. Se generalizará para toda fecha.
  - main_mndwi - Genera MNDWI y lo almacena en Drive en la carpeta *_PAIS.* para cada país. Por el momento ejecuta instancias particulares. Se generalizará para toda fecha.
  - main_drive - Descarga desde Drive los mapas de mndwi almacenado en la carpeta *_PAIS.* para cada país. Por el momento ejecuta instancias particulares. Se generalizará para toda fecha.
  - mndwi_2_geoserver.py - Sube los mapas de mndwi al geoserver para ser publicados. Por el momento ejecuta instancias particulares. Se generalizará para toda fecha.
 
