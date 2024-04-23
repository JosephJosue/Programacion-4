from flask import Flask, jsonify, render_template
import pandas as pd

app = Flask(__name__)

# Lectura del archivo .xls
df = pd.read_excel('vacunacion.xls', sheet_name='Data', header=3, index_col=[0, 1, 2, 3])


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/todos_los_datos')
def obtener_todos_los_datos():
    # Obtener las columnas de los años y los valores
    columnas_anios = df.columns[4:25]  # Columnas de los años desde E4 hasta BP4
    columnas_valores = df.columns[24:]  # Columnas de los valores desde Y4 hasta el final

    # Convertir los datos a un formato que sea más fácil de procesar en JavaScript
    datos_formateados = []
    for idx, fila in df.iterrows():
        for anio, valor in zip(columnas_anios, fila[columnas_valores]):
            # Convertir NaN a None
            if pd.isna(valor):
                valor = None
            datos_formateados.append({
                'Country Name': idx[0],
                'Country Code': idx[1],
                'Indicator Name': idx[2],
                'Indicator Code': idx[3],
                'Year': anio,
                'Value': valor
            })

    return jsonify(datos_formateados)


if __name__ == '__main__':
    app.run(debug=True)
