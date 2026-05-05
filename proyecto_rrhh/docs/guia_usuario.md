# Guía de Usuario — ValidaRH

ValidaRH es una aplicación de escritorio desarrollada en Python con Tkinter que automatiza el proceso de selección de personal. Permite a reclutadores gestionar perfiles de vacantes y evaluar candidatos, y a postulantes administrar sus hojas de vida y analizar su compatibilidad con ofertas laborales.

---

## Acceso al sistema

Al iniciar la aplicación se presenta una ventana de autenticación con dos pestañas:

**Iniciar sesión** — ingrese su correo electrónico y contraseña. Si tiene cuentas con ambos roles (postulante y reclutador), el sistema le preguntará con cuál desea entrar.

**Registrarse** — complete el formulario con nombre, correo, contraseña, cédula, teléfono, nombre de usuario y fecha de nacimiento. Seleccione el tipo de cuenta (postulante o reclutador). Al enviar el formulario recibirá un código de verificación de 6 dígitos en su correo; si el servicio de correo no está configurado, el código aparecerá directamente en pantalla.

Una vez verificada la cuenta, puede iniciar sesión normalmente.

---

## Rol: Postulante

El espacio del postulante tiene tres sub-pestañas.

### Mis CVs

Permite registrar una o varias hojas de vida. Al agregar un nuevo CV puede escribir el texto directamente o cargar un archivo PDF o TXT. El sistema extrae automáticamente las palabras clave del contenido. Al seleccionar un CV de la lista se muestran los patrones léxicos detectados.

### Vacantes

Permite guardar las vacantes de interés. Al registrar una vacante se ingresan el título y la descripción de requisitos; el sistema normaliza el texto y extrae las keywords del perfil para facilitar la comparación posterior. Se pueden crear, consultar y eliminar vacantes.

### Analizador

Seleccione uno de sus CVs y una vacante guardada y presione "Analizar". El sistema ejecuta el motor de compatibilidad y muestra:

- El **score global** de compatibilidad (0–100 %).
- Una tabla con el resultado por cada requisito del perfil: si fue cumplido, parcialmente cumplido o no encontrado.
- Las palabras clave detectadas en el CV para cada requisito y un fragmento de contexto del documento.

---

## Rol: Reclutador

El panel del reclutador tiene dos sub-pestañas.

### Perfiles laborales

Permite crear y gestionar los perfiles de vacante de la empresa. Al crear un nuevo perfil se ingresan un título y la descripción de requisitos (uno por línea o en texto libre). El sistema extrae las keywords automáticamente al guardar. Los perfiles quedan listados con su título, keywords detectadas, fecha de creación y reclutador responsable.

### Candidatos

Muestra la lista de todos los postulantes registrados en el sistema. El reclutador puede seleccionar un candidato, elegir uno de los perfiles laborales creados y presionar "Analizar compatibilidad". El resultado es idéntico al que ve el postulante: score global, tabla de requisitos y contexto del CV. El análisis queda registrado en el historial.

---

## Historial de análisis

Desde la pestaña **Historial** (disponible según el rol) se consultan todos los análisis realizados: candidato evaluado, perfil utilizado, fecha y score obtenido.

---

## Motor de compatibilidad (CVMatcher)

El análisis no compara palabras exactas sino que aplica un pipeline de procesamiento léxico:

1. Normaliza el texto (elimina tildes, unifica mayúsculas/minúsculas).
2. Tokeniza y filtra stopwords y términos irrelevantes.
3. Construye términos compuestos (bigrams) como "machine learning" o "power bi".
4. Busca cada término del perfil en el CV mediante dos niveles: coincidencia exacta (peso 1.0) y cobertura léxica por prefijo común (peso 0.7), lo que permite que "gestión" cubra "gestionando" o "análisis" cubra "analizar".
5. Pondera los términos según su categoría: sustantivos y herramientas tienen mayor peso (1.0) que verbos de acción como "desarrollar" o "implementar" (0.5).

El score final es el promedio ponderado de todos los requisitos evaluados.
