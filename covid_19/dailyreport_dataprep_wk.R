#Covid daily report
## Weekly ratios

#date: "`r format(Sys.time(), '%d %B, %Y')`" 
knitr::opts_chunk$set(echo = FALSE, message = FALSE, warning = FALSE)
# Load packages
library(flexdashboard) ; library(shiny) ; library(readr); library(dplyr); library(tidyr); library(purrr); library(forcats); library(stringr); library(htmlwidgets); library(lubridate); library(sf); library(RcppRoll); library(plotly); library(shinythemes);library(leaflet); library(classInt); library(ggrepel); library(scales); library(leaflet.extras); library(RColorBrewer);
library(colorblindr); library(readxl);library(spatstat.utils);library(httr);library(cowplot)

source("weekly_ratios_2.R")
weekly_ratios <- weekly_ratios_2

# Import Scottish covid data
path <- paste0("Daily_Reports/COVID-19_Scotland_data_all_", {Sys.Date()}, ".xlsx") 
# Scottish cases data
scot_data_raw <- read_excel(path, sheet = "Cases By Health Board", skip = 1)
scot_data_raw <- filter(scot_data_raw, !Health_Board %in% c("Increase", "pIncrease")) %>%
  rename(confirmed_cases= Total,
         Date = Health_Board) %>%
  mutate(date = lubridate::ymd(Date)) %>%
  select(-Date)

scot_data_raw$date[nrow(scot_data_raw)] <- scot_data_raw$date[nrow(scot_data_raw)-1] + days(1)
#scot_data_raw$confirmed_cases[nrow(scot_data_raw)] <- 4565 ## REMOVE

scot_data <- scot_data_raw %>%
  mutate(new_cases = confirmed_cases - replace_na(lag(confirmed_cases),0)) %>%
  mutate(doubling_time_week = 7*log(2)/log(confirmed_cases/replace_na(lag(confirmed_cases,7),0))) 

write_csv(scot_data, "scot_data.csv")
# Per health board
scot_data_health_board <- scot_data %>% 
  select(date, Ayrshire:`Dumfries and Galloway`) %>%
  pivot_longer(Ayrshire:`Dumfries and Galloway`,
               names_to = "health_board",
               values_to = "confirmed_cases") %>% 
  group_by(health_board) %>%
  mutate(new_cases = confirmed_cases - replace_na(lag(confirmed_cases), 0)) %>%
  ungroup() %>%
  replace_na(list(new_cases = 0))

# Per health board for map
# Cumulative incidence
scot_ci_hb <- read_excel(path, sheet = "Cumulative Incidence Grouped") %>%
  slice(nrow(.)) %>%
  select(Ayrshire:Tayside) %>%
  pivot_longer(Ayrshire:Tayside, names_to = "health_board", values_to = "cumulative_incidence")

# Incidence over last day
scot_ti_hb <- read_excel(path, sheet = "Incidence by Health Board") %>%
  slice(nrow(.)) %>%
  select(Ayrshire:Tayside) %>%
  pivot_longer(Ayrshire:Tayside, names_to = "health_board", values_to = "today_incidence")

scot_data_health_board_total <- scot_data_health_board %>% 
  group_by(health_board) %>%
  summarise(confirmed_cases = max(confirmed_cases, na.rm = T)) %>%
  left_join(scot_ci_hb)

# Scottish death data
scot_deaths <- read_excel(path, sheet = "Scotland Deaths", skip = 1) %>%
  rename("deaths" = Deaths_Cum, 
         "new_deaths" = Deaths_New) %>%
  mutate(doubling_time_week = 7*log(2)/log(deaths/replace_na(lag(deaths,7),0))) %>%
  mutate(date = lubridate::ymd(Date)) 

scot_deaths$date[nrow(scot_deaths)] <- scot_deaths$date[nrow(scot_deaths)-1] + days(1)

# Scottish tests
scot_tests <- read_excel(path, sheet = "CPT & DPC") 
#scot_tests$Cases[nrow(scot_tests)] <- 4565 #REMOVE

scot_tests  <- scot_tests %>%
  rename("Conducted" = Tests, 
         "Total Positive" = Cases,
         "deaths_per_case" = DPC,
         "cases_per_test" = CPT) %>%
  mutate("Conducted today" = Conducted - replace_na(lag(Conducted), 0)) %>%
  mutate("Total Negative" = Conducted - `Total Positive`) %>%
  mutate("Positive" = `Total Positive` - replace_na(lag(`Total Positive`), 0),
         "Negative" = `Total Negative` - replace_na(lag(`Total Negative`), 0)) 
scot_tests$Positive[scot_tests$Date == ymd("2020-03-12")] <- 24
scot_tests$Negative[scot_tests$Date == ymd("2020-03-12")] <- 552


