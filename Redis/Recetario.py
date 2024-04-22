import redis
import uuid
from hashlib import sha256

def create_connection():
    """Crea una conexión a la base de datos Redis."""
    try:
        r = redis.Redis(host='localhost', port=6379, db=0)
        return r
    except Exception as e:
        print(f"Error al conectar a la base de datos: {e}")
        return None

def hash_password(password):
    """Hashea una contraseña utilizando el algoritmo SHA-256."""
    return sha256(password.encode()).hexdigest()

def create_user(r, usuario, contrasena, email):
    """Crea un nuevo usuario en la base de datos."""
    try:
        user_key = f"user:{usuario}"
        if r.exists(user_key):
            print("El nombre de usuario ya está en uso. Por favor, elija otro.")
        else:
            hashed_password = hash_password(contrasena)
            r.hset(user_key, "contrasena", hashed_password)
            r.hset(user_key, "email", email)
            print("¡Usuario creado con éxito!")
    except Exception as e:
        print(f"Error al crear usuario: {e}")

def log_in(r, usuario, contrasena):
    """Verifica las credenciales de inicio de sesión y devuelve el ID del usuario."""
    try:
        user_key = f"user:{usuario}"
        if r.exists(user_key):
            stored_password = r.hget(user_key, "contrasena").decode()
            hashed_password = hash_password(contrasena)
            if stored_password == hashed_password:
                print("¡Bienvenido a su recetario!")
                return user_key
        print("¡Credenciales inválidas!")
        return None
    except Exception as e:
        print(f"Error al iniciar sesión: {e}")

def add_recipe(r, receta, ingredientes, pasos, user_key):
    """Agrega una nueva receta a la base de datos."""
    try:
        recipe_id = str(uuid.uuid4())
        recipe_key = f"recipe:{recipe_id}"
        r.hset(recipe_key, "receta", receta)
        r.hset(recipe_key, "ingredientes", ",".join(ingredientes))
        r.hset(recipe_key, "pasos", ";".join(pasos))
        r.hset(recipe_key, "user_id", user_key)
        print("¡Receta agregada con éxito!")
        return recipe_id  # Devolvemos el ID de la receta agregada
    except Exception as e:
        print(f"Error al agregar receta: {e}")
        return None

def update_recipe(r, recipe_id, receta=None, ingredientes=None, pasos=None):
    """Modifica una receta existente en la base de datos."""
    try:
        recipe_key = f"recipe:{recipe_id}"
        if receta is not None:
            r.hset(recipe_key, "receta", receta)
        if ingredientes is not None:
            r.hset(recipe_key, "ingredientes", ",".join(ingredientes))
        if pasos is not None:
            r.hset(recipe_key, "pasos", ";".join(pasos))
        print("¡Receta modificada con éxito!")
    except Exception as e:
        print(f"Error al modificar receta: {e}")

def delete_recipe(r, recipe_id):
    """Elimina una receta de la base de datos."""
    try:
        recipe_key = f"recipe:{recipe_id}"
        r.delete(recipe_key)
        print("¡Receta eliminada con éxito!")
    except Exception as e:
        print(f"Error al eliminar receta: {e}")

def list_recipes(r, user_key):
    """Lista todas las recetas de un usuario específico."""
    try:
        user_recipes_keys = r.keys("recipe:*")
        user_recipes = []
        for recipe_key in user_recipes_keys:
            recipe_user_id = r.hget(recipe_key, "user_id").decode()
            if recipe_user_id == user_key:
                recipe_id = recipe_key.decode().split(":")[1]
                recipe_name = r.hget(recipe_key, "receta").decode()
                user_recipes.append({"id": recipe_id, "nombre": recipe_name})

        if user_recipes:
            print("Listado de recetas:")
            for recipe in user_recipes:
                print(f"ID: {recipe['id']}\nReceta: {recipe['nombre']}")
        else:
            print("No hay recetas disponibles.")
    except Exception as e:
        print(f"Error al listar recetas: {e}")

def view_recipe_details(r, recipe_id):
    """Muestra los detalles de una receta específica."""
    try:
        recipe_key = f"recipe:{recipe_id}"
        recipe = r.hgetall(recipe_key)
        if recipe:
            print("Detalles de la receta:")
            print(f"Receta: {recipe[b'receta'].decode()}")
            print("Ingredientes:")
            for i, ingrediente in enumerate(recipe[b'ingredientes'].decode().split(','), start=1):
                print(f"{i}. {ingrediente}")
            print("Pasos:")
            for i, paso in enumerate(recipe[b'pasos'].decode().split(';'), start=1):
                print(f"{i}. {paso}")
        else:
            print("No se encontró la receta con el ID proporcionado.")
    except Exception as e:
        print(f"Error al ver detalles de receta: {e}")

def search_recipe_by_ingredient(r, ingrediente):
    """Busca recetas que contengan un ingrediente específico."""
    try:
        found_recipes_keys = r.keys("recipe:*")
        found_recipes = []
        for recipe_key in found_recipes_keys:
            recipe_ingredientes = r.hget(recipe_key, "ingredientes").decode()
            if ingrediente in recipe_ingredientes:
                recipe_id = recipe_key.decode().split(":")[1]
                recipe_name = r.hget(recipe_key, "receta").decode()
                found_recipes.append({"id": recipe_id, "nombre": recipe_name})

        if found_recipes:
            print(f"Recetas que contienen '{ingrediente}':")
            for recipe in found_recipes:
                print(f"ID: {recipe['id']}\nReceta: {recipe['nombre']}")
        else:
            print(f"No se encontraron recetas que contengan '{ingrediente}'.")
    except Exception as e:
        print(f"Error al buscar receta por ingrediente: {e}")

def main():
    r = create_connection()
    if r is None:
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
            create_user(r, usuario, contrasena, email)

        elif opcion == "2":
            usuario = input("Nombre de usuario: ")
            contrasena = input("Contraseña: ")
            user_key = log_in(r, usuario, contrasena)
            if user_key is not None:
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
                        add_recipe(r, receta, ingredientes, pasos, user_key)

                    elif opcion_usuario == "2":
                        id_receta = input("ID de la receta a modificar: ")
                        receta = input("Nuevo nombre de la receta (deje en blanco si no desea modificar): ")
                        ingredientes = input("Nuevos ingredientes (deje en blanco si no desea modificar, separados por coma): ").split(',')
                        pasos = input("Nuevos pasos (deje en blanco si no desea modificar, separados por punto y coma): ").split(';')
                        update_recipe(r, id_receta, receta, ingredientes, pasos)

                    elif opcion_usuario == "3":
                        id_receta = input("ID de la receta a eliminar: ")
                        delete_recipe(r, id_receta)

                    elif opcion_usuario == "4":
                        while True:
                            print("\n--- MENÚ DE LISTADO DE RECETAS ---")
                            print("1. Listar todas las recetas")
                            print("2. Ver detalles de una receta")
                            print("3. Volver al menú anterior")

                            opcion_listado = input("Seleccione una opción: ")

                            if opcion_listado == "1":
                                list_recipes(r, user_key)

                            elif opcion_listado == "2":
                                id_receta = input("ID de la receta a ver detalles: ")
                                view_recipe_details(r, id_receta)

                            elif opcion_listado == "3":
                                break

                            else:
                                print("Opción Inválida.")

                    elif opcion_usuario == "5":
                        ingrediente = input("Ingrese un ingrediente para buscar recetas: ")
                        search_recipe_by_ingredient(r, ingrediente)

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