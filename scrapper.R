# install.packages("rvest")
# install.packages("dplyr")
# install.packages("stringr")
# install.packages("lubridate")
# install.packages("RSelenium")

library("wdman")
library("RSelenium")
library("httr")
library("rvest")
library("dplyr")
library("stringr")
library("ggplot2")
library("lubridate")
library("tidyverse")


google_scholar_profile <- "https://scholar.google.com/citations?user=7cOu9sAAAAAJ&hl=en"


get_articles <- function(gs_profile = google_scholar_profile) {
  # Start Selenium server with the correct ChromeDriver
  selServ <- selenium(
    port = 4444L,
    chromever = "106.0.5249.21" # Replace with your correct version
  )
  
  # Connect to the Selenium server
  remDr <- remoteDriver(
    remoteServerAddr = "localhost",
    port = 4444L,
    browserName = "chrome"
  )
  remDr$open()
  remDr$navigate(gs_profile)
  
  repeat {
    show_more <- tryCatch({
      remDr$findElement(using = "css selector", "#gsc_bpf_more .gs_wr") # Adjust selector if needed
    }, error = function(e) NULL)
    
    if (is.null(show_more)) break # Exit if the button no longer exists
    show_more$clickElement()
    Sys.sleep(2) # Wait for articles to load
  }
  
  page_source <- remDr$getPageSource()[[1]]
  page_content <- read_html(page_source)
  
  articles <- page_content %>% html_nodes(".gsc_a_at") %>% html_text()
    #str_extract(pattern = "of\\s(\\d*)", group = 1) %>% as.numeric()
  print(articles)
}

get_articles()
