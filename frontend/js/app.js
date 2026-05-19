const API_URL = window.DULCERIA_API_URL ||
    localStorage.getItem("dulceria_api_url") ||
    (window.location.protocol.startsWith("http") ? window.location.origin : "http://127.0.0.1:5000");
let deferredInstallPrompt = null;
let productoOperacionActual = null;

const loginView = document.getElementById("login-view");
const appView = document.getElementById("app-view");
const loginForm = document.getElementById("login-form");
const btnCrearAdmin = document.getElementById("btn-crear-admin");
const btnLogout = document.getElementById("btn-logout");
const usuarioLogueado = document.getElementById("usuario-logueado");
const authMessage = document.getElementById("auth-message");
const connectionStatus = document.getElementById("connection-status");
const btnInstallApp = document.getElementById("btn-install-app");

const listaProductos = document.getElementById("lista-productos");
const listaVentas = document.getElementById("lista-ventas");
const listaAlertas = document.getElementById("lista-alertas");
const listaMasVendidos = document.getElementById("lista-mas-vendidos");
const listaMovimientos = document.getElementById("lista-movimientos");
const listaCategorias = document.getElementById("lista-categorias");
const mensaje = document.getElementById("mensaje");

const formProducto = document.getElementById("form-producto");
const formTitle = document.getElementById("form-title");
const btnCancelarEdicion = document.getElementById("btn-cancelar-edicion");

const inputProductoId = document.getElementById("producto-id");
const inputNombre = document.getElementById("nombre");
const inputPrecio = document.getElementById("precio");
const inputCosto = document.getElementById("costo");
const inputStock = document.getElementById("stock");
const inputStockMinimo = document.getElementById("stock-minimo");
const inputCategoria = document.getElementById("categoria");
const inputProveedor = document.getElementById("proveedor");
const inputSku = document.getElementById("sku");
const inputNuevaCategoria = document.getElementById("nueva-categoria");

const filtroNombre = document.getElementById("filtro-nombre");
const filtroStockBajo = document.getElementById("filtro-stock-bajo");
const filtroCategoria = document.getElementById("filtro-categoria");
const filtroOrden = document.getElementById("orden");
const filtroDireccion = document.getElementById("direccion");

const metricProductos = document.getElementById("metric-productos");
const metricStock = document.getElementById("metric-stock");
const metricStockBajo = document.getElementById("metric-stock-bajo");
const metricValor = document.getElementById("metric-valor");
const metricCostoInventario = document.getElementById("metric-costo-inventario");
const metricIngresosVentas = document.getElementById("metric-ingresos-ventas");
const metricUtilidadVentas = document.getElementById("metric-utilidad-ventas");
const metricVentas = document.getElementById("metric-ventas");
const metricUnidadesVendidas = document.getElementById("metric-unidades-vendidas");
const contadorProductos = document.getElementById("contador-productos");

const modalAjusteStock = document.getElementById("modal-ajuste-stock");
const formAjusteStock = document.getElementById("form-ajuste-stock");
const btnCerrarAjuste = document.getElementById("btn-cerrar-ajuste");
const ajusteProductoTitulo = document.getElementById("ajuste-producto-titulo");
const ajusteProductoId = document.getElementById("ajuste-producto-id");
const ajusteStockActual = document.getElementById("ajuste-stock-actual");
const ajusteNuevoStock = document.getElementById("ajuste-nuevo-stock");
const ajusteMotivo = document.getElementById("ajuste-motivo");

const modalAdminInicial = document.getElementById("modal-admin-inicial");
const formAdminInicial = document.getElementById("form-admin-inicial");
const btnCerrarAdmin = document.getElementById("btn-cerrar-admin");
const inputAdminUsername = document.getElementById("admin-username");
const inputAdminPassword = document.getElementById("admin-password");

const modalOperacionProducto = document.getElementById("modal-operacion-producto");
const formOperacionProducto = document.getElementById("form-operacion-producto");
const btnCerrarOperacion = document.getElementById("btn-cerrar-operacion");
const operacionProductoEyebrow = document.getElementById("operacion-producto-eyebrow");
const operacionProductoTitulo = document.getElementById("operacion-producto-titulo");
const operacionProductoId = document.getElementById("operacion-producto-id");
const operacionProductoTipo = document.getElementById("operacion-producto-tipo");
const operacionProductoPrecio = document.getElementById("operacion-producto-precio");
const operacionProductoStock = document.getElementById("operacion-producto-stock");
const operacionProductoCantidad = document.getElementById("operacion-producto-cantidad");
const operacionProductoAyuda = document.getElementById("operacion-producto-ayuda");
const btnConfirmarOperacion = document.getElementById("btn-confirmar-operacion");

