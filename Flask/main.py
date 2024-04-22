from flask import Flask, render_template, request, redirect, url_for
import redis
import json

my_app = Flask(__name__)

REDIS_HOST = 'localhost'
REDIS_PORT = 6379

redis_client = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=0, decode_responses=True)

class Receta:
    def __init__(self, nombre, ingredientes, pasos):
        self.nombre = nombre
        self.ingredientes = ingredientes
        self.pasos = pasos

def cargar_receta(receta_id):
    receta_json = redis_client.hget(f"receta:{receta_id}", 'receta')
    if receta_json:
        receta_dict = json.loads(receta_json)
        return Receta(**receta_dict)
    return None

def guardar_receta(receta):
    receta_id = redis_client.incr('receta_id')
    receta_json = json.dumps(receta.__dict__)
    redis_client.hset(f"receta:{receta_id}", 'receta', receta_json)

@my_app.route('/')
def index():
    return render_template('index.html')

@my_app.route('/agregar_receta', methods=['GET', 'POST'])
def agregar_receta():
    if request.method == 'POST':
        nombre = request.form['nombre']
        ingredientes = request.form['ingredientes']
        pasos = request.form['pasos']

        nueva_receta = Receta(nombre, ingredientes, pasos)
        guardar_receta(nueva_receta)

        return redirect(url_for('ver_listado_recetas'))

    return render_template('agregar_receta.html')

@my_app.route('/actualizar_receta/<int:id_receta>', methods=['GET', 'POST'])
def actualizar_receta(id_receta):
    receta = cargar_receta(id_receta)

    if receta:
        if request.method == 'POST':
            nombre = request.form['nombre']
            ingredientes = request.form['ingredientes']
            pasos = request.form['pasos']

            receta.nombre = nombre
            receta.ingredientes = ingredientes
            receta.pasos = pasos

            guardar_receta(receta)

            return redirect(url_for('ver_listado_recetas'))

        return render_template('actualizar_receta.html', receta=receta)

    return "Receta no encontrada."

@my_app.route('/eliminar_receta/<int:id_receta>')
def eliminar_receta(id_receta):
    if redis_client.exists(f"receta:{id_receta}"):
        redis_client.delete(f"receta:{id_receta}")
        return redirect(url_for('ver_listado_recetas'))
    return "Receta no encontrada."

@my_app.route('/ver_listado_recetas')
def ver_listado_recetas():
    claves_recetas = redis_client.keys("receta:*")
    recetas = []

    if claves_recetas:
        for clave in claves_recetas:
            receta_id = int(clave.split(":")[-1])
            receta = cargar_receta(receta_id)
            if receta:
                recetas.append(receta)

    return render_template('ver_listado_recetas.html', recetas=recetas)

if __name__ == "__main__":
    my_app.run(debug=True)