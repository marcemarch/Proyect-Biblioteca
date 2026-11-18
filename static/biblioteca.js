function listarLibros() {

    fetch("/api/libros")
    .then(response => response.json())
    .then(data => {

        let tabla = document.getElementById("tablaLibros");
        tabla.innerHTML = "";

        for (let i = 0; i < data.length; i++) {

            let fila = tabla.insertRow();

            fila.insertCell().textContent = data[i].id;
            fila.insertCell().textContent = data[i].titulo;
            fila.insertCell().textContent = data[i].autor;
            fila.insertCell().textContent = data[i].stock;

            let celda = fila.insertCell();

            let modificar = document.createElement("a");
            modificar.textContent = "Modificar";
            modificar.href = "/modificar-libro/" + data[i].id;

            celda.appendChild(modificar);

            celda.appendChild(document.createTextNode(" | "));

            let eliminar = document.createElement("button");
            eliminar.textContent = "Eliminar";

            eliminar.onclick = function() {
                eliminarLibro(data[i].id);
            };

            celda.appendChild(eliminar);
        }

    })
    .catch(error => console.log(error));
}


function registrarLibro() {

    let titulo = document.getElementById("titulo").value;
    let autor = document.getElementById("autor").value;
    let stock = document.getElementById("stock").value;

    if (titulo.trim() == "" || autor.trim() == "" || stock == "") {
        alert("Complete todos los campos");
        return;
    }

    stock = Number(stock);

    if (!Number.isInteger(stock) || stock < 0) {
        alert("El stock debe ser un número entero no negativo");
        return;
    }

    let libro = {
        titulo: titulo,
        autor: autor,
        stock: stock
    };

    fetch("/api/libros", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(libro)
    })
    .then(response => response.json())
    .then(data => {

        if (data.error) {
            alert(data.error);
        } else {
            alert(data.mensaje);

            document.getElementById("titulo").value = "";
            document.getElementById("autor").value = "";
            document.getElementById("stock").value = "";
        }

        console.log(data);
    })
    .catch(error => {
        console.log(error);
        alert("Error de conexión con el servidor");
    });
}


function buscarLibro() {

    let id = document.getElementById("idBuscar").value;

    if (id == "" || Number(id) <= 0) {
        alert("Ingrese un ID válido");
        return;
    }

    fetch("/api/libros/" + id)
    .then(response => response.json())
    .then(data => {

        let resultado = document.getElementById("resultadoBusqueda");

        if (data.error) {
            resultado.textContent = data.error;
        } else {
            resultado.innerHTML = "";

            resultado.textContent =
                "ID: " + data.id + "\n" +
                "Título: " + data.titulo + "\n" +
                "Autor: " + data.autor + "\n" +
                "Stock: " + data.stock;
        }

        console.log(data);
    })
    .catch(error => {
        console.log(error);
        alert("Error al consultar el libro");
    });
}

function cargarLibroEditar() {

    let id = document.getElementById("editarId").value;

    fetch("/api/libros/" + id)
    .then(response => response.json())
    .then(data => {

        if (data.error) {
            alert(data.error);
            return;
        }

        document.getElementById("editarTitulo").value = data.titulo;
        document.getElementById("editarAutor").value = data.autor;
        document.getElementById("editarStock").value = data.stock;
    })
    .catch(error => console.log(error));
}


function modificarLibro() {

    let id = document.getElementById("editarId").value;
    let titulo = document.getElementById("editarTitulo").value;
    let autor = document.getElementById("editarAutor").value;
    let stock = document.getElementById("editarStock").value;
s
    if (titulo.trim() == "" || autor.trim() == "" || stock == "") {
        alert("Complete todos los campos");
        return;
    }

    stock = Number(stock);

    if (!Number.isInteger(stock) || stock < 0) {
        alert("El stock debe ser un número entero no negativo");
        return;
    }

    let libro = {
        titulo: titulo,
        autor: autor,
        stock: stock
    };

    fetch("/api/libros/" + id, {
        method: "PUT",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(libro)
    })
    .then(response => response.json())
    .then(data => {

        if (data.error) {
            alert(data.error);
        } else {
            alert(data.mensaje);

            window.location.href = "/libros";
        }

    })
    .catch(error => {
        console.log(error);
        alert("Error al modificar el libro");
    });
}


