const API_URL = "http://127.0.0.1:5000";

const listaProductos = document.getElementById("lista-productos");
const listaVentas = document.getElementById("lista-ventas");
const listaAlertas = document.getElementById("lista-alertas");
const listaMasVendidos = document.getElementById("lista-mas-vendidos");
const listaMovimientos = document.getElementById("lista-movimientos");
const mensaje = document.getElementById("mensaje");

const formProducto = document.getElementById("form-producto");
const formTitle = document.getElementById("form-title");
const btnCancelarEdicion = document.getElementById("btn-cancelar-edicion");

const inputProductoId = document.getElementById("producto-id");
const inputNombre = document.getElementById("nombre");
const inputPrecio = document.getElementById("precio");
const inputStock = document.getElementById("stock");

const filtroNombre = document.getElementById("filtro-nombre");
const filtroStockBajo = document.getElementById("filtro-stock-bajo");
const filtroOrden = document.getElementById("orden");
const filtroDireccion = document.getElementById("direccion");

const metricProductos = document.getElementById("metric-productos");
const metricStock = document.getElementById("metric-stock");
const metricStockBajo = document.getElementById("metric-stock-bajo");
const metricValor = document.getElementById("metric-valor");
const metricVentas = document.getElementById("metric-ventas");
const metricUnidadesVendidas = document.getElementById("metric-unidades-vendidas");
const contadorProductos = document.getElementById("contador-productos");

document.getElementById("btn-filtrar").addEventListener("click", cargarProductos);
document.getElementById("btn-limpiar-filtros").addEventListener("click", limpiarFiltros);
document.getElementById("btn-recargar").addEventListener("click", cargarDashboard);
btnCancelarEdicion.addEventListener("click", resetFormulario);
formProducto.addEventListener("submit", guardarProducto);

document.addEventListener("DOMContentLoaded", () => {
    cargarDashboard();
});

async function cargarDashboard() {
    await Promise.all([
        cargarProductos(),
        cargarVentas(),
        cargarResumen(),
        cargarMasVendidos(),
        cargarMovimientosRecientes()
    ]);
}

function mostrarMensaje(texto, tipo = "exito") {
    mensaje.textContent = texto;
    mensaje.className = `mensaje mensaje-${tipo}`;
    mensaje.classList.remove("oculto");

    setTimeout(() => {
        mensaje.classList.add("oculto");
    }, 3000);
}

function formatearPrecio(valor) {
    return `$${Number(valor).toLocaleString("es-CO")}`;
}

function formatearFecha(fecha) {
    return new Date(fecha).toLocaleString("es-CO");
}

function obtenerClaseStock(stock) {
    if (stock <= 2) return "stock-critico";
    if (stock <= 5) return "stock-bajo";
    return "stock-ok";
}

function obtenerClaseMovimiento(tipo) {
    if (tipo === "entrada") return "movimiento-entrada";
    if (tipo === "salida") return "movimiento-salida";
    return "movimiento-ajuste";
}

function construirQueryProductos() {
    const params = new URLSearchParams();

    if (filtroNombre.value.trim()) {
        params.append("nombre", filtroNombre.value.trim());
    }

    if (filtroStockBajo.value.trim()) {
        params.append("stock_bajo", filtroStockBajo.value.trim());
    }

    if (filtroOrden.value) {
        params.append("orden", filtroOrden.value);
        params.append("direccion", filtroDireccion.value);
    }

    const query = params.toString();
    return query ? `?${query}` : "";
}

async function cargarProductos() {
    try {
        const response = await fetch(`${API_URL}/productos/${construirQueryProductos()}`);
        const productos = await response.json();

        if (!response.ok) {
            throw new Error(productos.mensaje || "Error al cargar productos");
        }

        renderProductos(productos);
        renderAlertas(productos);
        actualizarMetricasLocales(productos);
    } catch (error) {
        mostrarMensaje(error.message, "error");
    }
}

