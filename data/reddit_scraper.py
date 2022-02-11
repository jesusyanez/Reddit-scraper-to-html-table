import praw
import pandas as pd
import config
import time
import datetime
import csv

# connects to reddit praw object using the reddit application api client id and client secret
def reddit_object():

    reddit = praw.Reddit(client_id = config.client_id,
                        client_secret = config.client_secret,
                        user_agent = config.user_agent,
                        username = config.username,
                        password = config.password)

    return reddit

#Calls up to the last 12 submissions from technology
def scrape_submissions_1000(reddit):
    sub_list = []
    # selects the subreddit technology
    subreddit = reddit.subreddit('technology')
    # have it currently calling 12 submissions at a time, but can be any number between 1 and 1000
    for submission in subreddit.hot(limit=12):
        # different submission attributes I choose to pull are below
        # look at the praw documentation for other submission attributes

        title = submission.title
        pk = submission.id
        direction = submission.url

        sub_list.append([pk, title, direction])
    df = pd.DataFrame(sub_list, columns=['id', 'title', 'direction'])
    # removes reddit mod posts from being added to dataframe
    df = df[~df.direction.str.contains("reddit.com")]
    #adds todays date
    current_date = datetime.datetime.now()
    date = current_date.strftime('%m/%d/%y')
    df['Date'] = date

    return df

#writes the first csv database file
def new_submissions(df):
    # pulls full csv
    df_current = pd.read_csv('reddit_submissions.csv', index_col=0)

    # Checks for only the new rows in the df
    new_submission = df[~df['id'].isin(df_current['id'])]
    new_sub_list = new_submission.values.tolist()

    # Appends the new submissions to the current pandas df which was read from the learnpython_submissions.csv
    df_current = df_current.append(new_submission, sort=False)

    # saves new version of the csv
    df_current.to_csv('reddit_submissions.csv')

    return new_sub_list, new_submission, df_current

#creates timestamped csv file copy for data backup
def csv_copy():
    # pulls full csv to df and closes it
    df_current = pd.read_csv('reddit_submissions.csv', index_col=0)
    df_current2 = df_current
    df_current.to_csv('reddit_submissions.csv')
    # Import time to make second csv file with concatenated title
    current_time = datetime.datetime.now()
    title_time = current_time.strftime('_%m_%d_%Y_%H_%M')
    time_concat = 'reddit_submissions' + title_time + '.csv'

    # Creates new csv file
    with open(time_concat, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["", "id", "direction", "title"])
        writer.writerow(["", "", "", ""])

    #saves dated version of csv file
    df_current2.to_csv(time_concat)

    return df_current2

#clones csv database into site/HTML version csv
def csv_copy_site():
    #Opens and clones original df, then closes it
    df_current = pd.read_csv('reddit_submissions.csv', index_col=0)
    df_current3 = df_current
    df_current.to_csv('reddit_submissions.csv')

    #remove first two columns of csv for displaying in html table
    df_current3 = df_current3.drop(df_current3.columns[[0]], axis=1)

    #open display(shortened) csv file
    df_short = pd.read_csv('techline_data.csv', index_col=0)
    df_short = df_current3[['title','Date','direction']]

    #save short csv file
    df_short.to_csv('techline_data.csv', index=False)

    return df_short


def main():
    reddit = reddit_object()
    df = scrape_submissions_1000(reddit)
    new_sub_list, new_submission, df_current = new_submissions(df)
    df_current2 = csv_copy()
    df_short = csv_copy_site()
    print("new submissions: ", new_submission.shape)
    print("Current Dataframe: ", df_current.shape)


main()
