document.addEventListener('DOMContentLoaded', () => {
    const listaDiv = document.getElementById('lista-profesionales');
    const form = document.getElementById('form-profesional');
    
    // 1. RECUPERAR EL TOKEN
    const token = localStorage.getItem('token');
    
    // Si no hay token, fuera
    if (!token) {
        window.location.href = 'login.html';
        return;
    }

    function cargarProfesionales() {
        // 2. ENVIAR TOKEN EN EL HEADER (Bearer ...)
        fetch(`${apiURL}/profesionales`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}` // <--- LA CLAVE
            }
        })
        .then(res => {
            if (res.status === 401 || res.status === 403) {
                alert("Sesión expirada");
                window.location.href = 'login.html';
                throw new Error("Token inválido");
            }
            return res.json();
        })
        .then(data => {
            if (data.error) {
                listaDiv.innerHTML = `<p style="color:red">${data.error}</p>`;
                return;
            }
            if (data.length === 0) {
                listaDiv.innerHTML = '<p>No hay profesionales registrados.</p>';
                return;
            }
            
            let html = '<ul style="list-style:none; padding:0;">';
            data.forEach(p => {
                html += `
                    <li style="padding:10px; border-bottom:1px solid #eee; display:flex; justify-content:space-between;">
                        <span>🩺 <strong>${p.name}</strong> - ${p.especialidad || 'General'}</span>
                        <button onclick="eliminarProfesional(${p.id})" style="color:red;">Eliminar</button>
                    </li>`;
            });
            html += '</ul>';
            listaDiv.innerHTML = html;
        })
        .catch(err => console.error(err));
    }

    // Cargar al inicio
    cargarProfesionales();

    // 3. REGISTRAR PROFESIONAL (CON TOKEN)
    if(form) {
        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const data = {
                name: document.getElementById('prof-nombre').value,
                especialidad: document.getElementById('prof-especialidad').value
                // El negocio_id lo pone el backend automáticamente
            };

            try {
                const res = await fetch(`${apiURL}/profesional`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${token}` // <--- AQUÍ TAMBIÉN
                    },
                    body: JSON.stringify(data)
                });

                const respuesta = await res.json();
                
                if (res.ok) {
                    alert("Profesional creado exitosamente");
                    form.reset();
                    cargarProfesionales();
                } else {
                    alert("Error: " + (respuesta.error || "No se pudo crear"));
                }
            } catch (error) {
                alert("Error de conexión");
            }
        });
    }

    // Función Global para Eliminar
    window.eliminarProfesional = async (id) => {
        if(!confirm("¿Eliminar este profesional?")) return;
        
        try {
            const res = await fetch(`${apiURL}/profesional/${id}`, {
                method: 'DELETE',
                headers: {
                    'Authorization': `Bearer ${token}` // <--- Y AQUÍ
                }
            });
            
            if(res.ok) {
                alert("Eliminado");
                cargarProfesionales();
            } else {
                alert("Error al eliminar");
            }
        } catch(e) { console.error(e); }
    };
});