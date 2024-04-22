from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import hashlib

Base = declarative_base()

class Usuario(Base):
    __tablename__ = 'usuarios'

    id = Column(Integer, primary_key=True)
    usuario = Column(String, unique=True, nullable=False)
    contrasena = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    recetas = relationship("Receta", back_populates="usuario")

class Receta(Base):
    __tablename__ = 'recetas'

    id = Column(Integer, primary_key=True)
    receta = Column(String, unique=True, nullable=False)
    ingredientes = Column(String)
    pasos = Column(String)
    id_usuario = Column(Integer, ForeignKey('usuarios.id'))
    usuario = relationship("Usuario", back_populates="recetas")

def hash_password(password):
    """Hashea una contraseña utilizando el algoritmo SHA-256."""
    return hashlib.sha256(password.encode()).hexdigest()

def create_connection():
    """Crea una conexión a la base de datos SQLite."""
    engine = create_engine('sqlite:///recetario.db')
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    return Session()

def create_user(session, usuario, contrasena, email):
    """Crea un nuevo usuario en la base de datos."""
    hashed_password = hash_password(contrasena)
    existing_user = session.query(Usuario).filter(Usuario.usuario == usuario).first()
    existing_email = session.query(Usuario).filter(Usuario.email == email).first()
    
    if existing_user:
        print("El nombre de usuario ya está en uso. Por favor, elija otro.")
    elif existing_email:
        print("La dirección de correo electrónico ya está en uso. Por favor, proporcione otro.")
    else:
        new_user = Usuario(usuario=usuario, contrasena=hashed_password, email=email)
        session.add(new_user)
        session.commit()
        print("¡Usuario creado con éxito!")

def log_in(session, usuario, contrasena):
    """Verifica las credenciales de inicio de sesión y devuelve el ID del usuario."""
    hashed_password = hash_password(contrasena)
    user = session.query(Usuario).filter(Usuario.usuario == usuario, Usuario.contrasena == hashed_password).first()
    
    if user:
        print("¡Bienvenido a su recetario!")
        return user.id
    else:
        print("¡Credenciales inválidas!")
        return None

def add_recipe(session, receta, ingredientes, pasos, id_usuario):
    """Agrega una nueva receta a la base de datos."""
    ingredientes_str = '\n'.join(ingredientes)
    pasos_str = '\n'.join(pasos)
    new_recipe = Receta(receta=receta, ingredientes=ingredientes_str, pasos=pasos_str, id_usuario=id_usuario)
    session.add(new_recipe)
    session.commit()
    print("¡Receta agregada con éxito!")

def update_recipe(session, id_receta, receta=None, ingredientes=None, pasos=None):
    """Modifica una receta existente en la base de datos."""
    recipe = session.query(Receta).filter(Receta.id == id_receta).first()
    
    if recipe:
        if receta is not None:
            recipe.receta = receta

        if ingredientes is not None:
            recipe.ingredientes = '\n'.join(ingredientes)

        if pasos is not None:
            recipe.pasos = '\n'.join(pasos)

        session.commit()
        print("¡Receta modificada con éxito!")
    else:
        print("No se encontró la receta con el ID proporcionado.")

def delete_recipe(session, id_receta):
    """Elimina una receta de la base de datos."""
    recipe = session.query(Receta).filter(Receta.id == id_receta).first()
    
    if recipe:
        session.delete(recipe)
        session.commit()
        print("¡Receta eliminada con éxito!")
    else:
        print("No se encontró la receta con el ID proporcionado.")

def list_recipes(session, id_usuario):
    """Lista todas las recetas de un usuario específico."""
    user = session.query(Usuario).get(id_usuario)
    
    if user:
        if user.recetas:
            print("Listado de recetas:")
            for receta in user.recetas:
                print(f"ID: {receta.id}\nReceta: {receta.receta}")
        else:
            print("No hay recetas disponibles para este usuario.")
    else:
        print("No se encontró el usuario.")

def view_recipe_details(session, id_receta):
    """Muestra los detalles de una receta específica."""
    receta = session.query(Receta).filter(Receta.id == id_receta).first()

    if receta:
        print("Detalles de la receta:")
        print(f"Receta: {receta.receta}")
        print("Ingredientes:")
        print(receta.ingredientes)
        print("Pasos:")
        print(receta.pasos)
    else:
        print("No se encontró la receta con el ID proporcionado.")

def search_recipe_by_ingredient(session, ingrediente):
    """Busca recetas que contengan un ingrediente específico."""
    recetas = session.query(Receta).filter(Receta.ingredientes.like(f'%{ingrediente}%')).all()
    
    if recetas:
        print(f"Recetas que contienen '{ingrediente}':")
        for receta in recetas:
            print(f"ID: {receta.id}\nReceta: {receta.receta}")
    else:
        print(f"No se encontraron recetas que contengan '{ingrediente}'.")

def main():
    session = create_connection()

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
            create_user(session, usuario, contrasena, email)

        elif opcion == "2":
            usuario = input("Nombre de usuario: ")
            contrasena = input("Contraseña: ")
            user_id = log_in(session, usuario, contrasena)
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
                        add_recipe(session, receta, ingredientes, pasos, user_id)

                    elif opcion_usuario == "2":
                        id_receta = input("ID de la receta a modificar: ")
                        receta = input("Nuevo nombre de la receta (deje en blanco si no desea modificar): ")
                        ingredientes = input("Nuevos ingredientes (deje en blanco si no desea modificar, separados por coma): ").split(',')
                        pasos = input("Nuevos pasos (deje en blanco si no desea modificar, separados por punto y coma): ").split(';')
                        update_recipe(session, id_receta, receta, ingredientes, pasos)

                    elif opcion_usuario == "3":
                        id_receta = input("ID de la receta a eliminar: ")
                        delete_recipe(session, id_receta)

                    elif opcion_usuario == "4":
                        list_recipes(session, user_id)
                        while True:
                            print("\n--- MENÚ DE LISTADO DE RECETAS ---")
                            print("1. Ver detalles de una receta")
                            print("2. Volver al menú anterior")

                            opcion_listado = input("Seleccione una opción: ")

                            if opcion_listado == "1":
                                id_receta = input("ID de la receta a ver detalles: ")
                                view_recipe_details(session, id_receta)

                            elif opcion_listado == "2":
                                break

                            else:
                                print("Opción inválida.")

                    elif opcion_usuario == "5":
                        ingrediente = input("Ingrese un ingrediente para buscar recetas: ")
                        search_recipe_by_ingredient(session, ingrediente)

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

