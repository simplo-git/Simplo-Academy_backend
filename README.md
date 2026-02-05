# Simplo Academy Backend

Backend para o sistema Simplo Academy, desenvolvido em Flask.

## Instalação

1.  Crie um ambiente virtual:
    ```bash
    python -m venv venv
    ```
2.  Ative o ambiente virtual:
    - Windows: `venv\Scripts\activate`
    - Linux/Mac: `source venv/bin/activate`
3.  Instale as dependências:
    ```bash
    pip install -r requirements.txt
    ```
4.  Configure as variáveis de ambiente no arquivo `.env` (ex: `MONGO`).

## Execução

```bash
python run.py
```
O servidor rodará em `http://localhost:5000`.

## Documentação da API

Todas as rotas são prefixadas com `/api`.

### 1. Usuários (`/users`)

| Método | Rota               | Descrição                                      |
| :----- | :----------------- | :--------------------------------------------- |
| POST   | `/users`           | Cria um novo usuário.                          |
| GET    | `/users`           | Lista todos os usuários.                       |
| GET    | `/users/<id>`      | Busca um usuário pelo ID.                      |
| PUT    | `/users/<id>`      | Atualiza um usuário.                           |
| DELETE | `/users/<id>`      | Remove um usuário.                             |
| POST   | `/users/login`     | Realiza login (retorna sucesso/falha).         |

### 2. Cargos (`/roles`)

| Método | Rota               | Descrição                                      |
| :----- | :----------------- | :--------------------------------------------- |
| POST   | `/roles`           | Cria um novo cargo.                            |
| GET    | `/roles`           | Lista todos os cargos.                         |
| PUT    | `/roles/<id>`      | Atualiza um cargo.                             |
| DELETE | `/roles/<id>`      | Remove um cargo.                               |

### 3. Certificados (`/certificates`)

| Método | Rota                 | Descrição                                      |
| :----- | :------------------- | :--------------------------------------------- |
| POST   | `/certificates`      | Cria um novo certificado.                      |
| GET    | `/certificates`      | Lista todos os certificados.                   |
| GET    | `/certificates/<id>` | Busca um certificado pelo ID.                  |
| PUT    | `/certificates/<id>` | Atualiza um certificado.                       |
| DELETE | `/certificates/<id>` | Remove um certificado.                         |

### 4. Templates de Atividade (`/activity-templates`)

| Método | Rota                                  | Descrição                                                                      |
| :----- | :------------------------------------ | :----------------------------------------------------------------------------- |
| POST   | `/activity-templates`                 | Cria um novo template de atividade.                                            |
| GET    | `/activity-templates`                 | Lista templates. Filtros opcionais: `?tipo=`.                                  |
| GET    | `/activity-templates/<id>`            | Busca um template pelo ID.                                                     |
| PUT    | `/activity-templates/<id>`            | Atualiza um template.                                                          |
| DELETE | `/activity-templates/<id>`            | Remove um template.                                                            |
| GET    | `/activity-templates/types`           | Lista tipos de atividade disponíveis.                                          |
| POST   | `/activity-templates/upload`          | Upload de arquivo base64. Retorna URL interna.                                 |
| POST   | `/activity-templates/video-upload`    | Cria template de vídeo com upload base64 integrado.                            |

### 5. Conteúdos (`/conteudos`)

| Método | Rota                 | Descrição                                      |
| :----- | :------------------- | :--------------------------------------------- |
| POST   | `/conteudos`         | Cria um novo conteúdo.                         |
| GET    | `/conteudos`         | Lista todos os conteúdos.                      |
| GET    | `/conteudos/<id>`    | Busca um conteúdo pelo ID.                     |
| PUT    | `/conteudos/<id>`    | Atualiza um conteúdo.                          |
| DELETE | `/conteudos/<id>`    | Remove um conteúdo.                            |

> **Nota sobre Conteúdos**: O campo `setor` é preenchido automaticamente com base nos setores dos usuários vinculados, ou resolve IDs enviados no campo `setores` (plural) para garantir que armazenamos `{"id": "...", "nome": "..."}`.

### 6. Arquivos (`/files`)

| Método | Rota                          | Descrição                                      |
| :----- | :---------------------------- | :--------------------------------------------- |
| GET    | `/files/<folder>/<filename>`  | Serve arquivos estáticos salvos (video/docs/img).|
| DELETE | `/files/<folder>/<filename>`  | Remove um arquivo físico do servidor.          |

### 7. Sistema

| Método | Rota          | Descrição                                      |
| :----- | :------------ | :--------------------------------------------- |
| GET    | `/verify-db`  | Verifica status da conexão com o Banco de Dados.|
