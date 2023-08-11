import pandas as pd
from fastapi import FastAPI
import ast 

app = FastAPI(
    title="SISRECO",
    description="Sistema de Recomendacion de Peliculas",
    version="beta 1.0",
    contact={
        'mail':'sabasrodriguez@gmail.com'
        'contact_name: Sabas'
        'Github':'"https://github.com/sabas4rc"'
        
    },
)

df_movies_mesydia = pd.read_csv(r'Datasets/Preprocesados/movies_dataset_v2_mesydia.csv', sep=',', header=0, parse_dates=["release_date"])
df_movies_score = pd.read_csv(r'Datasets/Preprocesados/movies_dataset_v2_score.csv', sep=',', header=0)
df_movies_votos = pd.read_csv(r'Datasets/Preprocesados/movies_dataset_v2_votos.csv', sep=',', header=0)
df_movies_actor = pd.read_csv(r'Datasets/Preprocesados/movies_dataset_v2_actor.csv', sep=',', header=0)
df_movies_director = pd.read_csv(r'Datasets/Preprocesados/movies_dataset_v2_director.csv', sep=',', header=0)
df_movies_director = df_movies_director.dropna(subset=['director'])
df_movies_recs = pd.read_csv(r'Datasets/Preprocesados/movies_dataset_v2_recs.csv', sep=',', header=0)

# Funciones
@app.get('/')  # Ruta raíz
def get_root():
    return 'API para consulta de datos de películas'

@app.get("/cantidad_filmaciones_mes/{mes}")
def cantidad_filmaciones_mes(mes: str):
    """
    Esta función devuelve la cantidad de películas que fueron estrenadas en el mes consultado (en idioma español)
    """
    meses_ingles = {
        'enero': 'January', 'febrero': 'February', 'marzo': 'March', 'abril': 'April', 'mayo': 'May', 'junio': 'June',
        'julio': 'July', 'agosto': 'August', 'septiembre': 'September', 'octubre': 'October', 'noviembre': 'November',
        'diciembre': 'December'
    }
    mes = mes.lower()
    mes_ingles = meses_ingles.get(mes)
    if mes_ingles is None:
        return f"Ingrese el nombre del mes que desea consultar. Ejemplo: '{', '.join(meses_ingles.keys())}'."
    cant = df_movies_mesydia[df_movies_mesydia.release_date.dt.month == datetime.strptime(mes_ingles, "%B").month].id.count()
    return {'mes': mes, 'cantidad': cant}

@app.get("/cantidad_filmaciones_dia/{dia}")
def cantidad_filmaciones_dia(dia: str):
    """
    Esta función devuelve la cantidad de películas que fueron estrenadas en el día consultado (en idioma español)
    """
    dias_ingles = {
        'lunes': 0, 'martes': 1, 'miércoles': 2, 'jueves': 3, 'viernes': 4, 'sábado': 5, 'domingo': 6
    }
    dia = dia.lower()
    dia_ingles = dias_ingles.get(dia)
    if dia_ingles is None:
        return f"Ingrese el nombre del día que desea consultar. Ejemplo: '{', '.join(dias_ingles.keys())}'."
    cant = df_movies_mesydia[df_movies_mesydia.release_date.dt.weekday == dia_ingles].shape[0]
    return {'dia': dia, 'cantidad': cant}

@app.get("/score_titulo/{titulo}")
def score_titulo(titulo: str):
    """
    Esta funcion devuelve el título de la película consultada junto con el año de estreno y la popularidad según TMDB (TheMoviesDataBase)
    """
    titulo = titulo.lower()
    df_score = df_movies_score.loc[df_movies_score.title.str.lower().str.contains(titulo), ["title", "release_year", "popularity"]].iloc[0]
    titulo = str(df_score.title)
    anio = int(df_score.release_year)
    score = float(df_score.popularity.round(2))
    if not anio:
        return f'No fue posible encontrar el título "{titulo}" en nuestra base de datos. Verificar si es correcto o probar con un título alternativo en español.'
    return {'titulo': titulo, 'anio': anio, 'popularidad': score}