async function cargarVentas() {
    try {
        const response = await fetch(`${API_URL}/ventas/`);
        const ventas = await response.json();

        if (!response.ok) {
            throw new Error(ventas.mensaje || "Error al cargar ventas");
        }

        renderVentas(ventas);
    } catch (error) {
        mostrarMensaje(error.message, "error");
    }
}

async function cargarResumen() {
    try {
        const response = await fetch(`${API_URL}/dashboard/resumen`);
        const resumen = await response.json();

        if (!response.ok) {
            throw new Error(resumen.mensaje || "Error al cargar resumen");
        }

        metricProductos.textContent = resumen.total_productos;
        metricStock.textContent = resumen.total_stock;
        metricStockBajo.textContent = resumen.stock_bajo;
        metricValor.textContent = formatearPrecio(resumen.valor_inventario);
        metricVentas.textContent = resumen.total_ventas;
        metricUnidadesVendidas.textContent = resumen.unidades_vendidas;
    } catch (error) {
        mostrarMensaje(error.message, "error");
    }
}

async function cargarMasVendidos() {
    try {
        const response = await fetch(`${API_URL}/dashboard/mas-vendidos`);
        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.mensaje || "Error al cargar productos más vendidos");
        }

        renderMasVendidos(data);
    } catch (error) {
        mostrarMensaje(error.message, "error");
    }
}

async function cargarMovimientosRecientes() {
    try {
        const response = await fetch(`${API_URL}/dashboard/movimientos-recientes`);
        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.mensaje || "Error al cargar movimientos recientes");
        }

        renderMovimientos(data);
    } catch (error) {
        mostrarMensaje(error.message, "error");
    }
}

function actualizarMetricasLocales(productos) {
    contadorProductos.textContent = `${productos.length} producto(s)`;
}

function renderProductos(productos) {
    listaProductos.innerHTML = "";

    if (productos.length === 0) {
        listaProductos.innerHTML = `<div class="empty-state">No hay productos para mostrar.</div>`;
        return;
    }

    productos.forEach(producto => {
        const card = document.createElement("article");
        card.className = "producto-card";

        card.innerHTML = `
            <div class="producto-header">
                <div>
                    <div class="producto-nombre">${producto.nombre}</div>
                    <div class="producto-precio">${formatearPrecio(producto.precio)}</div>
                </div>
                <span class="tag">ID: ${producto.id}</span>
            </div>

            <div class="producto-stock ${obtenerClaseStock(producto.stock)}">
                Stock actual: ${producto.stock}
            </div>

            <div class="inline-actions">
                <input type="number" min="1" value="1" id="cantidad-${producto.id}">
                <button class="btn btn-success">Vender</button>
                <button class="btn btn-secondary">+ Stock</button>
            </div>

            <div class="card-actions">
                <button class="btn btn-primary">Editar</button>
                <button class="btn btn-danger">Eliminar</button>
                <button class="btn btn-secondary">Ver ventas</button>
                <button class="btn btn-secondary">Ajustar stock</button>
            </div>
        `;

        const inputCantidad = card.querySelector(`#cantidad-${producto.id}`);
        const botonesInline = card.querySelectorAll(".inline-actions .btn");
        const botonesAccion = card.querySelectorAll(".card-actions .btn");

        botonesInline[0].addEventListener("click", () => venderProducto(producto.id, inputCantidad.value));
        botonesInline[1].addEventListener("click", () => agregarStock(producto.id, inputCantidad.value));

        botonesAccion[0].addEventListener("click", () => cargarProductoEnFormulario(producto.id));
        botonesAccion[1].addEventListener("click", () => eliminarProducto(producto.id));
        botonesAccion[2].addEventListener("click", () => cargarVentasPorProducto(producto.id, producto.nombre));
        botonesAccion[3].addEventListener("click", () => ajustarStockManual(producto));

        listaProductos.appendChild(card);
    });
}

