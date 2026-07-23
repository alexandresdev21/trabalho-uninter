# Sistema para Controle de Pedidos

Projeto da Unidade Curricular **Arquitetura de Sistemas Ciberfísicos e Modelagem (Mini-CPS)** — Grupo 4.

## Equipe

- Alexandre Eugênio Souza da Silveira (ES)
- André Felipe Coêlho Reis (ES)

## Descrição

Sistema de linha de comando desenvolvido em **Python** com banco de dados **SQLite**, que permite gerenciar todo o ciclo de um pedido: cadastro de clientes e produtos, criação de pedidos com múltiplos itens, cálculo automático de valores, controle de status e geração de relatórios gerenciais.

## Funcionalidades

- Cadastro e listagem de clientes
- Cadastro e listagem de produtos/serviços (com preço e estoque)
- Registro de pedidos com múltiplos itens e cálculo automático do valor total
- Visualização detalhada de um pedido (itens, cliente, valores)
- Atualização de status do pedido: `Pendente` → `Em Preparação` → `Enviado` → `Finalizado` / `Cancelado`
- Relatório de pedidos por período (data inicial/final)
- Relatório de pedidos por cliente

## Modelo de dados

O banco (`pedidos.db`) é criado automaticamente na primeira execução, com 4 tabelas:

| Tabela | Descrição |
|---|---|
| `clientes` | id, nome, email, telefone, data_cadastro |
| `produtos` | id, nome, descricao, preco, estoque |
| `pedidos` | id, cliente_id (FK), data_pedido, status, valor_total |
| `itens_pedido` | id, pedido_id (FK), produto_id (FK), quantidade, preco_unitario, subtotal |

## Tecnologias

- Python 3
- SQLite (módulo `sqlite3` da biblioteca padrão)

## Como executar

```bash
# Clone o repositório
git clone https://github.com/SEU-USUARIO/NOME-DO-REPOSITORIO.git
cd NOME-DO-REPOSITORIO

# Execute o sistema (não há dependências externas)
python3 main.py
```

O banco de dados `pedidos.db` será criado automaticamente na mesma pasta do `main.py` na primeira execução.

## Estrutura do menu

```
1. Cadastrar cliente
2. Listar clientes
3. Cadastrar produto/serviço
4. Listar produtos/serviços
5. Registrar novo pedido
6. Listar todos os pedidos
7. Ver detalhes de um pedido
8. Atualizar status de um pedido
9. Relatório por período
10. Relatório por cliente
0. Sair
```

