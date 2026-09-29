|Parámetro|Valor|
|---|---|
|Material|Hormigón armado|
|Cantidad estimada|40|
|Carga vertical por apoyo|8,03 kN|
|Criterio de diseño|Antivuelco + arrancamiento|



# 5.6 Consideraciones mecánicas del sistema móvil 

La incorporación de inclinación variable introduce una complejidad adicional en el diseño mecánico del sistema. A diferencia de estructuras fijas, el sistema móvil requiere elementos de transmisión capaces de modificar la posición angular de los paneles de forma segura, precisa y repetitiva. 

Los principales componentes mecánicos asociados al movimiento son: eje de rotación; actuadores lineales o rotativos; soportes articulados; topes mecánicos de seguridad; sistema de bloqueo en posición segura. 

Desde el punto de vista de ingeniería, el criterio principal consiste en garantizar que el mecanismo sea capaz de desplazar la estructura bajo carga y mantener su posición sin deformaciones excesivas. Además, el sistema debe responder automáticamente ante eventos de viento extremo, llevando los paneles hacia una posición de seguridad que reduzca las cargas aerodinámicas. Esta filosofía de diseño permite combinar eficiencia energética y protección estructural, constituyendo uno de los principales diferenciales del sistema agrivoltaico propuesto. 

# **CAPÍTULO VI: DISEÑO ELÉCTRICO DEL SISTEMA** 

# 6.1 Criterios generales de diseño eléctrico 

El diseño eléctrico del sistema agrivoltaico tiene como objetivo garantizar una conversión, distribución y gestión eficiente de la energía generada por los módulos fotovoltaicos, asegurando al mismo tiempo confiabilidad operativa, seguridad eléctrica y compatibilidad con 

los requerimientos energéticos del proyecto. A diferencia de instalaciones fotovoltaicas convencionales de pequeña escala, el sistema propuesto requiere una arquitectura capaz de integrar generación solar, almacenamiento energético, sistemas de automatización y posibles esquemas de operación autónoma o interconectada. 

Desde el punto de vista funcional, el sistema eléctrico debe cumplir cuatro funciones principales: captar energía solar mediante módulos fotovoltaicos, convertir la corriente continua generada en corriente alterna utilizable, gestionar el almacenamiento energético y distribuir la energía hacia las cargas conectadas. Estas etapas requieren la coordinación de diversos componentes eléctricos, incluyendo paneles solares, inversores, protecciones, conductores, bancos de baterías y sistemas de monitoreo. 

El diseño propuesto considera inicialmente una configuración con generación fotovoltaica y almacenamiento energético, contemplando dos posibles escenarios de operación: funcionamiento autónomo ( _off-grid_ ) y operación interconectada ( _grid-connected_ ). La elección definitiva entre ambas configuraciones dependerá de la factibilidad técnica y económica de vinculación con la red eléctrica rural cercana. Según Messenger y Ventre (2010), esta flexibilidad de diseño resulta recomendable en proyectos de mediana escala, ya que permite adaptar la arquitectura eléctrica a condiciones futuras sin necesidad de rediseños completos. 

Asimismo, el diseño deberá respetar criterios de seguridad eléctrica asociados a protecciones contra sobrecorriente, sobretensión, fallas a tierra y desconexión de emergencia. Estos criterios resultan esenciales para minimizar riesgos de falla, proteger equipos sensibles y garantizar continuidad de servicio. 

# 6.2 Selección de módulos fotovoltaicos 

La selección de los módulos fotovoltaicos constituye una de las decisiones técnicas más relevantes del diseño eléctrico, dado que estos componentes determinan la capacidad de generación primaria del sistema. Para el presente proyecto se seleccionaron módulos monocristalinos bifaciales de 650 Wp, debido a su alta eficiencia, buena densidad energética y mejor comportamiento frente a condiciones de radiación difusa. 

Los módulos monocristalinos presentan eficiencias superiores respecto de otras tecnologías comerciales, permitiendo obtener mayor potencia instalada por unidad de superficie. Además, la tecnología bifacial permite aprovechar radiación reflejada desde el terreno, incrementando la 

generación total bajo determinadas condiciones de albedo. Según Fraunhofer ISE (2024), esta tecnología puede incrementar entre 5% y 20% la producción energética anual respecto de paneles monofaciales convencionales. 

Las características eléctricas preliminares consideradas son: 

Tabla 6.1 Características eléctricas de módulos FV 

