const lista = document.getElementById('lista-productos');

fetch("http://127.0.0.1:5000/productos/")
    .then(response => {
        if (!response.ok) {
            throw new Error("Error al obtener productos");
        }
        return response.json();
    })
    .then(data => {
        data.forEach(producto => {
            const li = document.createElement('li');
            li.textContent = `${producto.nombre} - $${producto.precio} - Stock: ${producto.stock}`;

            const btnEliminar = document.createElement("button");
            btnEliminar.textContent = "Eliminar";
            btnEliminar.onclick = () => eliminarProducto(producto.id);
            li.appendChild(btnEliminar);

            const inputCantidad = document.createElement("input");
            inputCantidad.type = "number";
            inputCantidad.min = "1";
            inputCantidad.value = "1";
            inputCantidad.style.width = "50px";
            li.appendChild(inputCantidad);

            const btnVender = document.createElement("button");
            btnVender.textContent = "Vender";
            btnVender.onclick = () => venderProducto(producto.id, inputCantidad.value);
            li.appendChild(btnVender);

            lista.appendChild(li);
        });
    })
    .catch(error => {
        console.error('Error:', error);
    });

function crearProducto() {
    const nombre = document.getElementById('nombre').value;
    const precio = document.getElementById('precio').value;
    const stock = document.getElementById('stock').value;

    fetch("http://127.0.0.1:5000/productos/", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            nombre: nombre,
            precio: parseInt(precio),
            stock: parseInt(stock)
        })
    })
        .then(response => {
            if (!response.ok) {
                throw new Error("Error al crear producto");
            }
            return response.json();
        })
        .then(data => {
            console.log(data);
            location.reload();
        })
        .catch(error => console.error('Error:', error));
}

function eliminarProducto(id) {
    fetch(`http://127.0.0.1:5000/productos/${id}`, {
        method: "DELETE",
    })
        .then(response => {
            if (!response.ok) {
                throw new Error("Error al eliminar producto");
            }
            return response.json();
        })
        .then(data => {
            console.log(data);
            location.reload();
        })
        .catch(error => console.error('Error:', error));
}

function venderProducto(id, cantidad) {
    fetch(`http://127.0.0.1:5000/productos/${id}/vender`, {
        method: "PUT",
        headers: {
            "Content-Type": "application/json"
        },

        body: JSON.stringify({
            cantidad: parseInt(cantidad)
        })
    })
        .then(response => {
            if (!response.ok) {
                throw new Error("Error al vender producto");
            }
            return response.json();
        })
        .then(data => {
            console.log(data);
            location.reload();
        })
        .catch(error => console.error("Error:", error));
}