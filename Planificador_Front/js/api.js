// ==================== CONFIGURACIÓN ====================
const API_URL = 'http://127.0.0.1:8000/api';
let usuarioActual = null;
let conversacionId = localStorage.getItem('conversacionId') || null;

// ==================== INICIALIZAR ====================
function cargarUsuario() {
    const user = localStorage.getItem('usuario');
    if (user) {
        usuarioActual = JSON.parse(user);
    }
    actualizarUI();
}

// ==================== UTILIDADES ====================
function guardarUsuario(user) {
    usuarioActual = user;
    localStorage.setItem('usuario', JSON.stringify(user));
}

function actualizarUI() {
    const authButtons = document.getElementById('auth-buttons');
    if (!authButtons) return;
    
    if (usuarioActual) {
        const inicial = usuarioActual.nombre ? usuarioActual.nombre.charAt(0).toUpperCase() : 'U';
        authButtons.innerHTML = `
            <div class="user-info">
               <span class="user-name" style="color: #1a1a2e; font-weight: 500;">${usuarioActual.nombre}</span>
                <span class="user-role" style="background: ${usuarioActual.rol === 'admin' ? '#dc3545' : '#28a745'}; padding: 2px 8px; border-radius: 20px; font-size: 0.7rem; margin-left: 8px;">${usuarioActual.rol}</span>
            </div>
            <button onclick="cerrarSesion()" class="btn-logout">Cerrar sesión</button>
        `;
        actualizarNavbarPorRol();
    } else {
        authButtons.innerHTML = `
            <button onclick="window.location.href='/pages/login.html'" class="btn-login">Iniciar sesión</button>
            <button onclick="window.location.href='/pages/registro.html'" class="btn-register">Registrarse</button>
        `;
        
        const navCenter = document.querySelector('.nav-center');
        if (navCenter) {
            navCenter.innerHTML = `
                <button onclick="window.location.href='/index.html'">Inicio</button>
                <button onclick="window.location.href='/pages/chatbot.html'">Crear Evento</button>
                <button onclick="window.location.href='/pages/mis-eventos.html'">Mis Eventos</button>
                <button onclick="window.location.href='/pages/admin/usuarios.html'">Usuarios</button>
                <button onclick="window.location.href='/pages/admin/proveedores.html'">Proveedores</button>
                <button onclick="window.location.href='/pages/admin/planes.html'">Planes</button>
            `;
        }
    }
}

function actualizarNavbarPorRol() {
    const navCenter = document.querySelector('.nav-center');
    if (!navCenter) return;
    
    let botones = `
        <button onclick="window.location.href='/index.html'">Inicio</button>
        <button onclick="window.location.href='/pages/chatbot.html'">Crear Evento</button>
        <button onclick="window.location.href='/pages/mis-eventos.html'">Mis Eventos</button>
        <button onclick="window.location.href='/pages/admin/usuarios.html'">Usuarios</button>
        <button onclick="window.location.href='/pages/admin/proveedores.html'">Proveedores</button>
        <button onclick="window.location.href='/pages/admin/planes.html'">Planes</button>
    `;
    
    navCenter.innerHTML = botones;
}

function cerrarSesion() {
    usuarioActual = null;
    localStorage.removeItem('usuario');
    localStorage.removeItem('conversacionId');
    conversacionId = null;
    actualizarUI();
    window.location.href = '/index.html';
}

// ==================== PETICIONES API ====================
async function apiRequest(endpoint, method = 'GET', body = null) {
    const options = {
        method: method,
        headers: { 'Content-Type': 'application/json' }
    };
    
    if (body) {
        options.body = JSON.stringify(body);
    }
    
    const response = await fetch(`${API_URL}${endpoint}`, options);
    const data = await response.json();
    
    if (!response.ok) {
        throw new Error(data.error || 'Error en la petición');
    }
    
    return data;
}

// ==================== AUTH ====================
async function login(event) {
    event.preventDefault();
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    
    try {
        const data = await apiRequest('/login/', 'POST', { email, password });
        guardarUsuario(data);
        window.location.href = '/index.html';
    } catch (error) {
        const errorDiv = document.getElementById('error-message');
        errorDiv.textContent = error.message;
        errorDiv.style.display = 'block';
    }
}

