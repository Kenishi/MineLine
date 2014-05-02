MineLine
========

Python based NLP toolkit for analyzing LINE chat logs, but eventually other logs

Usage: A GUI is currently being put together. When its finally put together and handles current analysis already
        implemented, then I'll commit it to the repository.

========

LINE (http://line.me/en/) is an Instant Messenger style chat program created by NAVER Japan.
It has gained popularity in Japan primarily because of the ability to use Stickers, which are fancy emote-pictures.

One of the other features about the application is that you can create groups and invite a large number of people
to particapte in a chat. These groups are persistant and messages posted to the chat will be updated on your
application when you open the group chat back up again even if you weren't looking at it. 

The idea for this analysis package came to me when I realized that some of the groups I particpate in tend to
see a lot of chatter. On an average day, 600 new messages/events posted in the chat. I got curious as to the content
of what was being talked about. With nearly 300,000 events from a single chat, it seemed like an interesting thing to
try.

========

Learning Goals: Natural Language Processing using Python NLTK

Analysis that can be done (eventually).

Event counts and the ability to specify specific events types.
Event distribution based on time of day or day of week.

Word Frequency distribution: Strip out STOP words, like "the" "a" "he," words with little content, and find out which
  words were mentioned the most.

Word Frequency distrib. by User: Same as above but specify a specific user.

Topic clustering: This is the analysis I want to get to most. The idea is to try and cluster chunks of the chat and
  figure out what the topic is about. This is the most difficult as it will likely require me to build a corpus that
  better reflects the region that most people are in and the topics that might come up. 

Corpus builder: Build a corpus from a chat?
