#restart R session
.rs.restartR()
# remove and objects (there shouldn't be any but let's be extra careful!)
rm(list=ls())

### render reports
library(rmarkdown)
library(stringr)

#HTML report
render("COVID-19_Scotland_Daily_Update_gr.Rmd", 
       output_file = str_glue("COVID-19-Scotland-Daily-Update-", {str_replace_all(Sys.Date(), pattern = "-", "-")}, ".html"))

#PDF report
render("COVID-19_Scotland_Daily_Update_pdf_gr.Rmd", 
       output_file = str_glue("COVID-19-Scotland-Daily-Update-", {str_replace_all(Sys.Date(), pattern = "-", "-")}, ".pdf"))

#library(knitr)
#opts_chunk$set(list(echo = FALSE, eval = FALSE))
#knit("COVID-19_Scotland_Daily_Update.Rmd")

#Word report
file_name_word <- str_glue("COVID-19-Scotland-Daily-Update-", {str_replace_all(Sys.Date(), pattern = "-", "-")}, ".docx")
render("COVID-19_Scotland_Daily_Update_word_gr.Rmd", 
       output_file = file_name_word)

#Create html code for email
# https://pandoc.org/MANUAL.html#general-options
#rmarkdown::pandoc_convert(input = "COVID-19_Scotland_Daily_Update_2020_04_11.docx", to="html", output = str_glue("COVID-19_Scotland_Daily_Update_", {str_replace_all(Sys.Date(), pattern = "-", "_")}, ".txt"))
rmarkdown::pandoc_convert(input = str_glue("COVID-19-Scotland-Daily-Update-", {str_replace_all(Sys.Date(), pattern = "-", "-")}, ".docx"), to="html", output = str_glue("COVID-19-Scotland-Daily-Update-", {str_replace_all(Sys.Date(), pattern = "-", "-")}, ".txt"))



#Delete useless files
file.remove(file_name_word)
unlink("COVID-19-Scotland-Daily-Update-word", recursive = TRUE)



