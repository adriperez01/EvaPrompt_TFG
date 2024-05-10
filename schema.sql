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

CREATE TABLE evaluaciones (
  id_evaluacion INT PRIMARY KEY AUTO_INCREMENT,
  id_prompt INT NOT NULL,
  id_conjunto_datos INT NOT NULL,
  texto_generado TEXT NOT NULL,
  porcentaje_acierto FLOAT NOT NULL,
  fecha_evaluacion DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  id_usuario_evaluador INT NOT NULL,
  FOREIGN KEY (id_prompt) REFERENCES prompts(id_prompt),
  FOREIGN KEY (id_conjunto_datos) REFERENCES conjuntos_datos(id_conjunto_datos),
  FOREIGN KEY (id_usuario_evaluador) REFERENCES usuarios(id_usuario)
);

CREATE TABLE datos_columnas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    dataset_id INT,
    dato_evaluado VARCHAR(255),
    dato_asociado VARCHAR(255),
    FOREIGN KEY (dataset_id) REFERENCES conjuntos_datos(id_conjunto_datos)
);