|Parámetro|Valor|
|---|---|
|Potencia nominal|650 Wp|
|Tensión circuito abierto (Voc)|45–50 V|
|Corriente máxima|15–18 A|
|Tecnología|Monocristalino bifacial|
|Eficiencia|21–23%|



Dado el dimensionamiento preliminar realizado en el capítulo anterior, la planta requiere aproximadamente 770 módulos para alcanzar la potencia objetivo de 500 kWp. 

6.3 Configuración de strings 

Una vez seleccionados los módulos, resulta necesario definir la configuración de strings, es decir, la cantidad de paneles conectados en serie y en paralelo para alcanzar niveles de tensión y corriente compatibles con los inversores seleccionados. 

La conexión en serie incrementa la tensión total del string, mientras que la conexión en paralelo incrementa la corriente disponible. El diseño debe buscar una configuración que mantenga los valores eléctricos dentro del rango operativo del inversor, maximizando eficiencia y minimizando pérdidas. 

Para este diseño preliminar se adopta una configuración de 22 módulos por string. 

La tensión aproximada por string resulta: 

𝑉𝑠𝑡𝑟𝑖𝑛𝑔= 22 x 48 

𝑉𝑠𝑡𝑟𝑖𝑛𝑔= 1056 _V_ 

Este valor se encuentra dentro del rango habitual de entrada de inversores string comerciales de media potencia. 

La cantidad total de strings será: 

770 N = 22 

N = 35 

Por lo tanto, se adoptan 35 strings de diseño. 

Tabla 6.2 

Configuración preliminar de strings 

|Parámetro|Valor|
|---|---|
|Módulos totales|770|
|Paneles por string|22|
|Cantidad de strings|35|
|Tensión estimada/string|1056 V|



# 6.4 Selección de inversores 

Los inversores constituyen el elemento encargado de transformar la energía eléctrica generada en corriente continua por los módulos fotovoltaicos en corriente alterna utilizable por las cargas del sistema. Su selección impacta directamente en eficiencia global, confiabilidad y calidad de energía. 

Para el presente diseño se propone utilizar inversores trifásicos string de 100 kW, debido a su modularidad y facilidad de mantenimiento. 

La cantidad requerida se estima como: 

500 N = 100 

N = 5 

Por lo tanto, el sistema requiere: 5 inversores de 100 kW 

Tabla 6.3. Selección preliminar de inversores 

|Parámetro|Valor|
|---|---|
|Tipo|Trifásico|
|Potencia unitaria|100 kW|
|Cantidad|5|
|Potencia total|500 kW|



6.5 Dimensionamiento preliminar del sistema de almacenamiento energético (BESS) 

El sistema de almacenamiento energético cumple un rol central dentro de la arquitectura eléctrica propuesta, especialmente en escenarios de operación autónoma ( _off-grid_ ) o de baja disponibilidad de red. Su función principal consiste en almacenar excedentes de energía generados durante períodos de alta irradiancia y liberarlos posteriormente cuando la generación fotovoltaica disminuye o la demanda supera la producción instantánea. 

La incorporación de almacenamiento también aporta beneficios operativos relevantes, entre ellos la estabilización del sistema eléctrico, la reducción de variaciones bruscas de potencia, el soporte durante picos de demanda y la mejora del autoconsumo energético. Según Luo et al. (2015), los sistemas BESS constituyen uno de los componentes más importantes en microrredes renovables debido a su capacidad para mejorar confiabilidad y flexibilidad operativa. 

Para el presente proyecto se adopta preliminarmente un sistema de baterías basado en tecnología ion-litio (Li-ion). Esta elección responde a su elevada densidad energética, buena eficiencia de carga-descarga, menores requerimientos de mantenimiento y mayor vida útil frente a tecnologías convencionales como plomo-ácido. Además, las baterías de ion-litio presentan tiempos de respuesta muy rápidos, característica particularmente útil en aplicaciones con variabilidad solar. 

Con fines de diseño preliminar, se considera una autonomía energética objetivo de 4 horas, criterio habitual en sistemas híbridos de mediana escala. 

La energía requerida puede estimarse mediante: 

E = P x _t_ 

donde: 

- E = energía almacenada (kWh) 

- P = potencia demandada (kW) 

- t = tiempo de autonomía (h) 

Adoptando una potencia crítica de respaldo de 250 kW: 

- E = 250 x 4 

E = 1000 _kWh_ 

Por lo tanto, el sistema de almacenamiento deberá disponer de una capacidad mínima de: 

# 1 _MWh_ 

Sin embargo, considerando profundidad de descarga, degradación y márgenes de seguridad, se adopta una capacidad nominal superior de 1,2 MWh. 

