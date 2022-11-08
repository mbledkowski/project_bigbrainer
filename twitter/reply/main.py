import openai
import tweepy
from config import (
    API_KEY,
    API_SECRET_KEY,
    ACCESS_TOKEN,
    ACCESS_TOKEN_SECRET,
    OPENAI_API_KEY,
)

# Authenticate to Twitter
client = tweepy.Client(
    consumer_key=API_KEY,
    consumer_secret=API_SECRET_KEY,
    access_token=ACCESS_TOKEN,
    access_token_secret=ACCESS_TOKEN_SECRET,
)

# Authenticate to OpenAI
openai.api_key = OPENAI_API_KEY

# Initial prompt
prompt_init = "Your name is Sarah Smith. You was born on October 10th, 1995 in Los Angeles, CA. You are a student of the internet. Your boyfriend is John and he is a doctor. You are a heterosexual cis-gender woman, but you support the LGBTQ+ community. You are an atheist. Your Twitter handle is @bigbrainer2137. You are probably able to pass the Turing test.\n\n"

prompt_introduction = "\nYou see a following tweet on your Twitter feed:\n"

# Get the tweets from the timeline
timeline = client.get_home_timeline(
    tweet_fields="attachments,author_id,context_annotations,created_at,entities,geo,id,in_reply_to_user_id,lang,possibly_sensitive,public_metrics,referenced_tweets,source,text,withheld"
).data

# Iterate through the tweets and send them to GPT-3
for tweet in timeline:
    tweet_author = client.get_user(id=tweet.author_id, user_auth=True).data
    tweet_info = f"""
Display name: {tweet_author.name}
Twitter handle: @{tweet_author.username}
Post: \n{tweet.text}
Posted on: {tweet.created_at}
Statistics:
 - Retweets: {tweet.public_metrics["retweet_count"]}
 - Quote Tweets: {tweet.public_metrics["quote_count"]}
 - Likes: {tweet.public_metrics["like_count"]}
 - Comments: {tweet.public_metrics["reply_count"]}
    """
    prompt_action = f"\nDo you respond to this tweet? (Yes/No):\n"
    prompt = prompt_init + prompt_introduction + tweet_info + prompt_action
    action: bool = False
    response = (
        openai.Completion.create(
            model="text-davinci-002",
            prompt=prompt,
            temperature=0,
            max_tokens=1500,
        )
        .choices[0]
        .text.strip()
    )
    prompt += response
    if response == "Yes":
        action = True
    if action:
        prompt_respond = f"\nYou decide to respond to the tweet with the following:\n"
        prompt += prompt_respond
        response = (
            openai.Completion.create(
                model="text-davinci-002",
                prompt=prompt,
                temperature=0,
                max_tokens=1500,
            )
            .choices[0]
            .text.strip()
        )
        prompt += response
        response_tweet = client.create_tweet(
            text=response, in_reply_to_tweet_id=tweet.id
        )
        print(response_tweet)

    print(prompt, "\n")
