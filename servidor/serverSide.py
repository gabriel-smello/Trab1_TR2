import socket
import sys
import select
import json


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
        case 'JOIN':
            join(dado, usuario)
        case 'SAY':
            say(dado, usuario)
        case 'PART':
            part(dado, usuario)
        case 'LIST':
            lista(dado, usuario)
        case 'PRIVMSG':
            privmsg(dado, usuario)
        case 'WHO':
            who(dado, usuario)
        case _:
            errorCode = '500 ERR UNKNOWNCOMMAND'
            print(errorCode)
            usuario.send(errorCode.encode('UTF-8'))


def user(usuario):
    return


def nick(nome, usuario):

    if listaUsuario.__contains__(usuario):
        errorCode = (f'400 Você já está logado')
        usuario.send(errorCode.encode('UTF-8'))
        return 0

    for socket in listaUsuario:
        if listaUsuario[socket]['nome'] == nome:
            errorCode = f'401 O Nick {nome} já está em uso'
            usuario.send(errorCode.encode('utf-8'))
            return 0

    listaUsuario[usuario] = {
        'nome': nome,
        'salas': [],
        'socket': usuario
    }

    usuario.send(f'200 Bem Vindo {nome}'.encode('utf-8'))
    return


def quit(INPUT, entradaUsuario):
    # QUIT

    nome = listaUsuario[entradaUsuario]['nome']
    print(f'{nome} foi desconectado')

    for sala in listaUsuario[entradaUsuario]['salas']:
        listaSalas[sala]['usuarios'].remove(listaUsuario[entradaUsuario])

    listaUsuario.pop(entradaUsuario)

    entradaUsuario.close()
    INPUT.remove(entradaUsuario)
    global contaUsuarios
    contaUsuarios -= 1

    return 0


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

    usuariosNestaSala = listaSalas[nomeSala]['usuarios']
    usuarioAtual = listaUsuario[usuario]

    # remove usuario da sala
    usuariosNestaSala.remove(usuarioAtual)

    # remove sala de usuario
    usuarioAtual['salas'].remove(nomeSala)

    sucesso = f'200 Voce saiu na sala "{nomeSala}"'
    usuario.send(sucesso.encode('utf-8'))
    return 0


def lista(dado, usuario):
    sucesso = '200 Salas no servidor:\n'
    for sala in listaSalas:
        sucesso += listaSalas[sala]['nome'] + \
            ' (' + str(len(listaSalas[sala]['usuarios'])) + ')' '\n'

    usuario.send(sucesso.encode('utf-8'))
    return 0


def privmsg(dado, usuario):
    dado = dado.partition(' ')
    mensagem = dado[2]
    destinatario = dado[0]

    # ---------------------------- ERROS ----------------------------
    # Comando informado de forma incorreta
    if not (len(dado) == 3 and len(dado[0]) > 0 and len(dado[2]) > 0):
        errorCode = f'401 Comando inválido'
        usuario.send(errorCode.encode('utf-8'))
        return 0
    # ----------------------------------------------------------------
    nomeRemetente = listaUsuario[usuario]['nome']

    for socketCliente in listaUsuario:
        # Verifica se destinatário existe
        if listaUsuario[socketCliente]['nome'] == destinatario:
            # Envia mensagem privada
            sucesso = f'200 Mensagem privada de "{nomeRemetente}" > {mensagem}'
            listaUsuario[socketCliente]['socket'].send(sucesso.encode('utf-8'))
            return 0

    for sala in listaSalas:
        if not (listaSalas[sala]['nome'] == destinatario):
            errorCode = f'300 Usuario/Sala "{destinatario}" não encontrado'
            usuario.send(errorCode.encode('utf-8'))
            return 0

        usuariosNestaSala = listaSalas[destinatario]['usuarios']
        usuarioAtual = listaUsuario[usuario]

        if not (listaUsuario[usuario] in listaSalas[destinatario]['usuarios']):
            errorCode = f'300 Usuário não está na sala'
            usuario.send(errorCode.encode('utf-8'))
            return 0

        for cliente in usuariosNestaSala:
            if not (cliente == usuarioAtual):
                sucesso = f'200 [{destinatario}] {nomeRemetente} > {mensagem}'
                cliente['socket'].send(sucesso.encode('utf-8'))
                return 0


def who(nomeSala, usuario):

    # ----------------------- ERROS ---------------------------------
    # Comando informado de forma incorreta
    if (len(str.split(nomeSala, ' ')) > 1 or len(nomeSala) == 0):
        errorCode = f'400 Nome de sala incorreta'
        usuario.send(errorCode.encode('utf-8'))
        return 0

    # Sala mencionada não existe
    if not listaSalas.__contains__(nomeSala):
        errorCode = f'300 Sala "{nomeSala}" não existe'
        usuario.send(errorCode.encode('utf-8'))
        return 0
    # ---------------------------------------------------------------

    usuariosNestaSala = listaSalas[nomeSala]['usuarios']

    sucesso = f'200 Usuários em {nomeSala}:\n'

    for cliente in usuariosNestaSala:
        nome = cliente['nome']
        sucesso += f'\t{nome}\n'

    usuario.send(sucesso.encode('utf-8'))
    return 0


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
        'nome': 'Futebol',
        'usuarios': []
    },
    'Receitas': {
        'nome': 'Receitas',
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
            try:
                mensagem = entradaUsuario.recv(1000)
            except:
                quit(INPUT, entradaUsuario)
            if mensagem:
                mensagem = mensagem.decode('utf-8')

                socketFileDescriptor = entradaUsuario.fileno()
                print('Recebido de ' +
                      str(socketFileDescriptor) + ' - ' + mensagem)
                dadosFunc(mensagem, entradaUsuario)
            else:
                quit(INPUT, entradaUsuario)

server.close()
print("server fechou")
