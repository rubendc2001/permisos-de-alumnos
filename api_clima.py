import requests

#api clima
def clima():
    latitud = 16.897122264135664
    longitud = -92.0633798556129
    apikey = "bfe0ffec6823337da7bb654fdcdc76df"
    url = "https://api.openweathermap.org/data/2.5/weather?lat={}&lon={}&appid={}&units=metric".format(latitud, longitud, apikey)

    data = ""

    try:
        response = requests.get(url)
        data = response.json()
    except Exception:
        print("Error al obtener datos")


    if data != "":
        temp = data["main"]["temp"]
        hum = data["main"]["humidity"]
        wind_speed = data["wind"]["speed"]
        name = data["name"]
        country = data["sys"]["country"]
        icon = data["weather"][0]["icon"]
        datosClima = [country, name, temp, hum, wind_speed, icon]
        return datosClima

    else:
        print("No se recibieron datos")
        return data