scot_tests_long <- scot_tests %>%
  pivot_longer(cols = Positive:Negative, names_to = "Result", values_to = "Number") %>%
  mutate(Result = factor(Result, levels = c("Positive", "Negative")))


# Map files
# SCOTLAND MAP
cases_by_area <- sf::st_read("SG_NHS_HealthBoards_2019b.geojson") %>%
  mutate(health_board = case_when(HBName == "Ayrshire and Arran" ~ "Ayrshire",
                                  HBName %in% c("Grampian", "Shetland", "Orkney") ~ "Grampian, Shetland and Orkney",
                                  HBName %in% c("Highland", "Western Isles") ~ "Highland and Western Isles",
                                  TRUE ~ as.character(HBName))) %>%
  st_transform(crs = st_crs("+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs")) %>%
  left_join(scot_data_health_board_total, by = c("health_board" = "health_board")) 

# Plot colours
#nice_blue <- palette_OkabeIto[5]
#nice_red <- palette_OkabeIto[6]  
nice_blue <- "#0072B2"
nice_red <- "#D55E00"
nice_green <- "#009E73"
nice_orange <- "#E69F00"


# Weekly ratios 
wk_gr_newcases <- scot_data %>% select(new_cases, date) %>%
  mutate(outcome = new_cases) %>%
  weekly_ratios() %>%
  filter(!is.na(ratio) & !is.infinite(ratio)) %>%
  significance_wk() 

wk_gr_newdeaths <- scot_deaths %>% select(new_deaths, date) %>%
  mutate(outcome = new_deaths) %>%
  weekly_ratios() %>%
  filter(!is.na(ratio) & !is.infinite(ratio)) %>%
  significance_wk()

wk_gr_newcases_hb <- scot_data_health_board %>% rename("outcome" = new_cases) %>%
  #mutate(outcome = case_when(date == ymd("2020-05-13") & health_board == "Dumfries and Galloway" ~ 0,
  #                           TRUE ~ outcome)) %>%
  mutate(outcome = case_when(outcome < 0 ~ 0,
                             TRUE ~ outcome)) %>%
  group_by(health_board) %>%
  nest() %>%
  mutate(gr = map(data, ~weekly_ratios(.x))) %>%
  unnest(gr) %>%
  filter(date >= ymd("2020-03-23")) %>%
  filter(!is.na(ratio) & !is.infinite(ratio)) %>%
  significance_wk() %>%
  mutate(symbol = case_when(significance == "not significantly greater than 1" ~ "not sig <>1",
                            significance == "not significantly less than 1" ~ "not sig <>1",
                            significance == "significantly greater than 1" ~ "sig <> 1",
                            significance == "significantly less than 1" ~ "sig <> 1")) %>%
  mutate(sign_ci = case_when(significance == "not significantly greater than 1" ~ "This is not significantly greater than 1",
                             significance == "not significantly less than 1" ~ "This is not significantly less than 1",
                             significance == "significantly greater than 1" ~ "This is significantly greater than 1",
                             significance == "significantly less than 1" ~ "This is significantly less than 1"))


# Import hospital data
## Covid daily hospital data
myurl <- "https://www.gov.scot/binaries/content/documents/govscot/publications/statistics/2020/04/coronavirus-covid-19-trends-in-daily-data/documents/trends-in-number-of-people-in-hospital-with-confirmed-or-suspected-covid-19/trends-in-number-of-people-in-hospital-with-confirmed-or-suspected-covid-19/govscot%3Adocument/Trends%2Bin%2Bdaily%2BCOVID-19%2Bdata%2B-%2B110520.xlsx"
GET(myurl, write_disk(tmp <- tempfile(fileext = ".xlsx")))

#data_hosp <- read_excel(tmp, sheet = "Table 1", skip = 3)
data_hosp <- read_excel(tmp, sheet = "Table 2 - Hospital Care", skip = 3)

data_hosp <- data_hosp %>%
  rename("date" = "...1",
         "ICU_confirmed" = "Confirmed...2",
         "ICU_suspected" ="Suspected...3", 
         "ICU_total" = "Total...4",
         "Hospital_confirmed" = "Confirmed...5",
         "Hospital_suspected" = "Suspected...6",
         "Hospital_total" = "Total...7" ) %>%
  filter(!is.na(ICU_total)) %>%
  mutate(date = lubridate::ymd(date)) %>%
  mutate(date = case_when(date == ymd("2020-06-05") & Hospital_total == 1019 ~ ymd("2020-06-06"),
                            TRUE ~ ymd(date))) %>%
  #mutate(date = as.Date(as.numeric(date), origin = "1899-12-30")) %>%
  mutate(ICU_confsusp = case_when(is.na(ICU_confirmed) & is.na(ICU_suspected) ~ ICU_total)) %>%
  mutate(Hospital_confsusp = case_when(is.na(Hospital_confirmed) & is.na(Hospital_suspected) ~ Hospital_total)) %>%
  select(date, contains("ICU"), everything()) %>%
  select(date, ICU_total, Hospital_total) 

