# Como usei IA

**Ferramenta:** Claude (Anthropic), no chat do claude.ai e na extensão do VS Code. Até o início do desafio, a ferramenta oficial do programa não tinha sido informada.

**Como trabalhei:** a IA atuou como par no código do ETL e como tutora nos conceitos e no SQL. Cada passo foi feito um por vez: a IA propunha o código, eu revisava, rodava e testava, e só depois aprovava. Defini algumas regras durante o projeto: a IA não edita arquivos sem eu pedir, não sai do escopo do desafio sem perguntar, e todo commit só é feito depois de eu aprovar a mensagem.

Usei as duas ferramentas com papéis diferentes: o Claude no VS Code como par no código, configurado com um arquivo de instruções (`CLAUDE.md`) que limita a IA a um passo por vez, sem editar arquivos sem pedir e sem entregar o ETL pronto; e o chat do claude.ai como tutor de conceitos e como revisor independente, para conferir o código proposto no VS Code antes de aplicar.

## Sugestões aceitas

### 1. Aceitar só o status 200 na extração
- **Papel da IA:** par (ETL)
- **O que pedi:** verificar o status HTTP de cada página da API.
- **O que a IA propôs:** interromper com erro quando `status_code != 200`.
- **Decisão:** aceitei, depois de questionar.
- **Por quê:** perguntei por que tratar todo status diferente de 200 como erro, já que nem todo código diferente de 200 é falha. A IA comparou com `resposta.ok` e `raise_for_status()`: as duas opções aceitariam 204 (sem corpo) e 206 (conteúdo parcial), e o ETL perderia dados sem perceber. Mantive o `!= 200` e pedi um comentário no código explicando o motivo.
- **Como validei:** conferi no `api_verdejar.py` que a API só responde 200, 400 e 404. Testei com a API desligada e com uma rota errada: os dois casos mostram uma mensagem de uma linha, sem traceback.

### 2. Usar `Decimal(str(valor))` para os valores em dinheiro
- **Papel da IA:** par (ETL)
- **O que pedi:** a função da A4, para converter `valor_total` com vírgula.
- **O que a IA propôs:** converter com `Decimal(str(valor))` e `quantize` de 2 casas, e reaproveitar a mesma função para o `preco_unitario` dos itens.
- **Decisão:** aceitei.
- **Por quê:** o `float` acumula erro de arredondamento (`3 * 4.3` dá `12.899999999999999`), e a reconciliação exige diferença zero.
- **Como validei:** testes da A4 e da A6 (com `4.3` e `1.1`, que com float dariam `15.099999999999998`) e a reconciliação com `diferenca=0.00`.

### 3. Idempotência com DELETE na ordem inversa das FKs
- **Papel da IA:** par (ETL)
- **O que pedi:** que rodar o ETL duas vezes não duplicasse dados.
- **O que a IA propôs:** duas opções: (A) `DELETE` na ordem inversa das FKs e `INSERT` na ordem direta, em uma transação, ou (B) `INSERT ... ON CONFLICT DO UPDATE`.
- **Decisão:** aceitei a A.
- **Por quê:** é mais simples de explicar, e o banco fica sempre igual à última extração. Na B, registros que saíssem da origem continuariam no banco.
- **Como validei:** duas execuções seguidas, ambas com `carga: clientes=1000 produtos=12 pedidos=5000 itens=12455`, sem erro de chave duplicada.

### 4. Um mini-ETL análogo para entender o conceito
- **Papel da IA:** tutora (conceitos)
- **O que pedi:** no início eu não conseguia visualizar o desafio. Pedi um exemplo parecido, mais simples, para entender o caminho completo antes de começar.
- **O que a IA propôs:** um mini-ETL de uma livraria fictícia (7 livros, com as mesmas armadilhas de data, valor com vírgula e registro repetido), carregado no SQLite, com reconciliação e 3 testes, explicado passo a passo com comparações com JavaScript.
- **Decisão:** aceitei.
- **Por quê:** era um exemplo análogo, não a solução do desafio. Serviu para entender a lógica de extrair, transformar, carregar e provar.
- **Como validei:** rodei o mini-ETL na minha máquina: saída esperada nas 4 linhas, duas execuções com as mesmas contagens e `3 passed` no pytest.

### 5. Contar datas, valores e divergentes só depois da A5
- **Papel da IA:** par (ETL)
- **O que pedi:** a função que transforma os pedidos, com os contadores.
- **O que a IA propôs:** remover os repetidos primeiro e contar só entre os pedidos únicos, e me pediu para confirmar a decisão.
- **Decisão:** aceitei.
- **Por quê:** se a contagem fosse sobre os registros brutos, um pedido repetido contaria duas vezes, mas só é gravado uma vez. Os contadores precisam descrever o que vai para o banco.
- **Como validei:** um teste com um pedido repetido que conta uma vez só, e a revisão independente da função com os pedidos reais.

### 6. Tutoria nas consultas SQL
- **Papel da IA:** tutora (SQL)
- **O que pedi:** ajuda para escrever as três consultas de validação.
- **O que a IA fez:** explicou os conceitos (agrupar por mês, JOIN com clientes, filtro por divergente) e me deu um esqueleto com lacunas, sem as consultas prontas. Depois de escrever as minhas, pedi as respostas da IA para comparar.
- **Decisão:** as consultas são minhas; a comparação confirmou que estavam iguais.
- **Por quê das decisões:** somei `valor_itens` porque é o valor reconciliado com a origem, e excluí os cancelados da consulta (a) porque não geraram venda. Na (b), contei todos os status porque a pergunta é a quantidade de pedidos.
- **Como validei:** o teste de consulta: a soma dos meses bateu com a soma geral, com o mesmo filtro nas duas.

## Sugestões rejeitadas

