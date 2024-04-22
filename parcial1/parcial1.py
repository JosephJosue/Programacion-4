import sqlite3
import hashlib

# Función para conectar a la base de datos
def connect_db():
    conn = sqlite3.connect('budget.db')
    return conn

# Función para crear la tabla de usuarios
def create_user_table(conn):
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT NOT NULL,
                        password TEXT NOT NULL)''')
    conn.commit()

# Función para crear la tabla de artículos
def create_article_table(conn):
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS articles (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        title TEXT NOT NULL,
                        description TEXT,
                        cost REAL,
                        user_id INTEGER NOT NULL,
                        FOREIGN KEY (user_id) REFERENCES users(id))''')
    conn.commit()

# Función para registrar un nuevo usuario
def register_user(conn, username, password):
    cursor = conn.cursor()
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_password))
    conn.commit()
    print("Usuario registrado correctamente.")

# Función para iniciar sesión
def login(conn, username, password):
    cursor = conn.cursor()
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (username, hashed_password))
    user = cursor.fetchone()
    if user:
        print("Inicio de sesión exitoso.")
        return user[0]  # Devuelve el ID del usuario
    else:
        print("Nombre de usuario o contraseña incorrectos.")
        return None

# Función para agregar un artículo
def add_article(conn, user_id, title, description, cost):
    cursor = conn.cursor()
    cursor.execute("INSERT INTO articles (title, description, cost, user_id) VALUES (?, ?, ?, ?)", (title, description, cost, user_id))
    conn.commit()
    print("Artículo agregado correctamente.")

# Función para buscar artículos por título
def search_article(conn, title):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM articles WHERE title LIKE ?", ('%' + title + '%',))
    articles = cursor.fetchall()
    if articles:
        for article in articles:
            print(f"ID: {article[0]}, Nombre: {article[1]}\nDescripción: {article[2]}\nCosto: {article[3]}")
    else:
        print("No se encontraron artículos.")

# Función para editar un artículo
def edit_article(conn, article_id, title, description, cost):
    cursor = conn.cursor()
    cursor.execute("UPDATE articles SET title=?, description=?, cost=? WHERE id=?", (title, description, cost, article_id))
    conn.commit()
    print("Artículo editado correctamente.")

# Función para eliminar un artículo
def delete_article(conn, article_id):
    cursor = conn.cursor()
    cursor.execute("DELETE FROM articles WHERE id=?", (article_id,))
    conn.commit()
    print("Artículo eliminado correctamente.")

# Función para obtener el costo total de los artículos de un usuario
def total_cost(conn, user_id):
    cursor = conn.cursor()
    cursor.execute("SELECT title, description, cost FROM articles WHERE user_id=?", (user_id,))
    articles = cursor.fetchall()
    total_cost = 0
    if articles:
        print("Lista de artículos:")
        for article in articles:
            title, description, cost = article
            print(f"Nombre: {title}\nDescripción: {description}\nCosto: {cost:.2f}")
            total_cost += cost
        print(f"\nEl costo total de los artículos es: {total_cost:.2f}")
    else:
        print("No hay artículos registrados.")

# Función principal
def main():
    conn = connect_db()
    create_user_table(conn)
    create_article_table(conn)

    while True:
        print("\nMenú:")
        print("1. Registrarse")
        print("2. Iniciar sesión")
        print("3. Salir")

        choice = input("Seleccione una opción: ")

        if choice == '1':
            username = input("Ingrese un nombre de usuario: ")
            password = input("Ingrese una contraseña: ")
            register_user(conn, username, password)
        elif choice == '2':
            username = input("Ingrese su nombre de usuario: ")
            password = input("Ingrese su contraseña: ")
            user_id = login(conn, username, password)
            if user_id:
                while True:
                    print("\nMenú de usuario:")
                    print("1. Agregar artículo")
                    print("2. Buscar artículo")
                    print("3. Editar artículo")
                    print("4. Eliminar artículo")
                    print("5. Ver costo total de artículos")
                    print("6. Cerrar sesión")

                    user_choice = input("Seleccione una opción: ")

                    if user_choice == '1':
                        title = input("Ingrese el nombre del artículo: ")
                        description = input("Ingrese la descripción del artículo: ")
                        cost = float(input("Ingrese el costo del artículo: "))
                        add_article(conn, user_id, title, description, cost)
                    elif user_choice == '2':
                        title = input("Ingrese el nombre del artículo a buscar: ")
                        search_article(conn, title)
                    elif user_choice == '3':
                        article_id = input("Ingrese el ID del artículo a editar: ")
                        title = input("Ingrese el nuevo nombre del artículo: ")
                        description = input("Ingrese la nueva descripción del artículo: ")
                        cost = float(input("Ingrese el nuevo costo del artículo: "))
                        edit_article(conn, article_id, title, description, cost)
                    elif user_choice == '4':
                        article_id = input("Ingrese el ID del artículo a eliminar: ")
                        delete_article(conn, article_id)
                    elif user_choice == '5':
                        total_cost(conn, user_id)
                    elif user_choice == '6':
                        break
                    else:
                        print("Opción no válida.")
        elif choice == '3':
            break
        else:
            print("Opción no válida.")

    conn.close()

if __name__ == "__main__":
    main()