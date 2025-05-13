#!/usr/bin/python3

# imports
import sqlalchemy
import os
import datetime
import zipfile
import io
import json
import logging
logging.basicConfig(
    level=logging.DEBUG,
    format=f'%(asctime)s.%(msecs)03d - {os.getpid()} - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
)

################################################################################
# helper functions
################################################################################


def remove_nulls(s):
    r'''
    Postgres doesn't support strings with the null character \x00 in them, but twitter does.
    This helper function replaces the null characters with an escaped version so that they can be loaded into postgres.
    Technically, this means the data in postgres won't be an exact match of the data in twitter,
    and there is no way to get the original twitter data back from the data in postgres.

    The null character is extremely rarely used in real world text (approx. 1 in 1 billion tweets),
    and so this isn't too big of a deal.
    A more correct implementation, however, would be to *escape* the null characters rather than remove them.
    This isn't hard to do in python, but it is a bit of a pain to do with the JSON/COPY commands for the denormalized data.
    Since our goal is for the normalized/denormalized versions of the data to match exactly,
    we're not going to escape the strings for the normalized data.

    >>> remove_nulls('\x00')
    ''
    >>> remove_nulls('hello\x00 world')
    'hello world'
    '''
    if s is None:
        return None 
    else:
        return s.replace('\x00','')


def get_id_urls(url, connection):
    '''
    Given a url, return the corresponding id in the urls table.
    If no row exists for the url, then one is inserted automatically.

    NOTE:
    This function cannot be tested with standard python testing tools because it interacts with the db.
    '''
    sql = sqlalchemy.sql.text('''
    insert into urls 
        (url)
        values
        (:url)
    on conflict do nothing
    returning id_urls
    ;
    ''')
    res = connection.execute(sql,{'url':url}).first()

    # when no conflict occurs, then the query above inserts a new row in the url table and returns id_urls in res[0];
    # when a conflict occurs, then the query above does not insert or return anything;
    # we need to run a select statement to put the already existing id_urls into res[0]
    if res is None:
        sql = sqlalchemy.sql.text('''
        select id_urls 
        from urls
        where
            url=:url
        ''')
        res = connection.execute(sql,{'url':url}).first()

    id_urls = res[0]
    return id_urls


def insert_tweet(connection,tweet):
    '''
    Insert the tweet into the database.

    Args:
        connection: a sqlalchemy connection to the postgresql db
        tweet: a dictionary representing the json tweet object

    NOTE:
    This function cannot be tested with standard python testing tools because it interacts with the db.
    
    FIXME:
    This function is only partially implemented.
    You'll need to add appropriate SQL insert statements to get it to work.
    '''

    # skip tweet if it's already inserted
    sql=sqlalchemy.sql.text('''
    SELECT id_tweets 
    FROM tweets
    WHERE id_tweets = :id_tweets
    ''')
    res = connection.execute(sql,{
        'id_tweets':tweet['id'],
        })
    connection.commit()
    if res.first() is not None:
        return

    # insert tweet within a transaction;
    # this ensures that a tweet does not get "partially" loaded
    with connection.begin() as trans:

        ########################################
        # insert into the users table
        ########################################
        #if tweet['user']['url'] is None:
        #    user_id_urls = None
        #else:
        #    user_id_urls = get_id_urls(tweet['user']['url'], connection)

        # create/update the user
        sql = sqlalchemy.sql.text(f'''
            INSERT INTO users
                ( id_users
                , screen_name
                , name
                )
                VALUES
                ( :id_users
                , :screen_name
                , :name
                )
                ON CONFLICT DO NOTHING
            ''')
        logging.debug(sql)
        screen_name = remove_nulls(tweet['user']['screen_name'])
        name = remove_nulls(tweet['user']['name'])
        if screen_name and name:

            res = connection.execute(sql, {
                'id_users': tweet['user']['id'],
                'screen_name': screen_name, 
                'name': name 
                })

        ########################################
        # insert into the tweets table
        ########################################


        try:
            text = tweet['extended_tweet']['full_text']
        except:
            text = tweet['text']

        # insert the tweet

        sql=sqlalchemy.sql.text(f'''
           INSERT INTO tweets 
           ( id_tweets
           , id_users
           , created_at
           , text
           , lang
           )
           VALUES
           ( :id_tweets
           , :id_users
           , :created_at
           , :text
           , :lang
           )
           ''')
        res = connection.execute(sql, {
           'id_tweets': tweet['id'],
           'id_users': tweet['user']['id'],
           'created_at': tweet['created_at'],
           'text': remove_nulls(text), 
           'lang': tweet.get('lang', None) 
           })

        ########################################
        # insert into the tweet_urls table
        ########################################