function renderVentas(ventas) {
    listaVentas.innerHTML = "";

    if (ventas.length === 0) {
        listaVentas.innerHTML = `<div class="empty-state">Aún no hay ventas registradas.</div>`;
        return;
    }

    ventas
        .slice()
        .reverse()
        .slice(0, 10)
        .forEach(venta => {
            const item = document.createElement("article");
            item.className = "venta-item";

            item.innerHTML = `
                <strong>${venta.producto.nombre}</strong>
                <div>Cantidad vendida: ${venta.cantidad}</div>
                <div>Precio referencia: ${formatearPrecio(venta.producto.precio)}</div>
                <div>Fecha: ${formatearFecha(venta.fecha)}</div>
            `;

            listaVentas.appendChild(item);
        });
}

function renderAlertas(productos) {
    listaAlertas.innerHTML = "";

    const productosBajos = productos.filter(p => p.stock <= 5);

    if (productosBajos.length === 0) {
        listaAlertas.innerHTML = `<div class="empty-state">No hay alertas de stock bajo.</div>`;
        return;
    }

    productosBajos.forEach(producto => {
        const item = document.createElement("article");
        item.className = "venta-item alerta-item";

        item.innerHTML = `
            <strong>${producto.nombre}</strong>
            <div>Stock actual: ${producto.stock}</div>
            <div>Precio: ${formatearPrecio(producto.precio)}</div>
        `;

        listaAlertas.appendChild(item);
    });
}

function renderMasVendidos(productos) {
    listaMasVendidos.innerHTML = "";

    if (productos.length === 0) {
        listaMasVendidos.innerHTML = `<div class="empty-state">No hay ventas suficientes para este reporte.</div>`;
        return;
    }

    productos.forEach((producto, index) => {
        const item = document.createElement("article");
        item.className = "venta-item top-item";

        item.innerHTML = `
            <strong>#${index + 1} - ${producto.nombre}</strong>
            <div>Total vendido: ${producto.total_vendido}</div>
            <div>Precio: ${formatearPrecio(producto.precio)}</div>
        `;

        listaMasVendidos.appendChild(item);
    });
}

function renderMovimientos(movimientos) {
    listaMovimientos.innerHTML = "";

    if (movimientos.length === 0) {
        listaMovimientos.innerHTML = `<div class="empty-state">No hay movimientos recientes.</div>`;
        return;
    }

    movimientos.forEach(movimiento => {
        const item = document.createElement("article");
        item.className = `venta-item ${obtenerClaseMovimiento(movimiento.tipo)}`;

        item.innerHTML = `
            <strong>${movimiento.producto.nombre}</strong>
            <div>Tipo: ${movimiento.tipo}</div>
            <div>Cantidad: ${movimiento.cantidad}</div>
            <div>Motivo: ${movimiento.motivo || "Sin motivo"}</div>
            <div>Fecha: ${formatearFecha(movimiento.fecha)}</div>
        `;

        listaMovimientos.appendChild(item);
    });
}

async function guardarProducto(event) {
    event.preventDefault();

    const id = inputProductoId.value;
    const payload = {
        nombre: inputNombre.value.trim(),
        precio: parseInt(inputPrecio.value),
        stock: parseInt(inputStock.value)
    };

    try {
        let response;

        if (id) {
            response = await fetch(`${API_URL}/productos/${id}`, {
                method: "PUT",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload)
            });
        } else {
            response = await fetch(`${API_URL}/productos/`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload)
            });
        }

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.mensaje || "Error al guardar producto");
        }

        mostrarMensaje(data.mensaje || "Operación exitosa");
        resetFormulario();
        await cargarDashboard();
    } catch (error) {
        mostrarMensaje(error.message, "error");
    }
}

async function eliminarProducto(id) {
    const confirmado = confirm("¿Seguro que quieres eliminar este producto?");
    if (!confirmado) return;

    try {
        const response = await fetch(`${API_URL}/productos/${id}`, {
            method: "DELETE"
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.mensaje || "Error al eliminar producto");
        }

        mostrarMensaje(data.mensaje || "Producto eliminado");
        await cargarDashboard();
    } catch (error) {
        mostrarMensaje(error.message, "error");
    }
}

