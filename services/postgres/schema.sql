CREATE EXTENSION postgis;
    
\set ON_ERROR_STOP on

BEGIN;
    
/*  
 * Users may be partially hydrated with only a name/screen_name 
 * if they are first encountered during a quote/reply/mention 
 * inside of a tweet someone else's tweet.
 */
CREATE TABLE users (
    id_users BIGINT PRIMARY KEY,
    created_at TIMESTAMPTZ,
    updated_at TIMESTAMPTZ,
    friends_count INTEGER,
    listed_count INTEGER,
    favourites_count INTEGER,
    statuses_count INTEGER,
    protected BOOLEAN,
    verified BOOLEAN,
    screen_name TEXT,
    name TEXT,
    location TEXT,
    description TEXT,
    withheld_in_countries VARCHAR(2)[]
);  

CREATE TABLE tweets (
id_tweets BIGINT PRIMARY KEY,
id_users BIGINT,
created_at TIMESTAMPTZ,
in_reply_to_status_id BIGINT,
in_reply_to_user_id BIGINT,
quoted_status_id BIGINT,
retweet_count SMALLINT,
favorite_count SMALLINT,
quote_count SMALLINT,
withheld_copyright BOOLEAN,
withheld_in_countries VARCHAR(2)[],
source TEXT,
text TEXT,
country_code VARCHAR(2),
state_code VARCHAR(2),
lang TEXT,
place_name TEXT,
geo geometry,
FOREIGN KEY (id_users) REFERENCES users(id_users)

-- NOTE:
-- We do not have the following foreign keys because they would require us
-- to store many unhydrated tweets in this table.
-- FOREIGN KEY (in_reply_to_status_id) REFERENCES tweets(id_tweets),
-- FOREIGN KEY (quoted_status_id) REFERENCES tweets(id_tweets)
);

CREATE TABLE tweet_tags (
    id_tweets BIGINT,
    tag TEXT,
    PRIMARY KEY (id_tweets, tag),
    FOREIGN KEY (id_tweets) REFERENCES tweets(id_tweets) DEFERRABLE INITIALLY DEFERRED
);
COMMENT ON TABLE tweet_tags IS 'This table links both hashtags and cashtags';
CREATE INDEX tweet_tags_index ON tweet_tags(id_tweets);

COMMIT;
