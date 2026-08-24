# 2026_ICS_Grupo10 - Plan de Gestión de Configuración (SCM)

## 📁 Estructura del Repositorio

```text
/General
    /Reglas_de_Juego
/Unidades
    /Unidad1
        /Bibliografia
        /Presentaciones_de_Clase
        /Material_Adicional
    /Unidad2
        /Bibliografia
        /Presentaciones_de_Clase
        /Material_Adicional
    /Unidad3
        /Bibliografia
        /Presentaciones_de_Clase
        /Material_Adicional
    /Unidad4
        /Bibliografia
        /Presentaciones_de_Clase
        /Material_Adicional
/Trabajos_Grupales
    /Trabajo_de_Investigación
        /TIG1
            /Material_Adicional
        /TIG2
            /Material_Adicional
    /Trabajos_Practicos
        /Enunciados
        /Templates
        /Evaluables
            /Tp4
                /Material_Adicional
            /Tp5
                /Material_Adicional
            /Tp6
                /Programa
                /Material_Adicional
            /Tp7
                /Material_Adicional
            /Tp11
                /Material_Adicional
            /Tp12
                /Material_Adicional
            /Tp14
                /Material_Adicional
            /Tp15
                /Material_Adicional
        /No_Evaluables
            /Tp1
                /Material_Adicional
            /Tp2
                /Material_Adicional
            /Tp3
                /Material_Adicional
            /Tp8
                /Material_Adicional
            /Tp9
                /Material_Adicional
            /Tp10
                /Material_Adicional
            /Tp13
                /Material_Adicional
/Parciales
    /Templates
    /Material_Adicional
```

---

## 🏷️ Nomenclatura de los items de Configuración

