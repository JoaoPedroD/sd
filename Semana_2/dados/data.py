def openFile(path):
    try:
        arq = open(path, mode="rt")
        return arq.read()
    except:
        raise Exception("Não foi possivel abrir o arquivo")