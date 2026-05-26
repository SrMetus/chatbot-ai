-- Add subtitle column to clients table
ALTER TABLE clients ADD COLUMN subtitle VARCHAR(200) NOT NULL DEFAULT 'Asistente Virtual';
