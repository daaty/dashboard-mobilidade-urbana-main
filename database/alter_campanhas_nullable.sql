-- Torna a coluna cidade da tabela campanhas nullable para permitir inserção apenas com cidade_id
ALTER TABLE campanhas ALTER COLUMN cidade DROP NOT NULL;

-- Após isso, os INSERTs funcionarão normalmente usando apenas cidade_id.
