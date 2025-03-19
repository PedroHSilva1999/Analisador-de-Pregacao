# Analisador de Pregações

Este é um sistema web que analisa pregações do YouTube, extraindo os principais tópicos e versículos bíblicos mencionados.

## Requisitos

- Python 3.8 ou superior
- Chave de API do Gemini

## Instalação

1. Clone este repositório
2. Instale as dependências:
```bash
pip install -r requirements.txt
```

3. Crie um arquivo `.env` na raiz do projeto e adicione sua chave da API OpenAI:
```
OPENAI_API_KEY=sua_chave_aqui
```

## Como usar

1. Inicie o servidor:
```bash
uvicorn main:app --reload
```

2. Acesse http://localhost:8000 no seu navegador

3. Cole a URL do vídeo do YouTube que deseja analisar

4. Clique em "Analisar Pregação" e aguarde o resultado

## Funcionalidades

- Extração automática de tópicos principais
- Identificação de versículos bíblicos citados
- Análise detalhada do conteúdo da pregação 



