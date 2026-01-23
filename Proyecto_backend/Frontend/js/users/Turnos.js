document.addEventListener('DOMContentLoaded', () => {

    const selectNegocio = document.getElementById('select-negocio');
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
    
    let myChart = null; 

 
    function initCalendar() {
        if (myChart) myChart.dispose(); // Limpiar si ya existe
        myChart = echarts.init(chartDom);

        // Obtener mes actual dinámicamente
        const today = new Date();
        const currentYear = today.getFullYear();
        // Formato YYYY-MM para el rango del calendario
        const range = `${currentYear}-${(today.getMonth() + 1).toString().padStart(2, '0')}`;

const option = {
            tooltip: {
                position: 'top',
                formatter: function (p) {
                    // Muestra la fecha al pasar el mouse
                    return 'Ver horarios para: ' + p.data[0];
                }
            },
            // 1. CAMBIO AQUÍ: Controlamos el color de las celdas
            visualMap: {
                min: 0,
                max: 1,
                calculable: false,
                show: false, // Ocultamos la barra de leyenda
                inRange: {
                    // Puedes cambiar '#ffffff' por el color que quieras (ej: '#e3f2fd' para azulito)
                    color: ['#ffffff'] 
                }
            },
            calendar: {
                top: 30,
                left: 30,
                right: 30,
                cellSize: ['auto', 40], // Celdas un poco más altas
                range: range,
                itemStyle: {
                    borderWidth: 1,
                    borderColor: '#ccc' // Color del borde de cada día
                },
                dayLabel: {
                    firstDay: 1, // Empezar semana en Lunes
                    nameMap: 'es' // Nombres en español (L, M, X...)
                },
                monthLabel: {
                    nameMap: 'es' // Nombre del mes en español
                },
                yearLabel: { show: false }
            },
            series: [{
                type: 'heatmap',
                coordinateSystem: 'calendar',
                itemStyle: {
                    borderRadius: 4, 
                    borderWidth: 1,
                    borderColor: '#e0e0e0'
                },
                emphasis: {
                    itemStyle: {
                        color: '#a5d6a7', // Color VERDE SUAVE al pasar el mouse
                        borderColor: '#4CAF50',
                        borderWidth: 2
                    }
                },
                data: [] 
            }]
        };

        myChart.setOption(option);

        myChart.on('click', function (params) {
            if (params.componentType === 'series') {

            }
        });
        

        const diasDelMes = [];
        const date = new Date(today.getFullYear(), today.getMonth(), 1);
        while (date.getMonth() === today.getMonth()) {
            const fechaStr = date.toISOString().split('T')[0];
            diasDelMes.push([fechaStr, 1]); // 1 = valor dummy
            date.setDate(date.getDate() + 1);
        }
        
        myChart.setOption({
            series: [{
                data: diasDelMes
            }]
        });

        myChart.on('click', function (params) {
            if (params.data) {
                const fechaSeleccionada = params.data[0];
                cargarHorarios(fechaSeleccionada);
            }
        });
    }

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
        inputFinal.value = ''; // Resetear selección

        // Llamar a la API
        fetch(`${apiURL}/turnos?profesional_id=${profesionalId}&fecha=${fecha}&servicio_id=${servicioId}`)
            .then(res => res.json())
            .then(horarios => {
                gridHorarios.innerHTML = '';
                
                if (horarios.length === 0) {
                    gridHorarios.innerHTML = '<p>No hay horarios disponibles.</p>';
                    return;
                }
                // Verificación de seguridad
            if (!Array.isArray(horarios)) {
                gridHorarios.innerHTML = `<p>Error: ${horarios.error || 'Respuesta inválida del servidor'}</p>`;
                return;
            }

                horarios.forEach(hora => {
                    const btn = document.createElement('button');
                    btn.type = 'button'; // Importante para no enviar form
                    btn.className = 'slot-btn';
                    btn.textContent = hora;
                    btn.onclick = () => {
                        // Desmarcar otros
                        document.querySelectorAll('.slot-btn').forEach(b => b.classList.remove('selected'));
                        // Marcar este
                        btn.classList.add('selected');
                        // Guardar valor final: 'YYYY-MM-DD HH:MM:00'
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


    if (!selectNegocio) return;

    // Cargar Negocios
    fetch(apiURL + '/negocios')
        .then(res => res.json())
        .then(data => {
            selectNegocio.innerHTML = '<option value="">-- Selecciona Negocio --</option>';
            data.forEach(negocio => {
                const option = document.createElement('option');
                option.value = negocio.id;
                option.textContent = negocio.name;
                selectNegocio.appendChild(option);
            });
        });

    // Evento Cambio de Negocio 
    selectNegocio.addEventListener('change', (e) => {
        const negocioId = e.target.value;
        // ... (Tu código existente para limpiar selects) ...
        selectServicio.innerHTML = '<option value="">-- Selecciona Servicio --</option>';
        selectProfesional.innerHTML = '<option value="">-- Selecciona Profesional --</option>';
        selectServicio.disabled = true;
        selectProfesional.disabled = true;
        
        // Ocultar calendario si se cambia el negocio
        if (contenedorHorarios) contenedorHorarios.style.display = 'none';
        if (myChart) myChart.dispose();
        myChart = null;

        if (negocioId) {
            cargarTurnosReservados(); // <--- ESTA ES LA CLAVE
        } else {
            // Si des-selecciona el negocio, limpiamos la lista
            document.getElementById('lista-turnos').innerHTML = '';
        }

        if (!negocioId) return;

        // Fetch Servicios
        fetch(`${apiURL}/servicios/${negocioId}`)
            .then(res => res.json())
            .then(servicios => {
                servicios.forEach(s => {
                    const opt = document.createElement('option');
                    opt.value = s.id;
                    opt.textContent = `${s.name} (${s.duracion} min)`;
                    selectServicio.appendChild(opt);
                });
                selectServicio.disabled = false;
            });

        // Fetch Profesionales
        fetch(`${apiURL}/profesionales/${negocioId}`)
            .then(res => res.json())
            .then(profesionales => {
                profesionales.forEach(p => {
                    const opt = document.createElement('option');
                    opt.value = p.id;
                    opt.textContent = p.name;
                    selectProfesional.appendChild(opt);
                });
                selectProfesional.disabled = false;
            });
    });

    selectProfesional.addEventListener('change', () => {
        if (selectProfesional.value && selectServicio.value) {
            setTimeout(initCalendar, 200); // Pequeño delay para asegurar renderizado
        } else {
             if (contenedorHorarios) contenedorHorarios.style.display = 'none';
        }
    });
    
    selectServicio.addEventListener('change', () => {
         if (selectProfesional.value && selectServicio.value) {
            setTimeout(initCalendar, 200);
             // Ocultar horarios previos porque la duración cambió
            if (contenedorHorarios) contenedorHorarios.style.display = 'none';
        }
    });


    formTurno.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const fechaSeleccionada = inputFinal.value; 

        // Validación extra para el cliente
        if (!selectCliente.value) {
            msgDiv.textContent = "Debes seleccionar un cliente.";
            msgDiv.className = "msg error";
            return;
        }

        const datosTurno = {
            // Aquí unimos, enviamos el ID del cliente seleccionado
            cliente_id: selectCliente.value, 
            profesional_id: selectProfesional.value,
            servicio_id: selectServicio.value,
            fecha_hora: fechaSeleccionada
        };

        try {
            const response = await fetch(`${apiURL}/turno`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(datosTurno)
            });
            const data = await response.json();

            if (response.ok) {
                msgDiv.textContent = "¡Turno reservado con éxito!";
                msgDiv.className = "msg success";
                cargarTurnosReservados();
                
                // Resetear UI
                formTurno.reset();
                contenedorHorarios.style.display = 'none';
                inputFinal.value = '';
                document.querySelectorAll('.slot-btn').forEach(b => b.classList.remove('selected'));
                
                
            } else {
                msgDiv.textContent = `Error: ${data.error || 'No se pudo reservar'}`;
                msgDiv.className = "msg error";
            }
        } catch (error) {
            msgDiv.textContent = "Error de conexión";
            msgDiv.className = "msg error";
            console.error(error);
        }
    });

    // Función para llenar el Select de Clientes
    function cargarSelectClientes() {
        const negocioId = localStorage.getItem('negocio_id');
        const token = localStorage.getItem('token');
        if (!negocioId || negocioId === "null") {
        console.error("No se encontró el ID del negocio. Redirigiendo...");
        window.location.href = 'login.html';
        return;
    }
        if (!selectCliente) return;

        fetch(`${apiURL}/clientes?negocio_id=${negocioId}`, {
        method: 'GET',
        headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
        }
        })

            .then(res => {
                if (!res.ok) throw new Error("Error al obtener clientes");
                return res.json();
            })
            .then(clientes => {
                // Limpiar opciones previas
                selectCliente.innerHTML = '<option value="">-- Selecciona un Cliente --</option>';
                
                if (clientes.length === 0) {
                     const option = document.createElement('option');
                     option.text = "No hay clientes registrados";
                     selectCliente.appendChild(option);
                     return;
                }

                // Rellenar con datos reales
                clientes.forEach(cliente => {
                    const option = document.createElement('option');
                    option.value = cliente.id; // El ID es lo que enviaremos a la BD
                    option.textContent = `${cliente.name} (${cliente.email})`;
                    selectCliente.appendChild(option);
                });
            })
            .catch(err => console.error("Error cargando clientes:", err));
    }

    // Llamamos a la función al iniciar para que la lista esté lista
    cargarSelectClientes();



    //  Función para mostrar la lista de turnos 
    function cargarTurnosReservados() {
        const token = localStorage.getItem('token');
        const listaDiv = document.getElementById('lista-turnos');
        // Obtenemos el ID del negocio del usuario logueado (asumiendo que se guardó al login)
        // Si no tienes el negocio_id en storage, puedes intentar obtenerlo del selectNegocio
        const negocioId = sessionStorage.getItem('negocio_id') || selectNegocio.value;

        if (!negocioId) {
            listaDiv.innerHTML = '<p>Selecciona un negocio para ver los turnos.</p>';
            return;
        }

        listaDiv.innerHTML = '<p>Cargando turnos...</p>';

        fetch(`${apiURL}/turnos/negocio/${negocioId}`)
            .then(res => {
                if (!res.ok) throw new Error("Error en la API");
                return res.json();
            })
            .then(turnos => {
                if (turnos.length === 0) {
                    listaDiv.innerHTML = '<p>No hay turnos registrados todavía.</p>';
                    return;
                }

                let html = '<ul class="turnos-list" style="list-style:none; padding:0;">';
                turnos.forEach(t => {
                    // Elegimos un color según el estado
                    let color = '#e3f2fd'; // Azul por defecto
                    if(t.estado === 'cancelado') color = '#ffebee';
                    
                    html += `
                        <li style="background:${color}; margin-bottom:10px; padding:15px; border-radius:8px; border-left: 5px solid #2196F3;">
                            <div style="display:flex; justify-content:space-between; align-items:center;">
                                <div>
                                    <strong>📅 ${t.fecha_hora}</strong><br>
                                    👤 Cliente:${t.cliente}<br>
                                        ${t.servicio} con ${t.profesional}
                                </div>
                                <span style="font-size:0.8em; text-transform:uppercase; font-weight:bold; color:#555;">
                                    ${t.estado}
                                </span>
                            </div>
                        </li>
                    `;
                });
                html += '</ul>';
                listaDiv.innerHTML = html;
            })
            .catch(err => {
                console.error(err);
                listaDiv.innerHTML = '<p>Error al cargar la lista.</p>';
            });
            
    }  if(selectNegocio.value) {
        cargarTurnosReservados();
    }

});