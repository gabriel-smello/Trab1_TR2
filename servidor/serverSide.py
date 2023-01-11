import socket
import sys
import select
import json


def desconectaUsuario():
    return


def dadosFunc(mensagem, usuario):
    mensagem = mensagem.strip()
    mensagem = mensagem.partition(' ')
    funcao = mensagem[0]
    dado = mensagem[2]
    match funcao:
        case 'USER':
            user(dado, usuario)
        case 'NICK':
            nick(dado, usuario)
        case 'QUIT':
            quit()
        case 'JOIN':
            join(dado, usuario)
        case 'PART':
            part(dado, usuario)
        case 'LIST':
            lista()
        case 'PRIVMSG':
            privmsg()
        case 'WHO':
            who()
        case _:
            errorCode = '500 Comando desconhecido'
            print(errorCode)
            usuario.send(errorCode.encode('UTF-8'))


def user(nome, usuario):
    if usuario in listaUsuario:
        usuario.send('400 Você já está logado'.encode('utf-8'))
        return

    listaUsuario[usuario] = {
        'nome': nome,
        'salas': [],
        'socket': usuario
    }

    usuario.send(f'200 Bem Vindo {nome}'.encode('utf-8'))
    return


def nick(usuario):
    return


def quit():
    return


def join(nomeSala, usuario):
    # -------------------- ERROS -------------------------------
    # Sala mencionada de forma incorreta
    if (len(str.split(nomeSala, ' ')) > 1 or len(nomeSala) == 0):
        errorCode = '401 Nome de sala inválido'
        usuario.send(errorCode.encode('utf-8'))
        return 0

    # Sala mencionada não existe
    if not listaSalas.__contains__(nomeSala):
        errorCode = f'300 Sala  "{nomeSala}" não existe'
        usuario.send(errorCode.encode('utf-8'))
        return 0

    # usuario já está na sala mencionada
    if listaUsuario[usuario] in listaSalas[nomeSala]['usuarios']:
        errorCode = f'300 Usuario já está na sala "{nomeSala}"'
        usuario.send(errorCode.encode('utf-8'))
        return 0
    # ------------------------------------------------------------

    clientesNestaSala = listaSalas[nomeSala]['usuarios']
    clienteAtual = listaUsuario[usuario]

    # Adiciona usuário na sala
    clientesNestaSala.append(clienteAtual)

    # Adciona sala no usuário
    clienteAtual['salas'].append(nomeSala)

    sucesso = f'200 Voce entrou na sala "{nomeSala}"'
    usuario.send(sucesso.encode('utf-8'))
    return 0


def part(nomeSala, usuario):
    # -------------------- ERROS -------------------------------
    # Sala mencionada de forma incorreta
    if (len(str.split(nomeSala, ' ')) > 1 or len(nomeSala) == 0):
        errorCode = '401 Nome de sala inválido'
        usuario.send(errorCode.encode('utf-8'))
        return 0

    # Sala mencionada não existe
    if not listaSalas.__contains__(nomeSala):
        errorCode = f'300 Sala "{nomeSala}" não existe'
        usuario.send(errorCode.encode('utf-8'))
        return 0

    # usuario não está na sala mencionada
    if not (listaUsuario[usuario] in listaSalas[nomeSala]['usuarios']):
        errorCode = f'300 Usuario não está na sala "{nomeSala}"'
        usuario.send(errorCode.encode('utf-8'))
        return 0
    # ------------------------------------------------------------

    clientesNestaSala = listaSalas[nomeSala]['usuarios']
    clienteAtual = listaUsuario[usuario]

    # remove usuario da sala
    clientesNestaSala.remove(clienteAtual)

    # remove sala de usuario
    clienteAtual['salas'].remove(nomeSala)

    sucesso = f'200 Voce saiu na sala "{nomeSala}"'
    usuario.send(sucesso.encode('utf-8'))
    return 0


def lista():
    return


def privmsg():
    return


def who():
    return


##################### MAIN #######################
CAPACITACAO = 5
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
porta = int(sys.argv[1])
host = ''
INPUT = [server, sys.stdin]
contaUsuarios = 0
listaUsuario = {}
listaSalas = {
    'Futebol': {
        'name': 'Futebol',
        'usuarios': []
    },
    'Receitas': {
        'name': 'Futebol',
        'usuarios': []
    }
}


serverStatus = 1

server.bind((host, porta))

server.listen(CAPACITACAO)

print('Server rodando...')

while serverStatus:
    leitura, escrita, excecao = select.select(INPUT, [], [])
    for entradaUsuario in leitura:
        if entradaUsuario == server:
            novaConexao, enderecoIp = server.accept()
            socketFileDescriptor = novaConexao.fileno()
            contaUsuarios += 1
            print('Usuario ' + str(socketFileDescriptor) +
                  ' conectou ', enderecoIp)
            INPUT.append(novaConexao)
        elif entradaUsuario == sys.stdin:
            inputUsuario = sys.stdin.readline()

            if inputUsuario.strip() == "q":
                serverStatus = 0
        else:
            mensagem = entradaUsuario.recv(1000)
            if mensagem:
                mensagem = mensagem.decode('utf-8')

                socketFileDescriptor = entradaUsuario.fileno()
                print('Recebido de ' +
                      str(socketFileDescriptor) + ' - ' + mensagem)
                dadosFunc(mensagem, entradaUsuario)
            else:
                desconectaUsuario()

server.close()
print("server fechou")