async function venderProducto(id, cantidad) {
    try {
        const response = await fetch(`${API_URL}/productos/${id}/vender`, {
            method: "PUT",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                cantidad: parseInt(cantidad)
            })
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.mensaje || "Error al vender producto");
        }

        mostrarMensaje(data.mensaje || "Venta realizada");
        await cargarDashboard();
    } catch (error) {
        mostrarMensaje(error.message, "error");
    }
}

async function agregarStock(id, cantidad) {
    try {
        const response = await fetch(`${API_URL}/productos/${id}/stock`, {
            method: "PUT",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                cantidad: parseInt(cantidad)
            })
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.mensaje || "Error al agregar stock");
        }

        mostrarMensaje(data.mensaje || "Stock actualizado");
        await cargarDashboard();
    } catch (error) {
        mostrarMensaje(error.message, "error");
    }
}

async function ajustarStockManual(producto) {
    const nuevoStockTexto = prompt(`Stock actual de ${producto.nombre}: ${producto.stock}\nIngresa el nuevo stock:`);
    if (nuevoStockTexto === null) return;

    const motivo = prompt("Motivo del ajuste:", "Ajuste manual desde dashboard");
    if (motivo === null) return;

    const nuevoStock = parseInt(nuevoStockTexto);

    try {
        const response = await fetch(`${API_URL}/productos/${producto.id}/ajustar-stock`, {
            method: "PUT",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                nuevo_stock: nuevoStock,
                motivo: motivo
            })
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.mensaje || "Error al ajustar stock");
        }

        mostrarMensaje(data.mensaje || "Stock ajustado");
        await cargarDashboard();
    } catch (error) {
        mostrarMensaje(error.message, "error");
    }
}

async function cargarProductoEnFormulario(id) {
    try {
        const response = await fetch(`${API_URL}/productos/${id}`);
        const producto = await response.json();

        if (!response.ok) {
            throw new Error(producto.mensaje || "Error al cargar producto");
        }

        inputProductoId.value = producto.id;
        inputNombre.value = producto.nombre;
        inputPrecio.value = producto.precio;
        inputStock.value = producto.stock;

        formTitle.textContent = "Editar producto";
        btnCancelarEdicion.classList.remove("oculto");
        window.scrollTo({ top: 0, behavior: "smooth" });
    } catch (error) {
        mostrarMensaje(error.message, "error");
    }
}

async function cargarVentasPorProducto(id, nombre) {
    try {
        const response = await fetch(`${API_URL}/productos/${id}/ventas`);
        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.mensaje || "Error al cargar ventas del producto");
        }

        listaVentas.innerHTML = "";

        if (data.ventas.length === 0) {
            listaVentas.innerHTML = `<div class="empty-state">No hay ventas registradas para ${nombre}.</div>`;
            return;
        }

        data.ventas
            .slice()
            .reverse()
            .forEach(venta => {
                const item = document.createElement("article");
                item.className = "venta-item";

                item.innerHTML = `
                    <strong>${nombre}</strong>
                    <div>Cantidad vendida: ${venta.cantidad}</div>
                    <div>Fecha: ${formatearFecha(venta.fecha)}</div>
                `;

                listaVentas.appendChild(item);
            });

        mostrarMensaje(`Mostrando ventas de ${nombre}`);
    } catch (error) {
        mostrarMensaje(error.message, "error");
    }
}

function resetFormulario() {
    formProducto.reset();
    inputProductoId.value = "";
    formTitle.textContent = "Agregar producto";
    btnCancelarEdicion.classList.add("oculto");
}

function limpiarFiltros() {
    filtroNombre.value = "";
    filtroStockBajo.value = "";
    filtroOrden.value = "";
    filtroDireccion.value = "asc";
    cargarProductos();
}