| Nombre del CI | Regla de Nombrado | Ubicación Física | Tipo de Item |
| :--- | :--- | :--- | :--- |
| **Programa de la materia** | `<<año>>-ICS_Programa.pdf` | `./2026_ICS_Grupo10/General/Reglas_del_Juego` | Cátedra |
| **Presentación de la materia** | `<<año>>-ICS_Presentacion_materia.pdf` | `./2026_ICS_Grupo10/General/Reglas_del_Juego` | Cátedra |
| **Pautas para el envío de mails a los docentes** | `<<año>>-ICS_Pautas_envio_mail_docentes.pdf` | `./2026_ICS_Grupo10/General/Reglas_del_Juego` | Cátedra |
| **Acceso a clases grabadas** | `<<año>>-ICS_Acceso_a_clases_grabadas.txt` | `./2026_ICS_Grupo10/General` | Cátedra |
| **Cronograma de clases** | `<<año>>-ICS_Cronograma_de_clases.txt` | `./2026_ICS_Grupo10/General` | Cátedra |
| **Material Bibliográfico de la cátedra** | `<<añoPublicacion>>_<<TítuloDelLibro>>_<<edición>>_<<Autor>>_<<UnidadX/X>>.pdf` | `./2026_ICS_Grupo10/<<UnidadX>>/Bibliografia` | Cátedra |
| **Filmina** | `<<año>>-ICS_Clase<<DD/MM>>_<<unidadX/X>>_<<tema>>.pdf` | `./2026_ICS_Grupo10/<<UnidadX>>/Presentaciones_de_Clase` | Clase |
| **Filminas con anotaciones** | `<<año>>-ICS_Clase<<DD/MM>>_<<unidadX/X>>_<<tema>>Con_Notas_<<NombreDelIntegrante>>.pdf` | `./2026_ICS_Grupo10/<<UnidadX>>/Material_Adicional` | Producción Propia |
| **Fotos e Imágenes** | `<<año>>-ICS_Imagen<<X>>_<<unidadX/X>>_<<tema>>_<<X>>_<<NombreDelIntegrante>>.png/jpg` | `./2026_ICS_Grupo10/<<UnidadX>>/Material_Adicional` | Producción Propia |
| **Resumen** | `<<año>>-ICS_Resumen<<X>>_<<unidadX/X>>_<<tema>>_<<X>>_<<NombreDelIntegrante>>.pdf` | `./2026_ICS_Grupo10/<<UnidadX>>/Material_Adicional` | Producción Propia |
| **Enlaces a contenido externos** | `<<año>>-ICS_Enlaces_Externos.txt` | `./2026_ICS_Grupo10/<<UnidadX>>/Material_Adicional` | Producción Propia |
| **Enunciado y Lineamientos trabajo de investigación grupal** | `<<año>>-ISW_Lineamientos_trabajo_investigacion_grupal.pdf` | `./2026_ICS_Grupo10/Trabajos_Grupales/Trabajo_de_Investigacion` | Cátedra |
| **Enlaces a contenido externos** | `<<año>>-ICS_Enlaces_Externos_Investigacion.txt` | `./2026_ICS_Grupo10/Trabajos_Grupales/Trabajo_de_Investigacion/TIG<<X>>/Material_Adicional` | Producción Propia |
| **Producción escrita** | `<<año>>-ICS_Produccion_Investigacion_TIG<<X>>_<<NombreDelIntegrante>>.pdf` | `./2026_ICS_Grupo10/Trabajos_Grupales/Trabajo_de_Investigacion/TIG<<X>>/Material_Adicional` | Producción Propia |
| **Fotos e Imágenes** | `<<año>>-ICS_Imagen<<X>>_TIG<<X>>_<<NombreDelIntegrante>>.png/jpg` | `./2026_ICS_Grupo10/Trabajos_Grupales/Trabajo_de_Investigacion/TIG<<X>>/Material_Adicional` | Producción Propia |
| **Filminas de Presentación** | `<<año>>-ICS_Presentación_TIG<<X>>.pdf/pptx` | `./2026_ICS_Grupo10/Trabajos_Grupales/Trabajo_de_Investigacion/TIG<<X>>` | Producción Propia |
| **Guía de Ejercicios Prácticos Resueltos** | `<<año>>-ICS_Guia_Ejercicios_Resueltos.pdf` | `./2026_ICS_Grupo10/Trabajos_Grupales/Trabajos_Practicos/Enunciados` | Cátedra |
| **Guía de Trabajos Prácticos Evaluables** | `<<año>>-ICS_Guia_Ejercicios_Evaluables.pdf` | `./2026_ICS_Grupo10/Trabajos_Grupales/Trabajos_Practicos/Enunciados` | Cátedra |
| **Templates** | `<<año>>-ICS_Template_<<tema>>_<<unidadX/X>>.doc/xls/pdf` | `./2026_ICS_Grupo10/Trabajos_Grupales/Trabajos_Practicos/Templates` | Cátedra |
| **Producción escrita** | `<<año>>-ICS_Produccion_TP<<X>>_<<NombreDelIntegrante>>.pdf` | `./2026_ICS_Grupo10/Trabajos_Grupales/Trabajos_Practicos/<<Evaluables/No evaluables>>/Material_Adicional` | Producción Propia |
| **Fotos e Imágenes** | `<<año>>-ICS_Imagen<<X>>_TP<<X>>_<<NombreDelIntegrante>>.png/jpg` | `./2026_ICS_Grupo10/Trabajos_Grupales/Trabajos_Practicos/<<Evaluables/No evaluables>>/Material_Adicional` | Producción Propia |
| **Código Fuente** | `<<Aclaración>>.<<ext>>` | `./2026_ICS_Grupo10/Trabajos_Grupales/Trabajos_Practicos/TP<<X>>/Programa` | Producción Propia |
| **Material de Apoyo para rendir parciales** | `<<año>>-ICS_Material_Apoyo_Parciales.pdf` | `./2026_ICS_Grupo10/Parciales` | Cátedra |
| **Templates de Parciales** | `<<año>>-ICS_Template_Parcial_<<X>>.doc/xls/pdf` | `./2026_ICS_Grupo10/Parciales/Templates` | Cátedra |
| **Producción escrita** | `<<año>>-ICS_Produccion_Parcial<<X>>_<<Tema>>_<<unidadX/X>>_<<NombreDelAutor>>.pdf` | `./2026_ICS_Grupo10/Parciales/Material_Adicional` | Producción Propia |

---

## 📖 Glosario de Variables

