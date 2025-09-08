/**
 * Servicio de comunicación con el lector de huellas DigitalPersona
 * 
 * Este servicio establece una conexión WebSocket con un servicio local que debe estar
 * corriendo en la máquina del cliente para interactuar con el SDK de DigitalPersona.
 * 
 * Requisitos:
 * 1. Driver de DigitalPersona instalado
 * 2. Servicio local ejecutándose (fingerprint-service.exe o similar)
 */

class FingerprintService {
    constructor(options = {}) {
        this.options = {
            wsUrl: 'ws://localhost:8090',  // Servicio CORREGIDO (errores específicos solucionados)
            autoReconnect: true,
            reconnectInterval: 3000,
            onStatusChange: null,
            onCaptureComplete: null,
            onError: null,
            ...options
        };
        
        this.ws = null;
        this.isConnected = false;
        this.isCapturing = false;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
    }
    
    /**
     * Inicializa la conexión con el servicio local
     * @return {Promise} Promesa que se resuelve cuando la conexión está lista
     */
    initialize() {
        return new Promise((resolve, reject) => {
            if (this.isConnected) {
                resolve(true);
                return;
            }
            
            try {
                this.ws = new WebSocket(this.options.wsUrl);
                
                this.ws.onopen = () => {
                    this.isConnected = true;
                    this.reconnectAttempts = 0;
                    console.log('Conexión establecida con el servicio de huellas');
                    
                    if (this.options.onStatusChange) {
                        this.options.onStatusChange({
                            status: 'connected',
                            message: 'Conexión establecida con el lector de huellas'
                        });
                    }
                    
                    resolve(true);
                };
                
                this.ws.onclose = () => {
                    this.isConnected = false;
                    console.log('Conexión cerrada con el servicio de huellas');
                    
                    if (this.options.onStatusChange) {
                        this.options.onStatusChange({
                            status: 'disconnected',
                            message: 'La conexión con el lector de huellas se ha cerrado'
                        });
                    }
                    
                    if (this.options.autoReconnect && this.reconnectAttempts < this.maxReconnectAttempts) {
                        this.reconnectAttempts++;
                        setTimeout(() => this.initialize(), this.options.reconnectInterval);
                    }
                };
                
                this.ws.onerror = (error) => {
                    console.error('Error en la conexión WebSocket:', error);
                    
                    if (this.options.onError) {
                        this.options.onError({
                            status: 'connectionError',
                            message: 'Error al conectar con el servicio de huellas digitales',
                            error
                        });
                    }
                    
                    reject(error);
                };
                
                this.ws.onmessage = (event) => {
                    this._handleMessage(event);
                };
                
            } catch (error) {
                console.error('Error al inicializar WebSocket:', error);
                
                if (this.options.onError) {
                    this.options.onError({
                        status: 'initializationError',
                        message: 'Error al inicializar el servicio de huellas digitales',
                        error
                    });
                }
                
                reject(error);
            }
        });
    }
    
    /**
     * Inicia la captura de huella digital
     * @return {Promise} Promesa que se resuelve cuando inicia la captura
     */
    startCapture() {
        return new Promise((resolve, reject) => {
            if (!this.isConnected) {
                const error = new Error('No hay conexión con el servicio de huellas');
                
                if (this.options.onError) {
                    this.options.onError({
                        status: 'notConnected',
                        message: 'No hay conexión con el servicio de huellas',
                        error
                    });
                }
                
                reject(error);
                return;
            }
            
            try {
                this.ws.send(JSON.stringify({
                    command: 'startCapture',
                    options: {
                        timeout: 30000 // 30 segundos de timeout
                    }
                }));
                
                this.isCapturing = true;
                
                if (this.options.onStatusChange) {
                    this.options.onStatusChange({
                        status: 'waitingForFinger',
                        message: 'Esperando huella digital...'
                    });
                }
                
                resolve(true);
            } catch (error) {
                console.error('Error al iniciar la captura:', error);
                
                if (this.options.onError) {
                    this.options.onError({
                        status: 'captureError',
                        message: 'Error al iniciar la captura de huella',
                        error
                    });
                }
                
                reject(error);
            }
        });
    }
    
    /**
     * Cancela la captura de huella digital
     */
    cancelCapture() {
        if (!this.isConnected || !this.isCapturing) {
            return;
        }
        
        try {
            this.ws.send(JSON.stringify({
                command: 'cancelCapture'
            }));
            
            this.isCapturing = false;
            
            if (this.options.onStatusChange) {
                this.options.onStatusChange({
                    status: 'captureCancelled',
                    message: 'Captura de huella cancelada'
                });
            }
        } catch (error) {
            console.error('Error al cancelar la captura:', error);
            
            if (this.options.onError) {
                this.options.onError({
                    status: 'cancelError',
                    message: 'Error al cancelar la captura de huella',
                    error
                });
            }
        }
    }
    
    /**
     * Cierra la conexión con el servicio local
     */
    disconnect() {
        if (this.isCapturing) {
            this.cancelCapture();
        }
        
        if (this.isConnected && this.ws) {
            this.ws.close();
            this.isConnected = false;
        }
    }
    
    /**
     * Maneja los mensajes recibidos del servicio WebSocket
     * @param {MessageEvent} event - Evento de mensaje WebSocket
     * @private
     */
    _handleMessage(event) {
        try {
            const data = JSON.parse(event.data);
            
            switch (data.status) {
                case 'deviceConnected':
                    if (this.options.onStatusChange) {
                        this.options.onStatusChange({
                            status: 'deviceConnected',
                            message: 'Dispositivo de huella conectado',
                            deviceInfo: data.deviceInfo
                        });
                    }
                    break;
                    
                case 'fingerDetected':
                    if (this.options.onStatusChange) {
                        this.options.onStatusChange({
                            status: 'fingerDetected',
                            message: 'Huella detectada, procesando...'
                        });
                    }
                    break;
                    
                case 'processingImage':
                    if (this.options.onStatusChange) {
                        this.options.onStatusChange({
                            status: 'processingImage',
                            message: 'Procesando imagen de huella...',
                            progress: data.progress
                        });
                    }
                    break;
                    
                case 'captureComplete':
                    this.isCapturing = false;
                    
                    if (this.options.onStatusChange) {
                        this.options.onStatusChange({
                            status: 'captureComplete',
                            message: 'Captura de huella completada'
                        });
                    }
                    
                    if (this.options.onCaptureComplete) {
                        this.options.onCaptureComplete({
                            templateData: data.templateData,
                            imageData: data.imageData,
                            quality: data.quality
                        });
                    }
                    break;
                    
                case 'error':
                    if (this.options.onError) {
                        this.options.onError({
                            status: data.errorType || 'unknownError',
                            message: data.message || 'Error desconocido en el servicio de huellas',
                            errorCode: data.errorCode
                        });
                    }
                    break;
                    
                default:
                    console.log('Mensaje no manejado del servicio de huellas:', data);
                    break;
            }
        } catch (error) {
            console.error('Error al procesar mensaje del servicio de huellas:', error, event.data);
            
            if (this.options.onError) {
                this.options.onError({
                    status: 'messageError',
                    message: 'Error al procesar mensaje del servicio de huellas',
                    error
                });
            }
        }
    }
}

// Exportar el servicio
window.FingerprintService = FingerprintService; 