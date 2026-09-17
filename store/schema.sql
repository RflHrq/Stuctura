-- Structura - esquema de persistencia (spec tecnica v1.0, §5.1).
--
-- Duas naturezas de tabela convivem aqui e nao devem ser confundidas:
--   FONTE     participants, sessions, events  -> a verdade; events e append-only
--   DERIVADA  node_state                      -> apagavel e reconstruivel (RNF04)
--
-- Executado por store.events.init_db() na inicializacao. Idempotente.

PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS participants (
  code          TEXT PRIMARY KEY,     -- anonimo: P01, P02... (§12)
  arm           TEXT NOT NULL CHECK (arm IN ('socratic', 'direct')),
  prior_c       TEXT,                 -- experiencia declarada
  consent_at    TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS sessions (
  id            TEXT PRIMARY KEY,
  participant   TEXT NOT NULL REFERENCES participants(code),
  arm           TEXT NOT NULL CHECK (arm IN ('socratic', 'direct')),
  kc_sequence   TEXT NOT NULL,        -- JSON: ["kc_07","kc_09","kc_11"]
  started_at    TEXT NOT NULL,
  ended_at      TEXT
);

CREATE INDEX IF NOT EXISTS idx_sessions_participant ON sessions(participant);

-- APPEND-ONLY. Nunca UPDATE, nunca DELETE. Os triggers abaixo transformam
-- essa regra de convencao em garantia: uma tentativa de mutacao aborta a
-- transacao inteira, inclusive vinda de um sqlite3 aberto a mao no laboratorio.
CREATE TABLE IF NOT EXISTS events (
  id            INTEGER PRIMARY KEY AUTOINCREMENT,
  session_id    TEXT NOT NULL REFERENCES sessions(id),
  seq           INTEGER NOT NULL,     -- ordem dentro da sessao, 1..n sem buraco
  ts            TEXT NOT NULL,
  type          TEXT NOT NULL,
  payload       TEXT NOT NULL,        -- JSON
  UNIQUE(session_id, seq)
);

CREATE INDEX IF NOT EXISTS idx_events_session_seq ON events(session_id, seq);
CREATE INDEX IF NOT EXISTS idx_events_type        ON events(type);

CREATE TRIGGER IF NOT EXISTS events_immutable_update
BEFORE UPDATE ON events
BEGIN
  SELECT RAISE(ABORT, 'events e append-only: UPDATE proibido');
END;

CREATE TRIGGER IF NOT EXISTS events_immutable_delete
BEFORE DELETE ON events
BEGIN
  SELECT RAISE(ABORT, 'events e append-only: DELETE proibido');
END;

-- DERIVADA. Pode ser apagada e reconstruida a partir de events (RNF04).
-- Nenhuma leitura de analise deve depender dela; ela existe para o motor
-- responder rapido durante a sessao (RNF03).
CREATE TABLE IF NOT EXISTS node_state (
  session_id    TEXT NOT NULL REFERENCES sessions(id),
  kc            TEXT NOT NULL,
  node          TEXT NOT NULL,
  -- 'accepted' é o nó aceito no percurso: o aluno concordou com a premissa
  -- posta, ou leu e seguiu. Sustenta a cadeia como 'confirmed', mas não é a
  -- mesma evidência — 'confirmed' exige acertar uma atividade que mira o nó.
  -- Banco criado antes desta linha mantém o CHECK antigo e recusa a escrita:
  -- recrie o banco de desenvolvimento (a coleta começa com banco novo).
  state         TEXT NOT NULL CHECK (state IN ('unknown','confirmed','accepted','absent','wrong')),
  updated_seq   INTEGER NOT NULL,
  PRIMARY KEY (session_id, kc, node)
);

CREATE INDEX IF NOT EXISTS idx_node_state_session_kc ON node_state(session_id, kc);
