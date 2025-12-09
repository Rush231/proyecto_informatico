document.addEventListener('DOMContentLoaded', () => {
    // Referencias existentes
    const selectNegocio = document.getElementById('select-negocio');
    const selectServicio = document.getElementById('select-servicio');
    const selectProfesional = document.getElementById('select-profesional');
    const formTurno = document.getElementById('form-turno');
    const msgDiv = document.getElementById('mensaje-reserva');
    const selectCliente = document.getElementById('select-cliente-turno'); // Asegúrate que exista en tu HTML

    // Nuevas Referencias para el calendario
    const chartDom = document.getElementById('calendario-echarts');
    const contenedorHorarios = document.getElementById('contenedor-horarios');
    const gridHorarios = document.getElementById('grid-horarios');
    const fechaTexto = document.getElementById('fecha-seleccionada-texto');
    const inputFinal = document.getElementById('input-fecha-final');
    
    let myChart = null; // Instancia de ECharts

    // ------------------------------------------
    // FUNCIONES AUXILIARES
    // ------------------------------------------
    
    // Iniciar Calendario ECharts
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
                // 2. CAMBIO AQUÍ: Estilo al pasar el mouse y al estar normal
                itemStyle: {
                    borderRadius: 4, // Bordes redondeados (opcional)
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

        // Evento Click en el Calendario
        myChart.on('click', function (params) {
            if (params.componentType === 'series') {
                // params.data[0] es la fecha en string 'YYYY-MM-DD' (si usamos data)
                // Pero en un calendario vacío, params.name o params.value puede variar.
                // ECharts devuelve la fecha en params.data[0] si hay datos, o necesitamos atrapar el click en la celda.
                // Truco: Usar coordinateSystem click suele devolver la fecha.
            }
        });
        
        // ECharts a veces es complejo con celdas vacías. 
        // Una forma más simple es usar el evento global del 'calendar' si es posible, 
        // o rellenar el calendario con datos "dummy" para todos los días del mes para que sean clickeables.
        
        // Rellenar días del mes para que sean interactivos
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
        fetch(`${apiURL}/turnos/disponibles?profesional_id=${profesionalId}&fecha=${fecha}&servicio_id=${servicioId}`)
            .then(res => res.json())
            .then(horarios => {
                gridHorarios.innerHTML = '';
                
                if (horarios.length === 0) {
                    gridHorarios.innerHTML = '<p>No hay horarios disponibles.</p>';
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


    // ------------------------------------------
    // LÓGICA EXISTENTE (MODIFICADA)
    // ------------------------------------------

    if (!selectNegocio) return;

    // Cargar Negocios (Igual que antes)
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

    // Evento Cambio de Negocio (Igual que antes)
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

    // NUEVO: Cuando se selecciona un profesional, mostramos el calendario
    selectProfesional.addEventListener('change', () => {
        if (selectProfesional.value && selectServicio.value) {
            setTimeout(initCalendar, 200); // Pequeño delay para asegurar renderizado
        } else {
             if (contenedorHorarios) contenedorHorarios.style.display = 'none';
        }
    });
    
    // También si cambia el servicio (podría afectar la duración y disponibilidad)
    selectServicio.addEventListener('change', () => {
         if (selectProfesional.value && selectServicio.value) {
            setTimeout(initCalendar, 200);
             // Ocultar horarios previos porque la duración cambió
            if (contenedorHorarios) contenedorHorarios.style.display = 'none';
        }
    });


    // Enviar Turno (MODIFICADO para usar el nuevo input)
    formTurno.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const fechaSeleccionada = inputFinal.value; // Usamos el input hidden

        if (!selectProfesional.value || !selectServicio.value || !fechaSeleccionada) {
            msgDiv.textContent = "Por favor selecciona un horario del calendario.";
            msgDiv.className = "msg error";
            return;
        }

        msgDiv.textContent = "Procesando...";
        msgDiv.className = "msg";

        const datosTurno = {
            cliente_id: selectCliente ? selectCliente.value : null, // Ajustar según tu lógica de cliente
            profesional_id: selectProfesional.value,
            servicio_id: selectServicio.value,
            fecha_hora: fechaSeleccionada
        };

        try {
            const response = await fetch(`${apiURL}/crear-turno`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(datosTurno)
            });
            const data = await response.json();

            if (response.ok) {
                msgDiv.textContent = "¡Turno reservado con éxito!";
                msgDiv.className = "msg success";
                
                // Resetear UI
                formTurno.reset();
                contenedorHorarios.style.display = 'none';
                inputFinal.value = '';
                document.querySelectorAll('.slot-btn').forEach(b => b.classList.remove('selected'));
                
                // Opcional: Recargar lista de turnos si existe la función
                // if (typeof cargarMisTurnos === 'function') cargarMisTurnos();
                
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
});