function eliminarLibro(id) {

    if (!confirm("¿Desea eliminar este libro?")) {
        return;
    }

    fetch("/api/libros/" + id, {
        method: "DELETE"
    })
    .then(response => response.json())
    .then(data => {

        if (data.error) {
            alert(data.error);
        } else {
            alert(data.mensaje);

            // Actualizar el listado
            cargarLibros();
        }
    })
    .catch(error => console.log(error));
}

function cargarLibros() {

    let select = document.getElementById("libro") ||
                 document.getElementById("prestamoLibro");

    if (!select) return;

    fetch("/api/libros")
    .then(response => response.json())
    .then(data => {

        if (data.error) {
            alert(data.error);
            return;
        }

        select.innerHTML = '<option value="">Seleccione un libro</option>';

        for (let i = 0; i < data.length; i++) {
            if (data[i].stock > 0) {
                let opcion = document.createElement("option");
                opcion.value = data[i].id;
                opcion.textContent = data[i].titulo + " - Stock: " + data[i].stock;
                select.appendChild(opcion);
            }
        }
    })
    .catch(error => console.log(error));
}

function cargarPrestamos() {

    let tabla = document.getElementById("tablaPrestamos");
    if (!tabla) return;

    fetch("/api/prestamos")
    .then(response => response.json())
    .then(data => {

        if (data.error) {
            alert(data.error);
            return;
        }

        tabla.innerHTML = "";
        let cantidad = 0;

        for (let i = 0; i < data.length; i++) {
            if (data[i].estado === "pendiente") {

                cantidad++;
                let fila = tabla.insertRow();

                fila.insertCell().textContent = data[i].id;
                fila.insertCell().textContent = data[i].libro;
                fila.insertCell().textContent = data[i].estudiante;

                let boton = document.createElement("button");
                boton.type = "button";
                boton.textContent = "Devolver";
                boton.onclick = function() {
                    devolverPrestamo(data[i].id);
                };

                fila.insertCell().appendChild(boton);
            }
        }

        if (cantidad === 0) {
            let fila = tabla.insertRow();
            let celda = fila.insertCell();
            celda.colSpan = 4;
            celda.textContent = "No hay préstamos pendientes";
        }
    })
    .catch(error => console.log(error));
}

function registrarPrestamo() {

    let select = document.getElementById("libro") ||
                 document.getElementById("prestamoLibro");
    let campo = document.getElementById("estudiante") ||
                document.getElementById("prestamoEstudiante");

    if (!select || !campo) {
        alert("No se encontraron los campos del préstamo");
        return;
    }

    let libro_id = Number(select.value);
    let estudiante = campo.value.trim();

    if (!libro_id || estudiante === "") {
        alert("Seleccione un libro y escriba el estudiante");
        return;
    }

    let prestamo = {
        libro_id: libro_id,
        estudiante: estudiante
    };

    fetch("/api/prestamos", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(prestamo)
    })
    .then(response => response.json())
    .then(data => {

        if (data.error) {
            alert(data.error);
        } else {
            alert(data.mensaje || "Préstamo registrado correctamente");
            campo.value = "";
            cargarLibros();
            cargarPrestamos();
        }
    })
    .catch(error => {
        console.log(error);
        alert("Error de conexión con el servidor");
    });
}

function devolverPrestamo(id) {

    fetch("/api/prestamos/" + id, {
        method: "PATCH"
    })
    .then(response => response.json())
    .then(data => {

        if (data.error) {
            alert(data.error);
        } else {
            alert(data.mensaje || "Devolución registrada correctamente");
            cargarLibros();
            cargarPrestamos();
        }
    })
    .catch(error => {
        console.log(error);
        alert("Error de conexión con el servidor");
    });
}