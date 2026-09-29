_Sistema fotovoltaico con seguidor solar biaxial_ 

|**Parámetro**|**Valor**|
|---|---|
|Ubicación|Puerto Madryn, Provincia de Chubut, Argentina|
|Potencia objetivo de la planta|8 MW (8 000 kWp)|
|Número de módulos (seguidores) estimado|1539 unidades (a confirmar en el layout de planta)|
|Número de paneles por módulo|8 unidades|
|Potencia unitaria del panel|625 – 650 W|
|Potencia unitaria del módulo (string)|5,2 kWp (con panel de 650 W)|
|Tipo de seguidor|Biaxial (doble eje: azimut y elevación)|
|Velocidad de viento de diseño|V = 50 m/s|
|Normativa aplicada|CIRSOC 102-2025 (Reglamento Argentino de Acción del<br>Viento sobre las Construcciones)|
|Categoría de riesgo del sistema|I|
|Categoría de exposición|C (campo abierto)|



2 

_Sistema fotovoltaico con seguidor solar biaxial_ 

# **2. Dispositivos requeridos** 

Esta sección describe los componentes electrónicos y mecánicos necesarios para el funcionamiento del sistema fotovoltaico con seguimiento solar biaxial, agrupados según su función dentro de la arquitectura general: generación, accionamiento mecánico, sensado, comunicación/IoT y cableado. 

## **2.1 Generación fotovoltaica** 

### **_2.1.1 Panel solar 650 W_** 



<!-- Start of picture text -->
al<br><!-- End of picture text -->

_Figura 2.1 – Panel fotovoltaico bifacial 650 W (Relight Energy, s. f.)_ 

|**Característica**<br>|**Especificación**<br>|
|---|---|
|Modelo<br>|JKM625-650N-66HL4M-BDV-Z1<br>|
|Potencia nominal<br>|625 – 650 W<br>|
|Eficiencia máxima<br>|24.1 %<br>|
|Tecnología de celda<br>|N-Type TOPCon HOT 2.0<br>|
|Tipo de módulo<br>|Bifacial de doble vidrio<br>|
|Configuración<br>|132 medias celdas (66 × 2)<br>|
|Dimensiones<br>|2382 × 1134 × 30 mm<br>|
|Peso<br>|32.4 kg<br>|



3 

_Sistema fotovoltaico con seguidor solar biaxial_ 

|**Característica**|**Especificación**|
|---|---|
|Voltaje máximo del sistema|1500 V DC|
|Carga mecánica máxima|Frontal: 5400 Pa / Posterior: 2400 Pa|
|Temperatura de operación|-40 °C a +70 °C|
|Bifacialidad|85 ± 5 %|
|Garantía|12 años producto / 30 años potencia|



_Fuente: Relight Energy (s. f.)._ 

## **2.2 Sistema de seguimiento (tracking)** 

### **_2.2.1 Motor de engranaje de doble eje SVH7_** 



_Figura 2.2 – Motorreductor de doble eje SVH7 (Coresun Drive Equipment Changzhou Co., Ltd., s. f.)_ 

Es un sistema de giro de doble eje con motorreductor, diseñado para mover seguidores solares fotovoltaicos (PV) y concentradores solares (CPV) en dos direcciones a la vez, permitiendo que los paneles sigan al sol con precisión durante todo el día. 

|**Característica**|**Especificación**|
|---|---|
|Modelo|SVH7-71-60-RC-24H30100-REV. A|
|Fabricante|Coresun Drive|
|Tipo de mecanismo|Slewing Drive de doble eje (Dual Axis)|
|Aplicación|Seguidores solares PV/CPV|
|Motor eléctrico|24 VDC|
|Relación de transmisión|71:1|
|Torque de salida|937 N·m|
|Torque de momento de inclinación|13.5 kN·m|
|Torque de retención (Holding Torque)|10.4 kN·m|



4 

_Sistema fotovoltaico con seguidor solar biaxial_ 

|**Característica**|**Especificación**|
|---|---|
|Velocidad de salida|0.042 rpm|
|Clase de protección|IP65|
|Eficiencia|40 %|
|Peso|85 kg|
|Capacidad|6-10 paneles o de 200-600 kg|
|Pernos de montaje|M12|



_Fuente: Coresun Drive Equipment Changzhou Co., Ltd. (s. f.)._ 

### **_2.2.2 Controlador Creasol DomBusTracker2_** 



<!-- Start of picture text -->
, ERE EGER BSUEH) ;<br>rd |Creasol DomBusTracker2<br>Single/Dual axis solar tracker<br>t www.creasol.it - Made in EU<br>dbus proce /<br>Emons protcel DK<br>ees Es<br>Secchi gaeoerentat BOxABS LabeL VE<br>| Paapepety wus =)EnsTH  ew ane<br>if J e e s<br><!-- End of picture text -->

_Figura 2.3 – Controlador Creasol DomBusTracker2 Rev.2_ 

De acuerdo con Creasol (s. f.), este controlador opera automáticamente mediante la integración de sensores de luz impermeables, incluidos en el equipo, los cuales permiten detectar la dirección de mayor incidencia de radiación solar y orientar los paneles fotovoltaicos hacia la región más iluminada del cielo, optimizando así la captación de energía. El fabricante especifica que este dispositivo puede instalarse a una distancia de hasta 1000 m del DomBus, utilizando cable apantallado. 

Adicionalmente, el controlador dispone de una entrada dedicada para la conexión directa de un anemómetro con señal de salida de 3 a 5 V. Esta función permite implementar un mecanismo de protección ante condiciones meteorológicas adversas: cuando la velocidad del viento supera el umbral configurado, el sistema posiciona automáticamente los paneles fotovoltaicos en una posición de seguridad (stow position) para reducir las cargas aerodinámicas y minimizar el riesgo de daños estructurales. El anemómetro, para evitar picos de tensión o ruido eléctrico, debe conectarse a un condensador (100 ÷ 220 µF) entre los terminales Wind y GND. 

|**Característica**|**Descripción técnica**|
|---|---|
|Consumo de potencia|15 mW|



5 

_Sistema fotovoltaico con seguidor solar biaxial_ 

|**Característica**|**Descripción técnica**|
|---|---|
|Control de actuadores|4 salidas mediante relés, permitiendo el control de 2<br>actuadores para motores con capacidad de hasta 800 kgf|
|Tensión alimentación de actuadores|Compatible con actuadores alimentados a 24 Vcc<br>(recomendado por el fabricante) o 12 Vcc|
||Compatibles con sensores de proximidad NPN, con|
|Entradas para sensores de posición|referencia común a GND, para detectar las posiciones<br>máximas o finales de recorrido de los actuadores|



_Fuente: Creasol (s. f.)._ 

### **_2.2.3 Diagrama de conexión del controlador_** 



<!-- Start of picture text -->
Creasol DomBusTracker2<br>Connection diagram<br>=eS=(OL OME OOs*<br>“Main features: Ww Soest meaner =<br>on [| i ae<br>-tmancend<br>= wey ton poeWind oot poahoeconan fi a<br>~~ \ | |PpB) inser<br>® B aas| power sui 0<br>ats] a eo oa wll?<br>ianUd Ht3) O 3- 2,0)coh ‘WadeSrin EU<br>O . C4 ©} Ohm<br>— iid ino<br>~ Dil _| ten<br>| Bus 2x0 22mm’ shielded alarm cable- Sr est ND ‘Made in EU<br><!-- End of picture text -->

_Figura 2.4 – Diagrama de conexión del Creasol DomBusTracker2 (Creasol, s. f.)_ 

## **2.3 Sensores** 

### **_2.3.1 Sensor de viento analógico (anemómetro)_** 

6 

_Sistema fotovoltaico con seguidor solar biaxial_ 

Un anemómetro analógico mide la rapidez del aire y la convierte en un voltaje o corriente eléctrica variable. El valor de esta señal sube de forma proporcional conforme el viento sopla con más fuerza (AV Electronics, s. f.). 

### **_2.3.2 Sensor de proximidad NPN_** 

Los sensores NPN son componentes electrónicos que registran la cercanía de un objeto a distancia. Cuando el sensor se activa, utiliza un transistor NPN para enviar una señal de voltaje negativo (0 V) hacia el controlador, una lógica de control conocida técnicamente como sinking (HEBAI, 2024). 

## **2.4 Comunicación e Internet de las Cosas (IoT)** 

### **_2.4.1 Protocolo de comunicación_** 

El sistema de Creasol implementa un protocolo de comunicación para integrar el seguidor solar dentro de un ecosistema de Internet de las Cosas (IoT). Esta arquitectura permite la adquisición, transmisión y visualización de datos operativos en tiempo real, así como el control remoto del sistema mediante una computadora o un teléfono inteligente utilizando la aplicación Domoticz, de acceso gratuito (Creasol, s. f.). 

Para establecer esta comunicación se requiere una conexión entre el DomBusTracker2 y Domoticz mediante un bus de datos físico RS485, un convertidor USR-DR404 y un convertidor industrial USR-W610. 



<!-- Start of picture text -->
Serial device USR-DR404<br>y 4 Rs485 } AP Intemet Remote server<br>aly! wiFL<br>Serial device USR-DR404 A Local server<br>RS485 =“<br>i Local server<br>Diagram4 STAmode<br><!-- End of picture text -->

_Figura 2.5 – Arquitectura de comunicación RS485 – Wi-Fi/Ethernet (Jinan USR IOT Technology Limited, 2026)_ 

En primera instancia se utiliza el protocolo Modbus, el cual emplea un modelo de comunicación maestroesclavo que permite la interconexión y el flujo de datos entre los componentes electrónicos de la red (National Instruments, 2025). El set de DomBusTracker2 se integra al convertidor USR-DR404 a través de un bus de datos RS485, que garantiza el flujo de información de hasta 32 dispositivos con una distancia menor a 1200 metros. El USR-DR404 transforma las señales del puerto serie a redes Ethernet o Wi-Fi, agilizando la comunicación y garantizando una transmisión de datos eficiente con un uso mínimo del ancho de banda. 

El encargado de recibir la señal del USR-DR404 es el convertidor industrial de puertos serie a Wi-Fi y Ethernet USR-W610, que permite recolectar toda la información en el computador. Su alcance inalámbrico es de hasta 280 metros y admite un máximo de 24 dispositivos conectados simultáneamente (Industriales Andes, s. f.). 

7 

_Sistema fotovoltaico con seguidor solar biaxial_ 

En resumen, esta centralización de la información conecta directamente el seguidor solar con sistemas de gestión y plataformas IoT, asegurando un monitoreo continuo en tiempo real y una compatibilidad total con redes masivas de dispositivos conectados (Amazon Web Services, s. f.). 

Nota de escala: la arquitectura de comunicación aquí descripta corresponde a un (1) módulo. Dado que el bus RS485 admite hasta 32 dispositivos DomBusTracker2 por convertidor USR-DR404 (Jinan USR IOT Technology Limited, 2026), una planta de aproximadamente 1539 módulos (Capítulo 1) requiere replicar este segmento de bus en múltiples ramales independientes —del orden de 49 concentradores USR-DR404 como mínimo (1539 / 32)—, cada uno con su propio USR-W610 o punto de acceso Wi-Fi, agregados hacia uno o varios servidores Domoticz/SCADA centrales. El diseño detallado de esta red de comunicaciones a nivel de planta (segmentación de ramales, ubicación de concentradores, redundancia) corresponde a una etapa de ingeniería posterior y no se desarrolla en este documento, que se limita al módulo unitario. 

### **_2.4.2 Adaptador convertidor USB a RS485_** 

Este dispositivo electrónico permite conectar una computadora a equipos industriales o de automatización. Traduce las señales del puerto USB a un protocolo serial diferencial RS485, logrando una comunicación estable a largas distancias (Grupo Electrostore, s. f.). 

### **_2.4.3 Convertidor USR-DR404_** 

Es un dispositivo industrial que convierte señales de puerto serie RS485 a redes inalámbricas Wi-Fi. Permite conectar equipos tradicionales a internet o redes locales para control remoto y monitoreo en tiempo real (Proactive & Innovative Automation S.A.S., s. f.). 

### **_2.4.4 Convertidor USR-W610_** 

Es un dispositivo de red industrial que funciona como convertidor o servidor serial. Permite conectar equipos antiguos o industriales con puertos RS232 o RS485 a redes inalámbricas Wi-Fi (2.4 GHz) o redes por cable Ethernet (RJ45), logrando una transmisión de datos transparente y bidireccional (PUSR IOT., s. f.). 

### **_2.4.5 Plataforma Domoticz_** 

Domoticz es un sistema de automatización libre y de código abierto que permite controlar luces, sensores, medidores de energía, entre otros dispositivos. Funciona mediante una interfaz web accesible, permite el monitoreo del sistema y el envío de avisos. Además, es gratuito y soporta múltiples protocolos y una gran variedad de marcas de dispositivos (Domotuto, 2020). 

8 

_Sistema fotovoltaico con seguidor solar biaxial_ 



<!-- Start of picture text -->
Dual axis sun tracker controlled by DomBusTracker + Domoticz<br>Tae oo 7 5<br>—— > o_o a<br>a Sas o-—or sat<br>a ew SS en<br>Tose oer rc o« esa<br>‘Tracker SensorNS Elevation is perfect al =e =<br>fee oS<br><!-- End of picture text -->

