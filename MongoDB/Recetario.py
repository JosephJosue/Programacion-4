from pymongo import MongoClient
from bson import ObjectId
from hashlib import sha256


def create_connection():
    """Crea una conexión a la base de datos MongoDB."""
    try:
        client = MongoClient("mongodb://localhost:27017/")
        db = client["recetario"]
        return db
    except Exception as e:
        print(f"Error al conectar a la base de datos: {e}")
        return None


def hash_password(password):
    """Hashea una contraseña utilizando el algoritmo SHA-256."""
    return sha256(password.encode()).hexdigest()


def create_user(db, usuario, contrasena, email):
    """Crea un nuevo usuario en la base de datos."""
    try:
        usuarios = db["usuarios"]
        existing_user_email = usuarios.find_one({"$or": [{"usuario": usuario}, {"email": email}]})

        if existing_user_email:
            if existing_user_email["usuario"] == usuario:
                print("El nombre de usuario ya está en uso. Por favor, elija otro.")
            else:
                print("La dirección de correo electrónico ya está en uso. Por favor, proporcione otro.")
        else:
            hashed_password = hash_password(contrasena)
            usuarios.insert_one({"usuario": usuario, "contrasena": hashed_password, "email": email})
            print("¡Usuario creado con éxito!")
    except Exception as e:
        print(f"Error al crear usuario: {e}")


def log_in(db, usuario, contrasena):
    """Verifica las credenciales de inicio de sesión y devuelve el ID del usuario."""
    try:
        usuarios = db["usuarios"]
        hashed_password = hash_password(contrasena)
        user = usuarios.find_one({"usuario": usuario, "contrasena": hashed_password})

        if user:
            print("¡Bienvenido a su recetario!")
            return user["_id"]
        else:
            print("¡Credenciales inválidas!")
            return None
    except Exception as e:
        print(f"Error al iniciar sesión: {e}")


def add_recipe(db, receta, ingredientes, pasos, id_usuario):
    """Agrega una nueva receta a la base de datos."""
    try:
        recetas = db["recetas"]
        recetas.insert_one({"receta": receta, "ingredientes": ingredientes, "pasos": pasos, "id_usuario": id_usuario})
        print("¡Receta agregada con éxito!")
    except Exception as e:
        print(f"Error al agregar receta: {e}")


def update_recipe(db, id_receta, receta=None, ingredientes=None, pasos=None):
    """Modifica una receta existente en la base de datos."""
    try:
        recetas = db["recetas"]
        update_query = {}

        if receta is not None:
            update_query["receta"] = receta

        if ingredientes is not None:
            update_query["ingredientes"] = ingredientes

        if pasos is not None:
            update_query["pasos"] = pasos

        recetas.update_one({"_id": id_receta}, {"$set": update_query})
        print("¡Receta modificada con éxito!")
    except Exception as e:
        print(f"Error al modificar receta: {e}")


def delete_recipe(db, id_receta):
    """Elimina una receta de la base de datos."""
    try:
        recetas = db["recetas"]
        recetas.delete_one({"_id": id_receta})
        print("¡Receta eliminada con éxito!")
    except Exception as e:
        print(f"Error al eliminar receta: {e}")


def list_recipes(db, id_usuario):
    """Lista todas las recetas de un usuario específico."""
    try:
        recetas = db["recetas"]
        user_recipes = recetas.find({"id_usuario": id_usuario})

        if user_recipes:
            print("Listado de recetas:")
            for receta in user_recipes:
                print(f"ID: {receta['_id']}\nReceta: {receta['receta']}")
        else:
            print("No hay recetas disponibles.")
    except Exception as e:
        print(f"Error al listar recetas: {e}")


def view_recipe_details(db, id_receta):
    """Muestra los detalles de una receta específica."""
    try:
        recetas = db["recetas"]
        receta = recetas.find_one({"_id": ObjectId(id_receta)})

        if receta:
            print("Detalles de la receta:")
            print(f"Receta: {receta['receta']}")
            print("Ingredientes:")
            for i, ingrediente in enumerate(receta['ingredientes'], start=1):
                print(f"{i}. {ingrediente}")
            print("Pasos:")
            for i, paso in enumerate(receta['pasos'], start=1):
                print(f"{i}. {paso}")
        else:
            print("No se encontró la receta con el ID proporcionado.")
    except Exception as e:
        print(f"Error al ver detalles de receta: {e}")


def search_recipe_by_ingredient(db, ingrediente):
    """Busca recetas que contengan un ingrediente específico."""
    try:
        recetas = db["recetas"]
        ingredient_query = {"ingredientes": {"$regex": ingrediente, "$options": "i"}}
        found_recipes = recetas.find(ingredient_query)

        if found_recipes:
            print(f"Recetas que contienen '{ingrediente}':")
            for receta in found_recipes:
                print(f"ID: {receta['_id']}\nReceta: {receta['receta']}")
        else:
            print(f"No se encontraron recetas que contengan '{ingrediente}'.")
    except Exception as e:
        print(f"Error al buscar receta por ingrediente: {e}")


def main():
    db = create_connection()
    if db is None:
        print("Error: No se pudo establecer la conexión a la base de datos.")
        return

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
            create_user(db, usuario, contrasena, email)

        elif opcion == "2":
            usuario = input("Nombre de usuario: ")
            contrasena = input("Contraseña: ")
            user_id = log_in(db, usuario, contrasena)
            if user_id is not None:
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
                        add_recipe(db, receta, ingredientes, pasos, user_id)

                    elif opcion_usuario == "2":
                        id_receta = input("ID de la receta a modificar: ")
                        receta = input("Nuevo nombre de la receta (deje en blanco si no desea modificar): ")
                        ingredientes = input(
                            "Nuevos ingredientes (deje en blanco si no desea modificar, separados por coma): ").split(
                            ',')
                        pasos = input(
                            "Nuevos pasos (deje en blanco si no desea modificar, separados por punto y coma): ").split(
                            ';')
                        update_recipe(db, id_receta, receta, ingredientes, pasos)

                    elif opcion_usuario == "3":
                        id_receta = input("ID de la receta a eliminar: ")
                        delete_recipe(db, id_receta)

                    elif opcion_usuario == "4":
                        while True:
                            print("\n--- MENÚ DE LISTADO DE RECETAS ---")
                            print("1. Listar todas las recetas")
                            print("2. Ver detalles de una receta")
                            print("3. Volver al menú anterior")

                            opcion_listado = input("Seleccione una opción: ")

                            if opcion_listado == "1":
                                list_recipes(db, user_id)

                            elif opcion_listado == "2":
                                id_receta = input("ID de la receta a ver detalles: ")
                                view_recipe_details(db, id_receta)

                            elif opcion_listado == "3":
                                break

                            else:
                                print("Opción Inválida.")

                    elif opcion_usuario == "5":
                        ingrediente = input("Ingrese un ingrediente para buscar recetas: ")
                        search_recipe_by_ingredient(db, ingrediente)

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


if __name__ == "__main__":
    main()