@app.get("/votos_titulo/{titulo}")
def votos_titulo(titulo: str):
    """
    Esta funcion devuelve el promedio de votos de la película junto con la cantidad de votos según TMDB (TheMoviesDataBase). En caso de ser una cantidad de votos menor a 2000, se informa solamente el incumplimiento de esta condición.
    """
    titulo = titulo.lower()
    df_votos = df_movies_votos.loc[df_movies_votos.title.str.lower().str.contains(titulo), ["title", "release_year", "vote_average", "vote_count"]].iloc[0]
    titulo = str(df_votos.title)
    anio = int(df_votos["release_year"])
    voto_promedio = float(df_votos.vote_average.round(2))
    voto_total = int(df_votos["vote_count"])
    if not anio:
        return f'No fue posible encontrar el título "{titulo}" en nuestra base de datos. Verificar si es correcto o probar con un título alternativo en español.'
    elif voto_total < 2000:
        return f'El título "{titulo}" no cuenta con la cantidad suficiente de valoraciones por lo que no es posible informar la valoración promedio.'
    return {'titulo': titulo, 'anio': anio, 'voto_total': voto_total, 'voto_promedio': voto_promedio}

@app.get("/get_actor/{nombre_actor}")
def get_actor(nombre_actor: str):
    """
    Esta funcion devuelve el actor consultado junto con la cantidad de películas en las que participó, el retorno total conseguido y el retorno promedio por película.
    """
    nombre_actor = nombre_actor.lower()
    fila = df_movies_actor.loc[df_movies_actor.actor.str.lower().str.contains(nombre_actor), "actor"].iloc[0]
    fila = ast.literal_eval(fila)
    for i in fila:
        if nombre_actor in i.lower():
            nombre_actor = i
            break
    cant = df_movies_actor.loc[df_movies_actor.actor.str.contains(nombre_actor), "id"].shape[0]
    retorno_total = df_movies_actor.loc[df_movies_actor.actor.str.contains(nombre_actor), "return"].sum().round(2)
    retorno_prom = df_movies_actor.loc[df_movies_actor.actor.str.contains(nombre_actor), "return"].mean().round(2)
    if not cant:
        return f'No fue posible encontrar películas del actor "{nombre_actor}" en nuestra base de datos. Verificar si es correcto o probar con un nombre alternativo en español.'
    return {'actor': nombre_actor, 'cantidad_filmaciones': cant, 'retorno_total': retorno_total, 'retorno_promedio': retorno_prom}

@app.get("/get_director/{nombre_director}")
def get_director(nombre_director: str):
    """
    Esta funcion devuelve el director consultado junto el retorno total conseguido por sus películas y un detalle de sus películas con fecha de lanzamiento, retorno, presupuesto y recaudación.
    """
    nombre_director = nombre_director.lower()
    df_director = df_movies_director.dropna(subset=['director'])
    nombre_director = str(df_director.loc[df_director.director.str.lower().str.contains(nombre_director), "director"].iloc[0])
    cant = df_director.loc[df_director.director == nombre_director, "id"].shape[0]
    retorno_total = df_director.loc[df_director.director == nombre_director, "return"].sum().round(2)
    df_peliculas = df_director.loc[df_director.director == nombre_director, ["title", "release_year", "return", "budget", "revenue", "director"]].head(5).sort_values(by="release_year", ascending=False)
    peliculas = df_peliculas.title.tolist()
    anios = df_peliculas.release_year.tolist()
    retornos = df_peliculas['return'].tolist()
    budget = df_peliculas.budget.tolist()
    revenue = df_peliculas.revenue.tolist()
    if not cant:
        return f'No fue posible encontrar películas del director "{nombre_director}" en nuestra base de datos. Verificar si es correcto o probar con un nombre alternativo en español.'
    return {'director': nombre_director, 'retorno_total_director': retorno_total, 'peliculas': peliculas, 'anio': anios, 'retorno_pelicula': retornos, 'budget_pelicula': budget, 'revenue_pelicula': revenue}

@app.get("/recomendacion/{titulo}")
def recomendacion(titulo: str):
    recs = df_movies_recs.loc[df_movies_recs.title.str.lower().str.contains(titulo), 'recs'].iloc[0]
    recs = ast.literal_eval(recs)
    return {'lista recomendada': recs}