# wk_gr_hosp_icu <- data_hosp %>%
#   mutate(ICU_prev = lag(ICU_total , 7), 
#          weekdays(date)) %>%
#   filter(date >= ymd("2020-03-25")) %>%
#   pivot_longer(c(ICU_total, ICU_prev), names_to = "week", values_to = "number") %>%
#   group_by(date) %>%
#   nest() %>%
#   mutate(mod = map(data, ~ glm(number ~ week,
#                                data = .x, family = poisson))) %>%
#   mutate(ratio_m = map_dbl(mod, ~ exp(coef(.x)["weekICU_total"]))) %>% 
#   mutate(lci = map_dbl(mod, ~ exp(confint(.x)["weekICU_total", "2.5 %"]))) %>%
#   mutate(uci = map_dbl(mod, ~ exp(confint(.x)["weekICU_total", "97.5 %"]))) %>%
#   ungroup() %>%
#   select(date, ratio_m, lci, uci) %>%
#   mutate(comparison = if_else(ratio_m >1, "greater than", "less than")) %>%
#   significance_wk() 

wk_gr_hosp_icu <- data_hosp %>%
  mutate(ICU_prev = lag(ICU_total , 7), 
         weekdays(date)) %>%
  filter(date >= ymd("2020-03-25")) %>%
  #pivot_longer(c(ICU_total, ICU_prev), names_to = "week", values_to = "number") %>%
  group_by(date) %>%
  nest() %>%
  mutate(tab = map(data, ~ weekly_ratios_ci(.x$ICU_total, .x$ICU_prev))) %>%
  mutate(ratio_m = map_dbl(tab, ~parse_number(as.character((.x[1,2]))))) %>% 
  mutate(lci = map_dbl(tab, ~parse_number(as.character((.x[2,2]))))) %>% 
  mutate(uci = map_dbl(tab, ~parse_number(as.character((.x[3,2]))))) %>% 
  ungroup() %>%
  select(date, ratio_m, lci, uci) %>%
  mutate(comparison = if_else(ratio_m >1, "greater than", "less than")) %>%
  significance_wk() 


wk_gr_hosp_icu_latest <- filter(wk_gr_hosp_icu, date == max(wk_gr_hosp_icu$date))

# wk_gr_hosp_hosp <- data_hosp %>%
#   mutate(Hosp_prev = lag(Hospital_total , 7), 
#          weekdays(date)) %>%
#   filter(date >= ymd("2020-03-25")) %>%
#   pivot_longer(c(Hospital_total, Hosp_prev), names_to = "week", values_to = "number") %>%
#   group_by(date) %>%
#   nest() %>%
#   mutate(mod = map(data, ~ glm(number ~ week,
#                                data = .x, family = poisson))) %>%
#   mutate(ratio_m = map_dbl(mod, ~ exp(coef(.x)["weekHospital_total"]))) %>% 
#   mutate(lci = map_dbl(mod, ~ exp(confint(.x)["weekHospital_total", "2.5 %"]))) %>%
#   mutate(uci = map_dbl(mod, ~ exp(confint(.x)["weekHospital_total", "97.5 %"]))) %>%
#   ungroup() %>%
#   select(date, ratio_m, lci, uci) %>%
#   mutate(comparison = if_else(ratio_m >1, "greater than", "less than")) %>%
#   significance_wk() 

wk_gr_hosp_hosp <- data_hosp %>%
  mutate(Hosp_prev = lag(Hospital_total , 7), 
         weekdays(date)) %>%
  filter(date >= ymd("2020-03-25")) %>%
  #pivot_longer(c(Hospital_total, Hosp_prev), names_to = "week", values_to = "number") %>%
  group_by(date) %>%
  nest() %>%
  mutate(tab = map(data, ~ weekly_ratios_ci(.x$Hospital_total, .x$Hosp_prev))) %>%
  mutate(ratio_m = map_dbl(tab, ~parse_number(as.character((.x[1,2]))))) %>% 
  mutate(lci = map_dbl(tab, ~parse_number(as.character((.x[2,2]))))) %>% 
  mutate(uci = map_dbl(tab, ~parse_number(as.character((.x[3,2]))))) %>% 
  ungroup() %>%
  select(date, ratio_m, lci, uci) %>%
  mutate(comparison = if_else(ratio_m >1, "greater than", "less than")) %>%
  significance_wk() 


wk_gr_hosp_hosp_latest <- filter(wk_gr_hosp_hosp, date == max(wk_gr_hosp_icu$date))

