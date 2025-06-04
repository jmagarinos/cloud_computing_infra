CREATE TABLE IF NOT EXISTS persona (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    apellido VARCHAR(100) NOT NULL,
    telefono VARCHAR(20) NOT NULL,
    direccion VARCHAR(200) NOT NULL,
    mail VARCHAR(100) NOT NULL UNIQUE,
    cognito_sub VARCHAR(255) UNIQUE
);

CREATE TABLE IF NOT EXISTS vianda (
    id SERIAL PRIMARY KEY,
    titulo VARCHAR(100) NOT NULL,
    imagen VARCHAR(255),
    descripcion TEXT NOT NULL,
    precio DECIMAL(10,2) NOT NULL,
    fk_dueno INTEGER NOT NULL,
    FOREIGN KEY (fk_dueno) REFERENCES persona(id)
);

CREATE TABLE IF NOT EXISTS ventas (
    id SERIAL PRIMARY KEY,
    fk_vianda INTEGER NOT NULL,
    fk_persona INTEGER NOT NULL,
    cantidad INTEGER NOT NULL,
    fecha_venta TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (fk_vianda) REFERENCES vianda(id),
    FOREIGN KEY (fk_persona) REFERENCES persona(id)
);

CREATE INDEX IF NOT EXISTS idx_vianda_dueno ON vianda(fk_dueno);
CREATE INDEX IF NOT EXISTS idx_ventas_vianda ON ventas(fk_vianda);
CREATE INDEX IF NOT EXISTS idx_ventas_persona ON ventas(fk_persona);
