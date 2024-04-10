import sys
import json
import random
import tweepy
import datetime


# Set up directory locations

root = '/usr/local/google/home/adrobertson/twitter_bot'
data_root = '/usr/local/google/home/adrobertson/twitter_bot/data'
log_root = '/usr/local/google/home/adrobertson/twitter_bot/auto_tweet'
asset_root = '/usr/local/google/home/adrobertson/twitter_bot/renamed_assets'


# Load in the data files

with open(f'{data_root}/success_strings.json') as f:
    success_strings = json.load(f)

with open(f'{data_root}/name_to_emoji.json') as f:
    n2e = json.load(f)

with open(f'{data_root}/valid_combos.json') as f:
    valid_combos = json.load(f)


# Set up Twitter access

TWITTER_CONSUMER_KEY='1'
TWITTER_CONSUMER_SECRET='2'
TWITTER_ACCESS_TOKEN='3'
TWITTER_ACCESS_TOKEN_SECRET='4'

bearer_token = '5'

auth = tweepy.OAuthHandler(TWITTER_CONSUMER_KEY, TWITTER_CONSUMER_SECRET)
auth.set_access_token(TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_TOKEN_SECRET)
api1 = tweepy.API(auth)

api2 = tweepy.Client(bearer_token=bearer_token,
                     consumer_key=TWITTER_CONSUMER_KEY, consumer_secret=TWITTER_CONSUMER_SECRET,
                     access_token=TWITTER_ACCESS_TOKEN, access_token_secret=TWITTER_ACCESS_TOKEN_SECRET,                 
                    )

# Load the last 25 combinations that were tweeted.
# Want to make sure that the next tweet does not contain any of the
# emoji used recently.

all_last = []

with open(f'{log_root}/automated_tweet_log.txt') as f:
    for line in f.readlines()[-24:]:
        line = line.split('\t')[1].replace('.png', '')
        last1, last2 = line.split('/')

        all_last.extend([last1, last2])


e1 = all_last[0]
e2 = all_last[0]


# Keep trying until a valid combination is found
# If it takes too long, just accept that we have
# at least one repeated element

c = 0
while e1 in all_last or e2 in all_last:
    if c > 500:
        break
    e1 = random.choice(list(valid_combos))
    e2 = random.choice(valid_combos[e1])
    c += 1


# Sort the elements to make it easy to locate
# the asset against the file structure I used

e1, e2 = sorted([e1, e2])

filepath = f'{asset_root}/{e1}/{e2}.png'

# Get the strings. Have to try both ways due to
# error in the formatting of that file...

try:
    text = random.choice(success_strings[e1][e2])
except:
    text = random.choice(success_strings[e2][e1])

# Try uploading the image
# Otherwise, update the error log and exit

try:
    img = api1.media_upload(filename=filepath)
except Exception as e:
    with open(f'{log_root}/failure_log.txt', 'a') as f:
        f.write(f'{str(datetime.datetime.now())}\t{filepath.replace(root + "/", "")}\tFAILED_TO_UPLOAD_MEDIA\t{e}\n')
    sys.exit()

# Once image is uploaded, create a tweet using it
# and the text strings and the emoji
# Again, if failure then update log and exit

try:
    # tweet = api.update_status(status=f"{text} {n2e[e1]} {n2e[e2]}", media_ids=[img.media_id_string])
    tweet = api2.create_tweet(text=f"{text} {n2e[e1]} {n2e[e2]}", media_ids=[img.media_id_string])
except Exception as e:
    with open(f'{log_root}/failure_log.txt', 'a') as f:
        f.write(f'{str(datetime.datetime.now())}\t{filepath.replace(root + "/", "")}\tFAILED_TO_TWEET\t{e}\n')
    sys.exit()

# Update the success log and we are done

with open(f'{log_root}/automated_tweet_log.txt', 'a') as f:
    f.write(f'{str(datetime.datetime.now())}\t{filepath.replace(asset_root + "/", "")}\t{text}\n')