async function registro(event) {
    event.preventDefault();
    const nombre = document.getElementById('nombre').value;
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    
    if (password.length < 8) {
        const errorDiv = document.getElementById('error-message');
        errorDiv.textContent = 'La contraseña debe tener al menos 8 caracteres';
        errorDiv.style.display = 'block';
        return;
    }
    
    try {
        await apiRequest('/registro/', 'POST', { nombre, email, password });
        alert('✅ Registro exitoso. Ahora inicia sesión.');
        window.location.href = '/pages/login.html';
    } catch (error) {
        const errorDiv = document.getElementById('error-message');
        errorDiv.textContent = error.message;
        errorDiv.style.display = 'block';
    }
}

// ==================== CHATBOT CON GROQ ====================
async function iniciarConversacion() {
    if (!usuarioActual) {
        console.log("No hay usuario, no se puede crear conversación");
        return false;
    }
    
    try {
        const response = await fetch(`${API_URL}/conversaciones/crear/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ usuario_id: usuarioActual.id, titulo: "Chat con IA" })
        });
        const data = await response.json();
        conversacionId = data.id;
        localStorage.setItem('conversacionId', conversacionId);
        console.log("Conversación creada:", conversacionId);
        return true;
    } catch (error) {
        console.error('Error al crear conversación:', error);
        return false;
    }
}

// ==================== EVENTOS ====================
async function guardarEvento(eventoData) {
    if (!usuarioActual) {
        throw new Error('Debes iniciar sesión para guardar un evento');
    }
    
    try {
        const response = await fetch(`${API_URL}/eventos/guardar/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(eventoData)
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.error || 'Error al guardar el evento');
        }
        
        return data;
    } catch (error) {
        console.error('Error en guardarEvento:', error);
        throw error;
    }
}

async function obtenerEventosUsuario() {
    if (!usuarioActual) {
        throw new Error('Debes iniciar sesión para ver tus eventos');
    }
    
    try {
        const eventos = await apiRequest(`/eventos/usuario/${usuarioActual.id}/`);
        return eventos;
    } catch (error) {
        console.error('Error en obtenerEventosUsuario:', error);
        throw error;
    }
}

async function obtenerEvento(eventoId) {
    try {
        const evento = await apiRequest(`/eventos/${eventoId}/`);
        return evento;
    } catch (error) {
        console.error('Error en obtenerEvento:', error);
        throw error;
    }
}

async function actualizarEvento(eventoId, datosActualizados) {
    if (!usuarioActual) {
        throw new Error('Debes iniciar sesión para actualizar un evento');
    }
    
    try {
        const response = await fetch(`${API_URL}/eventos/${eventoId}/actualizar/`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(datosActualizados)
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.error || 'Error al actualizar el evento');
        }
        
        return data;
    } catch (error) {
        console.error('Error en actualizarEvento:', error);
        throw error;
    }
}

async function eliminarEvento(eventoId) {
    if (!usuarioActual) {
        throw new Error('Debes iniciar sesión para eliminar un evento');
    }
    
    try {
        const response = await fetch(`${API_URL}/eventos/${eventoId}/eliminar/`, {
            method: 'DELETE',
            headers: { 'Content-Type': 'application/json' }
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.error || 'Error al eliminar el evento');
        }
        
        return data;
    } catch (error) {
        console.error('Error en eliminarEvento:', error);
        throw error;
    }
}

// ==================== PROVEEDORES (SPARQL) ====================
async function cargarProveedoresDestacados() {
    const container = document.getElementById('proveedores-destacados');
    if (!container) return;
    
    container.innerHTML = '<div class="loading">Cargando proveedores destacados...</div>';
    
    try {
        const proveedores = await apiRequest('/proveedores/destacados/');
        if (!proveedores.length) {
            container.innerHTML = '<p>No hay proveedores destacados disponibles</p>';
            return;
        }
        
        container.innerHTML = proveedores.map(p => `
            <div class="feature-card">
                <div class="feature-icon">⭐</div>
                <h3>${p.nombre || 'Proveedor'}</h3>
                <p class="calificacion">⭐ ${p.calificacion || 'N/A'}/5</p>
                <p>📍 ${p.ciudad || 'Ubicación no especificada'}</p>
                <button class="btn-ver" onclick="verDetalleProveedor('${p.nombre}')">Ver detalles</button>
            </div>
        `).join('');
    } catch (error) {
        console.error('Error:', error);
        container.innerHTML = '<p>Error al cargar proveedores destacados</p>';
    }
}