#        try:
#            urls = tweet['extended_tweet']['entities']['urls']
#        except KeyError:
#            urls = tweet['entities']['urls']
#
#        for url in urls:
#            id_urls = get_id_urls(url['expanded_url'], connection)
#
#            sql=sqlalchemy.sql.text(f'''
#                INSERT INTO tweet_urls
#                    ( id_tweets
#                    , id_urls
#                    )
#                    VALUES
#                    ( :id_tweets
#                    , :id_urls
#                    )
#                ''')
#            res = connection.execute(sql, {
#                'id_tweets': tweet['id'],
#                'id_urls': id_urls
#                })
#
#        ########################################
#        # insert into the tweet_mentions table
#        ########################################
#        mentions = None 
#        try:
#            mentions = tweet['extended_tweet']['entities']['user_mentions']
#        except KeyError:
#            mentions = tweet['entities']['user_mentions']
#        #print("These are mentions: ", mentions)
#
#        for mention in mentions:
#            # insert into users table;
#            # note that we already have done an insert into the users table above for the user who sent a tweet;
#            # that insert had lots of information inside of it (i.e. the user row was "hydrated");
#            # when we only have a mention of a user, however, we do not have all the information to store in the row;
#            # therefore, we must store the user info "unhydrated"
#            # HINT:
#            # use the ON CONFLICT DO NOTHING syntax
#
#            sql_insert_user = sqlalchemy.sql.text(f'''
#                INSERT INTO users (id_users, name)
#                VALUES (:id_users, :name)
#                ON CONFLICT DO NOTHING
#            ''')
#            #logging.debug(sql_insert_user)
#            connection.execute(sql_insert_user, {'id_users': mention['id'], 'name': mention['name']}) 
#
#            # insert into tweet_mentions
#            sql=sqlalchemy.sql.text(f'''
#                INSERT INTO tweet_mentions
#                    ( id_tweets, id_users)
#                VALUES (:id_tweets, :id_users)
#                ON CONFLICT DO NOTHING
#                ''')
#            #logging.debug(sql)
#            results = connection.execute(sql, {'id_tweets': tweet['id'], 'id_users': mention['id']})
#        ########################################
#        # insert into the tweet_tags table
#        ########################################
        try:
            hashtags = tweet['extended_tweet']['entities']['hashtags'] 
            cashtags = tweet['extended_tweet']['entities']['symbols'] 
        except KeyError:
            hashtags = tweet['entities']['hashtags']
            cashtags = tweet['entities']['symbols']


        tags = [ '#'+hashtag['text'] for hashtag in hashtags ] + [ '$'+cashtag['text'] for cashtag in cashtags ]

        for tag in tags:
            sql=sqlalchemy.sql.text(f'''
                INSERT INTO tweet_tags (id_tweets, tag)
                VALUES (:id_tweets, :tag)
                ON CONFLICT DO NOTHING
                ''')
            results = connection.execute(sql, {'id_tweets': tweet['id'], 'tag': tag})


#        ########################################
#        # insert into the tweet_media table
#        ########################################
#
#        try:
#            media = tweet['extended_tweet']['extended_entities']['media']
#        except KeyError:
#            try:
#                media = tweet['extended_entities']['media']
#            except KeyError:
#                media = []
#
#        for medium in media:
#            id_urls = get_id_urls(medium['media_url'], connection)
#            sql=sqlalchemy.sql.text(f'''
#                INSERT INTO tweet_media (id_tweets, id_urls)
#                VALUES (:id_tweets, :id_urls)
#                ON CONFLICT DO NOTHING
#                ''')
#            results = connection.execute(sql, {'id_tweets': tweet['id'], 'id_urls': id_urls})

################################################################################
# main functions
################################################################################

if __name__ == '__main__':
    
    # process command line args
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--db',required=True)
    parser.add_argument('--inputs',nargs='+',required=True)
    parser.add_argument('--print_every',type=int,default=1000)
    parser.add_argument('--max_rows', type=int, default=0)
    args = parser.parse_args()

    # create database connection
    engine = sqlalchemy.create_engine(args.db, connect_args={
        'application_name': 'load_tweets.py',
        })
    connection = engine.connect()

    row_count = 0
    stop = False

    # loop through the input file
    # NOTE:
    # we reverse sort the filenames because this results in fewer updates to the users table,
    # which prevents excessive dead tuples and autovacuums
    for filename in sorted(args.inputs, reverse=True):
        with zipfile.ZipFile(filename, 'r') as archive: 
            print(datetime.datetime.now(),filename)
            for subfilename in sorted(archive.namelist(), reverse=True):
                with io.TextIOWrapper(archive.open(subfilename)) as f:
                    for i,line in enumerate(f):


                        # load and insert the tweet
                        tweet = json.loads(line)
                        insert_tweet(connection,tweet)

                        row_count += 1

                        # print message
                        if i%args.print_every==0:
                            print(datetime.datetime.now(),filename,subfilename,'i=',i,'id=',tweet['id'])
                        if args.max_rows != 0 and row_count >= args.max_rows:
                            stop = True
                            break
                if stop: 
                    break 
        if stop:
            break 
