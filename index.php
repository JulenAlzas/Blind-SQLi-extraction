<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Ejercicio 1</title>
    <style>
    body {
        margin: 0;
        box-sizing: border-box;
    }
  
    .container {
        height: 100vh;
        display: flex;
        align-items: center;
        flex-direction: column;
        background: linear-gradient(to right, rgb(39, 39, 39), rgba(53, 53, 53, 0)), url('http://curiouspost.com/wp-content/uploads/2017/01/sql-injection.jpg');
        background-size: cover;
		padding-top: 100px;
        justify-content: top;
    }
  
    h1 {
        font-size: 2rem;
        color: white;
        text-transform: uppercase;
        font-weight: 600;
    }
    .button {
        background-color: #61adb8; 
        border: none;
        color: white;
        padding: 15px;
        text-decoration: none;
        display: inline-block;
        font-size: 16px;
        margin: 5px 2px;
        border-radius: 10px;
        cursor: pointer;
    }

    </style>
  </head>
</head>

<body>
    <div class="container">
        <h1>¿Quieres hacer la solicitud GET?</h1>
		<a class="button" href="get_sqli.php?id=1">Iniciar la solicitud</a>
    </div>
</body>

</html>