async function verDetalleProveedor(nombre) {
    try {
        const proveedores = await apiRequest(`/proveedores/buscar/${encodeURIComponent(nombre)}/`);
        const p = proveedores[0];
        if (p) {
            alert(`📋 ${p.nombre}\n⭐ Calificación: ${p.calificacion || 'N/A'}\n📍 Ciudad: ${p.ciudad || 'N/A'}\n📞 Teléfono: ${p.telefono || 'No registrado'}`);
        }
    } catch (error) {
        alert('Error al cargar detalles del proveedor');
    }
}

// ==================== TIPOS DE EVENTO ====================
async function cargarTiposEvento() {
    try {
        const tipos = await apiRequest('/tipos-evento/');
        const select = document.getElementById('tipo-evento-select');
        if (select) {
            select.innerHTML = '<option value="">Selecciona un tipo</option>' + 
                tipos.map(t => `<option value="${t.nombre}">${t.nombre}</option>`).join('');
        }
        return tipos;
    } catch (error) {
        console.error('Error:', error);
        return [];
    }
}

// ==================== SERVICIOS ====================
async function cargarServiciosPorTipo(tipoEvento) {
    if (!tipoEvento) return;
    
    const container = document.getElementById('servicios-container');
    if (!container) return;
    
    container.innerHTML = '<div class="loading">Cargando servicios...</div>';
    
    try {
        const servicios = await apiRequest(`/servicios/tipo/${encodeURIComponent(tipoEvento)}/`);
        
        if (!servicios.length) {
            container.innerHTML = '<p>No hay servicios disponibles para este tipo de evento</p>';
            return;
        }
        
        container.innerHTML = servicios.map(s => `
            <div class="card servicio-card">
                <h4>${s.nombre}</h4>
                <p>💰 Precio: $${parseFloat(s.precioBase || 0).toLocaleString()}</p>
                ${s.precioPorPersona ? `<p>👤 Por persona: $${parseFloat(s.precioPorPersona).toLocaleString()}</p>` : ''}
                <p>🏢 ${s.empresa || 'Proveedor no especificado'}</p>
                <p>📁 ${s.categoria || 'Sin categoría'}</p>
            </div>
        `).join('');
    } catch (error) {
        console.error('Error:', error);
        container.innerHTML = '<p>Error al cargar servicios</p>';
    }
}

// ==================== PAQUETES ====================
async function cargarPaquetesPorTipo(tipoEvento) {
    if (!tipoEvento) return;
    
    const container = document.getElementById('paquetes-container');
    if (!container) return;
    
    container.innerHTML = '<div class="loading">Cargando paquetes...</div>';
    
    try {
        const paquetes = await apiRequest(`/paquetes/tipo/${encodeURIComponent(tipoEvento)}/`);
        
        if (!paquetes.length) {
            container.innerHTML = '<p>No hay paquetes disponibles para este tipo de evento</p>';
            return;
        }
        
        container.innerHTML = paquetes.map(p => `
            <div class="card paquete-card">
                <h4>📦 ${p.nombre}</h4>
                <p>💰 Precio base: $${parseFloat(p.precioBase || 0).toLocaleString()}</p>
                ${p.descuentoPct ? `<p>🎉 Descuento: ${p.descuentoPct}%</p>` : ''}
            </div>
        `).join('');
    } catch (error) {
        console.error('Error:', error);
        container.innerHTML = '<p>Error al cargar paquetes</p>';
    }
}