| Sigla / Variable | Significado |
| :--- | :--- |
| `<<año>>` | Año actual o correspondiente a la fecha de creación del CI. |
| `<<añoPublicacion>>` | Año de publicación de la edición específica del libro o paper. |
| `<<edicion>>` | Número de edición del material (libro o paper). |
| `<<Autor>>` | Nombre del autor del libro o paper en formato CamelCase. |
| `<<unidadX/X>>` | Unidad de la asignatura asociada. |
| `<<tema>>` | Nombre del contenido teórico o unidad asociado. |
| `<<X>>` | Número identificador (creciente y único dentro de una misma carpeta). |
| `<<NombreDelIntegrante>>` | Nombre y apellido del integrante que realizó las anotaciones en formato CamelCase. |
| `<<Evaluables/No_evaluables>>` | Distinción entre carpetas de trabajos prácticos, pudiendo corresponder a la carpeta de “Evaluables” o de “No Evaluables”. |
| `<<NombreDelAutor>>` | Nombre de quien creó el documento en formato CamelCase. |

---

## 💡 Aclaraciones Generales

* **Clases y Cronograma:** Las clases grabadas y el cronograma de clases se enlazan dentro de un archivo `.txt` en lugar de poner directamente el archivo `.xls` para evitar duplicar/repetir modificaciones si el archivo original cambia.
* **Bibliografía:** En la regla de nomenclatura de Libros, `<<unidadX/X>>` puede contener más de un número separado por barra diagonal (ej. `1/2`).
* **Trabajos Prácticos:** En principio solo se agregan carpetas para trabajos prácticos entregables respetando el número correspondiente según lo publicado en la UV, dejando abierta la posibilidad de agregar los que hiciesen falta más adelante.
* **Templates:** Dado que un template puede servir para más de un trabajo práctico, se agrupan en una sola carpeta centralizada para evitar duplicados.
* **Enlaces Externos:** Archivo que contiene enlaces a fuentes externas de internet (videos, páginas) con un título descriptivo que lo acompaña.
* **Código Fuente:** Debido a la incertidumbre sobre la estructura del proyecto de código, se mantiene una descripción flexible dentro de la carpeta `/Programa`.
* **Autores Externos:** La variable `<<NombreDelAutor>>` se utiliza para casos de documentos generados por alguien externo al grupo.

---

## 📝 Regla de Commits

Nos basamos en Conventional Commits:

```text
<tipo>: <descripción>

[cuerpo opcional]
[nota de pie opcional]
```

### Glosario de Tipos
* **Docs:** Documento (Tanto para añadir archivos como para extender archivos).
* **Fix:** Arreglo/corrección (aplicable tanto a código como a otros documentos de ser necesario).
* **Test:** Pruebas.
* **Feat:** Nueva función (código).
* **Especial:** Cambios que no entren en ninguna otra categoría.

---

## 🚩 Línea Base

Para la conformación de las líneas bases consideramos 4 momentos:
1. **Primera línea base:** Será la presentada en el *“Trabajo Práctico N°4: SCM - Herramientas de SCM”*.
2. **Segunda línea base:** Conformada previa al primer parcial (Fecha límite: Viernes 02/10/2026).
3. **Tercera línea base:** Conformada previa al segundo parcial (Fecha límite: Viernes 30/10/2026).
4. **Cuarta línea base:** Conformada para la presentación del *“Trabajo Práctico N°5: SCM - Uso de Repositorio”*.

> **Formato de Tags:** Cada tag se define como `vX.0.0` donde `X` es un número identificativo, creciente y único. En el cuerpo o anotación del tag se detalla que corresponde a la creación de una línea base y cualquier detalle necesario.

---

## 👥 Colaboradores

| Nombre completo | Usuario de GitHub |
| :--- | :--- |
| Gamboa Cataldi, Martin Mario | `@MartinGamboa2429` |
| Salina Arrieta, Lucas | `@LucasSalina` |
| Di Liddo, Lucas Ezequiel | `@LucasDiLiddo` |
| Redin, Martin Fidel | `@martinyb7` |
| Frias, Rodrigo Iván | `@rodrfrias` |
| Daolio Rinaldi, Franco Tomás | `@DevFrancoDaolio` |
| Cesar, Jorge Fidel | `@JFidel17` |
| Agustín Succar | `@agustinsuccar` |
| Juncos, Conrado Nahuel | `@ConradoJuncos` |
| Rueda, Tomas Francisco | `@Tomru3107` |
| Bani, Nicolás Matías | `@NiccoBa` |
| Marinangeli, Mateo | `@mateomarinangeli` |
