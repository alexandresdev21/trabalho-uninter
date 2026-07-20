
import sqlite3
import os
from datetime import datetime

NOME_BANCO = "pedidos.db"
STATUS_VALIDOS = ["Pendente", "Em Preparação", "Enviado", "Finalizado", "Cancelado"]


#BANCO DE DADOS#

def conectar():
    """Abre e retorna uma conexão com o banco SQLite."""
    caminho = os.path.join(os.path.dirname(os.path.abspath(__file__)), NOME_BANCO)
    conexao = sqlite3.connect(caminho)
    conexao.execute("PRAGMA foreign_keys = ON")
    conexao.row_factory = sqlite3.Row
    return conexao


def criar_tabelas():
    """Cria as tabelas do sistema caso ainda não existam."""
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS clientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            email TEXT,
            telefone TEXT,
            data_cadastro TEXT DEFAULT (datetime('now', 'localtime'))
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS produtos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            descricao TEXT,
            preco REAL NOT NULL CHECK (preco >= 0),
            estoque INTEGER DEFAULT 0
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS pedidos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente_id INTEGER NOT NULL,
            data_pedido TEXT DEFAULT (datetime('now', 'localtime')),
            status TEXT NOT NULL DEFAULT 'Pendente',
            valor_total REAL DEFAULT 0,
            FOREIGN KEY (cliente_id) REFERENCES clientes (id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS itens_pedido (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pedido_id INTEGER NOT NULL,
            produto_id INTEGER NOT NULL,
            quantidade INTEGER NOT NULL CHECK (quantidade > 0),
            preco_unitario REAL NOT NULL,
            subtotal REAL NOT NULL,
            FOREIGN KEY (pedido_id) REFERENCES pedidos (id),
            FOREIGN KEY (produto_id) REFERENCES produtos (id)
        )
    """)

    conexao.commit()
    conexao.close()

#FUNÇÕES AUXILIARES DE ENTRADA#

def ler_inteiro(mensagem, permitir_vazio=False):
    while True:
        valor = input(mensagem).strip()
        if permitir_vazio and valor == "":
            return None
        try:
            return int(valor)
        except ValueError:
            print("  >> Digite um número inteiro válido.")


def ler_float(mensagem):
    while True:
        valor = input(mensagem).strip().replace(",", ".")
        try:
            return float(valor)
        except ValueError:
            print("  >> Digite um valor numérico válido (ex: 19.90).")


def ler_data(mensagem, permitir_vazio=True):
    while True:
        valor = input(mensagem).strip()
        if valor == "" and permitir_vazio:
            return None
        try:
            datetime.strptime(valor, "%Y-%m-%d")
            return valor
        except ValueError:
            print("  >> Use o formato AAAA-MM-DD (ex: 2026-07-01).")


def pausar():
    input("\nPressione ENTER para continuar...")


#CADASTRO DE CLIENTES#

def cadastrar_cliente():
    print("\n--- Cadastro de Cliente ---")
    nome = input("Nome do cliente: ").strip()
    if not nome:
        print("Nome é obrigatório. Operação cancelada.")
        return
    email = input("Email (opcional): ").strip()
    telefone = input("Telefone (opcional): ").strip()

    conexao = conectar()
    conexao.execute(
        "INSERT INTO clientes (nome, email, telefone) VALUES (?, ?, ?)",
        (nome, email, telefone),
    )
    conexao.commit()
    conexao.close()
    print(f"Cliente '{nome}' cadastrado com sucesso!")


def listar_clientes():
    conexao = conectar()
    clientes = conexao.execute("SELECT * FROM clientes ORDER BY nome").fetchall()
    conexao.close()

    print("\n--- Lista de Clientes ---")
    if not clientes:
        print("Nenhum cliente cadastrado.")
        return
    for c in clientes:
        print(f"[{c['id']}] {c['nome']} | Email: {c['email'] or '-'} | Tel: {c['telefone'] or '-'}")


def buscar_cliente_por_id(cliente_id):
    conexao = conectar()
    cliente = conexao.execute(
        "SELECT * FROM clientes WHERE id = ?", (cliente_id,)
    ).fetchone()
    conexao.close()
    return cliente

#CADASTRO DE PRODUTOS#

def cadastrar_produto():
    print("\n--- Cadastro de Produto ---")
    nome = input("Nome do produto/serviço: ").strip()
    if not nome:
        print("Nome é obrigatório. Operação cancelada.")
        return
    descricao = input("Descrição (opcional): ").strip()
    preco = ler_float("Preço unitário: R$ ")
    estoque = ler_inteiro("Estoque disponível (ENTER = 0): ", permitir_vazio=True) or 0

    conexao = conectar()
    conexao.execute(
        "INSERT INTO produtos (nome, descricao, preco, estoque) VALUES (?, ?, ?, ?)",
        (nome, descricao, preco, estoque),
    )
    conexao.commit()
    conexao.close()
    print(f"Produto '{nome}' cadastrado com sucesso!")


def listar_produtos():
    conexao = conectar()
    produtos = conexao.execute("SELECT * FROM produtos ORDER BY nome").fetchall()
    conexao.close()

    print("\n--- Lista de Produtos/Serviços ---")
    if not produtos:
        print("Nenhum produto cadastrado.")
        return
    for p in produtos:
        print(f"[{p['id']}] {p['nome']} | R$ {p['preco']:.2f} | Estoque: {p['estoque']}")


def buscar_produto_por_id(produto_id):
    conexao = conectar()
    produto = conexao.execute(
        "SELECT * FROM produtos WHERE id = ?", (produto_id,)
    ).fetchone()
    conexao.close()
    return produto


#REGISTRO DE PEDIDOS#

def criar_pedido():
    print("\n--- Novo Pedido ---")
    listar_clientes()
    cliente_id = ler_inteiro("\nID do cliente: ")
    cliente = buscar_cliente_por_id(cliente_id)
    if not cliente:
        print("Cliente não encontrado. Operação cancelada.")
        return

    itens = []  # cada item: (produto_id, quantidade, preco_unitario, subtotal)
    listar_produtos()

    print("\nAdicione os itens do pedido (digite 0 no ID do produto para finalizar).")
    while True:
        produto_id = ler_inteiro("\nID do produto (0 = finalizar itens): ")
        if produto_id == 0:
            break
        produto = buscar_produto_por_id(produto_id)
        if not produto:
            print("  >> Produto não encontrado, tente novamente.")
            continue
        quantidade = ler_inteiro(f"Quantidade de '{produto['nome']}': ")
        if quantidade <= 0:
            print("  >> Quantidade deve ser maior que zero.")
            continue
        preco_unitario = produto["preco"]
        subtotal = preco_unitario * quantidade
        itens.append((produto_id, quantidade, preco_unitario, subtotal))
        print(f"  >> Adicionado: {quantidade} x {produto['nome']} = R$ {subtotal:.2f}")

    if not itens:
        print("\nPedido cancelado: nenhum item adicionado.")
        return

    valor_total = sum(item[3] for item in itens)

    conexao = conectar()
    cursor = conexao.cursor()
    cursor.execute(
        "INSERT INTO pedidos (cliente_id, status, valor_total) VALUES (?, ?, ?)",
        (cliente_id, "Pendente", valor_total),
    )
    pedido_id = cursor.lastrowid

    for produto_id, quantidade, preco_unitario, subtotal in itens:
        cursor.execute(
            """INSERT INTO itens_pedido
               (pedido_id, produto_id, quantidade, preco_unitario, subtotal)
               VALUES (?, ?, ?, ?, ?)""",
            (pedido_id, produto_id, quantidade, preco_unitario, subtotal),
        )

    conexao.commit()
    conexao.close()

    print(f"\nPedido #{pedido_id} criado com sucesso para {cliente['nome']}!")
    print(f"Valor total: R$ {valor_total:.2f}")


def listar_pedidos(pedidos=None):
    """Lista pedidos (resumo). Se 'pedidos' não for informado, lista todos."""
    if pedidos is None:
        conexao = conectar()
        pedidos = conexao.execute("""
            SELECT p.*, c.nome AS cliente_nome
            FROM pedidos p
            JOIN clientes c ON c.id = p.cliente_id
            ORDER BY p.data_pedido DESC
        """).fetchall()
        conexao.close()

    print("\n--- Pedidos ---")
    if not pedidos:
        print("Nenhum pedido encontrado.")
        return
    for p in pedidos:
        print(f"[#{p['id']}] Cliente: {p['cliente_nome']} | "
              f"Data: {p['data_pedido']} | Status: {p['status']} | "
              f"Total: R$ {p['valor_total']:.2f}")


def ver_detalhes_pedido():
    pedido_id = ler_inteiro("\nID do pedido: ")
    conexao = conectar()
    pedido = conexao.execute("""
        SELECT p.*, c.nome AS cliente_nome, c.email, c.telefone
        FROM pedidos p JOIN clientes c ON c.id = p.cliente_id
        WHERE p.id = ?
    """, (pedido_id,)).fetchone()

    if not pedido:
        print("Pedido não encontrado.")
        conexao.close()
        return

    itens = conexao.execute("""
        SELECT i.*, pr.nome AS produto_nome
        FROM itens_pedido i JOIN produtos pr ON pr.id = i.produto_id
        WHERE i.pedido_id = ?
    """, (pedido_id,)).fetchall()
    conexao.close()

    print(f"\n--- Pedido #{pedido['id']} ---")
    print(f"Cliente: {pedido['cliente_nome']} ({pedido['email'] or '-'})")
    print(f"Data: {pedido['data_pedido']}")
    print(f"Status: {pedido['status']}")
    print("Itens:")
    for i in itens:
        print(f"  - {i['quantidade']} x {i['produto_nome']} "
              f"(R$ {i['preco_unitario']:.2f} cada) = R$ {i['subtotal']:.2f}")
    print(f"VALOR TOTAL: R$ {pedido['valor_total']:.2f}")


#CONTROLE DE STATUS#

def atualizar_status_pedido():
    print("\n--- Atualizar Status do Pedido ---")
    pedido_id = ler_inteiro("ID do pedido: ")

    conexao = conectar()
    pedido = conexao.execute("SELECT * FROM pedidos WHERE id = ?", (pedido_id,)).fetchone()
    if not pedido:
        print("Pedido não encontrado.")
        conexao.close()
        return

    print(f"Status atual: {pedido['status']}")
    print("Status disponíveis:")
    for idx, status in enumerate(STATUS_VALIDOS, start=1):
        print(f"  {idx}. {status}")

    opcao = ler_inteiro("Escolha o novo status (número): ")
    if opcao is None or opcao < 1 or opcao > len(STATUS_VALIDOS):
        print("Opção inválida.")
        conexao.close()
        return

    novo_status = STATUS_VALIDOS[opcao - 1]
    conexao.execute("UPDATE pedidos SET status = ? WHERE id = ?", (novo_status, pedido_id))
    conexao.commit()
    conexao.close()
    print(f"Status do pedido #{pedido_id} atualizado para '{novo_status}'.")

#RELATÓRIOS#

def relatorio_por_periodo():
    print("\n--- Relatório de Pedidos por Período ---")
    data_inicio = ler_data("Data inicial (AAAA-MM-DD, ENTER = sem limite): ")
    data_fim = ler_data("Data final (AAAA-MM-DD, ENTER = sem limite): ")

    query = """
        SELECT p.*, c.nome AS cliente_nome
        FROM pedidos p JOIN clientes c ON c.id = p.cliente_id
        WHERE 1=1
    """
    parametros = []
    if data_inicio:
        query += " AND date(p.data_pedido) >= date(?)"
        parametros.append(data_inicio)
    if data_fim:
        query += " AND date(p.data_pedido) <= date(?)"
        parametros.append(data_fim)
    query += " ORDER BY p.data_pedido"

    conexao = conectar()
    pedidos = conexao.execute(query, parametros).fetchall()
    conexao.close()

    listar_pedidos(pedidos)
    if pedidos:
        total = sum(p["valor_total"] for p in pedidos)
        print(f"\nTotal de pedidos: {len(pedidos)} | Valor total somado: R$ {total:.2f}")


def relatorio_por_cliente():
    print("\n--- Relatório de Pedidos por Cliente ---")
    listar_clientes()
    cliente_id = ler_inteiro("\nID do cliente: ")

    conexao = conectar()
    pedidos = conexao.execute("""
        SELECT p.*, c.nome AS cliente_nome
        FROM pedidos p JOIN clientes c ON c.id = p.cliente_id
        WHERE p.cliente_id = ?
        ORDER BY p.data_pedido DESC
    """, (cliente_id,)).fetchall()
    conexao.close()

    listar_pedidos(pedidos)
    if pedidos:
        total = sum(p["valor_total"] for p in pedidos)
        print(f"\nTotal de pedidos: {len(pedidos)} | Valor total somado: R$ {total:.2f}")

#MENU PRINCIPAL#

def menu_principal():
    while True:
        print("\n" + "=" * 45)
        print(" SISTEMA DE CONTROLE DE PEDIDOS")
        print("=" * 45)
        print(" 1. Cadastrar cliente")
        print(" 2. Listar clientes")
        print(" 3. Cadastrar produto/serviço")
        print(" 4. Listar produtos/serviços")
        print(" 5. Registrar novo pedido")
        print(" 6. Listar todos os pedidos")
        print(" 7. Ver detalhes de um pedido")
        print(" 8. Atualizar status de um pedido")
        print(" 9. Relatório por período")
        print("10. Relatório por cliente")
        print(" 0. Sair")
        print("=" * 45)

        opcao = input("Escolha uma opção: ").strip()

        if opcao == "1":
            cadastrar_cliente()
        elif opcao == "2":
            listar_clientes()
        elif opcao == "3":
            cadastrar_produto()
        elif opcao == "4":
            listar_produtos()
        elif opcao == "5":
            criar_pedido()
        elif opcao == "6":
            listar_pedidos()
        elif opcao == "7":
            ver_detalhes_pedido()
        elif opcao == "8":
            atualizar_status_pedido()
        elif opcao == "9":
            relatorio_por_periodo()
        elif opcao == "10":
            relatorio_por_cliente()
        elif opcao == "0":
            print("Encerrando o sistema. Até logo!")
            break
        else:
            print("Opção inválida, tente novamente.")

        pausar()


if __name__ == "__main__":
    criar_tabelas()
    menu_principal()