_Figura 2.6 – Panel de control del seguidor solar biaxial en Domoticz_ 

## **2.5 Cableado y configuración** 

### **_2.5.1 Conexión física (cableado)_** 

- Interfaz RS485: conectar los bornes A y B del DomBusTracker2 a un adaptador USB-RS485 conectado al USR-DR404. 

- Alimentación: conectar el DomBusTracker2 a la fuente de alimentación, según la alimentación de los motores con que se va a trabajar. 

- Resistencias de terminación: colocar una resistencia de 120 ohmios en los extremos del bus RS485 para evitar interferencias en distancias largas. 

### **_2.5.2 Instalación del plugin en Domoticz_** 

Para que Domoticz entienda el protocolo de Creasol, se necesita instalar un plugin descargado del repositorio oficial de Creasol (CreasolTech, 2026). 

### **_2.5.3 Configuración en la interfaz de Domoticz_** 

Una vez reiniciado el servidor, se activa el hardware de comunicación: 

- En la interfaz web, ir a Configuración > Hardware. 

- En Nombre, escribir el nombre asignado al módulo. 

- En Tipo, seleccionar Creasol DomBus en el desplegable. 

- Seleccionar el puerto serie correcto. 

- Configurar la velocidad del bus a 115200 bps. 

- Hacer clic en Añadir. 

### **_2.5.4 Activación de los dispositivos del rastreador_** 

Al añadir el hardware, Domoticz escaneará el bus automáticamente y el DomBusTracker2 se registrará solo: 

9 

_Sistema fotovoltaico con seguidor solar biaxial_ 

- Dirigirse a Configuración > Dispositivos. 

- Aparecerán variables e interruptores de manera automática, como mandos manuales (azimut y elevación), lecturas del sensor de luz, estado del sensor de viento (anemómetro), y gráficos/estados de consumo de los actuadores. 

- Se selecciona cada parámetro que se desea monitorizar en la pestaña principal. 

10 

_Sistema fotovoltaico con seguidor solar biaxial_ 

# **3. Diseño de la estructura metálica** 

En este capítulo se determinan las cargas que actúan sobre el seguidor solar biaxial (gravitacionales y de viento) y se dimensionan los elementos estructurales que lo componen: vigas secundarias, viga principal, columna y cimentación. El procedimiento sigue el recorrido natural de las cargas, de arriba hacia abajo: paneles → vigas secundarias → viga principal → columna → cimentación. 

## **3.1 Cargas gravitacionales** 

Se calculan las cargas externas de los elementos que forman parte del mecanismo del seguidor solar de dos ejes: 

|**Elemento**|**Cantidad**|**Masa unitaria**|**Masa total**|**Carga vertical**|
|---|---|---|---|---|
|Panel fotovoltaico|8|32,4 kg|259,2 kg|2,543 kN|
|SVH7|1|85 kg|85 kg|0,834 kN|
|Carga de mantenimiento|1|200 kg|200 kg|1,962 kN|
|TOTAL CONOCIDO|||544,2 kg|5,339 kN|



## **3.2 Cargas críticas de viento (CIRSOC 102-2025)** 

Adicionalmente, es necesario conocer las cargas críticas de viento que actúan sobre el sistema. Estas se calculan en base al Reglamento CIRSOC 102-2025: Reglamento Argentino de Acción del Viento sobre las Construcciones, siguiendo los pasos que se detallan a continuación. 

### **_3.2.1 Velocidad de viento_** 

Referenciados en capítulos anteriores, se tiene que la velocidad del viento para la longitud y latitud correspondientes posee un valor de: 



### **_3.2.2 Factor de direccionalidad del viento, Kd_** 

11 

_Sistema fotovoltaico con seguidor solar biaxial_ 



<!-- Start of picture text -->
Tabla 1.6-1. Factor de direccionalidad de viento,<br>Ka<br>Tipo de estructura | direccionalidadFactor de Ky"<br>Edificios<br>Sistema principal resistente a<br>la fuerza de viento 0,85<br>Componentes y<br>revestimientos 0,85<br>Cubiertas abovedadas [oss|<br>Chimeneas, tanques y estructuras|<br>similares<br>Cuadradas 0,90<br>Hexagonales 095<br>Redondas 1,00°<br>Octagonales 1.00%<br>[Carteles llenos [oss<br>Carteles abiertos y estructura<br>reticulada<br>Torres reticuladas<br>Triangular, cuadrada,<br>rectangular 085<br>Toda otra secci6n transversal! 0,95<br>* El factor de direccionalidad Ky se ha calibrado con las<br>combinaciones de carga especificadas en el Apéndice B.<br>Este factor se debe aplicar solo cuando se use<br>conjuntamente con las combinaciones de carga<br>especificadas en B.3 0 en los respectivos reglamentos de<br>aplicacion<br>a Se permitir el factor de direccionalidad Ky = 0,95 para<br>redondos u octogonales. Estructuras con sistemas<br>estructurales no asimetricos<br><!-- End of picture text -->

_Tabla 3.1 – Factor de direccionalidad de viento, Kd (CIRSOC 102-2025, Tabla 1.6-1)_ 

Este valor corresponde a sistemas generales y carteles, ya que debe evaluarse considerando la posición más desfavorable de los seguidores solares, que en este caso es stow position. 

### _Kd = 0,85_ 

### **_3.2.3 Clasificación del edificio_** 



<!-- Start of picture text -->
‘Tabla 1.144, Categoria de riesgo para edificios y otras estructuras<br>u ocupacion. lificio<br>Uso u otra estructura Categoria<br>[ronpormnniappaninnreneemeee yan onara anuw ccupaciin dl ediiclou ota extract TdCetogore<br>scorenicoEatonEatin) cesoesnolan extucares exucresnoua cya nc lectaaooServesfal representanamasta euepeaelaun iesgesustancia atseago carpetcobsura ee parlecomrioedvide para umana ensrunsrs un evorto knpacoGe<br>ioe<br>FatsndafastlsEeitesycomo oraseonbuetiesde merulocura,estuctrespalgorce,qimcosnoprion,inidesranulsco®en la pelgoscs,clegraarecenarhenl,deesuuosHes pelgescsV (reuendo,wo¢ dapoecanexposes)pre denocoments sonnettimiado 2.|<br>trator toican @ exconvee dere ls canted ob matenal exeede an unbral de cartced<br>sctablecid<br>Steen pole Autoried Jursaclonalycssucorte Fare oer an ena par l pul o<br>EcifcosEatcosy crsyeas estucirasdesignades estuchrascoyetolreprosete come insalcionesesenclalsun etenacs susan pala comunied<br>Eaitons oes exbucureninauyerdo pore foto a, ilsloceres Se manera, proceso,<br>Franpuledntucostints  pelgoocsoreiauegee excedenatnacoromonef umbral plpoons) carcrondswoode, canliedaupeisineetasiecdode ulcerssosancinpor cantéodesdosustanccsatioentsleslr Auton’samo ennatbiesdunackecionaperroce,Yeo | 1<br>sunt para pecer una omeraza ai able se lberen<br>Eatceoncopeh gas errs oman pre mart! ucorld de oto nsalacees de catego<br><!-- End of picture text -->

_Tabla 3.2 – Categoría de riesgo para edificios y otras estructuras (CIRSOC 102-2025, Tabla 1.14-1)_ 

12 

_Sistema fotovoltaico con seguidor solar biaxial_ 

De acuerdo a la Tabla 1.14-1, se encuentra que el sistema posee una categoría de riesgo I. 

### **_3.2.4 Categoría de exposición_** 

Al sistema le corresponde una exposición C (campo abierto), pues en el apartado 1.7.3 aplica a todos los casos que no encajan en las definiciones de las exposiciones B o D. Incluye terrenos abiertos con obstrucciones dispersas que tienen alturas generalmente menores a 9 metros. En este caso, los campos de siembra, cultivos bajos, pastizales y terrenos planos entran estrictamente en esta categoría. Además, no hay elementos que frenen el viento, es decir que las ráfagas impactarán con total intensidad sobre los paneles biaxiales. 

### **_3.2.5 Coeficiente de exposición dinámica, Kz_** 

Este coeficiente representa el mínimo constante de velocidad del viento exigido por el reglamento para la zona entre el suelo y los 5 metros de altura, diseñado para garantizar la seguridad estructural al considerar el impacto directo en campo abierto (Exposición C) sin obstáculos que frenen la ráfaga. 



