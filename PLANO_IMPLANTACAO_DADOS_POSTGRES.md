# 📊 Plano de Implantação: API FastAPI + PostgreSQL + Webscraping

## Objetivo
Integrar a API FastAPI com um banco de dados PostgreSQL alimentado por webscraping da dashboard real da empresa, eliminando mockdata e garantindo dados reais e atualizados para a dashboard.

---

## 1. Infraestrutura do Banco de Dados
- [ ] Definir onde o PostgreSQL ficará hospedado (local, cloud, Docker, etc).
- [ ] Criar o banco de dados e usuário dedicado para a aplicação.
- [ ] Modelar e criar as tabelas necessárias (corridas, alertas, performance, etc).
- [ ] Testar conexão ao banco via ferramenta (DBeaver, psql, etc).

---

## 2. Webscraping e Ingestão de Dados
- [ ] Definir as páginas/rotas da dashboard real a serem extraídas.
- [ ] Implementar script de scraping (Python: BeautifulSoup, Selenium, Playwright, etc).
- [ ] Mapear e tratar os dados extraídos para o formato das tabelas do banco.
- [ ] Inserir/atualizar os dados no PostgreSQL (usar SQLAlchemy ou psycopg2).
- [ ] Testar scraping manualmente e validar dados no banco.
- [ ] Automatizar execução do scraping (cron, agendador, Airflow, etc).

---

## 3. Integração FastAPI + PostgreSQL
- [ ] Instalar dependências: `asyncpg`, `sqlalchemy`.
- [ ] Configurar conexão assíncrona no FastAPI (usar variáveis de ambiente).
- [ ] Criar models SQLAlchemy para as tabelas.
- [ ] Refatorar endpoints para buscar dados reais do banco (substituir mockdata).
- [ ] Testar endpoints com dados reais (Swagger, Postman).

---

## 4. Segurança e Boas Práticas
- [ ] Usar variáveis de ambiente para credenciais do banco.
- [ ] Validar e sanitizar dados do scraping antes de inserir no banco.
- [ ] Implementar logs e tratamento de erros no scraping e na API.
- [ ] (Opcional) Implementar cache (Redis) para endpoints de leitura intensiva.

---

## 5. Checklist Final
- [ ] Banco de dados populado e acessível.
- [ ] Scraping automatizado e funcional.
- [ ] API FastAPI servindo dados reais para o frontend.
- [ ] Dashboard exibindo dados atualizados.
- [ ] Documentação dos fluxos e scripts.

---

## Referências
- [SQLAlchemy](https://docs.sqlalchemy.org/)
- [asyncpg](https://magicstack.github.io/asyncpg/current/)
- [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)
- [Selenium](https://selenium-python.readthedocs.io/)
- [Playwright](https://playwright.dev/python/)
- [FastAPI](https://fastapi.tiangolo.com/)
- [PostgreSQL](https://www.postgresql.org/)
