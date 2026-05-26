
-- EKSTENSI

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ENUM TYPES

DO $$ BEGIN
    CREATE TYPE role_enum AS ENUM ('mahasiswa', 'admin');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
    CREATE TYPE status_akun_enum AS ENUM ('aktif', 'nonaktif', 'banned');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
    CREATE TYPE tipe_post_enum AS ENUM ('kehilangan', 'temuan');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
    CREATE TYPE status_post_enum AS ENUM ('aktif', 'selesai', 'dihapus');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
    CREATE TYPE status_claim_enum AS ENUM ('pending', 'diterima', 'ditolak');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
    CREATE TYPE status_report_enum AS ENUM ('pending', 'ditinjau', 'selesai');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
    CREATE TYPE action_type_enum AS ENUM ('warning', 'takedown', 'restore', 'ban_user');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

-- TABEL USERS

CREATE TABLE IF NOT EXISTS users (
    user_id         UUID            PRIMARY KEY DEFAULT uuid_generate_v4(),
    nama            VARCHAR(100)    NOT NULL,
    email_ipb       VARCHAR(150)    NOT NULL UNIQUE,
    nim             VARCHAR(20)     NOT NULL UNIQUE,
    fakultas        VARCHAR(100),
    password        VARCHAR(255)    NOT NULL,
    foto_profile    TEXT,
    role            role_enum       NOT NULL DEFAULT 'mahasiswa',
    status_akun     status_akun_enum NOT NULL DEFAULT 'aktif',
    created_at      TIMESTAMP       NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE  users                 IS 'Data akun pengguna aplikasi';
COMMENT ON COLUMN users.user_id         IS 'Primary key UUID';
COMMENT ON COLUMN users.email_ipb       IS 'Email institusi IPB, harus unik';
COMMENT ON COLUMN users.nim             IS 'Nomor Induk Mahasiswa, harus unik';
COMMENT ON COLUMN users.role            IS 'mahasiswa | admin';
COMMENT ON COLUMN users.status_akun     IS 'aktif | nonaktif | banned';



-- TABEL EMAIL_VERIFICATIONS

CREATE TABLE IF NOT EXISTS email_verifications (
    verification_id UUID        PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id         UUID        NOT NULL
                    REFERENCES users(user_id) ON DELETE CASCADE,
    token_hash      VARCHAR(128) NOT NULL UNIQUE,
    expires_at      TIMESTAMP   NOT NULL,
    verified_at     TIMESTAMP,
    created_at      TIMESTAMP   NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE  email_verifications             IS 'Token verifikasi email akun baru';
COMMENT ON COLUMN email_verifications.token_hash  IS 'SHA-256 hash dari token verifikasi email';



-- TABEL PASSWORD_RESET_TOKENS

CREATE TABLE IF NOT EXISTS password_reset_tokens (
    reset_id        UUID         PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id         UUID         NOT NULL
                    REFERENCES users(user_id) ON DELETE CASCADE,
    token_hash      VARCHAR(128) NOT NULL UNIQUE,
    expires_at      TIMESTAMP    NOT NULL,
    used_at         TIMESTAMP,
    created_at      TIMESTAMP    NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE password_reset_tokens IS 'Token sementara untuk mengubah password akun';



-- TABEL NOTIFICATIONS

CREATE TABLE IF NOT EXISTS notifications (
    notification_id UUID         PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id         UUID         NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    actor_id        UUID         REFERENCES users(user_id) ON DELETE SET NULL,
    type            VARCHAR(50)  NOT NULL,
    title           VARCHAR(150) NOT NULL,
    message         TEXT         NOT NULL,
    target_url      VARCHAR(255) NOT NULL,
    item_id         UUID,
    claim_id        UUID,
    is_read         BOOLEAN      NOT NULL DEFAULT FALSE,
    created_at      TIMESTAMP    NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE notifications IS 'Riwayat notifikasi user untuk chat dan klaim';



-- TABEL CATEGORIES

CREATE TABLE IF NOT EXISTS categories (
    category_id     UUID            PRIMARY KEY DEFAULT uuid_generate_v4(),
    nama_kategori   VARCHAR(100)    NOT NULL UNIQUE
);

COMMENT ON TABLE  categories            IS 'Kategori barang hilang/temuan';



-- TABEL POSTS

CREATE TABLE IF NOT EXISTS posts (
    post_id             UUID            PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id             UUID            NOT NULL
                            REFERENCES users(user_id) ON DELETE CASCADE,
    category_id         UUID            NOT NULL
                            REFERENCES categories(category_id) ON DELETE RESTRICT,
    tipe_post           tipe_post_enum  NOT NULL,
    nama_barang         VARCHAR(200)    NOT NULL,
    deskripsi           TEXT,
    lokasi              VARCHAR(255),
    tanggal_kejadian    DATE,
    waktu_kejadian      TIME,
    is_anonymous        BOOLEAN         NOT NULL DEFAULT FALSE,
    status_post         status_post_enum NOT NULL DEFAULT 'aktif',
    created_at          TIMESTAMP       NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE  posts                     IS 'Post laporan barang hilang atau temuan';
COMMENT ON COLUMN posts.tipe_post           IS 'kehilangan | temuan';
COMMENT ON COLUMN posts.is_anonymous        IS 'TRUE = identitas pemilik disembunyikan';
COMMENT ON COLUMN posts.status_post         IS 'aktif | selesai | dihapus';



-- TABEL POST_IMAGES

CREATE TABLE IF NOT EXISTS post_images (
    image_id        UUID    PRIMARY KEY DEFAULT uuid_generate_v4(),
    post_id         UUID    NOT NULL
                        REFERENCES posts(post_id) ON DELETE CASCADE,
    image_url       TEXT    NOT NULL
);

COMMENT ON TABLE  post_images           IS 'Foto-foto lampiran pada sebuah post';
COMMENT ON COLUMN post_images.image_url IS 'URL gambar yang disimpan di storage';



-- TABEL CLAIMS

CREATE TABLE IF NOT EXISTS claims (
    claim_id                UUID                PRIMARY KEY DEFAULT uuid_generate_v4(),
    post_id                 UUID                NOT NULL
                                REFERENCES posts(post_id) ON DELETE CASCADE,
    claimer_id              UUID                NOT NULL
                                REFERENCES users(user_id) ON DELETE CASCADE,
    nama_pengklaim          VARCHAR(100)        NOT NULL,
    alasan_kepemilikan      TEXT                NOT NULL,
    bukti_foto              TEXT,
    status_claim            status_claim_enum   NOT NULL DEFAULT 'pending',
    created_at              TIMESTAMP           NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE  claims                        IS 'Klaim kepemilikan atas barang temuan';
COMMENT ON COLUMN claims.claimer_id             IS 'User yang mengajukan klaim';
COMMENT ON COLUMN claims.alasan_kepemilikan     IS 'Penjelasan mengapa barang ini miliknya';
COMMENT ON COLUMN claims.bukti_foto             IS 'URL foto bukti kepemilikan';
COMMENT ON COLUMN claims.status_claim           IS 'pending | diterima | ditolak';



-- TABEL REPORTS

CREATE TABLE IF NOT EXISTS reports (
    report_id       UUID                PRIMARY KEY DEFAULT uuid_generate_v4(),
    reporter_id     UUID                NOT NULL
                        REFERENCES users(user_id) ON DELETE CASCADE,
    post_id         UUID
                        REFERENCES posts(post_id) ON DELETE SET NULL,
    alasan_report   TEXT                NOT NULL,
    status_report   status_report_enum  NOT NULL DEFAULT 'pending',
    created_at      TIMESTAMP           NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE  reports               IS 'Laporan pelanggaran terhadap sebuah post';
COMMENT ON COLUMN reports.reporter_id   IS 'User yang melaporkan';
COMMENT ON COLUMN reports.post_id       IS 'Post yang dilaporkan (nullable jika post dihapus)';
COMMENT ON COLUMN reports.status_report IS 'pending | ditinjau | selesai';



-- TABEL ADMIN_ACTIONS

CREATE TABLE IF NOT EXISTS admin_actions (
    action_id       UUID                PRIMARY KEY DEFAULT uuid_generate_v4(),
    admin_id        UUID                NOT NULL
                        REFERENCES users(user_id) ON DELETE CASCADE,
    post_id         UUID
                        REFERENCES posts(post_id) ON DELETE SET NULL,
    user_target_id  UUID
                        REFERENCES users(user_id) ON DELETE SET NULL,
    action_type     action_type_enum    NOT NULL,
    notes           TEXT,
    created_at      TIMESTAMP           NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE  admin_actions                 IS 'Log tindakan admin terhadap post atau user';
COMMENT ON COLUMN admin_actions.admin_id        IS 'Admin yang melakukan tindakan';
COMMENT ON COLUMN admin_actions.post_id         IS 'Post yang dikenai tindakan (opsional)';
COMMENT ON COLUMN admin_actions.user_target_id  IS 'User yang dikenai tindakan (opsional)';
COMMENT ON COLUMN admin_actions.action_type     IS 'warning | takedown | restore | ban_user';
COMMENT ON COLUMN admin_actions.notes           IS 'Catatan/alasan tindakan admin';



-- TABEL CHATS

CREATE TABLE IF NOT EXISTS chats (
    chat_id         UUID        PRIMARY KEY DEFAULT uuid_generate_v4(),
    post_id         UUID        NOT NULL
                        REFERENCES posts(post_id) ON DELETE CASCADE,
    sender_id       UUID        NOT NULL
                        REFERENCES users(user_id) ON DELETE CASCADE,
    receiver_id     UUID        NOT NULL
                        REFERENCES users(user_id) ON DELETE CASCADE,
    created_at      TIMESTAMP   NOT NULL DEFAULT NOW(),

    CONSTRAINT chk_chats_different_users
        CHECK (sender_id <> receiver_id)
);

COMMENT ON TABLE  chats             IS 'Sesi percakapan antara dua user terkait sebuah post';
COMMENT ON COLUMN chats.sender_id   IS 'User yang memulai chat';
COMMENT ON COLUMN chats.receiver_id IS 'User pemilik post yang dihubungi';



-- TABEL CHAT_MESSAGES

CREATE TABLE IF NOT EXISTS chat_messages (
    message_id          UUID        PRIMARY KEY DEFAULT uuid_generate_v4(),
    chat_id             UUID        NOT NULL
                            REFERENCES chats(chat_id) ON DELETE CASCADE,
    sender_id           UUID        NOT NULL
                            REFERENCES users(user_id) ON DELETE CASCADE,
    isi_pesan           TEXT,
    image_attachment    TEXT,
    sent_at             TIMESTAMP   NOT NULL DEFAULT NOW(),
    is_read             BOOLEAN     NOT NULL DEFAULT FALSE,

    CONSTRAINT chk_message_has_content
        CHECK (isi_pesan IS NOT NULL OR image_attachment IS NOT NULL)
);

COMMENT ON TABLE  chat_messages                     IS 'Pesan individual dalam sebuah sesi chat';
COMMENT ON COLUMN chat_messages.image_attachment    IS 'URL gambar yang dilampirkan (opsional)';
COMMENT ON COLUMN chat_messages.is_read             IS 'TRUE = pesan sudah dibaca penerima';



-- INDEXES


-- posts
CREATE INDEX IF NOT EXISTS idx_posts_user_id        ON posts(user_id);
CREATE INDEX IF NOT EXISTS idx_posts_category_id    ON posts(category_id);
CREATE INDEX IF NOT EXISTS idx_posts_status_post    ON posts(status_post);
CREATE INDEX IF NOT EXISTS idx_posts_tipe_post      ON posts(tipe_post);

-- post_images
CREATE INDEX IF NOT EXISTS idx_post_images_post_id  ON post_images(post_id);

-- claims
CREATE INDEX IF NOT EXISTS idx_claims_post_id       ON claims(post_id);
CREATE INDEX IF NOT EXISTS idx_claims_claimer_id    ON claims(claimer_id);
CREATE INDEX IF NOT EXISTS idx_claims_status        ON claims(status_claim);

-- reports
CREATE INDEX IF NOT EXISTS idx_reports_post_id      ON reports(post_id);
CREATE INDEX IF NOT EXISTS idx_reports_reporter_id  ON reports(reporter_id);
CREATE INDEX IF NOT EXISTS idx_reports_status       ON reports(status_report);

-- admin_actions
CREATE INDEX IF NOT EXISTS idx_admin_actions_post_id        ON admin_actions(post_id);
CREATE INDEX IF NOT EXISTS idx_admin_actions_admin_id       ON admin_actions(admin_id);
CREATE INDEX IF NOT EXISTS idx_admin_actions_user_target    ON admin_actions(user_target_id);

-- chats
CREATE INDEX IF NOT EXISTS idx_chats_post_id        ON chats(post_id);
CREATE INDEX IF NOT EXISTS idx_chats_sender_id      ON chats(sender_id);
CREATE INDEX IF NOT EXISTS idx_chats_receiver_id    ON chats(receiver_id);

-- chat_messages
CREATE INDEX IF NOT EXISTS idx_chat_messages_chat_id    ON chat_messages(chat_id);
CREATE INDEX IF NOT EXISTS idx_chat_messages_sender_id  ON chat_messages(sender_id);
CREATE INDEX IF NOT EXISTS idx_chat_messages_sent_at    ON chat_messages(sent_at);

-- email_verifications
CREATE INDEX IF NOT EXISTS idx_email_verifications_user_id      ON email_verifications(user_id);
CREATE INDEX IF NOT EXISTS idx_email_verifications_token_hash   ON email_verifications(token_hash);

-- password_reset_tokens
CREATE INDEX IF NOT EXISTS idx_password_reset_tokens_user_id      ON password_reset_tokens(user_id);
CREATE INDEX IF NOT EXISTS idx_password_reset_tokens_token_hash   ON password_reset_tokens(token_hash);

-- notifications
CREATE INDEX IF NOT EXISTS idx_notifications_user_id      ON notifications(user_id);
CREATE INDEX IF NOT EXISTS idx_notifications_is_read      ON notifications(is_read);
CREATE INDEX IF NOT EXISTS idx_notifications_created_at   ON notifications(created_at);


-- ------------------------------------------------------------
-- 12. SAMPLE DATA (opsional — hapus jika tidak diperlukan)
-- ------------------------------------------------------------

-- Admin user
INSERT INTO users (nama, email_ipb, nim, fakultas, password, role)
VALUES ('Super Admin', 'admin@apps.ipb.ac.id', '000000000', 'IPB University', 'hashed_password_here', 'admin')
ON CONFLICT (email_ipb) DO NOTHING;

-- Kategori dasar
INSERT INTO categories (nama_kategori) VALUES
    ('Elektronik'),
    ('Dompet / Tas'),
    ('Kartu Identitas'),
    ('Kunci'),
    ('Pakaian'),
    ('Lainnya')
ON CONFLICT (nama_kategori) DO NOTHING;