const modalConfirmacion = document.getElementById("modal-confirmacion");
const formConfirmacion = document.getElementById("form-confirmacion");
const btnCerrarConfirmacion = document.getElementById("btn-cerrar-confirmacion");
const btnCancelarConfirmacion = document.getElementById("btn-cancelar-confirmacion");
const confirmacionEyebrow = document.getElementById("confirmacion-eyebrow");
const confirmacionTitulo = document.getElementById("confirmacion-titulo");
const confirmacionTexto = document.getElementById("confirmacion-texto");
const confirmacionTipo = document.getElementById("confirmacion-tipo");
const confirmacionId = document.getElementById("confirmacion-id");

document.getElementById("btn-filtrar").addEventListener("click", cargarProductos);
document.getElementById("btn-limpiar-filtros").addEventListener("click", limpiarFiltros);
document.getElementById("btn-recargar").addEventListener("click", cargarDashboard);
document.getElementById("btn-crear-categoria").addEventListener("click", crearCategoria);
btnCancelarEdicion.addEventListener("click", resetFormulario);
formProducto.addEventListener("submit", guardarProducto);
loginForm.addEventListener("submit", iniciarSesion);
btnCrearAdmin.addEventListener("click", abrirModalAdminInicial);
btnLogout.addEventListener("click", cerrarSesion);
btnInstallApp.addEventListener("click", instalarApp);
formAdminInicial.addEventListener("submit", crearAdminInicial);
btnCerrarAdmin.addEventListener("click", () => cerrarDialog(modalAdminInicial));
formOperacionProducto.addEventListener("submit", guardarOperacionProducto);
btnCerrarOperacion.addEventListener("click", () => cerrarDialog(modalOperacionProducto));
formAjusteStock.addEventListener("submit", guardarAjusteStock);
btnCerrarAjuste.addEventListener("click", cerrarModalAjuste);
formConfirmacion.addEventListener("submit", ejecutarConfirmacion);
btnCerrarConfirmacion.addEventListener("click", () => cerrarDialog(modalConfirmacion));
btnCancelarConfirmacion.addEventListener("click", () => cerrarDialog(modalConfirmacion));
window.addEventListener("online", actualizarEstadoConexion);
window.addEventListener("offline", actualizarEstadoConexion);
window.addEventListener("beforeinstallprompt", prepararInstalacion);

document.querySelectorAll("[data-scroll-target]").forEach(button => {
    button.addEventListener("click", () => navegarASeccion(button));
});

document.addEventListener("DOMContentLoaded", () => {
    actualizarEstadoConexion();
    registrarServiceWorker();
    verificarSesion();
});

async function apiFetch(url, options = {}) {
    const response = await fetch(url, {
        ...options,
        credentials: "include",
        headers: {
            "Content-Type": "application/json",
            ...(options.headers || {})
        }
    });

    return response;
}

function registrarServiceWorker() {
    if (!("serviceWorker" in navigator) || window.location.protocol === "file:") {
        return;
    }

    if (["localhost", "127.0.0.1"].includes(window.location.hostname)) {
        limpiarCacheLocal();
        return;
    }

    navigator.serviceWorker.register("./sw.js").catch(error => {
        console.warn("No se pudo registrar el service worker", error);
    });
}

async function limpiarCacheLocal() {
    const registrations = await navigator.serviceWorker.getRegistrations();
    await Promise.all(registrations.map(registration => registration.unregister()));

    if ("caches" in window) {
        const keys = await caches.keys();
        await Promise.all(keys.map(key => caches.delete(key)));
    }
}

function prepararInstalacion(event) {
    event.preventDefault();
    deferredInstallPrompt = event;
    btnInstallApp.classList.remove("oculto");
}

