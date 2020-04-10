### render reports
library(rmarkdown)
library(stringr)

#HTML report
render("COVID-19_Scotland_Daily_Update.Rmd", 
       output_file = str_glue("COVID-19_Scotland_Daily_Update_", {str_replace_all(Sys.Date(), pattern = "-", "_")}, ".html"))

#PDF report
render("COVID-19_Scotland_Daily_Update_pdf.Rmd", 
       output_file = str_glue("COVID-19_Scotland_Daily_Update_", {str_replace_all(Sys.Date(), pattern = "-", "_")}, ".pdf"))

#library(knitr)
#opts_chunk$set(list(echo = FALSE, eval = FALSE))
#knit("COVID-19_Scotland_Daily_Update.Rmd")

#Word report
file_name_word <- str_glue("COVID-19_Scotland_Daily_Update_", {str_replace_all(Sys.Date(), pattern = "-", "_")}, ".docx")
render("COVID-19_Scotland_Daily_Update_word.Rmd", 
       output_file = file_name_word)

#Create html code for email
# https://pandoc.org/MANUAL.html#general-options
rmarkdown::pandoc_convert(input = "COVID-19_Scotland_Daily_Update_2020_04_10.docx", to="html", output = str_glue("COVID-19_Scotland_Daily_Update_", {str_replace_all(Sys.Date(), pattern = "-", "_")}, ".txt"))

#Delete useless files
file.remove(file_name_word)
unlink("COVID-19_Scotland_Daily_Update_word", recursive = TRUE)



