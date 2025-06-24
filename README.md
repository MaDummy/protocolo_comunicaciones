# Diseño e Implementación de un Protocolo de Comunicaciones

## Docs
https://docs.google.com/document/d/14M2NY1FqXoXGEV5xdnM0JvOWpwydOYqhahMPnwGBSDE/edit?usp=sharing

## Dependencias

```cmd
pip install crcmod
```

## Ejecucion
Use una terminal para ejecutar emisor como python emisor.py <archivo.ext>\
Donde:
- archivo.ext: El archivo que desea leer y pasar de emisor a receptor, se aceptan distintos tipos de archivos. EJ: imagen.png

Use una terminal para ejecutar receptor como python receptor.py <archivo_salida.ext> <mostrar texto: 0|1>\
Donde:
- archivo_salida.ext: nombre con que desea guardar el archivo que el receptor recibe y reconstruye, asegurese de tener la misma extension usada en el emisor. EJ: copia_imagen.png
- mostrar texto: Un 0 o 1 indicando si desea que la data recibida en el receptor se imprima en consola, util si tiene un archivo de texto, se recomienda tener en 0 si es cualquier otro tipo de archivo