async function instalarApp() {
    if (!deferredInstallPrompt) {
        return;
    }

    deferredInstallPrompt.prompt();
    await deferredInstallPrompt.userChoice;
    deferredInstallPrompt = null;
    btnInstallApp.classList.add("oculto");
}

function actualizarEstadoConexion() {
    if (!connectionStatus) return;

    if (navigator.onLine) {
        connectionStatus.textContent = "En línea";
        connectionStatus.className = "tag status-online";
    } else {
        connectionStatus.textContent = "Sin conexión";
        connectionStatus.className = "tag status-offline";
    }
}

async function verificarSesion() {
    try {
        const response = await apiFetch(`${API_URL}/auth/me`, {
            method: "GET"
        });

        const data = await response.json();

        if (data.autenticado) {
            usuarioLogueado.textContent = data.usuario.username;
            mostrarApp();
            await cargarDashboard();
        } else {
            mostrarLogin();
        }
    } catch (error) {
        mostrarLogin();
    }
}

function mostrarLogin() {
    loginView.classList.remove("oculto");
    appView.classList.add("oculto");
}

function mostrarApp() {
    loginView.classList.add("oculto");
    appView.classList.remove("oculto");
}

function abrirDialog(dialog) {
    if (typeof dialog.showModal === "function") {
        dialog.showModal();
    } else {
        dialog.classList.add("dialog-visible");
    }
}

function cerrarDialog(dialog) {
    if (typeof dialog.close === "function") {
        dialog.close();
    } else {
        dialog.classList.remove("dialog-visible");
    }
}

