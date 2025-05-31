# Cambios realizados y comentarios
## 31/5/25
- Agregué dos funciones al final del archivo ['converter.py'](./csv2pronto/src/converter.py) que verifican que se pueda obtener el valor de una fila, y si no se puede, devuelve un valor [`NoneLiteral`](./csv2pronto/src/null_objects/null_objects.py)
  - TRY_IF_ROW_EXISTS(row, encabezado) --> Intenta obtener un valor row.get(encabezado), y si no devuelve NoneLiteral
  - TRY_OBTAIN_DATE(row, encabezado) --> Intenta obtener un valor fecha de row.get(encabezado), y si no devuelve NoneLiteral
- Reemplacé algunas llamadas a la función row.get(encabezado) con estas nuevas funciones
- Inserté un valor sitio temporal y un bloque try-except en el archivo ['faker.py'](./csv2pronto/src/faker/faker.py) para controlar el caso en el que no exista el encabezado 'sitio'
  - Esto no sé si está bien, meter un sitio extra podría meter ruido en el grafo final, por eso habría que ver si hay que poner un sitio por defecto para estos casos o si no hay que controlarlo
- Declaré el método "replace" dentro de la clase [`NoneLiteral`](./csv2pronto/src/null_objects/null_objects.py) para así, cada vez que se le invoque el método a un objeto de esta clase, el código no tire error
  - De nuevo, no sé si este override esté bien o sea lo que se pide, no pude ver el grafo por lo que no sé como esté funcionando esto.
### Comentarios
- Ahora el código no falla al ejecutar el 'test-data.csv' o el 'input.csv'
- Habría que fijarse si hay que controlar el caso en el que cualquier atributo encabezado no se encuentre en el archivo csv, si hay que tirar NoneLiteral cuando este no se encuentra, o si hay que manejarlo de una forma mucho mas sofisticada y que dependa del caso