Tabla 6.4. Parámetros preliminares del BESS 

|Parámetro|Valor|
|---|---|
|Tecnología|Ion-litio|



|Parámetro|Valor|
|---|---|
|Potencia nominal|250 kW|
|Capacidad energética|1,2 MWh|
|Autonomía estimada|4 h|
|Eficiencia|90–95%|



# 6.6 Protecciones eléctricas del sistema 

La seguridad eléctrica constituye un aspecto crítico dentro del diseño del sistema agrivoltaico. La incorporación de generación distribuida, almacenamiento energético y automatización exige implementar protecciones capaces de detectar fallas y aislar sectores comprometidos antes de que se produzcan daños sobre equipos o riesgos para las personas. 

El sistema deberá incorporar protecciones tanto en corriente continua como en corriente alterna. 

En el lado de corriente continua, las principales protecciones consideradas son: fusibles DC por string; seccionadores de aislamiento; protección contra sobretensiones transitorias (SPD); protección frente a cortocircuito. 

Estas protecciones permiten aislar strings defectuosos y proteger módulos e inversores frente a perturbaciones eléctricas, especialmente aquellas provocadas por descargas atmosféricas o maniobras de conmutación. Según IEC 62548 (2016), la protección en sistemas fotovoltaicos debe diseñarse contemplando selectividad y rápida desconexión ante fallas. 

En corriente alterna, el sistema incorpora: interruptores termomagnéticos; interruptores diferenciales; protección contra sobrecorriente; relés de falla a tierra; protecciones contra sobretensión. 

Estas protecciones resultan fundamentales para preservar inversores, banco de baterías y cargas conectadas. 

Tabla 6.5. Protecciones eléctricas principales 

|Protección|Función|
|---|---|
|Fusible DC|Protección de strings|
|Seccionador DC|Aislamiento|
|SPD|Sobretensión|
|Interruptor termomagnético|Sobrecorriente|
|Diferencial|Protección personal|
|Relé de falla a tierra|Seguridad operativa|



# 6.7 Esquema unifilar del sistema 

El esquema unifilar constituye la representación simplificada de la arquitectura eléctrica general del sistema, permitiendo visualizar la relación funcional entre generación, conversión, almacenamiento y consumo. 

La configuración eléctrica propuesta se estructura en cinco bloques principales: 

- ⮚ Campo fotovoltaico 

- ⮚ Inversores solares 

- ⮚ Banco de baterías (BESS) 

- ⮚ Tablero general de distribución 

- ⮚ Cargas y sistemas auxiliares 

El flujo energético comienza en el campo fotovoltaico, donde la radiación solar es convertida en energía eléctrica de corriente continua. Esta energía es conducida hacia los inversores, encargados de transformarla en corriente alterna trifásica compatible con las cargas del sistema. 

Paralelamente, el sistema de almacenamiento puede absorber excedentes de energía durante períodos de alta generación o suministrar potencia cuando la generación solar resulta 

insuficiente. Esta lógica de operación permite mejorar estabilidad y reducir dependencia de fuentes externas de energía. 

Desde el tablero general de distribución se alimentan las cargas principales del sistema agrivoltaico, incluyendo: bombas de riego; actuadores mecánicos; sensores y automatización; iluminación y cargas auxiliares. 

El esquema unifilar también contempla la posibilidad de incorporar una futura conexión a red o fuente de respaldo externa, permitiendo escalabilidad del sistema. 

La arquitectura eléctrica adoptada permite una operación flexible, segura y escalable, facilitando futuras ampliaciones y mejorando la confiabilidad energética global del sistema. 

# **CAPÍTULO VII: AUTOMATIZACIÓN Y CONTROL DEL SISTEMA** 

# 7.1 Automatización aplicada al sistema agrivoltaico 

La automatización constituye una pieza central dentro del diseño del sistema agrivoltaico propuesto, ya que permite integrar de manera eficiente la generación energética, el comportamiento mecánico de las estructuras móviles y la gestión de variables ambientales que influyen directamente sobre el rendimiento de la planta. En este tipo de proyectos, donde conviven subsistemas eléctricos, mecánicos e hidráulicos, el control automatizado deja de ser un elemento accesorio para convertirse en una necesidad operativa. 

En términos prácticos, automatizar el sistema implica dotarlo de la capacidad de monitorear continuamente su estado de funcionamiento y responder de manera autónoma ante cambios del entorno. Esto resulta especialmente importante en el predio seleccionado, donde factores como el viento patagónico, las variaciones térmicas diarias y los cambios en la radiación solar pueden 

