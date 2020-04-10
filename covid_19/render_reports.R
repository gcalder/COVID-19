### render reports
library(rmarkdown)
library(stringr)
render("COVID-19_Scotland_Daily_Update_2020_04_.Rmd", 
       output_file = str_glue("COVID-19_Scotland_Daily_Update_", {str_replace_all(Sys.Date(), pattern = "-", "_")}, ".html"))

render("COVID-19_Scotland_Daily_Update_2020_04_pdf.Rmd", 
       output_file = str_glue("COVID-19_Scotland_Daily_Update_", {str_replace_all(Sys.Date(), pattern = "-", "_")}, ".pdf"))

