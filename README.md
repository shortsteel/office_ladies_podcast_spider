This is a spider to scrap office ladies podcast information and audio

## selenium and chromedriver

This script is using selenium, so chromedriver is needed.  
[Selenium installation guide](https://til.simonwillison.net/selenium/selenium-python-macos)

## run the spider

run the following command in your terminal

```bash
pip install -r requiremnets.txt
scrapy runspider office_ladies_spider.py -o episodes.json
```

## output

files will be writen to ./episodes/

## episode json example

```json
{
  "title": "Episode 101 | Broke",
  "date": "December 1, 2021",
  "excerpt": "This week we\u2019re breaking down \u201cBroke\u201d. The Michael Scott Paper Company is struggling to stay in business after Ryan made a serious accounting error. Meanwhile, Dunder Mifflin has taken a hit from all the customers they lost to the Michael Scott Paper Company, so with the help of Jim, Dunder Mifflin decides to buy out the Michael Scott Paper Company even though they have no idea that\u2019s exactly what Michael, Pam and Ryan want. This is the first \u201cOffice\u201d episode directed by Steve Carell. The ladies help a fan clarify what Michael yells when pranking Ryan, Jenna simplifies the difference between fixed-costs vs variable-costs and Angela shares a deleted scene about Charles Miner that will make you gasp! So enjoy this episode because well, well, well, how the turn tables...",
  "href": "https://officeladies.com/episodes/2021/1/12/episode-101-broke",
  "audio_href": "https://pdst.fm/e/stitcher.simplecastaudio.com/eeecdf60-9801-4195-90c3-84742003404a/episodes/918c9b69-b8f9-4605-99bf-db871f986180/audio/128/default.mp3?awCollectionId=eeecdf60-9801-4195-90c3-84742003404a&awEpisodeId=918c9b69-b8f9-4605-99bf-db871f986180&aid=embed"
}
```