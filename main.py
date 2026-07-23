import sqlite3

#banco de dados

NOME_BANCO = "pedidos.db"
STATUS_VALIDOS = ["Pendente", "Em Preparação", "Enviado", "Finalizado", "Cancelado"]

def conectar():
    conexao = sqlite3.connect(NOME_BANCO)
    conexao.row_factory = sqlite3.Row  # permite acessar colunas pelo nome, tipo dicionário
    return conexao

def criar_tabelas():
    conexao = conectar()
    cursor = conexao.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS clientes (id INTEGER PRIMARY KEY AUTOINCREMENT, nome TEXT NOT NULL, email TEXT, telefone TEXT)")
    cursor.execute("CREATE TABLE IF NOT EXISTS produtos (id INTEGER PRIMARY KEY AUTOINCREMENT, nome TEXT NOT NULL, preco REAL NOT NULL, estoque INTEGER DEFAULT 0)")
    cursor.execute("CREATE TABLE IF NOT EXISTS pedidos (id INTEGER PRIMARY KEY AUTOINCREMENT, cliente_id INTEGER NOT NULL, status TEXT NOT NULL DEFAULT 'Pendente', valor_total REAL DEFAULT 0)")
    cursor.execute("CREATE TABLE IF NOT EXISTS itens_pedido (id INTEGER PRIMARY KEY AUTOINCREMENT, pedido_id INTEGER NOT NULL, produto_id INTEGER NOT NULL, quantidade INTEGER NOT NULL, preco_unitario REAL NOT NULL, subtotal REAL NOT NULL)")
    conexao.commit()
    conexao.close()


#FUNÇÕES AUXILIARES DE ENTRADA

def ler_inteiro(mensagem):
    while True:
        try:
            return int(input(mensagem))
        except ValueError:
            print("Digite um número inteiro válido.")

def ler_float(mensagem):
    while True:
        try:
            return float(input(mensagem).replace(",", "."))
        except ValueError:
            print("Digite um valor numérico válido (ex: 19.90).")

def pausar():
    input("\nPressione ENTER para continuar...")

def buscar_por_id(tabela, item_id):
    """Busca uma linha pelo id em 'clientes' ou 'produtos'."""
    conexao = conectar()
    linha = conexao.execute(f"SELECT * FROM {tabela} WHERE id = ?", (item_id,)).fetchone()
    conexao.close()
    return linha


#cadastro de clientes

def cadastrar_cliente():
    print("\n--- Cadastro de Cliente ---")
    nome = input("Nome do cliente: ").strip()
    if nome == "":
        print("Nome é obrigatório. Operação cancelada.")
        return
    email = input("Email (opcional): ").strip()
    telefone = input("Telefone (opcional): ").strip()
    conexao = conectar()
    conexao.execute("INSERT INTO clientes (nome, email, telefone) VALUES (?, ?, ?)", (nome, email, telefone))
    conexao.commit()
    conexao.close()
    print(f"Cliente '{nome}' cadastrado com sucesso!")

def listar_clientes():
    conexao = conectar()
    clientes = conexao.execute("SELECT * FROM clientes ORDER BY nome").fetchall()
    conexao.close()
    print("\n--- Lista de Clientes ---")
    if len(clientes) == 0:
        print("Nenhum cliente cadastrado.")
    for cliente in clientes:
        print(f"[{cliente['id']}] {cliente['nome']} | Tel: {cliente['telefone'] or '-'}")


#CADASTRO DE PRODUTOS#

def cadastrar_produto():
    print("\n--- Cadastro de Produto ---")
    nome = input("Nome do produto: ").strip()
    if nome == "":
        print("Nome é obrigatório. Operação cancelada.")
        return
    preco = ler_float("Preço unitário: R$ ")
    estoque = ler_inteiro("Estoque disponível: ")
    conexao = conectar()
    conexao.execute("INSERT INTO produtos (nome, preco, estoque) VALUES (?, ?, ?)", (nome, preco, estoque))
    conexao.commit()
    conexao.close()
    print(f"Produto '{nome}' cadastrado com sucesso!")

def listar_produtos():
    conexao = conectar()
    produtos = conexao.execute("SELECT * FROM produtos ORDER BY nome").fetchall()
    conexao.close()
    print("\n--- Lista de Produtos ---")
    if len(produtos) == 0:
        print("Nenhum produto cadastrado.")
    for produto in produtos:
        print(f"[{produto['id']}] {produto['nome']} | R$ {produto['preco']:.2f} | Estoque: {produto['estoque']}")

#PEDIDOS