### 1. A1 tratando também e-mail vazio
- **Papel da IA:** par (ETL)
- **O que pedi:** a função da A1 (e-mail nulo).
- **O que a IA propôs:** tratar também `""` e e-mails só com espaços, com `strip()`. Ela também alterou sozinha a linha da A1 no contrato de dados, que eu já tinha aprovado.
- **Decisão:** rejeitei.
- **Por quê:** o desafio define a A1 só como valor nulo, e conferi que nenhum e-mail vem vazio ou com espaços. O tratamento extra não mudaria nenhum resultado e só adicionaria código para testar e explicar. Voltei o contrato ao texto original e deixei a premissa documentada no README.
- **Como validei:** conferi nos dados que não há e-mails vazios. Os testes da A1 cobrem `None` e um e-mail preenchido.

### 2. Nome da tabela com f-string no `count(*)`
- **Papel da IA:** par (ETL)
- **O que pedi:** as contagens das tabelas depois da carga.
- **O que a IA propôs:** um laço com `f"SELECT count(*) FROM {tabela}"`, com os nomes vindos de uma lista fixa no código.
- **Decisão:** rejeitei.
- **Por quê:** mesmo sem risco real, montar SQL com f-string parece quebrar a regra de não montar SQL concatenando texto. Preferi uma consulta por tabela, escrita por extenso.
- **Como validei:** a linha `carga:` saiu igual nas duas execuções.

### 3. Restaurar o `schema_sqlite.sql`
- **Papel da IA:** par (organização do repositório)
- **O que pedi:** tirar a pasta de anotações pessoais do versionamento.
- **O que a IA propôs:** também restaurar o `insumos/schema_sqlite.sql`, que eu tinha apagado, por ser um insumo oficial do desafio.
- **Decisão:** rejeitei.
- **Por quê:** o projeto usa o caminho B (PostgreSQL), e o schema do SQLite não faz sentido nele.
- **Como validei:** a busca por `schema_sqlite` no projeto só encontrou citações no `README_insumos.md`, nenhuma em código.

### 4. Manter o psycopg usando a libpq do instalador oficial
- **Papel da IA:** par (ETL)
- **O que pedi:** uma forma de continuar com o psycopg depois do bloqueio do Windows (ver Falhas e retrabalho, item 4).
- **O que a IA propôs:** desinstalar o `psycopg-binary` e usar a implementação "python" do psycopg, carregando a `libpq.dll` das ferramentas de cliente do instalador oficial do PostgreSQL, com a pasta no PATH.
- **Decisão:** rejeitei.
- **Por quê:** exigiria instalar o PostgreSQL (mesmo só o cliente) e configurar o PATH, sem garantia de que o Windows não bloquearia a DLL também. O pg8000 resolve sem nada disso.
- **Como validei:** a conexão e a carga completa funcionaram com o pg8000.

## Falhas e retrabalho

### 1. Commits feitos sem a minha revisão da mensagem
- **Papel da IA:** par (organização do repositório)
- **O que aconteceu:** a IA fez commits depois que aprovei o código, sem me mostrar a mensagem antes, e incluiu uma linha de coautoria em todos.
- **Como percebi:** pedi a lista de todos os commits e revisei um por um.
- **Retrabalho:** os 3 commits locais foram reescritos com títulos aprovados por mim e sem a linha de coautoria. Passei a exigir aprovar cada título antes de qualquer commit, porque os commits são avaliados.
- **Como validei:** `git log` antes e depois, com o conteúdo dos arquivos idêntico. Nada tinha ido para o GitHub.

### 2. Função da A1 que não fazia nada
- **Papel da IA:** par (ETL)
- **O que aconteceu:** depois que voltei a A1 para só `null`, a função proposta (`tratar_email`) apenas devolvia o próprio valor recebido.
- **Como percebi:** a A1 pede manter o cliente, gravar nulo e contar. Não há nada para transformar, só para identificar.
- **Retrabalho:** substituí pela minha própria função, `email_ausente(email)`, que devolve `email is None`. A contagem ficou na função que transforma os clientes.
- **Como validei:** 2 testes (`None` → `True`; e-mail preenchido → `False`) e `emails_nulos` na saída do ETL.

### 3. Comando de instalação bloqueado pelo Windows
- **Papel da IA:** tutora (ambiente)
- **O que aconteceu:** a IA me orientou a instalar as bibliotecas com `pip install -r requirements.txt`. O Windows (Smart App Control) bloqueou o `pip.exe`: "Uma política de Controle de Aplicativo bloqueou este arquivo".
- **Como percebi:** o erro no terminal.
- **Retrabalho:** troquei por `python -m pip install -r requirements.txt`, que chama o pip pelo Python (que é assinado). Pelo mesmo motivo, os testes rodam com `python -m pytest`.
- **Como validei:** a instalação concluiu, e as bibliotecas apareceram no `python -m pip list`.

### 4. Biblioteca de conexão sugerida bloqueada pelo Windows
- **Papel da IA:** par (ETL)
- **O que aconteceu:** a IA sugeriu o `psycopg[binary]` no `requirements.txt`. Na carga, o Windows bloqueou a DLL da libpq que vem no pacote ("DLL load failed while importing pq").
- **Como percebi:** o import do psycopg falhou ao testar a conexão.
- **Retrabalho:** a IA sugeriu o pg8000, que é 100% Python, e eu aceitei. Não desliguei o Smart App Control, que é uma proteção do sistema e, no Windows 11, só volta reinstalando o Windows. O desafio permite outra biblioteca ("por exemplo, psycopg"). Troquei o `conectar()` e o `requirements.txt`.
- **Como validei:** `SELECT count(*) FROM produtos` pelo `conectar()`, depois a carga completa e a reconciliação com `diferenca=0.00`.