// ==================== MIS EVENTOS ====================
async function cargarMisEventos() {
    const container = document.getElementById('eventos-container');
    if (!container) return;
    
    if (!usuarioActual) {
        window.location.href = '/pages/login.html';
        return;
    }
    
    container.innerHTML = '<div class="loading">Cargando tus eventos...</div>';
    
    try {
        let eventos = [];
        try {
            eventos = await obtenerEventosUsuario();
        } catch (e) {
            console.log("No hay eventos guardados aún");
        }
        
        if (!eventos.length) {
            container.innerHTML = `
                <div class="card" style="text-align: center;">
                    <p>No tienes eventos guardados aún.</p>
                    <button class="btn btn-primary" onclick="window.location.href='/pages/chatbot.html'">✨ Crear mi primer evento</button>
                </div>
            `;
            return;
        }
        
        container.innerHTML = eventos.map(e => {
            let estadoClass = '';
            let estadoTexto = '';
            switch(e.estado) {
                case 'borrador':
                    estadoClass = 'estado-borrador';
                    estadoTexto = '📝 Borrador';
                    break;
                case 'planificando':
                    estadoClass = 'estado-planificando';
                    estadoTexto = '🔄 Planificando';
                    break;
                case 'confirmado':
                    estadoClass = 'estado-confirmado';
                    estadoTexto = '✅ Confirmado';
                    break;
                case 'completado':
                    estadoClass = 'estado-completado';
                    estadoTexto = '🎉 Completado';
                    break;
                case 'cancelado':
                    estadoClass = 'estado-cancelado';
                    estadoTexto = '❌ Cancelado';
                    break;
                default:
                    estadoClass = 'estado-activo';
                    estadoTexto = '📋 Activo';
            }
            
            return `
                <div class="card evento-card" data-evento-id="${e.id}">
                    <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap;">
                        <h3>🎉 ${e.nombre}</h3>
                        <span class="estado-badge ${estadoClass}">${estadoTexto}</span>
                    </div>
                    <div class="evento-detalles">
                        <div class="detalle-grupo"><strong>🎉 Tipo:</strong> ${e.tipo_evento}</div>
                        <div class="detalle-grupo"><strong>📅 Fecha:</strong> ${e.fecha_evento ? formatearFecha(e.fecha_evento) : 'No especificada'}</div>
                        <div class="detalle-grupo"><strong>👥 Personas:</strong> ${e.num_personas}</div>
                        <div class="detalle-grupo"><strong>💰 Presupuesto:</strong> $${e.presupuesto_total.toLocaleString()}</div>
                        <div class="detalle-grupo"><strong>📍 Ciudad:</strong> ${e.ciudad || 'No especificada'}</div>
                        <div class="detalle-grupo"><strong>📅 Creado:</strong> ${formatearFecha(e.created_at)}</div>
                    </div>
                    <div style="margin-top: 15px; display: flex; gap: 10px; flex-wrap: wrap;">
                        <button class="btn-ver" onclick="verDetalleEvento(${e.id})">🔍 Ver detalles</button>
                        <button class="btn-plan" onclick="planificarEvento(${e.id})">📋 Planificar</button>
                        <button class="btn-editar" onclick="editarEvento(${e.id})">✏️ Editar</button>
                        <button class="btn-eliminar" onclick="eliminarEventoConfirmar(${e.id})">🗑️ Eliminar</button>
                    </div>
                </div>
            `;
        }).join('');
        
    } catch (error) {
        console.error('Error:', error);
        container.innerHTML = `<div class="card"><p class="alert alert-error">Error al cargar eventos: ${error.message}</p></div>`;
    }
}

async function verDetalleEvento(eventoId) {
    try {
        const evento = await obtenerEvento(eventoId);
        alert(`📋 DETALLES DEL EVENTO\n\n🎉 Nombre: ${evento.nombre}\n🎭 Tipo: ${evento.tipo_evento}\n📅 Fecha: ${evento.fecha_evento || 'No especificada'}\n👥 Personas: ${evento.num_personas}\n💰 Presupuesto: $${evento.presupuesto_total.toLocaleString()}\n📍 Ciudad: ${evento.ciudad || 'No especificada'}\n📌 Estado: ${evento.estado}\n📅 Creado: ${formatearFecha(evento.created_at)}`);
    } catch (error) {
        alert('Error al cargar detalles del evento');
    }
}

function planificarEvento(eventoId) {
    localStorage.setItem('eventoPlanificarId', eventoId);
    window.location.href = '/pages/chatbot.html';
}

function editarEvento(eventoId) {
    localStorage.setItem('eventoEditarId', eventoId);
    window.location.href = '/pages/editar-evento.html';
}

