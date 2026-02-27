Lston-Project (Backend) 🛒⚙️
Lston é uma plataforma de e-commerce estruturada para oferecer uma experiência de compra rápida e segura. Este repositório foca no backend da aplicação, construído para ser robusto e escalável, fornecendo os dados e as regras de negócio para a interface do usuário.

✨ Funcionalidades

API RESTful: Endpoints estruturados para gerenciamento de produtos, categorias e pedidos.

Autenticação Segura: Sistema de login com proteção de rotas utilizando JSON Web Tokens (JWT).

Criptografia de Dados: Hashing de senhas de usuários para garantir a segurança dos dados (utilizando bcrypt).

Gestão de Banco de Dados: Conexão otimizada e persistência de dados relacionais.

Middleware de Segurança e CORS: Controle de acesso e compartilhamento de recursos entre origens diferentes.

🚀 Tecnologias Utilizadas

Backend (API)

Linguagem: JavaScript (Node.js)

Framework Web: Express.js

Banco de Dados: PostgreSQL (via pacote pg)

Segurança: JWT (jsonwebtoken) e Bcrypt (bcryptjs)

Utilitários: Body-parser, CORS, Dotenv (variáveis de ambiente)

📦 Estrutura do Projeto
O repositório concentra-se na camada de serviços e dados:

server.js: Arquivo principal de inicialização do servidor Express e rotas.

db.js: Configuração e pool de conexão com o banco de dados PostgreSQL.

⚙️ Configuração e Instalação
Pré-requisitos

Node.js instalado.

Servidor PostgreSQL rodando.

Arquivo .env configurado com as credenciais do banco e chave secreta JWT.
