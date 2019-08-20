#import dependencies
from bs4 import BeautifulSoup as BS
from splinter import Browser
import os
import pandas as pd

def init_browser():
    # @NOTE: Replace the path with your actual path to the chromedriver
    executable_path = {"executable_path": "/usr/local/bin/chromedriver"}
    return Browser("chrome", **executable_path, headless=False)

def scrape():
    browser = init_browser()
    mars_facts_data = {}

    url_news = "https://mars.nasa.gov/news/"
    browser.visit(url_news)
    
    html_news = browser.html
    news_soup = BS(html_news, "html.parser")
    
    # Collect the latest News Title and Paragraph Text
    news_title = news_soup.find("div",class_="content_title").text
    news_p = news_soup.find("div", class_="article_teaser_body").text
    mars_facts_data['news_title'] = news_title
    mars_facts_data['news_paragraph'] = news_p
            
    # Mars Featured Image
    url_img = "https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars"
    browser.visit(url_img)
    
    # Option1: Directly scraping with Chrome
    html_img = browser.html
    image_soup = BS(html_img, "html.parser")
    img_url_opt1 = image_soup.find_all('a', class_ = 'fancybox')[1]["data-fancybox-href"]

    # # Option2 (Preferred): Design an xpath selector to grab the image
    # html_img = browser.html
    # xpath = "//*[@id=\"page\"]/section[3]/div/ul/li[1]/a/div/div[2]/img"
    # # Use splinter to click to bring the full resolution image
    # img = browser.find_by_xpath(xpath)[0]
    # img.click()
    # html_img = browser.html
    # image_soup = BS(html_img, "html.parser")
    # img_url_opt2 = image_soup.find("img", class_="fancybox-image")["src"]

    # Get base url
    img_url_opt = img_url_opt1
    from urllib.parse import urlsplit
    base_url = "{0.scheme}://{0.netloc}/".format(urlsplit(url_img))
    featured_img_url = base_url + img_url_opt
    mars_facts_data["featured_image"] = featured_img_url
    
    #### Mars Weather
    # # Visit the Mars Weather twitter account and scrape the latest Mars weather tweet from the page
    url_weather = "https://twitter.com/marswxreport?lang=en"
    browser.visit(url_weather)

    html_weather = browser.html
    weather_soup = BS(html_weather, "html.parser")
    
    # Get latest Mars weather tweet
    tweets = weather_soup.find_all("div",class_="js-tweet-text-container")[0].text
    mars_weather = tweets[9:-27].replace('\n','')
    mars_facts_data["mars_weather"] = mars_weather

    #### Mars Facts
    # Scrape the table containing Mars Planet Profile
    url_mars_facts = "https://space-facts.com/mars/"
    table_df = pd.read_html(url_mars_facts)[1]
    table_df.columns = ["Description", "Values"]
    table_df_new = table_df.set_index(["Description"])
    html_mars_facts = table_df_new.to_html().replace("\n","")
    mars_facts_data["mars_facts_table"] = html_mars_facts

    #### Mars Hemisperes
    url_hemispheres = "https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars"
    url_hemispheres_base  = "{0.scheme}://{0.netloc}/".format(urlsplit(url_hemispheres))
    browser.visit(url_hemispheres)
    
    hemisphere_image_urls = []
    for x in range(1,5):  # Four results in total
        # click each of the links
        products = browser.find_by_xpath( "//*[@id='product-section']/div[2]/div["+str(x)+"]/a/img").click()
        full_img = browser.find_by_xpath( "//*[@id='wide-image-toggle']").click()
        # Parse HTML with Beautiful Soup
        image = browser.html
        soup = BS(image, "html.parser")
        url = soup.find("img", class_="wide-image")["src"]
        full_url = url_hemispheres_base + url
        title = soup.find("h2",class_="title").text
        # Append the dictionary with the image url string and the hemisphere title to a list
        hemisphere_image_urls.append({"title": title, "img_url": full_url})
        # Going back
        browser.visit(url_hemispheres)   

    mars_facts_data["hemisphere_img_url"] = hemisphere_image_urls
    
    return mars_facts_data