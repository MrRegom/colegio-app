/**
 * DigitalPersona WebService Cliente
 * Este archivo proporciona una interfaz JavaScript para interactuar con el servicio local
 * de DigitalPersona que debe estar instalado en la máquina cliente.
 */

// Namespace principal
window.DigitalPersona = (function() {
    
    // Determinar si esta reconociendo el lector de huellas
    const SIMULATION_MODE = false; // Activado temporalmente para desarrollo
    
    /**
     * Clase para interactuar con los dispositivos DigitalPersona
     */
    class Devices {
        constructor() {
            this.wsUrl = 'ws://localhost:8090';  // Servicio CORREGIDO (errores específicos solucionados)
            this.timeoutMs = 15000; // 15 segundos de timeout
            this.ws = null;
        }
        
        /**
         * Obtiene la lista de lectores de huellas conectados
         * @returns {Promise<Array>} Promesa que resuelve con la lista de lectores
         */
        getReaders() {
            return new Promise((resolve, reject) => {
                // Si estamos en modo simulación, devolver un lector simulado
                if (SIMULATION_MODE) {
                    console.log("Modo simulación activado: devolviendo lectores simulados");
                    // Mostrar una advertencia en la consola
                    console.warn("ADVERTENCIA: Usando lectores de huellas simulados para fines de desarrollo. " +
                                "Este NO es un lector real ni ofrece seguridad biométrica real.");
                    
                    // Devolver un lector simulado después de un pequeño retraso para simular la latencia de red
                    setTimeout(() => {
                        resolve([
                            new Reader({
                                id: 'simulated-1',
                                name: 'DigitalPersona 5160 (Simulado)',
                                model: 'U.are.U 5160',
                                manufacturer: 'DigitalPersona/HID Global',
                                status: 'connected'
                            })
                        ]);
                    }, 800);
                    return;
                }
                
                try {
                    // Crear la conexión WebSocket
                    this.ws = new WebSocket(this.wsUrl);
                    
                    // Establecer un timeout
                    const timeoutId = setTimeout(() => {
                        if (this.ws) {
                            this.ws.close();
                        }
                        reject(new Error('Tiempo de espera agotado al conectar con el servicio'));
                    }, this.timeoutMs);
                    
                    // Manejar errores de conexión
                    this.ws.onerror = (error) => {
                        clearTimeout(timeoutId);
                        reject(new Error('Error al conectar con el servicio de huellas: ' + (error.message || 'conexión rechazada')));
                    };
                    
                    // Manejar apertura de conexión
                    this.ws.onopen = () => {
                        // Solicitar la lista de dispositivos
                        this.ws.send(JSON.stringify({
                            command: 'getDevices'
                        }));
                    };
                    
                    // Manejar mensajes recibidos
                    this.ws.onmessage = (event) => {
                        clearTimeout(timeoutId);
                        
                        try {
                            const response = JSON.parse(event.data);
                            
                            if (response.success && response.devices) {
                                // Convertir los datos de dispositivos a objetos Reader
                                const readers = response.devices.map(device => new Reader(device));
                                
                                // Cerrar la conexión
                                this.ws.close();
                                
                                // Resolver con la lista de lectores
                                resolve(readers);
                            } else if (response.success === false) {
                                reject(new Error(response.error || 'Error desconocido al obtener los dispositivos'));
                            } else {
                                reject(new Error('Respuesta inesperada del servicio'));
                            }
                        } catch (e) {
                            reject(new Error('Error al procesar la respuesta del servicio: ' + e.message));
                        }
                    };
                } catch (e) {
                    reject(new Error('Error al inicializar la comunicación: ' + e.message));
                }
            });
        }
        
        /**
         * Captura una huella digital
         * @returns {Promise<Object>} Promesa que resuelve con los datos de la huella
         */
        captureFingerprint() {
            return new Promise((resolve, reject) => {
                // Si estamos en modo simulación, devolver datos simulados
                if (SIMULATION_MODE) {
                    console.log("Modo simulación activado: devolviendo datos de huella simulados");
                    
                    // Simular un retardo para la captura
                    setTimeout(() => {
                        // Generar una cadena base64 simulada para los datos de la huella
                        const simulatedTemplateData = generateSimulatedFingerprintData();
                        
                        resolve({
                            templateData: simulatedTemplateData,
                            quality: 85, // Calidad de 0-100
                            status: 'success'
                        });
                    }, 2500);
                    return;
                }
                
                // Implementación real
                try {
                    // Crear la conexión WebSocket
                    this.ws = new WebSocket(this.wsUrl);
                    
                    // Establecer un timeout más largo para la captura
                    const timeoutId = setTimeout(() => {
                        if (this.ws) {
                            this.ws.send(JSON.stringify({ command: 'cancelCapture' }));
                            this.ws.close();
                        }
                        reject(new Error('Tiempo de espera agotado al capturar la huella'));
                    }, 30000); // 30 segundos para la captura
                    
                    // Manejar errores de conexión
                    this.ws.onerror = (error) => {
                        clearTimeout(timeoutId);
                        reject(new Error('Error al conectar con el servicio de huellas: ' + (error.message || 'conexión rechazada')));
                    };
                    
                    // Manejar apertura de conexión
                    this.ws.onopen = () => {
                        // Iniciar la captura
                        this.ws.send(JSON.stringify({
                            command: 'captureFingerprint'
                        }));
                    };
                    
                    // Manejar mensajes recibidos
                    this.ws.onmessage = (event) => {
                        try {
                            const response = JSON.parse(event.data);
                            
                            // Si la captura se completó, resolver
                            if (response.success && response.template) {
                                clearTimeout(timeoutId);
                                this.ws.close();
                                
                                resolve({
                                    templateData: response.template,
                                    quality: response.quality || 85,
                                    status: 'success'
                                });
                            } 
                            // Si hay un error, rechazar
                            else if (response.success === false) {
                                clearTimeout(timeoutId);
                                this.ws.close();
                                
                                reject(new Error(response.error || 'Error desconocido al capturar la huella'));
                            }
                            // Otros estados no requieren acción aquí
                        } catch (e) {
                            reject(new Error('Error al procesar la respuesta del servicio: ' + e.message));
                        }
                    };
                } catch (e) {
                    reject(new Error('Error al inicializar la comunicación: ' + e.message));
                }
            });
        }
    }
    
    /**
     * Clase que representa un lector de huellas
     */
    class Reader {
        constructor(deviceInfo) {
            this.id = deviceInfo.id || '';
            this.name = deviceInfo.name || 'Lector desconocido';
            this.model = deviceInfo.model || '';
            this.manufacturer = deviceInfo.manufacturer || 'DigitalPersona';
            this.status = deviceInfo.status || 'connected';
            this.isSimulated = deviceInfo.id && deviceInfo.id.startsWith('simulated');
        }
        
        /**
         * Verifica si el lector está disponible
         * @returns {boolean} true si el lector está disponible
         */
        isAvailable() {
            return this.status === 'connected';
        }
        
        /**
         * Obtiene información del lector
         * @returns {Object} Información del dispositivo
         */
        getInfo() {
            return {
                id: this.id,
                name: this.name,
                model: this.model,
                manufacturer: this.manufacturer,
                status: this.status,
                isSimulated: this.isSimulated
            };
        }
    }
    
    /**
     * Genera datos simulados de huella digital
     * @returns {string} Cadena base64 simulada
     * @private
     */
    function generateSimulatedFingerprintData() {
        const length = 2048; // Tamaño típico de una plantilla de huella
        const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/';
        let result = '';
        
        for (let i = 0; i < length; i++) {
            result += chars.charAt(Math.floor(Math.random() * chars.length));
        }
        
        return result;
    }
    
    /**
     * Verificar disponibilidad del servicio biométrico
     * @returns {Promise<boolean>} true si el servicio está disponible
     */
    function checkServiceAvailability() {
        return new Promise((resolve, reject) => {
            try {
                const ws = new WebSocket('ws://localhost:8090');
                
                const timeout = setTimeout(() => {
                    ws.close();
                    reject(new Error('Timeout de conexión'));
                }, 3000);
                
                ws.onopen = () => {
                    ws.send(JSON.stringify({ command: 'getDevices' }));
                };
                
                ws.onmessage = (event) => {
                    try {
                        const response = JSON.parse(event.data);
                        clearTimeout(timeout);
                        ws.close();
                        
                        if (response.success && response.devices && response.devices.length > 0) {
                            console.log('INFO: Dispositivos encontrados:', response.devices);
                            resolve(true);
                        } else {
                            console.log('WARNING: No hay dispositivos disponibles');
                            resolve(false);
                        }
                    } catch (e) {
                        clearTimeout(timeout);
                        reject(new Error('Respuesta inválida'));
                    }
                };
                
                ws.onerror = (error) => {
                    clearTimeout(timeout);
                    reject(new Error('Error de conexión WebSocket'));
                };
                
            } catch (error) {
                reject(error);
            }
        });
    }

    /**
     * Verificar lectores al cargar la página
     */
    async function initializeBiometricService() {
        try {
            console.log("INFO: Verificando servicio biométrico HID Global...");
            
            const ws = new WebSocket('ws://localhost:8090');
            
            const connectionPromise = new Promise((resolve, reject) => {
                const timeout = setTimeout(() => {
                    ws.close();
                    reject(new Error('Tiempo de espera agotado'));
                }, 5000);
                
                ws.onopen = () => {
                    clearTimeout(timeout);
                    ws.send(JSON.stringify({ command: 'getDevices' }));
                };
                
                ws.onmessage = (event) => {
                    try {
                        const response = JSON.parse(event.data);
                        clearTimeout(timeout);
                        ws.close();
                        resolve(response);
                    } catch (e) {
                        reject(new Error('Respuesta inválida del servicio'));
                    }
                };
                
                ws.onerror = (error) => {
                    clearTimeout(timeout);
                    reject(new Error('Error de conexión con el servicio biométrico'));
                };
            });
            
            const result = await connectionPromise;
            
            if (result.success && result.devices && result.devices.length > 0) {
                const deviceNames = result.devices.map(d => d.name).join(", ");
                console.log("INFO: Dispositivos biométricos conectados:", deviceNames);
                
                if (window.Swal) {
                    Swal.fire({
                        icon: 'success',
                        title: 'Lector Biométrico Detectado',
                        html: `
                            <p><strong>Dispositivos disponibles:</strong></p>
                            <ul class="text-left">
                                ${result.devices.map(d => `<li>${d.name} <span class="badge bg-success">CONECTADO</span></li>`).join('')}
                            </ul>
                            <p class="text-success mt-2">Listo para capturar huellas digitales</p>
                        `,
                        confirmButtonText: 'Entendido'
                    });
                }
                return true;
            } else {
                console.log("WARNING: No se detectaron dispositivos biométricos");
                if (window.Swal) {
                    Swal.fire({
                        icon: 'warning',
                        title: 'Sin Dispositivos Biométricos',
                        text: "No se detectaron lectores de huellas. Verifique que el dispositivo esté conectado.",
                        confirmButtonText: 'Entendido'
                    });
                }
                return false;
            }
            
        } catch (e) {
            console.error("ERROR: Error al conectar con el servicio biométrico:", e);
            if (window.Swal) {
                Swal.fire({
                    icon: 'error',
                    title: 'Error de Conexión',
                    text: "No se pudo conectar con el servicio biométrico HID Global.\nVerifique que el servicio esté corriendo en el puerto 8090.\n\nDetalles: " + e.message,
                    confirmButtonText: 'Entendido'
                });
            }
            return false;
        }
    }

    /**
     * Capturar huella usando WebSocket HID Global
     * @returns {Promise<Object>} Datos de la huella capturada
     */
    function captureFingerprint() {
        return new Promise((resolve, reject) => {
            console.log('INFO: Iniciando captura con servicio HID Global...');
            
            const ws = new WebSocket('ws://localhost:8090');
            
            const captureTimeout = setTimeout(() => {
                ws.close();
                reject(new Error('Tiempo de espera agotado'));
            }, 30000); // 30 segundos timeout
            
            ws.onopen = () => {
                console.log('INFO: Conectado al servicio biométrico');
                ws.send(JSON.stringify({ command: 'captureFingerprint' }));
            };
            
            ws.onmessage = (event) => {
                try {
                    const response = JSON.parse(event.data);
                    console.log('INFO: Respuesta del servicio:', response);
                    
                    if (response.success) {
                        clearTimeout(captureTimeout);
                        ws.close();
                        
                        resolve({
                            hash: response.hash,
                            template: response.template,
                            quality: response.quality,
                            image_png: response.image_png
                        });
                    } else {
                        clearTimeout(captureTimeout);
                        ws.close();
                        reject(new Error(response.error || 'Error desconocido al capturar la huella'));
                    }
                } catch (e) {
                    reject(new Error('Error al procesar la respuesta del servicio: ' + e.message));
                }
            };
            
            ws.onerror = (error) => {
                clearTimeout(captureTimeout);
                reject(new Error('Error de conexión WebSocket'));
            };
            
            ws.onclose = () => {
                console.log('INFO: Conexión WebSocket cerrada');
            };
        });
    }

    // Exponer las clases y funciones públicas
    return {
        Devices: Devices,
        Reader: Reader,
        checkServiceAvailability: checkServiceAvailability,
        initializeBiometricService: initializeBiometricService,
        captureFingerprint: captureFingerprint
    };
})();