<!-- Start of picture text -->
Tabla 1.13-1. Coeficientes de exposicién para la<br>presion dinamica, Ky y K;<br>el nivel del<br>1y2 1y2<br>Pm [oer | ee a<br>| [o-5 0.59 o.87 1.057 |<br>a |<br>ps Tro oa 27 |<br>p20 Tes 5 34 |<br>J 25 | 90 P20 1.39 |<br>} 30 Ts 254<br>}| 3540 | toaooo T204733st |<br>|<br>p60 Tt aa 62 |<br>|<br>} so] 23 | 453 4.70 |<br>|<br>| ato T3463|4.80 |<br>} 30] 40 Teo 1.85 |<br>[iso as 74 90 |<br><!-- End of picture text -->

_Tabla 3.3 – Coeficientes de exposición para la presión dinámica, Kh y Kz (CIRSOC 102-2025, Tabla 1.13-1)_ 

_Kz = 0,87_ 

### **_3.2.6 Factor topográfico, Kzt_** 

### _Kzt = (1 + k1·k2·k3)² = (1 + 0)² = 1_ 

El factor topográfico representa el aumento de la velocidad del viento cuando pasa por encima de accidentes geográficos como lomas, crestas o acantilados aislados. En este caso, con un terreno con ondulaciones muy suaves —tal como es el caso de las zonas agrícolas—, no hay aceleración por relieve, por lo que el factor se toma igual a 1, manteniendo la presión del viento sin cambios significativos. 

13 

_Sistema fotovoltaico con seguidor solar biaxial_ 

### **_3.2.7 Factor del efecto de ráfaga, G_** 

El valor es 0,85 porque el reglamento establece este número como un factor fijo y simplificado para estructuras rígidas. Estructuralmente, un poste corto anclado al suelo ofrece una rigidez estática elevada. Debido a su baja altura y alta resistencia, los desplazamientos horizontales son mínimos, lo que garantiza de forma directa que la estructura se comporte mecánicamente como un cuerpo rígido. 



### **_3.2.8 Presión dinámica, qz_** 

Para calcular la presión dinámica se emplea la siguiente fórmula: 



Reemplazando los valores disponibles hasta el momento: 



### **_3.2.9 Clasificación del cerramiento_** 

Es un lugar abierto, ya que el reglamento define como "abierta" a toda estructura que tiene, como mínimo, el 80 % de su área de paredes abierta en cada una de sus fachadas. Para el presente proyecto, al tratarse de una pantalla de paneles solares suspendida en el aire sobre un poste central (sin paredes, ventanas ni techos perimetrales), el aire fluye y circula libremente por debajo y alrededor de toda la estructura. No existe ninguna posibilidad de atrapamiento de aire que genere presiones internas. 

### _Ao ≥ 0,8 Ag_ 

### **_3.2.10 Coeficiente de presión interna, GCpi_** 



<!-- Start of picture text -->
Tabla 1.11-1. Cooficiontes de presién interna para odificios (SPRFV, Componentes y Rovestimientos),<br>| Lestcorsterescerramiento: [azocerramiento: | oopeone | ompe ‘|<br>Exllciesparcalmente‘os parciaimen | astcacones‘Un edifico quecorades-parcamenteno cumple con | Moderado xO48<br>Edificiios parcialmermente Ag> 04m? 6 >0,014gfae a, el que sea menor Elevado “0,55<br>cerrados Agi! Agi S 0,20 0.55<br><!-- End of picture text -->

_Tabla 3.4 – Coeficientes de presión interna para edificios (CIRSOC 102-2025, Tabla 1.11-1)_ 

Este coeficiente mide la presión o succión que se genera dentro de un espacio cuando el viento entra y queda atrapado. En este caso, el aire circula libremente por arriba, por abajo y por los costados, y no existen paredes que encierren el aire, por lo que físicamente es imposible que se genere una presión interna. 



### **_3.2.11 Coeficiente de presión externa Cp y neta CN_** 

14 

_Sistema fotovoltaico con seguidor solar biaxial_ 

Se calculan en base a la Figura 2.4-1 y la Figura 2.4-4 del reglamento, respectivamente, considerando dos situaciones: cuando el panel se encuentra en posición de trabajo y cuando se encuentra en posición de seguridad (stow position). 



<!-- Start of picture text -->
Cxw oN<br>Direccion ow exw Direceisn<br>el viento el viento<br>| ose ose | ose ast<br>L L<br>Notacion:<br>|.=1 == dimensionalturadieceionmediahorizontal del techo,deen m,techo, media en la direccion del viento alo largo, en m.<br>) = angulo deldelplano viento,del techoen gradosdesde la horizontal, en grados.<br>Direccion<br>Angulo del viento 7=0" Direccibndel vientoy= 180"<br>tere [Sin bloqueo |” Con bloqued | Sin bloqueo | Con bloqued_|<br>peo[efef aaeeeTon [aaee[oeeefaa forPe far]Te06 ||<br>eea = OS eee<br>[« -} Se eee eee<br>pe [~s[~sfe [1s[2403pu {0 “2 [23pie[06[08 [18pee[22 [osor [1203Jpa13 To<br>ee ee<br>[ wsoe [VF e [2soe2a [os [2sToeee 22ee Tai [a6Tr eear [1ar Teieee for]03]<br>|» A|e  |a ee<br><!-- End of picture text -->

_Figura 3.1 – Posición de trabajo del panel: notación y tabla de coeficientes CNW / CNL_ 



<!-- Start of picture text -->
VIENTO r 1G acc, WGCpCOsWS EE accp=s}estipeeNGC ae<br>so } = = =; =i<br>| maa = Esc KS =<br>Ly — a 5_4~—l[= SJ_4—lFE<br>PLANTA ELEVACION ELEVACION<br>CUBIERTAS DE VERTIENTE UNICA (Nota 4)<br><!-- End of picture text -->

_Figura 3.2 – Posición de seguridad (stow position): planta y elevaciones_ 

### **_3.2.12 Presiones totales_** 

Para hallar las presiones se utilizan las siguientes fórmulas, para posición de trabajo y para stow position, respectivamente: 





El resumen de los cálculos se dispone a continuación: 

15 

_Sistema fotovoltaico con seguidor solar biaxial_ 



<!-- Start of picture text -->
Cubierta de vertiente tinica, edificios abiertos<br>p=qh.G.CN<br>qh=  181,3N/m2 este valor es max 20 m/s<br>G 0.85<br>Or, OQ»,<br>=| SO Sp<br>Presién<br>Angulo del | Casode , total<br>techo Carga Wim N/m2<br>| a_{ a2 [os [ass | a6 [231 | u2 {03 [aes | a6 [231 |<br>{oe {aa [oa |-a70 | as | aes | aa | 02 [avo [as [85 |<br>75. LA [oe] a [92 [asa [247 [09 | is [139 [231 [370 |<br>|e [aalo |e | o | 26 | ie | 03 | 247 | a6 [293 |<br>as | A&__]o09 [13 [139 [200 | “339 [13 | 16 | 200 [27 | aa7_|<br>|e {as{ o |-203{ o | -203 | is { o6 [277 | 92 [370 |<br>| a | as | 16 |-231 | -2a7 | -avs_| a7 | i | 262 | 277 | 539 |<br>|e {24 | 03 |-370 | -a6 | -ais_| 2.2 | 07 | 339 | 108 [ a47_|<br>| a [8 | 18 |-277 |-277 [sso] 21 | 21 | 324 [32a [647 |<br>|e {25 | os | sas | -77 | 462 | 26 { a | aor | asa [555 |<br>375. | A 8 [8 | 277 [277 [sss 2a | 2.2 | 32a [339 | 663_|<br>|e {24 | 06 [370 | -92 | -aez | 27 [aa [ae [70 | se6_|<br>er fe<br>[es [23 [07 [35s |-t08 | -a62 [26 [a4 [aor [osc | 617 _|<br><!-- End of picture text -->

_Tabla 3.5 – Presiones totales por ángulo de techo y dirección de viento (cubierta de vertiente única)_ 



<!-- Start of picture text -->
Edificios parcilamente abiertos<br>p=qz.G.Cpqz= 1133 N/m2 4126Cp_<br>G= 0.85 I<br>Cp= 08 {<br>P= 770.4 N/m2<br><!-- End of picture text -->

_Figura 3.3 – Presión para edificios parcialmente abiertos (stow position, 90°)_ 

Finalmente, se tiene que las cargas máximas alcanzadas en el sistema son: 

- En posición de trabajo, con un ángulo del panel de 45° a barlovento: una carga de viento de 724 N/m². 

- En stow position, cuando los paneles se encuentran en posición totalmente vertical (90°): una carga de viento de 770,4 N/m². 

Posteriormente, para proceder al cálculo de los componentes estructurales del seguidor solar, se define el uso de la metodología de los esfuerzos permisibles (A.S.D.), en donde se establece que todo esfuerzo real debe ser menor o igual al permisible: 

_fb ≤ Fb_ 

16 

_Sistema fotovoltaico con seguidor solar biaxial_ 

Donde el esfuerzo permisible es igual al límite elástico o resistencia a la fluencia (yield strength, Sy) entre el factor de seguridad del sistema (1,66). Para el diseño a tracción, compresión, corte, torsión y flexión se tiene: 



De acuerdo con la A.I.S.C., si I se encuentra por encima de 1,1 el sistema fallará; en valores por debajo de 0,85 el sistema se encuentra sobredimensionado. Bajo este criterio se procede a realizar los respectivos cálculos, tomando en consideración cada una de las cargas estáticas que actúan sobre el sistema del seguidor solar. 

17 

_Sistema fotovoltaico con seguidor solar biaxial_ 

## **3.3 Cálculo e ingeniería de vigas secundarias** 

Se calculan las cargas máximas a las que van a trabajar los paneles solares: 

_qh(20) = 0,613 × 0,87 × 1 × 0,85 × (20)² = 181,3 N/m² → Pmax = 324 N/m²  (paneles a 45°, viento_ 

- _a 20 m/s)_ 

_qh(50) = 1133 N/m² → Pmax = 770 N/m²  (stow position, 90°, viento a 50 m/s)_ 



<!-- Start of picture text -->
2,30 m = 90,6 pulg<br><—________-<br>Anco total: 4,76 m<br>= 87 pulg<br><<<br>Longitud: 4,60 m = 181,1 pulg<br>Areas de influencia: Al = 10,95 m? - A2 = 10,95 m? - Atotal = 21,9 m?<br>(arreglo 2 filas x 4 paneles = 8 paneles; 5 vigas secundarias a 1,15 m de paso)<br><!-- End of picture text -->

_Figura 3.4 – Áreas de influencia sobre la viga secundaria_ 

- Ancho total: 4,76 m = 187 pulg 

- Longitud: 4,60 m = 181,1 pulg 

- Mitad de la longitud de la viga secundaria: 2,38 m = 93,7 pulg 

- Áreas de influencia: A1 = 10,95 m² · A2 = 10,95 m² · Atotal = 21,9 m² 

Se procede a trabajar con qh máx, que corresponde a la stow position; para el diseño de las vigas se define el uso de acero galvanizado ASTM A-36. 

_Qw = 770,4 N/m² · 21,9 m² = 16,87 kN_ 



<!-- Start of picture text -->
Ohaus > stow position<br>w = 0,7 kN/m<br><!-- End of picture text -->

_Figura 3.5 – Modelo de carga distribuida sobre la viga secundaria (stow position)_ 

18 

_Sistema fotovoltaico con seguidor solar biaxial_ 

_qw = 16,87 kN / 5 vigas = 3,37 kN por cada viga  →  qwL = 3,37 kN / 4,76 m = 0,7 kN/m_ 



<!-- Start of picture text -->
Anélisis de Vigas Z<br>Dlagrama de Cuerpo Libre Fuerza Cortantes 10°N)<br>Mp! 833.00<br>41650 416.50<br>070<br>eealm “#1650 416.50<br>nN c 8 oe 833.00<br>v0 19 aie a6 475 Momento Flector c10°KN.m]<br>hoo”Ayo -041 12500 KN 495.64 495.64<br>fgea 61 8261 ;<br>= 044 Kim<br>=o “4130 “4130 o<br>Me<br><!-- End of picture text -->

_Figura 3.6 – Diagrama de cuerpo libre, fuerzas cortantes y momento flector de la viga secundaria_ 

- Mmax = 0,5 kN·m = 4,4 klb·pulg 

- L = 4,76 m = 187 pulg 





_Sx > M/Fb = (4,4 klb·pulg)/(14,4 klb/pulg²) = 0,3 pulg³ = 4,9 cm³_ 

Se selecciona ► Perfil G 60x30x10x2, con Sx = 4,9 cm³ = 0,3 pulg³ y γ = 2,42 cm = 0,95 pulg. 

_λF = 187 pulg / 0,95 pulg = 196,8_ 

### **_3.3.1 Cálculo del factor Cb_** 

_Cb = 12,5·Mmax / (2,5·Mmax + 3·MA + 4·MB + 3·MC) = 12,5·0,5 / (2,5·0,5 + 3·0,5 + 4·0,083 + 3·0,5) = 1,36_ 

### **_3.3.2 Cálculo de la longitud Ls_** 

_Ls = √(510×10³·Cb / Sy) = √(510×10³·1,36 / 36) = 138,8 < λF_ 

Como Ls < λF: 



### **_3.3.3 Verificación (primer perfil propuesto)_** 

_fb = Mmax/Sx = 4,4 klb·pulg / 0,3 pulg³ = 14,7 kSI_ 

Como fb = 14,7 kSI > Fb = 6 kSI → el perfil FALLA. Tomando el límite Ls = λF: 

_γ ≥ L/138,8 = 187 pulg/138,8 = 1,35 pulg = 3,4 cm_ 

### **_3.3.4 Selección final del perfil_** 

Se selecciona ► Perfil G 100x50x15x2, con Sx = 13,85 cm³ = 0,85 pulg³ y γ = 4 cm = 1,57 pulg. 

19 

_Sistema fotovoltaico con seguidor solar biaxial_ 

_λF = 187 pulg / 1,57 pulg = 119 < 138,8_ 

_Fb = [2/3 − Sy·λF² / (1530×10³·Cb)] · Sy = [2/3 − 36·119² / (1530×10³·1,36)] · 36 = 15,18 kSI_ 

_fb = 4,4 klb·pulg / 0,85 pulg³ = 5,18 kSI_ 

_Ib = fb/Fb = 5,18/15,18 = 0,34 < 1  →  el perfil se encuentra sobredimensionado_ 

_Masa de la viga = 3,38 kg/m · 4,76 m = 16 kg por viga  →  Peso de la viga = 0,16 kN por viga_ 

### **_3.3.5 Refuerzo adicional mediante reticulado diagonal_** 

Con el fin de incrementar la rigidez efectiva de las vigas secundarias y reducir su deformación bajo las cargas de viento y peso propio calculadas en la presente sección, se incorporaron soportes adicionales tipo diagonal, dispuestos a manera de reticulado (celosía) entre la viga principal y cada una de las vigas secundarias del arreglo. Estos elementos se materializan mediante perfil angular L 2 x 2 x 1/8 pulg (50,8 x 50,8 x 3,2 mm), en el mismo acero ASTM A-36 galvanizado empleado para las vigas secundarias. 

Este reticulado diagonal no reemplaza el dimensionamiento de la viga secundaria desarrollado en la Sección 3.3.4 (perfil G 100x50x15x2, Ib = 0,34), sino que actúa como un apoyo intermedio adicional que acorta la luz efectiva de flexión de cada viga secundaria, incrementando su rigidez frente a la deformación bajo carga — un mecanismo complementario de control de deflexión, coherente con el criterio de servicio L/240 discutido en la validación numérica del Capítulo 6. La disposición geométrica de este reticulado, tal como fue modelada en Autodesk Inventor, puede observarse en las Figuras 6.1 y 6.2, y corresponde a los mismos elementos diagonales cuyo comportamiento tensional (tensión de corte Ty y tensión de torsión T) fue verificado mediante análisis por elementos finitos en la Sección 6.4 (Figuras 6.6 y 6.7), donde se confirmaron índices de aprovechamiento de 0,098 y 0,0086 respectivamente — márgenes amplios que corroboran la adecuación del perfil angular seleccionado para esta función de refuerzo. 

20 

_Sistema fotovoltaico con seguidor solar biaxial_ 

## **3.4 Cálculo e ingeniería de la viga principal** 



<!-- Start of picture text -->
353kn 353‘nN 353kn 353co 353kn<br>= 4,60my = 282,1 pulg<br><!-- End of picture text -->

_Figura 3.7 – Esquema de cargas puntuales sobre la viga principal (voladizo)_ 

_q = Pviga + qw = 0,16 kN + 3,37 kN = 3,53 kN_ 



<!-- Start of picture text -->
Fuerzas Cortantes (kN] Momento Flector (kN-m]<br>a 47.06 Z<br>°°<br>2ow<br>td 5e -10<br>-8 708 ea azae<br><!-- End of picture text -->

_Figura 3.8 – Diagrama de cuerpo libre, fuerzas cortantes y momento flector de la viga principal_ 

- Mmax = 12,18 kN·m = 108 klb·pulg 

• L = 4,60/2 m = 90,6 pulg (se considera media viga, como viga en voladizo) Para la viga principal se usa acero ASTM A 500 Grado C. 







Se selecciona tubo circular ► Perfil HSS 5 x 0,375, con Sx = 5,55 pulg³ y γ = 1,65 pulg. 







_Fb = [2/3 − Sy·λF² / (1530×10³·Cb)] · Sy = [2/3 − 50·54.9² / (1530×10³·1)] · 50 = 28,4 kSI_ 



_Ib = fb/Fb = 19,5/28,4 = 0,7  →  columna sobredimensionada_ 

_Masa de la viga = 18,54 lb/pie · (1,488 kg/m)/(lb/pie) · 4,60 m = 127 kg  →  Peso de la viga = 1,3_ 

_kN_ 

21 

_Sistema fotovoltaico con seguidor solar biaxial_ 

22 

_Sistema fotovoltaico con seguidor solar biaxial_ 

## **3.5 Cálculo e ingeniería de la columna** 



_Figura 3.9 – Esquema de la columna (altura libre 3 m)_ 

Se define el uso de acero ASTM A-588. 

_Wmax = 724 N/m² · 21,9 m² + (0,16 kN · 5) + 1,3 kN + 5,3 kN = 15,9 kN = 3,6 klb_ 





Se selecciona ► Perfil W4x13, con A = 3,83 pulg² y γmin = 1 pulg. 



Para el acero A588: 



Se procede a encontrar la longitud efectiva mediante el nomograma de Jackson y Moreland, con c1 = 1 (extremo empotrado) y c2 = ∞ (extremo libre): 

23 

_Sistema fotovoltaico con seguidor solar biaxial_ 



<!-- Start of picture text -->
Ga K Gy<br>100.050.0x 20010.0 *50.0100.0<br>30.0 50 30.0<br>200 40 20.0<br>10.0 30, 10.0<br>80 80<br>70 70<br>60 60<br>50 5.0<br>40 20 40<br>80 1.76 i<br>20 20<br>15<br>10 10<br>0.0 10 0.0<br><!-- End of picture text -->

_Figura 3.10 – Nomograma de Jackson y Moreland para longitud efectiva K_ 

_k12 = 2,2_ 

_λmax = 200  →  γmin = K·L/200 = 2,2·118/200 = 1,3 pulg_ 

Es decir que, para el perfil W8x13 (equivalente considerado), no cumple. 

Se selecciona ► Perfil W6 x 15, con A = 4,43 pulg² y γmin = 1,45 pulg. 





_Fa = 12·π²·E / (23·λ²) = 12·π²·30×10⁶ [PSI] / (23·179²) = 4821 psi = 4,8 kSI_ 

_Ia = fa/Fa = 0,8/4,8 = 0,17 < 1  →  se encuentra sobredimensionado y cumple_ 

_Masa de la columna = 15 lb/pie · (1,488 kg/m)/(lb/pie) · 3 m = 67 kg  →  Peso = 0,67 kN_ 

24 

_Sistema fotovoltaico con seguidor solar biaxial_ 

## **3.6 Cálculo e ingeniería de la cimentación** 

_Wtotal = 15,9 kN + 0,67 kN = 16,57 kN = 3,73 klb = 1692 kg_ 

_Qviento w = 16,87 kN_ 

_Ma = 16,87 kN · 3 m = 50,6 kN·m = 448 klb·pulg_ 



<!-- Start of picture text -->
i<br>F ° i .)<br>H n<br>U em a at .<br><!-- End of picture text -->

_Figura 3.11 – Placa base, planta y elevación de la cimentación_ 

- Perfil de la columna: W6 x 15 (ancho d, ala I, + 6,5 pulg). 

- Vista en planta de la placa base: dimensiones B x C, con distancias de borde n y m. 

   - _ρ = P/A ≤ F'c = f'c / F.S.   (F'c: esfuerzo admisible a la compresión del hormigón)_ 

   - _F'c = f'c/4 = 210/4 = 52,5 kg/cm²   (210 es la resistencia última a la compresión)_ 

_Ap = P/f'c = 1692/52,5 = 32,23 cm²  →  B x C, cimentación cuadrada (B = C)_ 



Si n = 2 cm → B = 15,21 + 4 cm = 19,21 cm. Si m = 5 cm → C = 15,21 cm + 10 cm = 25,21 cm. 



**_3.6.1 Espesor de la placa base (Acero A588 – Grado C)_** 

_t = √(12·f'c·n² / (0,66·Sy)) = √(12·210·4² / (0,66·3500 kg/cm²)) = 2 cm (3/4 pulg)_ 

Se determinan las características de la placa base: 25 x 25 x 2 [cm]. 

### **_3.6.2 Perno de anclaje (ISO 8.8)_** 



_F = Mx / (2·do) = 516 000 kg·cm / (2·21 cm) = 12,3 Tn   (distancia entre pernos do = 21 cm)_ 

25 

_Sistema fotovoltaico con seguidor solar biaxial_ 



<!-- Start of picture text -->
eK 2F.do<br>Z<br>Fl | x<br>‘<br>| de F ”<br>{1<br>(FI re<br>ap Ay aT a] es<br>x Ad | Fl<br>A2 eth“ 4, =|)Ga4] | Cea<br>v7<br>Ap a<br>J mPa FALL 4<br>2 - Le a Bos — op<br><!-- End of picture text -->

_Figura 3.12 – Esquema de fuerzas sobre los pernos de anclaje_ 

_F = F1 + F2_ 

Propiedades del hormigón: 

_fh = 45 kg/cm² → Fh = fh/3 = 15 kg/cm²  ;  f'c = 210 → F'c = f'c/4 = 52,5_ 

_Ap ≥ F/Ft = 12 300 kg / (0,6·6400 kg/cm²) = 3,20 cm²   (pernos ISO 8.8, Sy = 6400 kg/cm²)_ 

_d = √(4·Ap/π) = √(4·3,20 cm²/π) = 2,02 cm ≈ 1 pulg_ 



Por lo tanto, la altura del plinto es de 0,5 m y la dimensión de la "J" de los pernos de anclaje es a = 6 cm. 

**_3.6.3 Longitud de la soldadura del perfil W a la placa base_** 



<!-- Start of picture text -->
\<br>Ny ff moments de material;<br>EN T> fv<br>\ garganta g<br>\ del cordén de<br>soldadura.<br>g=0,707.a<br><!-- End of picture text -->

_Figura 3.13 – Detalle de la garganta del cordón de soldadura_ 

26 

_Sistema fotovoltaico con seguidor solar biaxial_ 



_Mx = 50,6 kN·m = 516 000 kg·cm  →  F = Mx/(2·d) = 516 000/(2·20) = 12,9 Tn = 28,4 klb_ 

_g = 0,707 · a = 0,707 · 0,5 pulg = 0,35 pulg_ 

Con 16,36 kSI como esfuerzo admisible para electrodo E8013: 

_L = 28,4 klb / (16,36 kSI × 0,35 pulg) = 4,97 pulg ≈ 5 pulg = 126 mm_ 

Esta es la longitud mínima que debe poseer la soldadura. 

## **3.7 Selección del tratamiento superficial: galvanizado** 

Todos los perfiles de acero estructural especificados a lo largo de este capítulo (vigas secundarias, viga principal, columna, placa base y el reticulado diagonal de refuerzo descrito en la Sección 3.3.5) se especifican en acero ASTM A-36 con un tratamiento superficial de galvanizado en caliente (hot-dip galvanizing). Esta decisión responde a que el seguidor solar es una estructura de intemperie, expuesta de forma permanente a humedad, radiación solar, variaciones térmicas y, según la ubicación de la planta, a ambientes con potencial agresividad salina o industrial, condiciones bajo las cuales el acero al carbono sin protección superficial desarrolla corrosión (oxidación) de manera progresiva. 

El galvanizado en caliente consiste en sumergir la pieza de acero en un baño de zinc fundido, con lo cual se forma una serie de capas de aleación hierro-zinc unidas metalúrgicamente al sustrato, cubiertas por una capa externa de zinc puro (ASTM International, 2017; Asociación Americana de Galvanizado [AGA], 2021). Esta capa protege al acero base mediante dos mecanismos simultáneos: una barrera física continua que aísla al acero del ambiente, y una protección catódica (galvánica), por la cual, ante una eventual discontinuidad o daño superficial del recubrimiento (por ejemplo, un rayón), el zinc circundante se sacrifica preferentemente y continúa protegiendo al acero expuesto, retardando así el inicio de la corrosión incluso en zonas puntualmente dañadas (AGA, 2021). 

Frente a otras alternativas de protección superficial (por ejemplo, pintura industrial o recubrimientos epóxicos aplicados en obra), el galvanizado en caliente presenta ventajas particularmente relevantes para una estructura como la del presente seguidor solar: 

- Durabilidad de largo plazo sin mantenimiento periódico: la vida útil típica de un recubrimiento galvanizado en ambientes atmosféricos rurales o suburbanos se estima en varias décadas, sin requerir repintados o inspecciones de mantenimiento recurrentes (AGA, 2021), lo cual resulta coherente con una instalación de 1539 unidades distribuidas en una planta de 8 MW, donde el mantenimiento correctivo individual de cada estructura sería logísticamente costoso. 

- Recubrimiento uniforme, incluyendo zonas internas: al ser un proceso por inmersión, el zinc recubre tanto las superficies externas como las internas y los bordes de los perfiles tubulares (HSS) y angulares empleados en la estructura, zonas que serían difíciles de proteger de manera uniforme mediante pintura aplicada por aspersión o brocha. 

- Resistencia mecánica del recubrimiento: la capa de aleación hierro-zinc formada durante el proceso queda unida metalúrgicamente al acero base, por lo que resiste mejor los golpes, la abrasión y el manipuleo durante el transporte y montaje de la estructura, en comparación con un recubrimiento de pintura aplicado superficialmente (ASTM International, 2017). 

27 

_Sistema fotovoltaico con seguidor solar biaxial_ 

La especificación de acero galvanizado conforme a la norma ASTM A123/A123M para perfiles estructurales (ASTM International, 2017), complementada por la norma internacional ISO 1461 para el mismo tipo de recubrimiento (International Organization for Standardization [ISO], 2009), constituye así el criterio de protección anticorrosiva adoptado para la totalidad de los componentes metálicos estructurales del seguidor solar, garantizando la integridad del sistema durante su vida útil de operación en condiciones de intemperie. 

28 

_Sistema fotovoltaico con seguidor solar biaxial_ 

# **4. Diseño eléctrico, mecánico y de control del sistema de seguimiento** 

Este capítulo desarrolla los cálculos eléctricos, mecánicos y de control necesarios para completar la ingeniería de detalle del seguidor solar biaxial: dimensionamiento de conductores y protecciones, puesta a tierra, canalizaciones, los tres subsistemas de accionamiento (elevación, azimut y frenos), el análisis cinemático del mecanismo de dos ejes, y la definición de entradas/salidas y lógica de control del sistema, incluyendo la posición de bandera (stow) ante viento excesivo. 

Alcance: como se indicó en el Capítulo 1, todos los cálculos siguientes corresponden al módulo unitario (un seguidor de 8 paneles, string de 5,2 kWp) que se repite aproximadamente 1539 veces a lo largo del predio para alcanzar la potencia objetivo de 8 MW. El dimensionamiento del conductor de salida de cada módulo (Sección 4.1) es, por lo tanto, el que debe repetirse en cada una de las aproximadamente 1539 unidades; la red de colección de continua o media tensión que agrupa los módulos hacia las estaciones inversoras y la subestación de interconexión de la planta no forma parte del alcance de este documento. 

## **4.1 Cálculo de conductores y protecciones eléctricas** 

### **_4.1.1 Datos eléctricos del generador fotovoltaico_** 

Los parámetros eléctricos reales del panel JKM625-650N-66HL4M-BDV-Z1 (bin de 650 Wp), obtenidos de la ficha técnica del fabricante, son: 

|**Parámetro**|**Símbolo**|**Valor**|
|---|---|---|
|Tensión en el punto de máxima potencia|Vmp|41,6 V|
|Corriente en el punto de máxima potencia|Imp|15,64 A|
|Tensión de circuito abierto|Voc|50,28 V|
|Corriente de cortocircuito|Isc|16,44 A|
|Corriente máxima admisible de fusible de serie|—|35 A|



_Fuente: Jinko Solar Co., Ltd. (2024). JKM625-650N-66HL4M-BDV-Z1-EN [Ficha técnica de producto]._ 

Se adopta una configuración de un (1) string de 8 paneles en serie, alimentando un único punto de conexión (tablero de continua). La tensión y corriente de string resultan: 

_Vmp,string = 8 × 41,6 V = 332,8 V   ;   Voc,string = 8 × 50,28 V = 402,2 V_ 

_Isc,string = Isc(módulo) = 16,44 A_ 

Ambos valores quedan muy por debajo de la tensión máxima de sistema del panel (1500 V DC), por lo que la configuración serie de 8 unidades es válida. 

### **_4.1.2 Corriente de diseño del circuito de continua_** 

Siguiendo el criterio de sobredimensionamiento por operación continua de generadores fotovoltaicos (AEA 90364-7-712), la corriente de diseño del conductor se calcula como: 

29 

_Sistema fotovoltaico con seguidor solar biaxial_ 

### _Ib = 1,25 × Isc,string = 1,25 × 16,44 A = 20,55 A_ 

### **_4.1.3 Selección de conductor_** 

Para el tramo panel–tablero de continua, expuesto a la intemperie y a temperaturas de operación de hasta 70 °C (según ficha del panel), se selecciona cable unipolar tipo solar H1Z2Z2-K, con conductor de cobre estañado clase 5, aislación y cubierta de goma reticulada libre de halógenos, fabricado según la norma armonizada EN 50618, con tensión asignada 1,5/1,5 (1,8) kV DC. 

|**Parámetro**|**Valor adoptado**|
|---|---|
|Tipo de cable|H1Z2Z2-K (EN 50618), unipolar, cobre estañado|
|Sección nominal|6 mm²|
|Tensión asignada|1,5/1,5 kV DC|
|Temperatura máxima de conductor|90 °C (120 °C en régimen transitorio)|
|Criterio de verificación|Ib ≤ In ≤ Iz (AEA 90364-5)|



La ampacidad admisible (Iz) del cable de 6 mm², corregida por temperatura ambiente y agrupamiento según las tablas del fabricante y de AEA 90364-5, debe verificarse en obra que sea igual o superior a la corriente nominal de la protección; la sección de 6 mm² provee margen amplio frente a los 20,55 A de diseño, típico de cables solares de esta sección en instalación al aire libre sobre bandeja o tubo. 

### **_4.1.4 Selección de la protección de continua_** 

Al tratarse de un único string (sin strings en paralelo), no es necesaria una protección de sobrecorriente por string para evitar corrientes inversas; se dispone igualmente un interruptor-seccionador de continua para maniobra y protección del tablero: 

_Ib (20,55 A) ≤ In ≤ Iz  y  In ≤ 35 A (corriente máxima de fusible de serie del módulo, dato de fabricante)_ 

Se selecciona un interruptor termomagnético bipolar de corriente continua, curva C, In = 25 A, tensión nominal de aislación ≥ 600 V DC (con amplio margen respecto a los 402,2 V de Voc de string), complementado con un descargador de sobretensiones (SPD) tipo 2 en el tablero de continua, conforme a las recomendaciones de protección contra sobretensiones de origen atmosférico de AEA 90364-7-712 (Asociación Electrotécnica Argentina, 2015). 

### **_4.1.5 Circuito de accionamiento (24 VDC)_** 

Los motorreductores del SVH7 (24 VDC) demandan, en régimen continuo de giro, una corriente reducida, calculada en la Sección 4.4 a partir del balance de potencia mecánica/eléctrica del accionamiento. Para el cableado entre el DomBusTracker2 y los actuadores se adopta cable multipolar apantallado de cobre, conductores de 1,5 mm² (norma IRAM 2183, conductores de cobre aislados con PVC para instalaciones fijas), protegido individualmente por interruptor termomagnético bipolar 24 VDC, curva C, In = 6 A por eje, coherente con los relés de salida del controlador (4 salidas por relé, hasta 2 actuadores) y con el criterio de la conexión de un condensador de 100–220 µF entre los bornes Wind y GND del anemómetro ya especificado en el Capítulo 2. 

30 

_Sistema fotovoltaico con seguidor solar biaxial_ 

## **4.2 Cálculo de puesta a tierra** 

### **_4.2.1 Esquema y resistividad del terreno_** 

Se adopta un esquema de puesta a tierra tipo TT, con jabalina(s) de acero cobreado como electrodo de dispersión, uniendo las masas metálicas de la estructura (columna, viga principal, gabinete del DomBusTracker2 y bastidores de los paneles) a un único sistema de tierra. Para el sitio del proyecto (Puerto Madryn, Chubut), correspondiente a un suelo árido de tipo gravoso-arenoso, se adopta una resistividad de diseño conservadora, dentro de los rangos típicos publicados para este tipo de terreno: 



### **_4.2.2 Resistencia de una jabalina simple_** 

Para una jabalina vertical de longitud L = 1,5 m y diámetro d = 14,3 mm (5/8″), la resistencia de dispersión se calcula con la fórmula clásica de electrodo de varilla: 





Este valor supera ampliamente el límite práctico recomendado para instalaciones con equipos electrónicos sensibles (≤ 10 Ω) y el límite formal de AEA asociado a la sensibilidad del interruptor diferencial adoptado. 

### **_4.2.3 Configuración de jabalinas múltiples_** 

Se dispone una configuración de jabalinas en paralelo, interconectadas mediante conductor de cobre desnudo, separadas una distancia igual a su longitud (s = L = 1,5 m) para minimizar el efecto de apantallamiento mutuo. La resistencia equivalente de n jabalinas en paralelo se estima como: 



donde Fc es un factor de corrección por acoplamiento mutuo (Fc ≈ 1,2 para separación s = L). Para n = 8 jabalinas: 



Dado que el valor aún no satisface el objetivo de diseño (≤ 10 Ω) en suelo árido, se complementa el sistema con tratamiento químico del terreno (bentonita sódica o gel electrolítico, GEM), una práctica reconocida en la literatura técnica de puesta a tierra como mejorador de resistividad, con una reducción típica de 30– 50 % sobre ρ: 



El valor final, ajustado con jabalinas adicionales o mejorador de suelo en obra, debe verificarse por medición directa con telurímetro y cumplir el límite formal de la reglamentación AEA vigente para el esquema TT adoptado. 

### **_4.2.4 Conductor de protección (PE)_** 

31 

_Sistema fotovoltaico con seguidor solar biaxial_ 

Para la sección del conductor de protección se aplica el criterio de AEA 90364-5 según el cual, si el conductor de fase se dimensiona por corriente admisible y no por caída de tensión, la sección del PE puede tomarse igual a la del conductor activo para secciones menores a 16 mm². Se adopta conductor de protección de cobre de 6 mm² (igual sección que el conductor activo de continua) para el circuito fotovoltaico, y de 2,5 mm² para el circuito de accionamiento de 24 VDC. 

Nota de escala: la configuración de jabalinas calculada corresponde a la puesta a tierra local de un (1) módulo (estructura, columna y gabinete del DomBusTracker2). En una planta de aproximadamente 1539 módulos, cada puesta a tierra local debe además vincularse, mediante conductor de equipotencialidad, a la malla de tierra general de la planta y a la de la subestación de interconexión, cuyo dimensionamiento (mucho más exigente en cuanto a corrientes de falla y tensiones de paso y de contacto) corresponde a la norma IEEE Guide for Safety in AC Substation Grounding (IEEE Std 80-2013) y queda fuera del alcance de este documento, centrado en el módulo unitario. 

## **4.3 Cálculo de canalizaciones** 

### **_4.3.1 Criterio de relleno_** 

Conforme al criterio general de AEA 90364-5 para la selección del conjunto canalización/conductores, la sección ocupada por el total de conductores no debe superar el factor de relleno admitido por el fabricante del conducto, tomándose como referencia de diseño un factor de ocupación máximo del 35 % de la sección interna del conducto para tres o más conductores. 

### **_4.3.2 Sección de conductores a canalizar_** 

Para el tramo panel–tablero de continua se agrupan 2 conductores unipolares de 6 mm² (positivo y negativo del string) más el conductor de protección de 6 mm²: 





### **_4.3.3 Selección del conducto_** 

Aplicando el factor de relleno del 35 %: 





Se selecciona caño de PVC rígido tipo pesado según IRAM 2206-3, de diámetro nominal 20 mm (3/4″), cuyo diámetro interno (≈ 18–19 mm según fabricante) satisface la condición de relleno calculada, dejando margen adicional para el cableado de control (par apantallado RS485 y alimentación 24 VDC a los actuadores), que se aloja en un conducto independiente de igual diámetro para evitar interferencia electromagnética entre el circuito de potencia y el de señal, conforme al criterio de segregación de circuitos de AEA 90364-5. 

32 

_Sistema fotovoltaico con seguidor solar biaxial_ 

## **4.4 Cálculo del sistema de elevación** 

El eje de elevación es accionado por uno de los dos salidas del motorreductor SVH7 (torque de salida nominal 937 N·m, Capítulo 2). El torque requerido para mover el arreglo contra la carga aerodinámica se obtiene a partir del momento diferencial entre las mitades a barlovento y a sotavento del panel, reutilizando los coeficientes de presión ya calculados en la Tabla 3.5 del Capítulo 3 para el caso más desfavorable en posición de trabajo (ángulo 45°, γ = 180°, Caso A): 



El momento neto sobre el eje de elevación surge de la diferencia de presión entre ambas mitades del panel, cada una actuando sobre su área mitad (A/2 = 10,95 m²) con brazo igual a un cuarto de la longitud total del arreglo (L/4), coherente con el criterio de viga en voladizo desde el centro ya adoptado en el Capítulo 3: 





Comparando contra el torque de salida nominal del SVH7 (937 N·m), y aplicando el mismo criterio de índice de aprovechamiento I = solicitación/admisible empleado en el Capítulo 3: 



Con el arreglo de 8 paneles el índice queda por debajo de 0,85, en la zona de sobredimensionamiento. Esto es coherente con operar en el extremo inferior del rango de capacidad comercial del fabricante (6 a 10 paneles) y brinda un margen de seguridad adicional en el eje de elevación. 

Para la condición de reposo (stow position, 90°), el momento diferencial no aplica de igual manera dado que la presión de diseño en esa condición actúa de forma uniforme sobre una superficie prácticamente simétrica respecto del eje de elevación; el mantenimiento de la posición en esa condición se resuelve mediante el torque de retención del propio mecanismo. Por otra parte, es necesario conocer si en esta posición se vence el torque producido por el peso propio del sistema, para lo cual en primera instancia se determina el centro de gravedad de los elementos que está moviendo el sistema: 



<!-- Start of picture text -->
Bewsaae enna 3 crc ropa x<br>Genes! Rene Porte Ete Pendins God Pons ae<br>ect]<br>corn Prema tte ==<br>oni(ini greelaiBees) fee ae(Cn Ande CORD<br>ae ERB xCenc[OREMpind|Err!<br>one [TOD| [OR ere<br>\enan [ROE<br>dc<br>Pra e! 7 Ro!<br>an ertfaci[Sineoeoss|recei2 [OROEHS!= p Sa(PRENEOS<br>(eter) ny [OMe Ererd me (AR Erer|<br><!-- End of picture text -->

_Figura 4.1 – Centro de gravedad respecto al centro del eje del actuador SVH7_ 

33 

_Sistema fotovoltaico con seguidor solar biaxial_ 



_Figura 4.2 – Posición del SCU, respecto al origen_ 

|En base a ello, se tiene que<br>que la carga total de las viga<br><br>|el centro de gra<br>s y de los panele<br><br>|vedad se encuentra<br>s es de 4,75 kN.<br> <br>|a 138 mm (0,138 m<br> <br>|) y además se tiene<br> <br>|
|---|---|---|---|---|
|**Elemento**<br>|**Cantidad**<br>|**Masa unitaria**<br>|**Masa total**<br>|**Carga vertical**<br>|
|Panel fotovoltaico<br>|8<br>|32,4 kg<br>|260 kg<br>|2,55 kN<br>|
|Vigas secundarias<br>|5<br>|16 kg<br>|80 kg<br>|0,79 kN<br>|
|Viga principal<br>|1<br>|144 kg<br>|144 kg<br>|1,41 kN<br>|
|TOTAL CONOCIDO<br>|||484 kg<br>|4,75 kN<br>|



Calculado el torque total requerido para salir de la _stow position_ es: 



Comparando contra el torque de salida nominal del SVH7 (937 N·m), y aplicando un índice de aprovechamiento I = solicitación/admisible: 



Para este caso, el índice también queda por debajo de 0,85, confirmando que el accionamiento se encuentra sobredimensionado frente al torque requerido para salir de la posición de reposo por peso propio, de forma consistente con el resultado obtenido para la condición de viento en 4.4. 

## **4.5 Cálculo del sistema de azimut** 

El eje de azimut (rotación sobre el plano horizontal) se acciona mediante la segunda salida del SVH7. A diferencia del eje de elevación, la diferencia de presión barlovento/sotavento de CIRSOC actúa sobre el eje horizontal de elevación, no sobre el eje vertical de azimut; el requerimiento de torque en este eje está gobernado principalmente por la inercia rotacional y la fricción del sistema, dado que un montaje balanceado respecto del eje vertical minimiza el momento estático de viento. 

34 

_Sistema fotovoltaico con seguidor solar biaxial_ 

### **_4.5.1 Torque de inercia_** 

Aproximando el conjunto móvil (paneles + estructura secundaria + SVH7) como un cuerpo esbelto de masa total y longitud característica L = 4,60 m (Capítulo 3): 

_m_total = 259,2 + 80,5 + 144,2 + 85 = 568,8 kg   (paneles + vigas secundarias + viga principal + SVH7)_ 



Con velocidad de salida nominal del SVH7 de 0,042 rpm (ω = 0,0044 rad/s) alcanzada en un arranque suave de 5 s: 





El torque de inercia resulta despreciable frente al torque nominal del accionamiento, confirmando que, a las velocidades de trabajo extremadamente bajas propias de un slewing drive (0,042 rpm), el dimensionamiento está gobernado por cargas estáticas y de fricción, no por la dinámica rotacional (Budynas & Nisbett, 2020). 

### **_4.5.2 Torque de fricción y margen de diseño_** 

Adoptando un torque de fricción del rodamiento de giro estimado en un 4 % del torque de retención nominal (valor típico de fricción interna en rodamientos de giro de gran diámetro, Budynas & Nisbett, 2020) y un torque residual por desalineación aerodinámica estimado conservadoramente en un 10 % del torque de elevación calculado en 4.4: 





_T_azimut,requerido = T_fricción + T_desalineación + T_inercia = 416 + 57,9 + 0,9 = 474,8 N·m_ 



El índice de aprovechamiento (0,51) confirma que el eje de azimut opera con holgura respecto de su capacidad nominal, resultado esperado para un mecanismo cuyo momento de viento dominante actúa sobre el eje perpendicular (elevación). 

## **4.6 Cálculo del sistema de frenos** 

El SVH7 emplea un mecanismo de tornillo sinfín con relación de transmisión 71:1. Un engranaje de tornillo sinfín es autoblocante (self-locking) cuando el ángulo de avance (lead angle, λ) del tornillo es menor que el ángulo de fricción del par de materiales (λ < arctan μ), condición típica de relaciones de reducción elevadas como la del SVH7 (Budynas & Nisbett, 2020, Cap. 13). Para un par acero-bronce lubricado (μ ≈ 0,05–0,10) y el ángulo de avance característico de una reducción 71:1 (λ < 5°, por lo que tan λ < 0,09), se verifica la condición de autobloqueo, lo cual es consistente con el torque de retención especificado por el fabricante (10,4 kN·m) sin consumo de energía en reposo. 

35 

_Sistema fotovoltaico con seguidor solar biaxial_ 

Se verifica la suficiencia de esta función de frenado mecánico frente al requerimiento de mantenimiento de posición en la condición más desfavorable, aplicando un factor de servicio de 1,25 (carga variable con impacto leve, Budynas & Nisbett, 2020) sobre el torque de elevación calculado en 4.4: 

_T_frenado,requerido = 1,25 × 579,1 N·m = 723,9 N·m_ 



El autobloqueo del tornillo sinfín, con un índice de aprovechamiento de apenas 0,070, resulta ampliamente suficiente como freno mecánico primario. En consecuencia, no se requiere incorporar un freno electromecánico adicional en el eje de elevación; sí se recomienda, como práctica de seguridad, que el sistema de control (DomBusTracker2) lleve el arreglo a la posición de bandera (stow, Sección 4.9) antes de que la velocidad de viento supere el umbral operativo de 20 m/s establecido en el Capítulo 3, minimizando así los ciclos de trabajo del mecanismo bajo carga elevada. 

### **_4.6.1 Justificación de la no necesidad de un dispositivo de seguridad adicional_** 

De acuerdo con el análisis desarrollado en esta sección, el actuador SVH7 no requiere de ningún dispositivo de seguridad adicional (freno electromecánico secundario, retenedor mecánico, sistema de bloqueo auxiliar, etc.) para prevenir una caída brusca o incontrolada del arreglo de paneles ante una eventual pérdida de energía o falla del sistema de control. Esta conclusión se sustenta en las siguientes características del actuador: 

- Autobloqueo mecánico inherente: el mecanismo de tornillo sinfín del SVH7, con relación de transmisión 71:1, cumple la condición de autobloqueo (λ < arctan μ) descrita en esta sección, lo que significa que la carga de salida (el peso del arreglo de paneles y el momento inducido por el viento) no puede retroaccionar sobre el motor ni hacer girar el mecanismo en sentido inverso, incluso en ausencia total de energía eléctrica. Se trata de una propiedad geométrica del engranaje, no de una función activa dependiente de electrónica, resortes o frenos de fricción, por lo que no se degrada por corte de energía, falla del sistema de control o falta de mantenimiento de un componente eléctrico adicional. 

- Margen amplio de capacidad de retención: el torque de retención especificado por el fabricante (10,4 kN·m) resulta muy superior al torque máximo requerido para mantener la posición del arreglo bajo la condición de viento más desfavorable (723,9 N·m), con un índice de aprovechamiento de apenas 0,070 — es decir, el actuador trabaja al 7,0% de su capacidad de retención, dejando un margen superior a 14 veces el requerimiento real. 

- Redundancia entre ejes: tanto el eje de elevación como el eje de azimut emplean el mismo tipo de accionamiento por tornillo sinfín autoblocante (Secciones 4.4 y 4.5), por lo que ambos grados de libertad del mecanismo quedan bloqueados de forma pasiva y simultánea, sin depender de un sistema de frenado centralizado único cuya falla comprometería ambos ejes a la vez. 

- Tecnología de uso comercial probado para seguidores solares: el SVH7 es un actuador de tipo slewing drive de doble eje, diseñado específicamente para aplicaciones de seguimiento solar fotovoltaico (Coresun Drive Equipment Changzhou Co., Ltd., s. f.), tecnología de uso extendido en la industria, en la cual el autobloqueo del tornillo sinfín —y no un freno mecánico separado— constituye el mecanismo estándar de retención de posición. 

En conjunto, estas características permiten prescindir de un dispositivo de seguridad adicional dedicado a evitar la caída brusca de los paneles: la función de retención de posición queda resuelta de forma pasiva, 

36 

_Sistema fotovoltaico con seguidor solar biaxial_ 

redundante entre ejes y con un margen de seguridad amplio, como consecuencia directa del principio de funcionamiento del actuador seleccionado. 

37 

_Sistema fotovoltaico con seguidor solar biaxial_ 

## **4.7 Análisis cinemático** 

El seguidor solar biaxial se modela como un mecanismo serial de dos grados de libertad (2 GDL): una articulación rotacional de azimut (eje vertical, sobre la columna) seguida de una articulación rotacional de elevación (eje horizontal, sobre la viga principal), empleando la convención de Denavit-Hartenberg (D-H) descripta por Craig (2005). 

### **_4.7.1 Parámetros D-H_** 

|**Eslabón i**|**aᵢ (m)**|**αᵢ**|**dᵢ (m)**|**θᵢ**|
|---|---|---|---|---|
|1 (azimut)|0|90°|3,00 (altura de columna)|θ1<br>(variable,<br>0–360°)|
|2 (elevación)|2,30 (L/2, brazo de viga<br>principal)|0°|0|θ2<br>(variable,<br>0–90°)|



Donde θ1 es el ángulo de azimut medido desde una referencia norte-sur, y θ2 es el ángulo de elevación medido desde la horizontal (0° = panel horizontal, 90° = stow/posición vertical de seguridad, coherente con las posiciones analizadas en el Capítulo 3). 

### **_4.7.2 Cinemática directa_** 

La matriz de transformación homogénea entre el sistema de referencia fijo (base de la columna) y el sistema solidario al panel se obtiene como el producto de las transformaciones elementales de cada articulación (Craig, 2005): 



A partir de esta transformación se obtiene el vector normal al plano del panel (dirección de apuntamiento) en función de los dos ángulos articulares, lo que permite verificar en todo momento la orientación real del arreglo respecto de la posición solar calculada por el algoritmo de seguimiento. 

### **_4.7.3 Cinemática inversa_** 

Dada la posición solar instantánea, expresada por su azimut solar γs y su elevación (altura solar) αs — obtenidos por un algoritmo de posición solar externo al alcance de este documento—, la cinemática inversa del mecanismo de dos ejes, al no existir desplazamiento (offset) entre los ejes de azimut y elevación, admite solución cerrada directa: 



Este resultado es el habitual para seguidores de dos ejes sin desplazamiento entre articulaciones (Craig, 2005) y es el que debe programarse en la lógica de control del DomBusTracker2 para el modo de seguimiento automático descripto en el Capítulo 2. 

## **4.8 Definición de entradas y salidas del PLC** 

38 

_Sistema fotovoltaico con seguidor solar biaxial_ 

Si bien el control del seguidor se implementa físicamente sobre el controlador dedicado Creasol DomBusTracker2 (Capítulo 2), su arquitectura de entradas y salidas se documenta a continuación siguiendo la metodología estándar de definición de E/S para controladores lógicos programables (Bolton, 2015), de manera que la lógica de control (Sección 4.9) resulte trazable e independiente del hardware específico. 

### **_4.8.1 Entradas digitales (DI)_** 

|**Dirección**|**Señal**|**Descripción**|
|---|---|---|
|I0.0|Fin de carrera Norte (elevación)|Sensor de proximidad NPN, posición<br>máxima de elevación|
|I0.1|Fin de carrera Sur (elevación)|Sensor de proximidad NPN, posición<br>mínima de elevación|
|I0.2|Fin de carrera Este (azimut)|Sensor de proximidad NPN, límite de<br>giro este|
|I0.3|Fin de carrera Oeste (azimut)|Sensor de proximidad NPN, límite de<br>giro oeste|
|I0.4|Pulsador manual elevación +|Mando manual local|
|I0.5|Pulsador manual elevación −|Mando manual local|
|I0.6|Pulsador manual azimut +|Mando manual local|
|I0.7|Pulsador manual azimut −|Mando manual local|
|I1.0|Selector Manual/Automático|Conmutador de modo de operación|
|I1.1|Alarma de viento (umbral superado)|Señal derivada del anemómetro<br>analógico (comparador)|



### **_4.8.2 Entradas analógicas (AI)_** 

|**Dirección**|**Señal**|**Rango**|
|---|---|---|
|AI0|Anemómetro (velocidad de viento)|3–5 V (según Capítulo 2)|
|AI1|Sensor de luz — eje Norte/Sur|0–10 V (sensor de luz<br>impermeable, DomBusTracker2)|
|AI2|Sensor de luz — eje Este/Oeste|0–10 V|



### **_4.8.3 Salidas digitales (DO)_** 

|**Dirección**|**Señal**|**Descripción**|
|---|---|---|
|Q0.0|Relé RL1 — Elevación +|Activación de actuador de elevación, sentido<br>positivo|



39 

_Sistema fotovoltaico con seguidor solar biaxial_ 

|**Dirección**|**Señal**|**Descripción**|
|---|---|---|
|Q0.1|Relé RL2 — Elevación −|Activación de actuador de elevación, sentido<br>negativo|
|Q0.2|Relé RL3 — Azimut +|Activación de actuador de azimut, sentido positivo|
|Q0.3|Relé RL4 — Azimut −|Activación de actuador de azimut, sentido negativo|
|Q0.4|Relé RL5 (propósito general)|Zumbador activo 24 V / señalización|
|Q0.5|Relé RL6 (propósito general)|Reserva / alarma remota|



El direccionamiento presentado sigue la convención genérica IEC 61131-3 (Bolton, 2015) y es directamente trasladable a los cuatro bornes de relé y las entradas de sensor de posición NPN disponibles físicamente en el Creasol DomBusTracker2 (Capítulo 2, Figura 2.4). 

## **4.9 Lógica de control y posición de bandera** 

Se denomina posición de bandera (o stow position, ya introducida en el Capítulo 2) a la orientación de seguridad en la cual el panel se coloca verticalmente (θ2 = 90°) y alineado con la dirección predominante del viento, ofreciendo la mínima superficie de resistencia aerodinámica, de forma análoga a una bandera que se orienta libremente según la dirección del viento en lugar de oponer su cara plana a la ráfaga. Esta es la condición de carga de 770,4 N/m² empleada en el Capítulo 3 para el dimensionamiento estructural. 

### **_4.9.1 Diagrama de estados_** 

El sistema de control opera bajo cuatro estados posibles, con transiciones gobernadas por las entradas digitales y analógicas definidas en 4.8: 

- Estado 0 — Reposo/Inicialización: a la energización, el sistema verifica los finales de carrera (I0.0–I0.3) y homologa la posición conocida antes de habilitar el seguimiento. 

- Estado 1 — Seguimiento automático: con el selector en modo Automático (I1.0 = 1) y sin alarma de viento (I1.1 = 0), el controlador calcula (θ1, θ2) por cinemática inversa (Sección 4.7.3) a partir de la posición solar y activa las salidas Q0.0–Q0.3 según corresponda hasta que los sensores de luz (AI1, AI2) indiquen equilibrio de iluminación entre cuadrantes. 

- Estado 2 — Posición de bandera (stow): si la velocidad de viento medida por el anemómetro (AI0) supera el umbral operativo de 20 m/s (Capítulo 3), la lógica de control interrumpe el seguimiento automático y ejecuta la secuencia de emplazamiento a θ2 = 90°, independientemente del estado del selector manual/automático, permaneciendo en este estado mientras persista la condición de alarma (I1.1 = 1) más un retardo de seguridad tras el cese de la alarma. 

- Estado 3 — Modo manual: con el selector en Manual (I1.0 = 0), las entradas de pulsadores (I0.4– I0.7) accionan directamente las salidas correspondientes, con enclavamiento por los finales de carrera (I0.0–I0.3) que impide sobrepasar los límites mecánicos del mecanismo en cualquier modo de operación. 

### **_4.9.2 Enclavamientos de seguridad_** 

40 

_Sistema fotovoltaico con seguidor solar biaxial_ 

Independientemente del estado activo, la lógica implementa los siguientes enclavamientos, consistentes con las buenas prácticas de diseño de control secuencial (Bolton, 2015): 

- El estado de posición de bandera (Estado 2) tiene prioridad absoluta sobre el seguimiento automático y el modo manual (enclavamiento de máxima prioridad ante alarma de viento). 

- Ninguna salida de accionamiento (Q0.0–Q0.3) puede activarse si el final de carrera correspondiente al sentido de movimiento solicitado se encuentra accionado (I0.0–I0.3), independientemente del estado o modo de operación. 

- Las salidas de un mismo eje en sentidos opuestos (p. ej. Q0.0 y Q0.1) son mutuamente excluyentes por enclavamiento lógico, evitando la activación simultánea de ambos sentidos de un mismo actuador. 

- Al recuperarse la condición normal de viento tras un evento de stow, el sistema retorna automáticamente al Estado 1 (seguimiento) solo si el selector permanece en modo Automático, evitando reinicios no supervisados en modo manual. 

41 

_Sistema fotovoltaico con seguidor solar biaxial_ 

# **5. Conclusiones y resumen de componentes seleccionados** 

A partir del análisis de cargas gravitacionales y de viento, y de la aplicación del método de esfuerzos permisibles (A.S.D.), se seleccionaron los siguientes perfiles estructurales para el seguidor solar biaxial de 8 paneles: 

|**Elemento**|**Perfil / material seleccionado**|**Índice de**<br>**aprovechamiento (I)**|
|---|---|---|
|Viga secundaria|Perfil G 100x50x15x2 – Acero ASTM A-36|0,34<br>(sobredimensionado)|
|Viga principal|Perfil HSS 5 x 0,375 – Acero ASTM A 500 Grado C|0,70<br>(sobredimensionado)|
|Columna|Perfil W8 x 24 – Acero ASTM A-588|0,13<br>(sobredimensionado)|
|Placa base|25 x 25 x 2 cm – Acero A588 Grado C|—|
|Perno de anclaje|1 pulg, ISO 8.8|—|
|Soldadura columna–placa|Electrodo E8013, L ≥ 126 mm|—|
|Sistema de elevación|Torque SVH7 937 N·m|0,62<br>(sobredimensionado)|
|Sistema de azimut|Torque SVH7 937 N·m|0,51 (con holgura)|
|Frenado (autobloqueo tornillo sinfín)|Torque de retención 10,4 kN·m|0,070 (amplio<br>margen)|



Las cargas de viento críticas resultaron determinantes en el diseño: 724 N/m² en posición de trabajo (45° a barlovento, viento de 20 m/s) y 770,4 N/m² en posición de seguridad o stow position (90°, viento de 50 m/s). Todos los elementos estructurales seleccionados presentan índices de aprovechamiento inferiores a 0,85 en los componentes principales, lo que indica que el sistema se encuentra sobredimensionado según el criterio A.I.S.C., incluido el sistema de elevación (I = 0,62), que en la configuración de 10 paneles operaba con un margen más ajustado y ahora, con 8 paneles, gana margen adicional, coherente con operar en el extremo inferior del rango de capacidad comercial del fabricante (6 a 10 paneles). 

En cuanto a los dispositivos electrónicos, el sistema integra un mecanismo de doble eje (SVH7) gobernado por un controlador dedicado (Creasol DomBusTracker2) con protección automática ante viento excesivo, y una arquitectura de comunicación RS485 → Wi-Fi/Ethernet que permite el monitoreo remoto en tiempo real mediante la plataforma Domoticz. El capítulo 4 amplió esta ingeniería con el dimensionamiento eléctrico (conductores, protecciones, puesta a tierra y canalizaciones), la verificación mecánica de los subsistemas de elevación, azimut y frenado, el análisis cinemático del mecanismo de dos grados de libertad, y la definición de entradas/salidas y lógica de control, incluyendo la posición de bandera ante viento excesivo. 

Como se estableció en el Capítulo 1, todo lo anterior corresponde al módulo unitario repetitivo del proyecto: un seguidor de 8 paneles (5,2 kWp) que se replica aproximadamente 1539 veces a lo largo del predio para alcanzar la potencia objetivo de la planta (8 MW). La red de colección de media tensión, las estaciones inversoras y la subestación de interconexión de la planta completa, así como la malla de puesta 

42 

_Sistema fotovoltaico con seguidor solar biaxial_ 

a tierra a nivel de subestación (IEEE Std 80-2013), constituyen etapas de ingeniería de balance de planta (BOP) adicionales, no desarrolladas en el presente documento. 

43 

_Sistema fotovoltaico con seguidor solar biaxial_ 

44 

_Sistema fotovoltaico con seguidor solar biaxial_ 

# **6. Validación numérica computacional del modelo estructural** 

## **6.1 Introducción y marco conceptual** 

Además de los cálculos analíticos desarrollados en los Capítulos 3 y 4 — basados en fórmulas clásicas de resistencia de materiales aplicadas manualmente a cada elemento por separado — se realizó una verificación numérica independiente del comportamiento estructural del seguidor solar, mediante simulación computacional. Esta verificación adicional permite contrastar los resultados obtenidos por ambos caminos (el cálculo analítico y la simulación digital) y detectar posibles inconsistencias que un modelo simplificado, calculado a mano, podría no capturar por sí solo. Esta práctica es habitual en la ingeniería estructural moderna (Logan, 2022). 

La herramienta empleada para esta verificación es el Método de los Elementos Finitos (MEF), una técnica numérica que consiste en dividir una estructura continua — en este caso, el conjunto de vigas, columna y diagonales del seguidor — en una gran cantidad de elementos pequeños e interconectados entre sí. El software resuelve, de forma simultánea, las ecuaciones de equilibrio de fuerzas y deformaciones en cada uno de esos elementos, y compone con ellas el comportamiento del conjunto completo bajo las cargas aplicadas (Logan, 2022). En términos simples, en lugar de calcular una sola viga aislada como se hizo en el Capítulo 3, el MEF calcula todas las piezas de la estructura a la vez, considerando cómo se transmiten las cargas entre ellas a través de sus conexiones reales. 

Dentro de esta verificación numérica se realizaron dos tipos de estudio, complementarios entre sí: 

1) Un análisis estático de tensiones, que aplica las cargas de peso propio y viento sobre el modelo y determina los esfuerzos (tensión normal, corte y torsión) y los desplazamientos resultantes en cada punto de la estructura, para verificar que ningún elemento supere su capacidad resistente. 

2) Un análisis modal, que no aplica ninguna carga externa, sino que determina las frecuencias naturales de vibración de la estructura — es decir, las frecuencias a las que la estructura tiende a vibrar por sí sola si se le da un impulso — y la forma en que se deforma en cada una de ellas (su "modo de vibración") (Chopra, 2017). Este análisis es relevante porque el viento no sopla de forma perfectamente constante: al pasar alrededor de un elemento cilíndrico o tubular, el aire se desprende en pequeños remolinos alternados (vórtices) a una frecuencia que depende de la velocidad del viento y del diámetro del elemento — fenómeno conocido como desprendimiento de vórtices (vortex shedding). Si esa frecuencia de excitación coincide con una frecuencia natural de la estructura, se produce un fenómeno de resonancia que puede amplificar peligrosamente las vibraciones (Blevins, 2001; CEN, 2005). Por eso, conocer las frecuencias naturales de la estructura permite verificar que estén suficientemente alejadas de las frecuencias de excitación esperadas por el viento. 

## **6.2 Modelado geométrico en Autodesk Inventor** 

Antes de poder realizar cualquiera de los dos análisis descritos en la sección anterior, fue necesario construir un modelo tridimensional (3D) completo del seguidor solar, en el que cada elemento estructural — vigas secundarias, viga principal, columna, diagonales de refuerzo, placa base y el actuador de elevación SVH7 — se representa con su perfil, sus dimensiones reales y el material que le corresponde según lo definido en el Capítulo 3. Este modelado se realizó en el software Autodesk Inventor (Autodesk, 2024), específicamente en su entorno de "Análisis de estructura" (Frame Analysis), que permite definir los elementos como vigas conectadas entre sí mediante nodos, vínculos rígidos y restricciones de apoyo, en lugar de tratarlos como sólidos macizos. 

45 

_Sistema fotovoltaico con seguidor solar biaxial_ 

Este modelo geométrico es la base indispensable sobre la cual se ejecutan tanto el análisis estático de tensiones como el análisis modal presentados en las secciones siguientes: sin una geometría, unos materiales y unas condiciones de apoyo correctamente definidos en el software, ninguno de los dos estudios puede realizarse ni sus resultados pueden considerarse representativos del diseño real. La columna se definió empotrada en su base (restricción de desplazamiento y giro nulos), replicando la condición de fundación descrita en la Sección 3.6. 



_Figura 6.1 – Modelo tridimensional del seguidor solar de 8 paneles en Autodesk Inventor, vista de la estructura de soporte con el actuador de elevación SVH7 (fuente propia)_ 

46 

_Sistema fotovoltaico con seguidor solar biaxial_ 



<!-- Start of picture text -->
We<br><!-- End of picture text -->

_Figura 6.2 – Modelo tridimensional del seguidor solar con el arreglo de 8 paneles fotovoltaicos incorporado, vista en posición de trabajo (fuente propia)_ 

## **6.3 Análisis modal (frecuencias naturales de la estructura)** 

|Sobre el modelo de<br>la columna empotr<br>orden creciente, ju<br><br>|scrito en la Sección 6.2 s<br>ada en su base. El soft<br>nto con la forma de vibr<br> <br>|e ejecutó un estudio modal, sin cargas externas aplicadas, con<br>ware extrae las primeras frecuencias naturales del sistema en<br>ación (modo) asociada a cada una.<br> <br>|
|---|---|---|
|**Modo**<br>|**Frecuencia (Hz)**<br>|**Naturaleza del modo**<br>|
|F1<br>|5,363<br>|Global — participación coordinada de columna, viga principal y<br>brazos<br>|
|F2<br>|6,775<br>|Local — vibración aislada de una diagonal de refuerzo<br>|
|F3<br>|6,794<br>|Local — vibración aislada de una diagonal de refuerzo<br>|
|F4<br>|7,158<br>|Local — vibración aislada de una diagonal de refuerzo<br>|
|F5<br>|7,160<br>|Local — vibración aislada de una diagonal de refuerzo<br>|
|F6<br>|7,212<br>|Local — vibración aislada de una diagonal de refuerzo<br>|
|||47|



_Sistema fotovoltaico con seguidor solar biaxial_ 

|**Modo**|**Frecuencia (Hz)**|**Naturaleza del modo**|
|---|---|---|
|F7|8,921|Global — segundo modo, participación conjunta de la estructura|
|F8|10,920|Local — vibración aislada de una diagonal de refuerzo|



Los modos calificados como "locales" corresponden a la vibración de una sola barra diagonal, esbelta y de baja rigidez individual, sin que el resto de la estructura participe de forma apreciable — un comportamiento esperable en elementos secundarios de refuerzo y que no compromete la respuesta global del sistema. Los modos F1 y F7, en cambio, muestran participación coordinada de la columna, la viga principal y los brazos del arreglo, por lo que se consideran los modos globales de la estructura. El primer modo global, F1 = 5,363 Hz, es el valor de referencia empleado para la verificación de resonancia por viento de la siguiente sección. 



_Figura 6.3 – Primer modo global de vibración de la estructura (F1 = 5,363 Hz), obtenido mediante análisis modal en Autodesk Inventor (fuente propia)_ 

### **_6.3.1 Verificación de resonancia por desprendimiento de vórtices_** 

Con la frecuencia natural global obtenida (f ₙ = 5,363 Hz) se verificó la posibilidad de resonancia por desprendimiento de vórtices sobre la viga principal (perfil HSS 5 x 0,375, diámetro exterior D = 127 mm), empleando la relación de Strouhal (Blevins, 2001): 

#### **f = St · V / D** 

48 

_Sistema fotovoltaico con seguidor solar biaxial_ 

donde St = 0,2 (número de Strouhal, típico de secciones circulares en régimen subcrítico) y V = 20 m/s (velocidad de viento de diseño en posición de trabajo, definida en la Sección 3.2.1). Con estos valores, la frecuencia de desprendimiento de vórtices a la velocidad de diseño resulta: 

#### **f = 0,2 × 20 / 0,127 = 31,50 Hz** 

A la velocidad de viento de diseño (V = 20 m/s), la frecuencia de desprendimiento de vórtices de la viga principal (31,50 Hz) se encuentra ampliamente separada del primer modo global de la estructura (5,363 Hz) — una diferencia de más de 5 veces entre ambas frecuencias. Por lo tanto, no existe riesgo de acoplamiento dinámico ni de resonancia bajo la condición de carga de diseño, conforme al criterio de separación de frecuencias del Anexo E de la norma EN 1991-1-4 (CEN, 2005), confirmando que la estructura posee la rigidez y separación de frecuencias necesarias para operar de forma segura frente a este fenómeno en su condición operativa normal. Se deja como verificación complementaria el comportamiento del sistema ante vientos de baja intensidad, fuera del alcance de este análisis. 

## **6.4 Análisis estático de tensiones (validación por elementos finitos)** 

Sobre el mismo modelo se aplicó el caso de carga de peso propio más viento a 45° en posición de trabajo (desarrollado analíticamente en el Capítulo 3, con qw = 770,4 N/m² conforme a CIRSOC 102-2025), con la columna empotrada en su base. Los resultados se evaluaron con el método de tensiones admisibles (Allowable Stress Design, ASD), definiendo el índice de aprovechamiento I = f / F_admisible, donde f es la tensión obtenida por el software y F_admisible es la tensión de fluencia del material dividida por un factor de seguridad FS = 1,66 (Budynas & Nisbett, 2020; American Institute of Steel Construction [AISC], 1989). Un índice I menor a 0,85 indica un elemento sobredimensionado; entre 0,85 y 1,1, un aprovechamiento adecuado; y mayor a 1,1, una condición de falla. 

Se evaluaron cuatro resultados independientes: el desplazamiento máximo de la estructura, la tensión normal máxima (Smax), la tensión de corte máxima (Ty) y la tensión de torsión máxima (T). 

|**Resultado**|**Valor máximo**|**Ubicación / criterio**|**Índice / verificación**|
|---|---|---|---|
|Desplazamiento|10,11 mm|Extremo del brazo lateral|76,4% de L/180 (cumple) —<br>101,9% de L/240|
|Tensión normal (Smax)|89,74 MPa|Base de la columna (ASTM A-500 Gr.<br>C)|I = 0,432 (cumple)|
|Tensión de corte (Ty)|11,78 MPa|Base de la columna (ASTM A-588)|I = 0,098 (cumple)|
|Tensión de torsión (T)|1,032 MPa|Viga principal (ASTM A-500 Gr. C)|I = 0,0086 (cumple)|



El desplazamiento máximo obtenido (10,11 mm) cumple el criterio estructural de deflexión L/180 (13,23 mm, 76,4% de utilización), aunque supera el criterio de servicio más estricto L/240 (9,93 mm), orientado a limitar la desviación óptica del seguimiento solar bajo la carga de viento de diseño. 

49 

_Sistema fotovoltaico con seguidor solar biaxial_ 



_Figura 6.4 – Distribución de desplazamiento bajo el caso de carga de peso propio y viento a 45°, obtenida mediante análisis por elementos finitos en Autodesk Inventor (fuente propia)_ 



50 

_Sistema fotovoltaico con seguidor solar biaxial_ 

_Figura 6.5 – Distribución de tensión normal máxima (Smax) bajo el caso de carga de peso propio y viento a 45°, obtenida mediante análisis por elementos finitos en Autodesk Inventor (fuente propia)_ 



_Figura 6.6 – Distribución de tensión de corte máxima (Ty) bajo el mismo caso de carga (fuente propia)_ 

51 

_Sistema fotovoltaico con seguidor solar biaxial_ 



_Figura 6.7 – Distribución de tensión de torsión máxima (T) bajo el mismo caso de carga (fuente propia)_ 

De los tres componentes de tensión evaluados, la tensión normal (Smax) resulta la más exigida, con un índice de aprovechamiento de 0,432 — es decir, la estructura trabaja al 43,2% de su capacidad admisible bajo el caso de carga analizado, mientras que el corte y la torsión presentan márgenes considerablemente mayores. 

## **6.5 Síntesis de la validación numérica** 

Los resultados obtenidos mediante el análisis por elementos finitos en Autodesk Inventor son consistentes con los resultados del cálculo analítico desarrollado en el Capítulo 3 para los mismos elementos (viga principal, columna y viga secundaria): ambos caminos de cálculo — el analítico, basado en fórmulas de resistencia de materiales aplicadas manualmente, y el numérico, basado en la simulación computacional del conjunto completo — coinciden en identificar a la estructura como adecuadamente dimensionada bajo el caso de carga de viento a 45°, con la salvedad del criterio de servicio L/240, que queda señalado como punto de atención para una eventual revisión de rigidez del brazo del seguidor. Esta convergencia entre ambos métodos aporta un nivel adicional de confianza sobre la validez del diseño estructural presentado en este documento. 

# **7. Referencias bibliográficas** 

## **7.1 Normativa** 

52 

_Sistema fotovoltaico con seguidor solar biaxial_ 

Reglamento CIRSOC 102-2025: Reglamento Argentino de Acción del Viento sobre las Construcciones. Secretaría de Obras Públicas. 

Asociación Electrotécnica Argentina. (2006). Reglamentación para la ejecución de instalaciones eléctricas en inmuebles (AEA 90364). AEA. 

Asociación Electrotécnica Argentina. (2015). Reglamentación para la ejecución de instalaciones eléctricas en inmuebles, Parte 7, Sección 712: Sistemas de suministro de energía mediante paneles solares fotovoltaicos (AEA 90364-7-712). AEA. 

IEEE. (2007). IEEE Recommended Practice for Grounding of Industrial and Commercial Power Systems (IEEE Std 142-2007). IEEE. 

IEEE. (2013). IEEE Guide for Safety in AC Substation Grounding (IEEE Std 80-2013). IEEE. 

Instituto Argentino de Normalización y Certificación. (s. f.). IRAM 2183: Conductores de cobre aislados con PVC para instalaciones fijas. IRAM. 

Instituto Argentino de Normalización y Certificación. (s. f.). IRAM 2206-3: Caños de policloruro de vinilo (PVC) rígido para instalaciones eléctricas. IRAM. 

CENELEC. (2014). EN 50618: Electric cables for photovoltaic systems. CENELEC. 

## **7.2 Bibliografía técnica (mecánica, control y robótica)** 

Budynas, R. G., & Nisbett, J. K. (2020). Shigley's Mechanical Engineering Design (11.ª ed.). McGraw-Hill Education. 

Craig, J. J. (2005). Introduction to Robotics: Mechanics and Control (3.ª ed.). Pearson/Prentice Hall. 

Bolton, W. (2015). Programmable Logic Controllers (6.ª ed.). Newnes. 

ASTM International. (2017). ASTM A123/A123M-17: Standard Specification for Zinc (Hot-Dip Galvanized) Coatings on Iron and Steel Products. ASTM International. 

International Organization for Standardization. (2009). ISO 1461:2009: Hot dip galvanized coatings on fabricated iron and steel articles — Specifications and test methods. ISO. 

Asociación Americana de Galvanizado [American Galvanizers Association]. (2021). Hot-Dip Galvanizing for Corrosion Prevention: A Specifier’s Guide. AGA. 

## **7.3 Fuentes técnicas y comerciales** 

Relight Energy. (s. f.). Jinko N Type Panel Solar Monocristalino 650W 625W 630W 635W N Type Photovoltaic Panels. Made-in-China.com. 

Jinko Solar Co., Ltd. (2024). JKM625-650N-66HL4M-BDV-Z1 [Ficha técnica de producto]. 

Coresun Drive Equipment Changzhou Co., Ltd. (s. f.). Dual Axis Gear Motor SVH7 Slewing Drive for Solar Tracker. Made-in-China.com. 

Creasol. (s. f.). Creasol DomBusTracker2: Single/Dual axis solar tracker controller Rev.2. 

Creasol. (2026). How to build a domotic system using DomBus modules. Creasol Support. 

53 

_Sistema fotovoltaico con seguidor solar biaxial_ 

CreasolTech. (2026). CreasolDomBus: Domoticz plugin for Creasol DomBus electronic modules [Repositorio de GitHub]. GitHub. 

Domotuto. (2020). Cómo Domoticz puede cambiar tu vida, qué es y para qué sirve. 

National Instruments. (2025). What is the Modbus Protocol & How Does It Work? 

Jinan USR IOT Technology Limited. (2026). USR-DR404 User Manual (Version V1.0.1). 

Industriales Andes. (s. f.). Convertidor industrial USR W610 RS232/RS485 Ethernet y WiFi. 

Proactive & Innovative Automation S.A.S. (s. f.). Conversor industrial USR-DR404 RS485 a Wi-Fi/Ethernet (SSL/TLS). 

PUSR IOT. (s. f.). Configuration of Serial to WiFi Converters USR-W610 by Web-page. 

AV Electronics. (s. f.). Anemómetro – Sensor de Viento Analógico. 

HEBAI. (2024). Sensores de proximidad PNP vs NPN: Entendiendo la diferencia. 

Grupo Electrostore. (s. f.). Conversor USB a RS485. 

Amazon Web Services. (s. f.). ¿Qué es MQTT? Explicación del protocolo MQTT. 

54 

_Sistema fotovoltaico con seguidor solar biaxial_ 

## **7.4 Fuentes de validación numérica (modelado CAD, análisis por elementos finitos y vibraciones inducidas por viento)** 

Autodesk Inc. (2024). Autodesk Inventor: Frame analysis and finite element simulation environment [Software]. 

American Institute of Steel Construction. (1989). Manual of Steel Construction: Allowable Stress Design (9.ª ed.). AISC. 

Blevins, R. D. (2001). Flow-Induced Vibration (2.ª ed.). Krieger Publishing Company. 

Comité Europeo de Normalización. (2005). Eurocode 1: Actions on structures — Part 1-4: General actions — Wind actions (EN 1991-1-4:2005), Anexo E: Vortex shedding and aeroelastic instabilities. CEN. 

Chopra, A. K. (2017). Dynamics of Structures: Theory and Applications to Earthquake Engineering (5.ª ed.). Pearson. 

Logan, D. L. (2022). A First Course in the Finite Element Method (6.ª ed.). Cengage Learning. 

# **Anexos** 

A continuación se presentan las cotizaciones y fichas comerciales de los principales dispositivos especificados en el capítulo 2. 

**Anexo 1 – Cotización motor SVH7 (Coresun Drive / COIE)** 



<!-- Start of picture text -->
\ cole QUOTATION<br>XS 7 No.: Ho198-0260804<br>Date: Auth 2028<br>Coresun Drive Equipment Changzhou Co.Ltd<br>wa coreuncve.com<br>‘Ad: Tanning Distt Changzhou<br>cia 213300 ly anu PR ‘A: Puerto Mad, ProciadeChub, el Doro<br>Contact Mr Jason Huang ATIN<br>EnaTelFax: +86-519-8-510osongouesundives0s00s2688000820  com EmailTet<br>9¥7-71-40-RC-24H90100.REVA 7" Dual"wo As Uns Enclosed 24VD6 StvingMotor rive so73600 40. usozo4a000<br>Frameverk<br>High Oi Sealing<br>Precision Soliton Sea Fight oo Buenos Aes USD480.00<br>TOTAL AMOUNT usD2s6e0.00<br>CF Buenos Aires SOx20% TTTT down payment downpayment 20 Days Aer The Payment<br>By Sea RALTO40 (Gey) 2482400000<br><!-- End of picture text -->

_Anexo 1 – Quotation No. H0198-Q260804, Coresun Drive Equipment Changzhou Co., Ltd._ 

**Anexo 2 – Proforma controlador Creasol DomBusTracker2** 

55 

_Sistema fotovoltaico con seguidor solar biaxial_ 



<!-- Start of picture text -->
(31053 Pieve<br>tie di Solisof PEC: paca sbiaco@ingpc8 TsGod dest: 000000073<br>PeProforma invoice SOP/202672678 haw<br>ines SerFides Peo Mane<br>ta ot<br>== EEE<br>Te sna beatae misaraoaas EY ty Sao<br>poo reranaua ta tea ante<br>7mSar REET =e oe sere<br>a ae — ao<br>gree:Sewring sce payment Total:c= 145.43900¢)€<br>jacbinbaminies<br>svn<br><!-- End of picture text -->

_Anexo 2 – Proforma Invoice SOP/2026/2678, Creasol di Subiaco Ing. Paolo_ 

## **Anexo 3 – Ficha comercial: anemómetro** 



<!-- Start of picture text -->
Borda Detector develo de ent, agg<br>‘anemémetrode medicién de viento, repuesto i! as<br>EI2 rest Cons es —" wee<br>—————c——we a}<br>eg] eee ote<br>eT rs roSS ye BR eea “: =<br>—adecoen a<br><!-- End of picture text -->

_Anexo 3 – Anemómetro / sensor de viento analógico (referencia comercial, Amazon)_ 

## **Anexo 4 – Ficha comercial: sensor de proximidad NPN** 



<!-- Start of picture text -->
 ie——emn pe iy<br>a savor<br>ey depronmisdncoceM12 LV DAS- 2708 =<br>S)t if i normalmente(paquete de 4) abierto 4mm NPN NO de 3 cablesDC 6V-36V_ =e<br>= Detalles de envio y tarita x<br>Corde yn kes pa ist ihoneal<br><!-- End of picture text -->

_Anexo 4 – Sensor de proximidad inductivo NPN (referencia comercial, Amazon)_ 

56 

_Sistema fotovoltaico con seguidor solar biaxial_ 

## **Anexo 5 – Ficha comercial: adaptador USB a RS485** 



<!-- Start of picture text -->
w\e compatible con Multi-OS, disefio abierto. 31 cro<br>eo (© tas caen stn nee ee ptt baatial<br>. - ines | wake eer<br><!-- End of picture text -->

_Anexo 5 – Adaptador convertidor USB a RS485/RS422 (referencia comercial, Amazon)_ 

## **Anexo 6 – Ficha comercial: convertidor USR-DR404** 



<!-- Start of picture text -->
Din-Rail—_— Wi-Fi serial device: server(2°) »© 5488 to Wireless R348 Ethernet UDP TCP<br>Bidirectional Transparent transmis D erinccutne sexmcrcinartens ennage ><br>—— ==<br>9 a<br>= st<br><!-- End of picture text -->

_Anexo 6 – Din Rail USR-DR404 Serial WiFi Converter (referencia comercial, eBay)_ 

## **Anexo 7 – Ficha comercial: convertidor USR-W610** 



<!-- Start of picture text -->
Fatintatomton @ naomi Ocrmcienvani Fe 7 © |f<br>. suai ant Wes tr<br>| sn no<br>SET ee<br>=<br>ae<br><!-- End of picture text -->

57 

_Sistema fotovoltaico con seguidor solar biaxial_ 

_Anexo 7 – Serial to WiFi Ethernet Wireless Converter USR-W610 (referencia comercial, eBay)_ 

58 