async function eliminarEventoConfirmar(eventoId) {
    if (confirm('¿Estás seguro de que deseas eliminar este evento? Esta acción no se puede deshacer.')) {
        try {
            await eliminarEvento(eventoId);
            alert('✅ Evento eliminado exitosamente');
            location.reload();
        } catch (error) {
            alert('❌ Error al eliminar el evento: ' + error.message);
        }
    }
}

// ==================== CONVERSACIONES ====================
async function cargarMisConversaciones() {
    const container = document.getElementById('conversaciones-container');
    if (!container) return;
    
    if (!usuarioActual) {
        window.location.href = '/pages/login.html';
        return;
    }
    
    container.innerHTML = '<div class="loading">Cargando tus conversaciones...</div>';
    
    try {
        const conversaciones = await apiRequest(`/conversaciones/usuario/${usuarioActual.id}/`);
        
        if (!conversaciones.length) {
            container.innerHTML = `
                <div class="card" style="text-align: center;">
                    <p>No tienes conversaciones aún.</p>
                    <button class="btn btn-primary" onclick="window.location.href='/pages/chatbot.html'">✨ Crear mi primer evento</button>
                </div>
            `;
            return;
        }
        
        container.innerHTML = conversaciones.map(c => `
            <div class="card evento-card">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <h3>${c.titulo || 'Conversación'}</h3>
                    <span class="estado-badge estado-${c.estado}">${c.estado || 'activa'}</span>
                </div>
                <div class="evento-detalles">
                    <div class="detalle-grupo"><strong>📅 Creado:</strong> ${formatearFecha(c.created_at)}</div>
                    <div class="detalle-grupo"><strong>🔄 Actualizado:</strong> ${formatearFecha(c.updated_at)}</div>
                    ${c.tipo_evento_uri ? `<div class="detalle-grupo"><strong>🎉 Tipo:</strong> ${c.tipo_evento_uri.replace('ev:', '')}</div>` : ''}
                    ${c.num_personas ? `<div class="detalle-grupo"><strong>👥 Personas:</strong> ${c.num_personas}</div>` : ''}
                    ${c.presupuesto ? `<div class="detalle-grupo"><strong>💰 Presupuesto:</strong> $${parseFloat(c.presupuesto).toLocaleString()}</div>` : ''}
                </div>
                <div style="margin-top: 15px; display: flex; gap: 10px;">
                    <button class="btn-ver" onclick="verDetalleConversacion(${c.id})">🔍 Ver detalles</button>
                    <button class="btn-plan" onclick="continuarConversacion(${c.id})">💬 Continuar</button>
                </div>
            </div>
        `).join('');
    } catch (error) {
        console.error('Error:', error);
        container.innerHTML = `<div class="card"><p class="alert alert-error">Error: ${error.message}</p></div>`;
    }
}

async function verDetalleConversacion(conversacionId) {
    try {
        const c = await apiRequest(`/conversaciones/${conversacionId}/`);
        alert(`📋 ${c.titulo}\n📅 ${formatearFecha(c.created_at)}\n💬 Mensajes: ${c.historial_json?.length || 0}\n🎉 Tipo: ${c.tipo_evento_uri?.replace('ev:', '') || 'No especificado'}\n👥 Personas: ${c.num_personas || 'N/A'}\n💰 Presupuesto: ${c.presupuesto ? `$${parseFloat(c.presupuesto).toLocaleString()}` : 'N/A'}`);
    } catch (error) {
        alert('Error al cargar detalles');
    }
}

function continuarConversacion(id) {
    localStorage.setItem('conversacionId', id);
    window.location.href = '/pages/chatbot.html';
}