def criar_pedido():
    print("\n--- Novo Pedido ---")
    listar_clientes()
    cliente_id = ler_inteiro("\nID do cliente: ")
    cliente = buscar_por_id("clientes", cliente_id)
    if cliente is None:
        print("Cliente não encontrado. Operação cancelada.")
        return

    itens = []  # cada item: (produto_id, quantidade, preco_unitario, subtotal)
    valor_total = 0
    listar_produtos()
    print("\nAdicione os itens do pedido (0 no ID do produto = finalizar).")
    while True:
        produto_id = ler_inteiro("\nID do produto (0 = finalizar): ")
        if produto_id == 0:
            break
        produto = buscar_por_id("produtos", produto_id)
        if produto is None:
            print("  >> Produto não encontrado, tente novamente.")
            continue
        quantidade = ler_inteiro(f"Quantidade de '{produto['nome']}': ")
        if quantidade <= 0:
            print("  >> Quantidade deve ser maior que zero.")
            continue
        subtotal = produto["preco"] * quantidade
        itens.append((produto_id, quantidade, produto["preco"], subtotal))
        valor_total = valor_total + subtotal
        print(f"  >> Adicionado: {quantidade} x {produto['nome']} = R$ {subtotal:.2f}")

    if len(itens) == 0:
        print("\nPedido cancelado: nenhum item adicionado.")
        return

    conexao = conectar()
    cursor = conexao.cursor()
    cursor.execute("INSERT INTO pedidos (cliente_id, status, valor_total) VALUES (?, 'Pendente', ?)", (cliente_id, valor_total))
    pedido_id = cursor.lastrowid
    for item in itens:
        produto_id, quantidade, preco_unitario, subtotal = item
        cursor.execute(
            "INSERT INTO itens_pedido (pedido_id, produto_id, quantidade, preco_unitario, subtotal) VALUES (?, ?, ?, ?, ?)",
            (pedido_id, produto_id, quantidade, preco_unitario, subtotal))
    conexao.commit()
    conexao.close()
    print(f"\nPedido #{pedido_id} criado para {cliente['nome']}! Valor total: R$ {valor_total:.2f}")

def listar_pedidos(cliente_id=None, mostrar_itens=False):
    conexao = conectar()
    sql = "SELECT p.*, c.nome AS cliente_nome FROM pedidos p JOIN clientes c ON c.id = p.cliente_id"
    if cliente_id is None:
        pedidos = conexao.execute(sql + " ORDER BY p.id DESC").fetchall()
    else:
        pedidos = conexao.execute(sql + " WHERE p.cliente_id = ? ORDER BY p.id DESC", (cliente_id,)).fetchall()

    print("\n--- Pedidos ---")
    if len(pedidos) == 0:
        print("Nenhum pedido encontrado.")
        conexao.close()
        return

    total_geral = 0
    for pedido in pedidos:
        print(f"[#{pedido['id']}] Cliente: {pedido['cliente_nome']} | Status: {pedido['status']} | Total: R$ {pedido['valor_total']:.2f}")
        total_geral = total_geral + pedido["valor_total"]
        if mostrar_itens:
            itens = conexao.execute(
                "SELECT i.*, pr.nome AS produto_nome FROM itens_pedido i JOIN produtos pr ON pr.id = i.produto_id WHERE i.pedido_id = ?",
                (pedido["id"],)).fetchall()
            for item in itens:
                print(f"      - {item['quantidade']} x {item['produto_nome']} = R$ {item['subtotal']:.2f}")
    conexao.close()
    print(f"\nTotal de pedidos: {len(pedidos)} | Soma geral: R$ {total_geral:.2f}")

def atualizar_status_pedido():
    print("\n--- Atualizar Status do Pedido ---")
    pedido_id = ler_inteiro("ID do pedido: ")
    pedido = buscar_por_id("pedidos", pedido_id)
    if pedido is None:
        print("Pedido não encontrado.")
        return

    print(f"Status atual: {pedido['status']}")
    print("Status disponíveis:")
    for indice in range(len(STATUS_VALIDOS)):
        print(f"  {indice + 1}. {STATUS_VALIDOS[indice]}")

    opcao = ler_inteiro("Escolha o novo status (número): ")
    if opcao < 1 or opcao > len(STATUS_VALIDOS):
        print("Opção inválida.")
        return

    novo_status = STATUS_VALIDOS[opcao - 1]
    conexao = conectar()
    conexao.execute("UPDATE pedidos SET status = ? WHERE id = ?", (novo_status, pedido_id))
    conexao.commit()
    conexao.close()
    print(f"Status do pedido #{pedido_id} atualizado para '{novo_status}'.")

def relatorio_por_cliente():
    print("\n--- Relatório de Pedidos por Cliente ---")
    listar_clientes()
    cliente_id = ler_inteiro("\nID do cliente: ")
    listar_pedidos(cliente_id)

#MENU PRINCIPAL

def menu_principal():
    while True:
        print("\n" + "=" * 40)
        print(" SISTEMA DE CONTROLE DE PEDIDOS")
        print("=" * 40)
        print("1. Cadastrar cliente")
        print("2. Listar clientes")
        print("3. Cadastrar produto")
        print("4. Listar produtos")
        print("5. Registrar novo pedido")
        print("6. Listar todos os pedidos")
        print("7. Ver pedidos com itens (detalhado)")
        print("8. Atualizar status de um pedido")
        print("9. Relatório por cliente")
        print("0. Sair")
        opcao = input("\nEscolha uma opção: ").strip()

        match opcao:
            case "1": cadastrar_cliente()
            case "2": listar_clientes()
            case "3": cadastrar_produto()
            case "4": listar_produtos()
            case "5": criar_pedido()
            case "6": listar_pedidos()
            case "7": listar_pedidos(mostrar_itens=True)
            case "8": atualizar_status_pedido()
            case "9": relatorio_por_cliente()
            case "0":
                print("Encerrando o sistema. Até logo!")
                break
            case _:
                print("Opção inválida, tente novamente.")
        pausar()


if __name__ == "__main__":
    criar_tabelas()
    menu_principal()
