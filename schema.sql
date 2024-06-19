CREATE TABLE usuarios (
  id_usuario INT PRIMARY KEY AUTO_INCREMENT,
  nombre VARCHAR(255) NOT NULL,
  correo_electronico VARCHAR(255) UNIQUE NOT NULL,
  password VARCHAR(255) NOT NULL,
  fecha_creacion DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE conjuntos_datos (
  id_conjunto_datos INT PRIMARY KEY AUTO_INCREMENT,
  nombre VARCHAR(255) NOT NULL,
  fecha_creacion DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  id_usuario_creador INT NOT NULL,
  columna_evaluar VARCHAR(255) NOT NULL,
  columna_asociada VARCHAR(255) NOT NULL,
  FOREIGN KEY (id_usuario_creador) REFERENCES usuarios(id_usuario)
);


CREATE TABLE prompts (
  id_prompt INT PRIMARY KEY AUTO_INCREMENT,
  nombre_prompt VARCHAR(255) NOT NULL,
  contenido_prompt TEXT NOT NULL,
  tecnica_utilizada VARCHAR(255) NOT NULL,
  nombre_dataset VARCHAR(255),
  porcentaje_acierto FLOAT NOT NULL,
  recall FLOAT NOT NULL,
  f1 FLOAT NOT NULL,
  precc FLOAT NOT NULL,
  id_usuario INT NOT NULL,
  FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario)
);



