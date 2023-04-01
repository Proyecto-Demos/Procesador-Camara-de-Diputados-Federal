# Procesador-Camara-de-Diputados-Federal

Un script para obtener de la pagina web de la camara de diputados la información de las votaciones del ultimo periodo. Los resultados se procesan a un JSON con el siguiente formato:

* Nombre del periodo
  * nombre
  * votos
    * nombre_partido
    * resultados
      * nombre
      * sentido_voto

Uso:
```bash
pipenv install
pipenv run app.py output.json
```