function mostrarAuthMensaje(texto, tipo = "exito") {
    authMessage.textContent = texto;
    authMessage.className = `mensaje mensaje-${tipo}`;
    authMessage.classList.remove("oculto");
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

function obtenerPrecioVenta(producto) {
    return producto.precio_venta ?? producto.precio ?? 0;
}

function obtenerCosto(producto) {
    return producto.costo ?? 0;
}

function obtenerStockMinimo(producto) {
    return producto.stock_minimo ?? 5;
}

function formatearFecha(fecha) {
    return new Date(fecha).toLocaleString("es-CO");
}

function navegarASeccion(button) {
    const target = document.getElementById(button.dataset.scrollTarget);
    if (!target) return;

    document.querySelectorAll("[data-scroll-target]").forEach(tab => tab.classList.remove("active"));
    button.classList.add("active");
    target.scrollIntoView({ behavior: "smooth", block: "start" });
}

function obtenerClaseStock(stock, stockMinimo = 5) {
    if (stock <= Math.max(1, Math.floor(stockMinimo / 2))) return "stock-critico";
    if (stock <= stockMinimo) return "stock-bajo";
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

    if (filtroCategoria.value) {
        params.append("categoria_id", filtroCategoria.value);
    }

    if (filtroOrden.value) {
        params.append("orden", filtroOrden.value);
        params.append("direccion", filtroDireccion.value);
    }

    const query = params.toString();
    return query ? `?${query}` : "";
}

async function iniciarSesion(event) {
    event.preventDefault();

    const username = document.getElementById("login-username").value.trim();
    const password = document.getElementById("login-password").value;

    if (!username || !password) {
        mostrarAuthMensaje("Ingresa usuario y contraseña", "error");
        return;
    }

    try {
        const response = await apiFetch(`${API_URL}/auth/login`, {
            method: "POST",
            body: JSON.stringify({ username, password })
        });

        const data = await response.json();

        if (!response.ok) {
            mostrarAuthMensaje(data.mensaje || "No se pudo iniciar sesión", "error");
            return;
        }

        usuarioLogueado.textContent = data.usuario.username;
        mostrarApp();
        await cargarDashboard();
    } catch (error) {
        mostrarAuthMensaje("No fue posible conectar con la API", "error");
    }
}

function abrirModalAdminInicial() {
    formAdminInicial.reset();
    inputAdminUsername.value = "admin";
    abrirDialog(modalAdminInicial);
    inputAdminUsername.focus();
    inputAdminUsername.select();
}

async function crearAdminInicial(event) {
    event.preventDefault();

    const username = inputAdminUsername.value.trim();
    const password = inputAdminPassword.value;

    if (!username || !password) {
        mostrarAuthMensaje("Ingresa usuario y contraseña para el administrador", "error");
        return;
    }

    try {
        const response = await apiFetch(`${API_URL}/auth/register`, {
            method: "POST",
            body: JSON.stringify({ username, password })
        });

        const data = await response.json();

        if (!response.ok) {
            mostrarAuthMensaje(data.mensaje || "No se pudo crear el usuario", "error");
            return;
        }

        cerrarDialog(modalAdminInicial);
        mostrarAuthMensaje(data.mensaje || "Usuario creado");
    } catch (error) {
        console.error(error);
        mostrarAuthMensaje("No fue posible crear el usuario. Revisa que la API esté activa.", "error");
    }
}

async function cerrarSesion() {
    try {
        await apiFetch(`${API_URL}/auth/logout`, {
            method: "POST"
        });

        mostrarLogin();
        loginForm.reset();
        mostrarAuthMensaje("Sesión cerrada correctamente");
    } catch (error) {
        mostrarMensaje("Error al cerrar sesión", "error");
    }
}

async function cargarDashboard() {
    await Promise.all([
        cargarCategorias(),
        cargarProductos(),
        cargarVentas(),
        cargarResumen(),
        cargarMasVendidos(),
        cargarMovimientosRecientes()
    ]);
}

async function cargarCategorias() {
    try {
        const response = await apiFetch(`${API_URL}/categorias/`);
        const categorias = await response.json();

        if (!response.ok) {
            throw new Error(categorias.mensaje || "Error al cargar categorías");
        }

        renderCategorias(categorias);
        renderSelectCategorias(categorias);
    } catch (error) {
        mostrarMensaje(error.message, "error");
    }
}

async function cargarProductos() {
    try {
        const response = await apiFetch(`${API_URL}/productos/${construirQueryProductos()}`);
        const productos = await response.json();

        if (response.status === 401) {
            mostrarLogin();
            return;
        }

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
        const response = await apiFetch(`${API_URL}/ventas/`);
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
        const response = await apiFetch(`${API_URL}/dashboard/resumen`);
        const resumen = await response.json();

        if (!response.ok) {
            throw new Error(resumen.mensaje || "Error al cargar resumen");
        }

        metricProductos.textContent = resumen.total_productos;
        metricStock.textContent = resumen.total_stock;
        metricStockBajo.textContent = resumen.stock_bajo;
        metricValor.textContent = formatearPrecio(resumen.valor_inventario || 0);
        metricCostoInventario.textContent = formatearPrecio(resumen.costo_inventario || 0);
        metricIngresosVentas.textContent = formatearPrecio(resumen.ingresos_ventas || 0);
        metricUtilidadVentas.textContent = formatearPrecio(resumen.utilidad_ventas || 0);
        metricVentas.textContent = resumen.total_ventas;
        metricUnidadesVendidas.textContent = resumen.unidades_vendidas;
    } catch (error) {
        mostrarMensaje(error.message, "error");
    }
}

async function cargarMasVendidos() {
    try {
        const response = await apiFetch(`${API_URL}/dashboard/mas-vendidos`);
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
        const response = await apiFetch(`${API_URL}/dashboard/movimientos-recientes`);
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

function renderCategorias(categorias) {
    listaCategorias.innerHTML = "";

    if (categorias.length === 0) {
        listaCategorias.innerHTML = `<div class="empty-state">No hay categorías creadas.</div>`;
        return;
    }

    categorias.forEach(categoria => {
        const item = document.createElement("article");
        item.className = "categoria-item";

        item.innerHTML = `
            <span>${categoria.nombre}</span>
            <button class="btn btn-danger">Eliminar</button>
        `;

        const btnEliminar = item.querySelector("button");
        btnEliminar.addEventListener("click", () => eliminarCategoria(categoria));

        listaCategorias.appendChild(item);
    });
}

function renderSelectCategorias(categorias) {
    inputCategoria.innerHTML = `<option value="">Sin categoría</option>`;
    filtroCategoria.innerHTML = `<option value="">Todas</option>`;

    categorias.forEach(categoria => {
        inputCategoria.innerHTML += `<option value="${categoria.id}">${categoria.nombre}</option>`;
        filtroCategoria.innerHTML += `<option value="${categoria.id}">${categoria.nombre}</option>`;
    });
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
        const precioVenta = obtenerPrecioVenta(producto);
        const costo = obtenerCosto(producto);
        const stockMinimo = obtenerStockMinimo(producto);
        const utilidad = precioVenta - costo;

        card.innerHTML = `
            <div class="producto-header">
                <div>
                    <div class="producto-nombre">${producto.nombre}</div>
                    <div class="producto-precio">${formatearPrecio(precioVenta)}</div>
                </div>
                <span class="tag">${producto.sku ? producto.sku : `ID: ${producto.id}`}</span>
            </div>

            <div>
                ${producto.categoria ? `<span class="categoria-badge">${producto.categoria.nombre}</span>` : `<span class="tag">Sin categoría</span>`}
            </div>

            <div class="producto-stock ${obtenerClaseStock(producto.stock, stockMinimo)}">
                Stock actual: ${producto.stock} · mínimo: ${stockMinimo}
            </div>

            <div class="producto-meta">
                <span>Costo: ${formatearPrecio(costo)}</span>
                <span>Utilidad/u: ${formatearPrecio(utilidad)}</span>
                <span>Proveedor: ${producto.proveedor || "Sin proveedor"}</span>
            </div>

            <div class="inline-actions">
                <input type="number" min="1" value="1" inputmode="numeric" id="cantidad-${producto.id}" aria-label="Cantidad para ${producto.nombre}">
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

        botonesInline[0].addEventListener("click", () => abrirOperacionProducto(producto, "venta", inputCantidad.value));
        botonesInline[1].addEventListener("click", () => abrirOperacionProducto(producto, "entrada", inputCantidad.value));

        botonesAccion[0].addEventListener("click", () => cargarProductoEnFormulario(producto.id));
        botonesAccion[1].addEventListener("click", () => eliminarProducto(producto));
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
                <div>Total venta: ${formatearPrecio(venta.total || 0)}</div>
                <div>Utilidad estimada: ${formatearPrecio(venta.utilidad || 0)}</div>
                <div>Precio unitario: ${formatearPrecio(venta.precio_unitario || venta.producto.precio)}</div>
                <div>Fecha: ${formatearFecha(venta.fecha)}</div>
            `;

            listaVentas.appendChild(item);
        });
}

function renderAlertas(productos) {
    listaAlertas.innerHTML = "";

    const productosBajos = productos.filter(p => p.stock <= obtenerStockMinimo(p));

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
            <div>Stock mínimo: ${obtenerStockMinimo(producto)}</div>
            <div>Categoría: ${producto.categoria ? producto.categoria.nombre : "Sin categoría"}</div>
            <div>Precio: ${formatearPrecio(obtenerPrecioVenta(producto))}</div>
            <div>Proveedor: ${producto.proveedor || "Sin proveedor"}</div>
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
            <div>Ingresos: ${formatearPrecio(producto.ingresos || 0)}</div>
            <div>Utilidad: ${formatearPrecio(producto.utilidad || 0)}</div>
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

async function crearCategoria() {
    const nombre = inputNuevaCategoria.value.trim();

    if (!nombre) {
        mostrarMensaje("Debes ingresar un nombre para la categoría", "error");
        return;
    }

    try {
        const response = await apiFetch(`${API_URL}/categorias/`, {
            method: "POST",
            body: JSON.stringify({ nombre })
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.mensaje || "Error al crear categoría");
        }

        inputNuevaCategoria.value = "";
        mostrarMensaje(data.mensaje || "Categoría creada");
        await cargarCategorias();
    } catch (error) {
        mostrarMensaje(error.message, "error");
    }
}

function eliminarCategoria(categoria) {
    abrirConfirmacion({
        tipo: "categoria",
        id: categoria.id,
        eyebrow: "Categoría",
        titulo: "Eliminar categoría",
        texto: `Vas a eliminar la categoría "${categoria.nombre}". Solo se podrá eliminar si no tiene productos asociados.`
    });
}

function abrirConfirmacion({ tipo, id, eyebrow, titulo, texto }) {
    confirmacionTipo.value = tipo;
    confirmacionId.value = id;
    confirmacionEyebrow.textContent = eyebrow;
    confirmacionTitulo.textContent = titulo;
    confirmacionTexto.textContent = texto;
    abrirDialog(modalConfirmacion);
}

async function ejecutarConfirmacion(event) {
    event.preventDefault();

    const tipo = confirmacionTipo.value;
    const id = confirmacionId.value;

    if (!tipo || !id) {
        cerrarDialog(modalConfirmacion);
        return;
    }

    if (tipo === "producto") {
        await eliminarProductoConfirmado(id);
    }

    if (tipo === "categoria") {
        await eliminarCategoriaConfirmada(id);
    }
}

async function eliminarCategoriaConfirmada(id) {
    try {
        const response = await apiFetch(`${API_URL}/categorias/${id}`, {
            method: "DELETE"
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.mensaje || "Error al eliminar categoría");
        }

        cerrarDialog(modalConfirmacion);
        mostrarMensaje(data.mensaje || "Categoría eliminada");
        await cargarCategorias();
        await cargarProductos();
    } catch (error) {
        mostrarMensaje(error.message, "error");
    }
}

async function guardarProducto(event) {
    event.preventDefault();

    const id = inputProductoId.value;
    const payload = {
        nombre: inputNombre.value.trim(),
        precio_venta: parseInt(inputPrecio.value),
        costo: inputCosto.value === "" ? 0 : parseInt(inputCosto.value),
        stock: parseInt(inputStock.value),
        stock_minimo: inputStockMinimo.value === "" ? 5 : parseInt(inputStockMinimo.value),
        categoria_id: inputCategoria.value ? parseInt(inputCategoria.value) : null,
        proveedor: inputProveedor.value.trim() || null,
        sku: inputSku.value.trim() || null
    };

    try {
        let response;

        if (id) {
            response = await apiFetch(`${API_URL}/productos/${id}`, {
                method: "PUT",
                body: JSON.stringify(payload)
            });
        } else {
            response = await apiFetch(`${API_URL}/productos/`, {
                method: "POST",
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

function eliminarProducto(producto) {
    abrirConfirmacion({
        tipo: "producto",
        id: producto.id,
        eyebrow: "Producto",
        titulo: "Eliminar producto",
        texto: `Vas a eliminar "${producto.nombre}". Esta acción también afecta su historial asociado si la base lo permite.`
    });
}

async function eliminarProductoConfirmado(id) {
    try {
        const response = await apiFetch(`${API_URL}/productos/${id}`, {
            method: "DELETE"
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.mensaje || "Error al eliminar producto");
        }

        cerrarDialog(modalConfirmacion);
        mostrarMensaje(data.mensaje || "Producto eliminado");
        await cargarDashboard();
    } catch (error) {
        mostrarMensaje(error.message, "error");
    }
}

function abrirOperacionProducto(producto, tipo, cantidadSugerida = 1) {
    const cantidad = parseInt(cantidadSugerida);
    productoOperacionActual = producto;

    operacionProductoId.value = producto.id;
    operacionProductoTipo.value = tipo;
    operacionProductoTitulo.textContent = producto.nombre;
    operacionProductoPrecio.textContent = `Venta: ${formatearPrecio(obtenerPrecioVenta(producto))}`;
    operacionProductoStock.textContent = `Stock actual: ${producto.stock} · mínimo: ${obtenerStockMinimo(producto)}`;
    operacionProductoCantidad.value = Number.isNaN(cantidad) || cantidad < 1 ? 1 : cantidad;

    if (tipo === "venta") {
        operacionProductoEyebrow.textContent = "Registrar venta";
        operacionProductoAyuda.textContent = `Se descontarán unidades del inventario. Disponible: ${producto.stock}.`;
        btnConfirmarOperacion.textContent = "Registrar venta";
        btnConfirmarOperacion.className = "btn btn-success";
    } else {
        operacionProductoEyebrow.textContent = "Ingreso de stock";
        operacionProductoAyuda.textContent = "Se sumarán unidades al stock actual.";
        btnConfirmarOperacion.textContent = "Agregar stock";
        btnConfirmarOperacion.className = "btn btn-primary";
    }

    abrirDialog(modalOperacionProducto);
    operacionProductoCantidad.focus();
    operacionProductoCantidad.select();
}

async function guardarOperacionProducto(event) {
    event.preventDefault();

    const id = operacionProductoId.value;
    const tipo = operacionProductoTipo.value;
    const cantidad = parseInt(operacionProductoCantidad.value);

    if (!id || Number.isNaN(cantidad) || cantidad <= 0) {
        mostrarMensaje("Ingresa una cantidad válida", "error");
        return;
    }

    if (tipo === "venta" && productoOperacionActual && cantidad > productoOperacionActual.stock) {
        mostrarMensaje("No hay stock suficiente para esa venta", "error");
        return;
    }

    const operacionExitosa = tipo === "venta"
        ? await venderProducto(id, cantidad)
        : await agregarStock(id, cantidad);

    if (operacionExitosa) {
        cerrarDialog(modalOperacionProducto);
    }
}

async function venderProducto(id, cantidad) {
    try {
        const response = await apiFetch(`${API_URL}/productos/${id}/vender`, {
            method: "PUT",
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
        return true;
    } catch (error) {
        mostrarMensaje(error.message, "error");
        return false;
    }
}

async function agregarStock(id, cantidad) {
    try {
        const response = await apiFetch(`${API_URL}/productos/${id}/stock`, {
            method: "PUT",
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
        return true;
    } catch (error) {
        mostrarMensaje(error.message, "error");
        return false;
    }
}

async function ajustarStockManual(producto) {
    ajusteProductoTitulo.textContent = producto.nombre;
    ajusteProductoId.value = producto.id;
    ajusteStockActual.value = producto.stock;
    ajusteNuevoStock.value = producto.stock;
    ajusteMotivo.value = "Ajuste manual desde dashboard";

    abrirDialog(modalAjusteStock);

    ajusteNuevoStock.focus();
    ajusteNuevoStock.select();
}

function cerrarModalAjuste() {
    cerrarDialog(modalAjusteStock);
}

async function guardarAjusteStock(event) {
    event.preventDefault();

    const id = ajusteProductoId.value;
    const nuevoStock = parseInt(ajusteNuevoStock.value);
    const motivo = ajusteMotivo.value.trim() || "Ajuste manual desde dashboard";

    if (!id || Number.isNaN(nuevoStock) || nuevoStock < 0) {
        mostrarMensaje("Ingresa un stock válido", "error");
        return;
    }

    try {
        const response = await apiFetch(`${API_URL}/productos/${id}/ajustar-stock`, {
            method: "PUT",
            body: JSON.stringify({
                nuevo_stock: nuevoStock,
                motivo
            })
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.mensaje || "Error al ajustar stock");
        }

        cerrarModalAjuste();
        mostrarMensaje(data.mensaje || "Stock ajustado");
        await cargarDashboard();
    } catch (error) {
        mostrarMensaje(error.message, "error");
    }
}

async function cargarProductoEnFormulario(id) {
    try {
        const response = await apiFetch(`${API_URL}/productos/${id}`);
        const producto = await response.json();

        if (!response.ok) {
            throw new Error(producto.mensaje || "Error al cargar producto");
        }

        inputProductoId.value = producto.id;
        inputNombre.value = producto.nombre;
        inputPrecio.value = obtenerPrecioVenta(producto);
        inputCosto.value = obtenerCosto(producto);
        inputStock.value = producto.stock;
        inputStockMinimo.value = obtenerStockMinimo(producto);
        inputCategoria.value = producto.categoria_id || "";
        inputProveedor.value = producto.proveedor || "";
        inputSku.value = producto.sku || "";

        formTitle.textContent = "Editar producto";
        btnCancelarEdicion.classList.remove("oculto");
        window.scrollTo({ top: 0, behavior: "smooth" });
    } catch (error) {
        mostrarMensaje(error.message, "error");
    }
}

async function cargarVentasPorProducto(id, nombre) {
    try {
        const response = await apiFetch(`${API_URL}/productos/${id}/ventas`);
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
                    <div>Total venta: ${formatearPrecio(venta.total || 0)}</div>
                    <div>Utilidad estimada: ${formatearPrecio(venta.utilidad || 0)}</div>
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
    inputCategoria.value = "";
    inputStockMinimo.value = "";
    inputProveedor.value = "";
    inputSku.value = "";
    formTitle.textContent = "Agregar producto";
    btnCancelarEdicion.classList.add("oculto");
}

function limpiarFiltros() {
    filtroNombre.value = "";
    filtroStockBajo.value = "";
    filtroCategoria.value = "";
    filtroOrden.value = "";
    filtroDireccion.value = "asc";
    cargarProductos();
}
