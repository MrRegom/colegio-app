/**
 * Formulario de Perfil - Gestión de Firma Digital
 * 
 * Este archivo maneja la lógica específica del formulario de solicitud de perfiles,
 * incluyendo la verificación de huella digital de la jefatura.
 * 
 * Dependencias:
 * - digital-persona.js
 * - SweetAlert2
 */

document.addEventListener("DOMContentLoaded", function() {
    // Referencias a elementos del DOM
    const leadershipSignatureBtn = document.getElementById('leadershipSignature');
    const submitToLeadershipBtn = document.getElementById('submitToLeadership');
    const fingerprintContainer = document.getElementById('fingerprintContainer');
    const fingerprintStatus = document.getElementById('fingerprintStatus');
    const fingerprintData = document.getElementById('fingerprintData');
    const cancelFingerprintBtn = document.getElementById('cancelFingerprint');
    const fingerprintScanArea = document.getElementById('fingerprintScanArea');
    const progressBar = document.querySelector('.progress-bar');
    
    // Variable para controlar si la huella ha sido verificada
    let isFingerprintVerified = false;
    let readerAvailable = false;
    
    // Verificar disponibilidad del lector al cargar
    initializeService();
    
    async function initializeService() {
        try {
            readerAvailable = await DigitalPersona.checkServiceAvailability();
            console.log(`INFO: Servicio biométrico disponible: ${readerAvailable}`);
        } catch (error) {
            console.log('ERROR: Error inicialización:', error);
            readerAvailable = false;
        }
    }
    
    // Event listener para el botón de firma de jefatura
    leadershipSignatureBtn.addEventListener('click', function(e) {
        e.preventDefault();
        console.log('INFO: Botón de Firma de Jefatura clickeado');
        
        // Verificar que los campos de la jefatura estén completos
        if (!validateLeadershipFields()) {
            console.log('WARNING: Campos de jefatura incompletos');
            Swal.fire({
                icon: 'warning',
                title: 'Datos incompletos',
                text: 'Por favor complete todos los datos de la jefatura antes de firmar.',
                confirmButtonText: 'Entendido'
            });
            return;
        }
        
        console.log('INFO: Campos de jefatura validados');
        
        // Mostrar el contenedor de la huella digital y resetear estado
        showFingerprintContainer();
        
        // Iniciar captura
        if (readerAvailable) {
            console.log('INFO: Iniciando captura...');
            startFingerprintCapture();
        } else {
            console.log('ERROR: Lector no disponible');
            Swal.fire({
                icon: 'error',
                title: 'Lector No Disponible',
                text: 'El lector de huellas no está disponible. Verifique que esté conectado y funcionando.',
                confirmButtonText: 'Entendido'
            });
            hideFingerprintContainer();
        }
    });
    
    // Event listener para cancelar captura
    cancelFingerprintBtn.addEventListener('click', function() {
        hideFingerprintContainer();
    });
    
    // Event listener para envío del formulario
    submitToLeadershipBtn.addEventListener('click', function() {
        if (!isFingerprintVerified) {
            Swal.fire({
                icon: 'warning',
                title: 'Verificación pendiente',
                text: 'Por favor verifique su identidad con huella digital antes de enviar el formulario.',
                confirmButtonText: 'Entendido'
            });
        } else {
            handleFormSubmit();
        }
    });
    
    function showFingerprintContainer() {
        fingerprintContainer.style.display = 'block';
        fingerprintStatus.textContent = "Esperando huella digital...";
        fingerprintStatus.className = "fingerprint-status";
        fingerprintScanArea.className = "fingerprint-image-container";
        progressBar.style.width = '0%';
    }
    
    function hideFingerprintContainer() {
        fingerprintContainer.style.display = 'none';
        fingerprintScanArea.className = "fingerprint-image-container";
        progressBar.style.width = '0%';
    }
    
    async function startFingerprintCapture() {
        console.log('INFO: Iniciando captura con servicio HID Global...');
        fingerprintStatus.textContent = "Conectando con lector biométrico...";
        fingerprintScanArea.classList.add('scanning');
        progressBar.style.width = '25%';
        
        try {
            // Usar la función del módulo DigitalPersona
            fingerprintStatus.textContent = "Coloque su dedo en el lector...";
            progressBar.style.width = '50%';
            
            const result = await DigitalPersona.captureFingerprint();
            
            // Captura exitosa
            fingerprintScanArea.classList.remove('scanning');
            fingerprintScanArea.classList.add('captured');
            fingerprintStatus.textContent = "¡Huella capturada correctamente!";
            fingerprintStatus.className = "fingerprint-status fingerprint-success";
            progressBar.style.width = '100%';
            
            // Guardar el hash de la huella
            fingerprintData.value = result.hash || result.template;
            isFingerprintVerified = true;
            
            console.log('INFO: Hash de huella guardado:', result.hash ? result.hash.substring(0, 16) + '...' : 'template');
            
            // Esperar un momento y cerrar
            setTimeout(function() {
                hideFingerprintContainer();
                
                const hashDisplay = (result.hash || result.template).substring(0, 16) + '...';
                Swal.fire({
                    icon: 'success',
                    title: 'Huella Verificada',
                    html: `
                        <p>La identidad de <strong>${document.getElementById('firstnameleadershipfloatingInput').value} ${document.getElementById('lastnameleadershipfloatingInput').value}</strong> ha sido verificada exitosamente.</p>
                        <p class="text-muted mt-2">Hash único generado: <code>${hashDisplay}</code></p>
                        ${result.image_png ? `<img src="data:image/png;base64,${result.image_png}" alt="Huella capturada" class="img-fluid mt-3" style="max-width:200px;border:1px solid #ccc;padding:4px;border-radius:4px;"/>` : ''}
                    `,
                    confirmButtonText: 'Continuar'
                });
                
                // Habilitar el botón de envío
                enableSubmitButton();
            }, 1500);
            
        } catch (error) {
            console.error('ERROR: Error en captura:', error);
            
            // Mostrar error y cerrar
            fingerprintScanArea.classList.remove('scanning');
            fingerprintStatus.textContent = "Error en captura";
            fingerprintStatus.className = "fingerprint-status fingerprint-error";
            progressBar.style.width = '0%';
            
            setTimeout(() => {
                hideFingerprintContainer();
                
                Swal.fire({
                    icon: 'error',
                    title: 'Error en Captura',
                    text: 'No se pudo capturar la huella dactilar.\n\nDetalle: ' + error.message,
                    confirmButtonText: 'Entendido'
                });
            }, 1500);
        }
    }
    
    function validateLeadershipFields() {
        const requiredFields = [
            'firstnameleadershipfloatingInput',
            'lastnameleadershipfloatingInput',
            'rutleadershipfloatingInput',
            'emailleadershipfloatingInput'
        ];
        
        for (const fieldId of requiredFields) {
            const field = document.getElementById(fieldId);
            if (!field || !field.value.trim()) {
                return false;
            }
        }
        
        return true;
    }
    
    function enableSubmitButton() {
        // Cambiar el aspecto del botón para indicar que está habilitado
        submitToLeadershipBtn.classList.add('btn-success');
        submitToLeadershipBtn.classList.remove('btn-primary');
    }
    
    function handleFormSubmit() {
        // Validar que todos los campos requeridos estén completos
        const form = document.getElementById('profileRequestForm');
        if (!form.checkValidity()) {
            form.classList.add('was-validated');
            return;
        }
        
        // Mostrar mensaje de éxito con Sweet Alert
        Swal.fire({
            icon: 'success',
            title: 'Formulario Enviado',
            text: 'La solicitud de perfil ha sido enviada exitosamente.',
            confirmButtonText: 'Continuar'
        }).then((result) => {
            if (result.isConfirmed) {
                // Resetear el formulario
                form.reset();
                form.classList.remove('was-validated');
                isFingerprintVerified = false;
                fingerprintData.value = '';
                submitToLeadershipBtn.classList.remove('btn-success');
                submitToLeadershipBtn.classList.add('btn-primary');
            }
        });
        
        // Aquí iría el código para enviar los datos al servidor
        console.log("INFO: Datos del formulario listos para enviar:", getFormData(form));
    }
    
    function getFormData(form) {
        const formData = new FormData(form);
        const formObject = {};
        
        formData.forEach((value, key) => {
            // Si la clave ya existe y es un array, añadir el valor
            if (formObject[key] && Array.isArray(formObject[key])) {
                formObject[key].push(value);
            }
            // Si la clave ya existe pero no es un array, convertirla en array
            else if (formObject[key]) {
                formObject[key] = [formObject[key], value];
            }
            // Si la clave no existe, asignar el valor
            else {
                // Si la clave termina con "[]", tratarla como array
                if (key.endsWith('[]')) {
                    const realKey = key.slice(0, -2);
                    formObject[realKey] = [value];
                } else {
                    formObject[key] = value;
                }
            }
        });
        
        return formObject;
    }
    
    // Inicializar verificación de servicio al cargar la página
    window.addEventListener('load', async function() {
        try {
            await DigitalPersona.initializeBiometricService();
        } catch (error) {
            console.log('WARNING: No se pudo inicializar el servicio biométrico automáticamente');
        }
    });
}); 