-- Create separate databases for each microservice
CREATE DATABASE auth_db;
CREATE DATABASE triagem_db;
CREATE DATABASE classificacao_db;
CREATE DATABASE prontuario_db;

-- Grant permissions to user
GRANT ALL PRIVILEGES ON DATABASE auth_db TO "user";
GRANT ALL PRIVILEGES ON DATABASE triagem_db TO "user";
GRANT ALL PRIVILEGES ON DATABASE classificacao_db TO "user";
GRANT ALL PRIVILEGES ON DATABASE prontuario_db TO "user";
