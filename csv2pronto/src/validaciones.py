def get_campos(array: list[str], row: dict)  -> dict[str, str]:
    salida = {}
    for campo in array:
        if row[campo] == "True":
            salida[campo] = row[campo] == "True"
        else:
            salida[campo] = "False"
    return salida