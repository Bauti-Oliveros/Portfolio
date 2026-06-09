# Laboratorio: FAWN

**Fecha:** 29 de abril de 2026
**IP objetivo:** 10.129.154.118

---

## Pasos realizados
1. Confirmé la conexión con la máquina mediante ping.
2. Escaneé los puertos abiertos con Nmap, identificando el servicio FTP en el puerto 21.
3. Verifiqué que la versión del servicio es vsftpd 3.0.3.
4. Intenté un inicio de sesión no autenticado usando el usuario `anonymous`, el cual fue aceptado por el servidor (Código 230).
5. Listé los archivos disponibles con `ls` y localicé el archivo `flag.txt`.
6. Descargué el archivo a mi máquina local con el comando `get`.
7. Leí el contenido de la flag con `cat` para finalizar el laboratorio.

## Evidencias

![Escaneo de puertos Nmap](Laboratorios_RedTeam/CTFs/Hackthebox/2_Fawn/nmap.png)

![Conexión FTP anónima](Laboratorios_RedTeam/CTFs/Hackthebox/2_Fawn/ftp.png)

![Lectura de la flag](Laboratorios_RedTeam/CTFs/Hackthebox/2_Fawn/flag.png)

---

## Vulnerabilidad identificada
El servidor FTP está mal configurado al permitir el ingreso de usuarios anónimos ("Anonymous FTP login allowed"), lo que permite el acceso a archivos compartidos sin necesidad de una cuenta válida.

## Riesgo asociado
Fuga de información sensible. En un entorno real, un atacante podría extraer logs, manuales técnicos o datos de la organización que estén almacenados en ese servidor, facilitando el mapeo de la red o la obtención de nombres de usuario.

## Controles recomendados
* Deshabilitar el acceso anónimo en la configuración del servicio FTP.
* Implementar el uso de protocolos cifrados como SFTP o FTPS para proteger los datos en tránsito y las credenciales.
* Aplicar el principio de mínimo privilegio en los directorios del servidor.

## Aprendizaje
Entendí que el protocolo FTP por sí solo es inseguro porque viaja en texto plano y que una configuración por defecto "abierta" es un riesgo crítico para la confidencialidad de los archivos de una empresa.