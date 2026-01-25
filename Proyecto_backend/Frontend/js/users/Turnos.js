document.addEventListener('DOMContentLoaded', () => {

    // Referencias del DOM
    const selectServicio = document.getElementById('select-servicio');
    const selectProfesional = document.getElementById('select-profesional');
    const formTurno = document.getElementById('form-turno');
    const msgDiv = document.getElementById('mensaje-reserva');
    const selectCliente = document.getElementById('select-cliente-turno');
    const chartDom = document.getElementById('calendario-echarts');
    const contenedorHorarios = document.getElementById('contenedor-horarios');
    const gridHorarios = document.getElementById('grid-horarios');
    const fechaTexto = document.getElementById('fecha-seleccionada-texto');
    const inputFinal = document.getElementById('input-fecha-final');
    
    // 1. RECUPERAR CREDENCIALES (Token y ID)
    const token = localStorage.getItem('token');
    const negocioId = localStorage.getItem('negocio_id');

    // Validación de seguridad
    if (!token || !negocioId) {
     //   window.location.href = 'login.html';
        return;
    }

    let myChart = null; 

    // --- LÓGICA DEL CALENDARIO (Echarts) ---
    function initCalendar() {
        if (myChart) myChart.dispose();
        myChart = echarts.init(chartDom);

        const today = new Date();
        const range = `${today.getFullYear()}-${(today.getMonth() + 1).toString().padStart(2, '0')}`;

        const option = {
            tooltip: { position: 'top', formatter: p => 'Ver horarios: ' + p.data[0] },
            visualMap: { show: false, min: 0, max: 1, inRange: { color: ['#ffffff'] } },
            calendar: {
                top: 30, left: 30, right: 30, cellSize: ['auto', 40],
                range: range,
                dayLabel: { firstDay: 1, nameMap: 'es' },
                monthLabel: { nameMap: 'es' },
                yearLabel: { show: false }
            },
            series: [{
                type: 'heatmap',
                coordinateSystem: 'calendar',
                itemStyle: { borderRadius: 4, borderWidth: 1, borderColor: '#e0e0e0' },
                emphasis: { itemStyle: { color: '#a5d6a7', borderColor: '#4CAF50', borderWidth: 2 } },
                data: [] 
            }]
        };

        myChart.setOption(option);

        // Generar días del mes
        const diasDelMes = [];
        const date = new Date(today.getFullYear(), today.getMonth(), 1);
        while (date.getMonth() === today.getMonth()) {
            diasDelMes.push([date.toISOString().split('T')[0], 1]);
            date.setDate(date.getDate() + 1);
        }
        
        myChart.setOption({ series: [{ data: diasDelMes }] });

        myChart.on('click', function (params) {
            if (params.data) {
                cargarHorarios(params.data[0]);
            }
        });
    }

    // --- CARGAR HORARIOS DISPONIBLES ---
    function cargarHorarios(fecha) {
        const profesionalId = selectProfesional.value;
        const servicioId = selectServicio.value;

        if (!profesionalId || !servicioId) {
            alert("Primero selecciona Servicio y Profesional");
            return;
        }

        fechaTexto.textContent = fecha;
        contenedorHorarios.style.display = 'block';
        gridHorarios.innerHTML = '<p>Cargando...</p>';
        inputFinal.value = '';

        // CORRECCIÓN: Agregamos headers con Token
        fetch(`${apiURL}/turnos?profesional_id=${profesionalId}&fecha=${fecha}&servicio_id=${servicioId}`, {
            headers: { 'Authorization': `Bearer ${token}` }
        })
        .then(res => res.json())
        .then(horarios => {
            gridHorarios.innerHTML = '';
            
            if (!Array.isArray(horarios) || horarios.length === 0) {
                gridHorarios.innerHTML = '<p>No hay horarios disponibles.</p>';
                return;
            }

            horarios.forEach(hora => {
                const btn = document.createElement('button');
                btn.type = 'button';
                btn.className = 'slot-btn';
                btn.textContent = hora;
                btn.onclick = () => {
                    document.querySelectorAll('.slot-btn').forEach(b => b.classList.remove('selected'));
                    btn.classList.add('selected');
                    inputFinal.value = `${fecha} ${hora}:00`;
                };
                gridHorarios.appendChild(btn);
            });
        })
        .catch(err => {
            console.error(err);
            gridHorarios.innerHTML = '<p>Error al cargar horarios</p>';
        });
    }

    // --- CARGAR DATOS INICIALES (Servicios y Profesionales) ---
    function cargarDatosNegocio() {
        // 1. Servicios (CON TOKEN)
        fetch(`${apiURL}/servicios`, { // La ruta backend usa el token para saber el negocio
            headers: { 'Authorization': `Bearer ${token}` }
        })
        .then(res => res.json())
        .then(servicios => {
            selectServicio.innerHTML = '<option value="">-- Selecciona Servicio --</option>';
            if(servicios.error) return; 
            
            servicios.forEach(s => {
                const opt = document.createElement('option');
                opt.value = s.id;
                opt.textContent = `${s.name} (${s.duracion} min)`;
                selectServicio.appendChild(opt);
            });
        });

        // 2. Profesionales (CON TOKEN)
        fetch(`${apiURL}/profesionales`, { 
            headers: { 'Authorization': `Bearer ${token}` }
        })
        .then(res => res.json())
        .then(profesionales => {
            selectProfesional.innerHTML = '<option value="">-- Selecciona Profesional --</option>';
            if(profesionales.error) return;

            profesionales.forEach(p => {
                const opt = document.createElement('option');
                opt.value = p.id;
                opt.textContent = p.name;
                selectProfesional.appendChild(opt);
            });
        });
    }

    // --- EVENTOS SELECTS ---
    if(selectProfesional && selectServicio) {
        const resetCalendar = () => {
            if (selectProfesional.value && selectServicio.value) {
                setTimeout(initCalendar, 200);
            } else {
                if (contenedorHorarios) contenedorHorarios.style.display = 'none';
            }
        };
        selectProfesional.addEventListener('change', resetCalendar);
        selectServicio.addEventListener('change', resetCalendar);
    }

    // --- CREAR TURNO ---
    if(formTurno) {
        formTurno.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            if (!inputFinal.value) {
                msgDiv.textContent = "Debes seleccionar un horario en el calendario.";
                msgDiv.className = "msg error";
                return;
            }
            if (!selectCliente.value) {
                msgDiv.textContent = "Debes seleccionar un cliente.";
                msgDiv.className = "msg error";
                return;
            }

            const datosTurno = {
                cliente_id: selectCliente.value, 
                profesional_id: selectProfesional.value,
                servicio_id: selectServicio.value,
                fecha_hora: inputFinal.value
                // El negocio_id lo pone el backend desde el token
            };

            try {
                const response = await fetch(`${apiURL}/turnos`, { // Corregido endpoint a plural si es tu estándar
                    method: 'POST',
                    headers: { 
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${token}` // Token Fundamental
                    },
                    body: JSON.stringify(datosTurno)
                });
                const data = await response.json();

                if (response.ok) {
                    msgDiv.textContent = "¡Turno reservado con éxito!";
                    msgDiv.className = "msg success";
                    cargarTurnosReservados(); // Actualizar lista
                    formTurno.reset();
                    contenedorHorarios.style.display = 'none';
                    inputFinal.value = '';
                } else {
                    msgDiv.textContent = `Error: ${data.error || 'No se pudo reservar'}`;
                    msgDiv.className = "msg error";
                }
            } catch (error) {
                msgDiv.textContent = "Error de conexión";
                msgDiv.className = "msg error";
            }
        });
    }

    // --- CARGAR CLIENTES ---
    function cargarSelectClientes() {
        if (!selectCliente) return;

        // Ya no enviamos ?negocio_id=... porque va en el Token
        fetch(`${apiURL}/clientes`, {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            }
        })
        .then(res => {
            if (res.status === 401) {
                window.location.href = 'login.html'; // Redirigir si expiró
                return [];
            }
            return res.json();
        })
        .then(clientes => {
            selectCliente.innerHTML = '<option value="">-- Selecciona un Cliente --</option>';
            if (!Array.isArray(clientes) || clientes.length === 0) {
                 return;
            }
            clientes.forEach(cliente => {
                const option = document.createElement('option');
                option.value = cliente.id;
                option.textContent = `${cliente.name} (${cliente.email})`;
                selectCliente.appendChild(option);
            });
        })
        .catch(err => console.error("Error clientes:", err));
    }

    // --- LISTAR TURNOS RESERVADOS ---
    function cargarTurnosReservados() {
        const listaDiv = document.getElementById('lista-turnos');
        if(!listaDiv) return;

        listaDiv.innerHTML = '<p>Cargando turnos...</p>';

        // Usamos la ruta protegida que filtra por token
        fetch(`${apiURL}/turnos`, {
            headers: { 'Authorization': `Bearer ${token}` }
        })
        .then(res => res.json())
        .then(turnos => {
            listaDiv.innerHTML = '';
            if (turnos.error || turnos.length === 0) {
                listaDiv.innerHTML = '<p>No hay turnos registrados.</p>';
                return;
            }

            let html = '<ul class="turnos-list" style="list-style:none; padding:0;">';
            turnos.forEach(t => {
                let color = '#e3f2fd';
                if(t.estado === 'cancelado') color = '#ffebee';
                
                html += `
                    <li style="background:${color}; margin-bottom:10px; padding:15px; border-radius:8px; border-left: 5px solid #2196F3;">
                        <strong>📅 ${t.fecha_hora}</strong> - ${t.estado}<br>
                        Cliente: ${t.cliente_nombre || 'N/A'} <br>
                        Servicio: ${t.servicio_nombre || 'N/A'}
                    </li>`;
            });
            html += '</ul>';
            listaDiv.innerHTML = html;
        });
    }

    // --- INICIALIZACIÓN ---
    // Eliminamos la dependencia de selectNegocio
    cargarDatosNegocio();
    cargarSelectClientes();
    cargarTurnosReservados();

});