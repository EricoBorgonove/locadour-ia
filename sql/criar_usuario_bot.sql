-- Execute como administrador, depois de trocar a senha de exemplo.
CREATE USER IF NOT EXISTS 'locadora_bot_read'@'localhost' IDENTIFIED BY 'SUBSTITUA_POR_SENHA_FORTE';
GRANT SELECT ON locadora_ia_demo.* TO 'locadora_bot_read'@'localhost';
-- Se o usuário já existir, use ALTER USER ... IDENTIFIED BY ... para atualizar sua senha.
SHOW GRANTS FOR 'locadora_bot_read'@'localhost';
