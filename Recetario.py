import sqlite3 as sql
import hashlib


def create_connection(database):
    """Crea una conexión a la base de datos SQLite."""
    try:
        conn = sql.connect(database)
        return conn
    except sql.Error as e:
        print(f"Error al conectar a la base de datos: {e}")
        return None


def create_tables(conn):
    """Crea las tablas 'usuarios' y 'recetas' si no existen."""
    try:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY,
                usuario TEXT UNIQUE NOT NULL,
                contrasena TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL
            )""")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS recetas (
                id INTEGER PRIMARY KEY,
                receta TEXT UNIQUE NOT NULL,
                ingredientes TEXT,
                pasos TEXT,
                id_usuario INTEGER,
                FOREIGN KEY(id_usuario) REFERENCES usuarios(id)
            )""")
        conn.commit()
    except sql.Error as e:
        print(f"Error al crear tablas: {e}")


def hash_password(password):
    """Hashea una contraseña utilizando el algoritmo SHA-256."""
    return hashlib.sha256(password.encode()).hexdigest()


def create_user(conn, usuario, contrasena, email):
    """Crea un nuevo usuario en la base de datos."""
    try:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT usuario, email FROM usuarios WHERE usuario = ? OR email = ?''', (usuario, email))
        existing_user_email = cursor.fetchone()

        if existing_user_email:
            if existing_user_email[0] == usuario:
                print("El nombre de usuario ya está en uso. Por favor, elija otro.")
            else:
                print("La dirección de correo electrónico ya está en uso. Por favor, proporcione otro.")
        else:
            hashed_password = hash_password(contrasena)
            cursor.execute('''
                INSERT INTO usuarios (usuario, contrasena, email) VALUES (?, ?, ?)''',
                           (usuario, hashed_password, email))
            conn.commit()
            print("¡Usuario creado con éxito!")
    except sql.Error as e:
        print(f"Error al crear usuario: {e}")


def log_in(conn, usuario, contrasena):
    """Verifica las credenciales de inicio de sesión y devuelve el ID del usuario."""
    try:
        cursor = conn.cursor()
        hashed_password = hash_password(contrasena)
        cursor.execute('''
            SELECT id FROM usuarios WHERE usuario = ? AND contrasena = ?''', (usuario, hashed_password))
        user_id = cursor.fetchone()

        if user_id:
            print("¡Bienvenido a su recetario!")
            return user_id[0]
        else:
            print("¡Credenciales inválidas!")
            return None
    except sql.Error as e:
        print(f"Error al iniciar sesión: {e}")


def add_recipe(conn, receta, ingredientes, pasos, id_usuario):
    """Agrega una nueva receta a la base de datos."""
    try:
        cursor = conn.cursor()
        ingredientes_str = '\n'.join(ingredientes)
        pasos_str = '\n'.join(pasos)
        cursor.execute('''
            INSERT INTO recetas (receta, ingredientes, pasos, id_usuario) VALUES (?, ?, ?, ?)''',
                       (receta, ingredientes_str, pasos_str, id_usuario))
        conn.commit()
        print("¡Receta agregada con éxito!")
    except sql.Error as e:
        print(f"Error al agregar receta: {e}")


def update_recipe(conn, id_receta, receta=None, ingredientes=None, pasos=None):
    """Modifica una receta existente en la base de datos."""
    try:
        cursor = conn.cursor()
        update_query = "UPDATE recetas SET"
        params = []

        if receta is not None:
            update_query += " receta = ?,"
            params.append(receta)

        if ingredientes is not None:
            update_query += " ingredientes = ?,"
            params.append('\n'.join(ingredientes))

        if pasos is not None:
            update_query += " pasos = ?,"
            params.append('\n'.join(pasos))

        update_query = update_query.rstrip(",") + " WHERE id = ?"
        params.append(id_receta)

        cursor.execute(update_query, params)
        conn.commit()
        print("¡Receta modificada con éxito!")
    except sql.Error as e:
        print(f"Error al modificar receta: {e}")


def delete_recipe(conn, id_receta):
    """Elimina una receta de la base de datos."""
    try:
        cursor = conn.cursor()
        cursor.execute('''
            DELETE FROM recetas WHERE id = ?''', (id_receta,))
        conn.commit()
        print("¡Receta eliminada con éxito!")
    except sql.Error as e:
        print(f"Error al eliminar receta: {e}")


def list_recipes(conn, id_usuario):
    """Lista todas las recetas de un usuario específico."""
    try:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, receta FROM recetas WHERE id_usuario = ?''', (id_usuario,))
        recetas = cursor.fetchall()

        if recetas:
            print("Listado de recetas:")
            for receta in recetas:
                print(f"ID: {receta[0]}\nReceta: {receta[1]}")
        else:
            print("No hay recetas disponibles.")
    except sql.Error as e:
        print(f"Error al listar recetas: {e}")