// ==================== ADMIN - USUARIOS ====================
async function cargarUsuariosAdmin() {
    if (!verificarAccesoAdmin()) return;
    
    const container = document.getElementById('usuarios-container');
    if (!container) return;
    
    container.innerHTML = '<div class="loading">Cargando usuarios...</div>';
    
    try {
        const usuarios = await apiRequest('/usuarios/');
        
        if (!usuarios.length) {
            container.innerHTML = '<div class="card"><p>No hay usuarios registrados</p></div>';
            return;
        }
        
        let html = '<div style="overflow-x: auto;"><table class="admin-table">';
        html += '<thead><tr><th>ID</th><th>Nombre</th><th>Email</th><th>Rol</th><th>Activo</th><th>Registrado</th>;</thead><tbody>';
        
        usuarios.forEach(u => {
            html += `<tr>
                        <td>${u.id}</td>
                        <td><strong>${u.nombre}</strong></td>
                        <td>${u.email}</td>
                        <td><span class="badge-${u.rol}">${u.rol}</span></td>
                        <td>${u.activo ? '✅' : '❌'}</td>
                        <td>${formatearFecha(u.created_at)}</td>
                      </tr>`;
        });
        
        html += '</tbody> nahil</div>';
        container.innerHTML = html;
        
    } catch (error) {
        container.innerHTML = `<div class="card"><p class="alert alert-error">Error: ${error.message}</p></div>`;
    }
}

// ==================== ADMIN - PROVEEDORES ====================
async function cargarProveedoresAdmin() {
    if (!verificarAccesoAdmin()) return;
    
    const container = document.getElementById('proveedores-container');
    if (!container) return;
    
    container.innerHTML = '<div class="loading">Cargando proveedores...</div>';
    
    try {
        const proveedores = await apiRequest('/proveedores/');
        
        if (!proveedores.length) {
            container.innerHTML = '<div class="card"><p>No hay proveedores registrados</p></div>';
            return;
        }
        
        let html = '<div style="overflow-x: auto;"><table class="admin-table">';
        html += '<thead><tr><th>Nombre</th><th>Calificación</th><th>Ciudad</th><th>Teléfono</th>;</thead><tbody>';
        
        proveedores.forEach(p => {
            html += `<tr>
                        <td><strong>${p.nombre}</strong></td>
                        <td>⭐ ${p.calificacion || 'N/A'}</td>
                        <td>📍 ${p.ciudad || 'N/A'}</td>
                        <td>📞 ${p.telefono || 'N/A'}</td>
                      </tr>`;
        });
        
        html += '</tbody></table></div>';
        container.innerHTML = html;
        
    } catch (error) {
        container.innerHTML = `<div class="card"><p class="alert alert-error">Error: ${error.message}</p></div>`;
    }
}

// ==================== ADMIN - PLANES ====================
async function cargarPlanesAdmin() {
    if (!verificarAccesoAdmin()) return;
    
    const container = document.getElementById('planes-container');
    if (!container) return;
    
    container.innerHTML = '<div class="loading">Cargando paquetes...</div>';
    
    try {
        const paquetes = await apiRequest('/paquetes/');
        
        if (!paquetes.length) {
            container.innerHTML = '<div class="card"><p>No hay paquetes disponibles</p></div>';
            return;
        }
        
        let html = '<div style="overflow-x: auto;"><table class="admin-table">';
        html += '<thead><tr><th>Nombre</th><th>Precio Base</th><th>Descuento</th><th>Tipo Evento</th>;</thead><tbody>';
        
        paquetes.forEach(p => {
            html += `<tr>
                        <td><strong>${p.nombre}</strong></td>
                        <td>💰 $${parseFloat(p.precioBase || 0).toLocaleString()}</td>
                        <td>🎉 ${p.descuentoPct || '0'}%</td>
                        <td>${p.tipoEvento || 'N/A'}</td>
                      </tr>`;
        });
        
        html += '</tbody></table></div>';
        container.innerHTML = html;
        
    } catch (error) {
        container.innerHTML = `<div class="card"><p class="alert alert-error">Error: ${error.message}</p></div>`;
    }
}

// ==================== FUNCIONES AUXILIARES ====================
function formatearFecha(fecha) {
    if (!fecha) return 'No especificada';
    const date = new Date(fecha);
    return date.toLocaleDateString('es-CO', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

function verificarAccesoAdmin() {
    if (!usuarioActual) {
        window.location.href = '/pages/login.html';
        return false;
    }
    if (usuarioActual.rol !== 'admin') {
        alert('⛔ Acceso denegado. Solo administradores.');
        window.location.href = '/index.html';
        return false;
    }
    return true;
}

// ==================== INICIALIZAR ====================
cargarUsuario();