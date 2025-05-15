CREATE EXTENSION rum;    
\set ON_ERROR_STOP on

BEGIN;
    
/*  
 * Users may be partially hydrated with only a name/screen_name 
 * if they are first encountered during a quote/reply/mention 
 * inside of a tweet someone else's tweet.
 */
CREATE TABLE users (
    id_users BIGINT PRIMARY KEY,
    screen_name TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    password TEXT
);  
CREATE INDEX ON users(screen_name, password);

CREATE TABLE tweets (
    id_tweets BIGINT PRIMARY KEY,
    id_users BIGINT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL,
    text TEXT NOT NULL,
    lang TEXT,
    FOREIGN KEY (id_users) REFERENCES users(id_users)

-- NOTE:
-- We do not have the following foreign keys because they would require us
-- to store many unhydrated tweets in this table.
-- FOREIGN KEY (in_reply_to_status_id) REFERENCES tweets(id_tweets),
-- FOREIGN KEY (quoted_status_id) REFERENCES tweets(id_tweets)
);
CREATE INDEX ON tweets(created_at);
CREATE INDEX ON tweets(id_users);

CREATE TABLE tweet_tags (
    id_tweets BIGINT,
    tag TEXT,
    PRIMARY KEY (id_tweets, tag),
    FOREIGN KEY (id_tweets) REFERENCES tweets(id_tweets) DEFERRABLE INITIALLY DEFERRED
);
COMMENT ON TABLE tweet_tags IS 'This table links both hashtags and cashtags';
CREATE INDEX tweet_tags_index ON tweet_tags(id_tweets);

COMMIT;
