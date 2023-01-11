import socket
import sys
import select
import os


def trataDado(dados, usuario):
    dados = dados.decode('utf-8')
    status = dados.partition(' ')[0]
    dados = dados.partition(' ')[2]
    print()
    print(dados)
    print()


def setNome(usuario):
    pronto = 0

    while not pronto:
        print(f'Digite seu nome: ', end='', flush=True)
        nome = sys.stdin.readline().rstrip()
        enviarDado = 'USER ' + nome
        usuario.send(enviarDado.encode('utf-8'))

        try:
            resposta = usuario.recv(1000).decode('utf-8').rstrip()
        except:
            sys.exit('Desconectado. ')

        status = resposta[0:3]
        resposta = resposta[4:]
        print()
        print(resposta)
        print()

        if (status == '200'):
            pronto = 1
    return nome


################### MAIN ###################
usuario = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serverIp = sys.argv[1]
serverPorta = int(sys.argv[2])
nome = 'usuario'
INPUT = [usuario, sys.stdin]

try:
    usuario.connect((serverIp, serverPorta))
except:
    print('Erro para se conectar ao servidor')
    quit()

print('Voce se conectou ao servidor ' + str(serverIp) + ':' + str(serverPorta))

nome = setNome(usuario)

while True:
    leitura, escrita, excessao = select.select(INPUT, [], [])

    for entradaServidor in leitura:
        if entradaServidor == usuario:
            try:
                dados = entradaServidor.recv(1000)
            except:
                print('Você foi desconectado do servidor')
                quit()

            if dados:
                trataDado(dados, usuario)
            else:
                print('Erro desconhecido.\nDesconectado do servidor')
                quit()
        else:
            mensagem = sys.stdin.readline()

            try:
                comando = mensagem.split()[0]
            except:
                continue

            if comando == 'QUIT':
                usuario.close()
                print('Você foi desconectado do servidor')
                quit()
            else:
                usuario.send(mensagem.encode('utf-8'))