def view_recipe_details(conn, id_receta):
    """Muestra los detalles de una receta específica."""
    try:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT receta, ingredientes, pasos FROM recetas WHERE id = ?''', (id_receta,))
        detalles_receta = cursor.fetchone()

        if detalles_receta:
            print("Detalles de la receta:")
            print(f"Receta: {detalles_receta[0]}")
            print("Ingredientes:")
            print(detalles_receta[1])
            print("Pasos:")
            print(detalles_receta[2])
        else:
            print("No se encontró la receta con el ID proporcionado.")
    except sql.Error as e:
        print(f"Error al ver detalles de receta: {e}")


def search_recipe_by_ingredient(conn, ingrediente):
    """Busca recetas que contengan un ingrediente específico."""
    try:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, receta FROM recetas WHERE ingredientes LIKE ?''', ('%' + ingrediente + '%',))
        recetas = cursor.fetchall()

        if recetas:
            print(f"Recetas que contienen '{ingrediente}':")
            for receta in recetas:
                print(f"ID: {receta[0]}\nReceta: {receta[1]}")
        else:
            print(f"No se encontraron recetas que contengan '{ingrediente}'.")
    except sql.Error as e:
        print(f"Error al buscar receta por ingrediente: {e}")


def main():
    # Crear una conexión a la base de datos y crear las tablas si no existen
    conn = create_connection("recetario.db")
    if conn is None:
        print("Error: No se pudo establecer la conexión a la base de datos.")
        return

    create_tables(conn)  # Añadimos esta línea para crear las tablas

    while True:
        print("\n--- MENÚ ---")
        print("1. Registrarse")
        print("2. Iniciar sesión")
        print("3. Salir")

        opcion = input("Seleccione una opción: ")

        if opcion == "1":
            usuario = input("Nombre de usuario: ")
            contrasena = input("Contraseña: ")
            email = input("Email: ")
            create_user(conn, usuario, contrasena, email)

        elif opcion == "2":
            usuario = input("Nombre de usuario: ")
            contrasena = input("Contraseña: ")
            user_id = log_in(conn, usuario, contrasena)
            if user_id is not None:
                # Menú del usuario autenticado
                while True:
                    print("\n--- MENÚ DE USUARIO ---")
                    print("1. Agregar receta")
                    print("2. Modificar receta")
                    print("3. Eliminar receta")
                    print("4. Listar recetas")
                    print("5. Buscar receta por ingrediente")
                    print("6. Salir")

                    opcion_usuario = input("Seleccione una opción: ")

                    if opcion_usuario == "1":
                        receta = input("Nombre de la receta: ")
                        ingredientes = input("Ingredientes (separados por coma): ").split(',')
                        pasos = input("Pasos (separados por punto y coma): ").split(';')
                        add_recipe(conn, receta, ingredientes, pasos, user_id)

                    elif opcion_usuario == "2":
                        id_receta = input("ID de la receta a modificar: ")
                        receta = input("Nuevo nombre de la receta (deje en blanco si no desea modificar): ")
                        ingredientes = input(
                            "Nuevos ingredientes (deje en blanco si no desea modificar, separados por coma): ").split(
                            ',')
                        pasos = input(
                            "Nuevos pasos (deje en blanco si no desea modificar, separados por punto y coma): ").split(
                            ';')
                        update_recipe(conn, id_receta, receta, ingredientes, pasos)

                    elif opcion_usuario == "3":
                        id_receta = input("ID de la receta a eliminar: ")
                        delete_recipe(conn, id_receta)

                    elif opcion_usuario == "4":
                        while True:
                            print("\n--- MENÚ DE LISTADO DE RECETAS ---")
                            print("1. Listar todas las recetas")
                            print("2. Ver detalles de una receta")
                            print("3. Volver al menú anterior")

                            opcion_listado = input("Seleccione una opción: ")

                            if opcion_listado == "1":
                                list_recipes(conn, user_id)

                            elif opcion_listado == "2":
                                id_receta = input("ID de la receta a ver detalles: ")
                                view_recipe_details(conn, id_receta)

                            elif opcion_listado == "3":
                                break

                            else:
                                print("Opción inválida.")

                    elif opcion_usuario == "5":
                        ingrediente = input("Ingrese un ingrediente para buscar recetas: ")
                        search_recipe_by_ingredient(conn, ingrediente)

                    elif opcion_usuario == "6":
                        print("Saliendo...")
                        break

                    else:
                        print("Opción inválida.")

        elif opcion == "3":
            print("Saliendo del programa...")
            break

        else:
            print("Opción inválida.")
