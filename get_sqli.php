<?php

if (isset($_GET['id'])) {
    //Inicializo los parámetros necesarios
    $id = $_GET['id'];
    $user = 'root';
    $pass = '';
    $db = 'prac1';
    //Creo la conexión
    $conn  = new mysqli('localhost', $user, $pass, $db);
    //Si la conexión falla aparecerá en pantalla
    if ($conn->connect_error) {
        die("Error al conectar con la BD: " . $conn->connect_error);
    }

    $sql = "SELECT Tittle, Body, Datetime FROM news where Id=$id LIMIT 0,1";

    try {
        $result = $conn->query($sql);
        $id_lower = strtolower($id);
        //En algunas pruebas como ?id=1' LIMIT 1,1 INTO @,@,@--+, $result === true devuelve 1, por lo que si no compruebo el resultado devuelvía el error
        if ($result !== true && $result->num_rows > 0 && !str_contains($id_lower, 'union')) {
            //En caso de que la query sea correcta, nos devuelve la primera fila, que presumiblemente será la del Título, Body y Datetime
            $row = $result->fetch_assoc();
            echo "<h1>" . $row["Tittle"] . "</h1>";
            echo "<h2>" . $row["Body"] . "</h2>";
            echo "<h2>" . $row["Datetime"] . "</h2>";
        } else {
            //En caso de no existir ninguna columna sobre el resultado de la query no devuelve nada.
        }
    } catch (Exception $e) {
        //Si existe cualquier error, no se mostrará por pantalla, de manera que nos deshacemos de la inyección basada en errores
    }

    $conn->close();
}
