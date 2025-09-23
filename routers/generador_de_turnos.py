from datetime import time, datetime, timedelta

hora_inicio = time(9, 0)
hora_fin = time(17, 0)
intervalo = timedelta(minutes=30)

generador_turnos = []
hora_actual = datetime.combine(datetime.today(), hora_inicio)

while hora_actual.time() <= hora_fin:
    generador_turnos.append(hora_actual.time().strftime("%H:%M"))
    hora_actual += intervalo
