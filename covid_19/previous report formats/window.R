library(tidyverse)
library(lubridate)

# data
#dat <- read_csv("~/Documents/GitHub/COVID-19/covid_19/growth_rates/scot_cases.csv") %>%
#  mutate(date = ymd(date))
path <- paste0("COVID-19_Scotland_data_all_", {Sys.Date()}, ".xlsx")

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

dat <-scot_data

# add windows
dat <- dat %>%
  crossing(tibble(
    start = seq(from = min(dat$date),
                to = max(dat$date) - days(6),
                by = 1),
    end   = seq(from = min(dat$date) + days(6),
              to = max(dat$date),
              by = 1)))
# make datasets
fit <- dat %>%
  arrange(date) %>%
  mutate(date_num = as.numeric(date)) %>%
  filter(date >= start & date <= end) %>% 
  filter(new_cases >0) %>% # run this if you want to fit new cases instead of cumulative cases
  group_by(start, end) %>%
  nest()

# examples
fit$data[[1]]

fit$data[[4]]

# fit lm(log) to each dataset and get growth etc
fit <- fit %>%
  #new cases 
  mutate(mod = map(data, ~ lm(log(new_cases) ~ date_num,
                              data = .x
  ))) %>%
  # cum cases
  #mutate(mod = map(data, ~ lm(log(confirmed_cases) ~ date_num,
  #                            data = .x
  #))) %>%
  mutate(coef = map(mod, coef)) %>%
  mutate(log_growth = map_dbl(coef, "date_num")) %>%
  mutate(lci_log_growth = map_dbl(mod, ~ confint(.x)["date_num", "2.5 %"])) %>%
  mutate(uci_log_growth = map_dbl(mod, ~ confint(.x)["date_num", "97.5 %"])) %>%
  mutate(growth = map_dbl(log_growth, exp)) %>%
  mutate(lci_growth = map_dbl(lci_log_growth, exp)) %>%
  mutate(uci_growth = map_dbl(uci_log_growth, exp)) %>%
  mutate(doubling = map_dbl(log_growth, ~ log(2) / .x)) %>%
  mutate(lci_doubling = map_dbl(lci_log_growth, ~ log(2) / .x)) %>%
  mutate(uci_doubling = map_dbl(uci_log_growth, ~ log(2) / .x))


# yeah - plot it
ggplot(fit) +
  aes(
    x = end, y = doubling,
    ymin = lci_doubling, ymax = uci_doubling
  ) +
  geom_errorbar(width = 0, colour = "orange") +
  geom_line() +
  geom_point() +
  scale_y_continuous(expand = c(0.2, 0)) +
  labs(
    x = "End date of 7 day period",
    y = "Doubling time (days)",
    title = "Doubling time estimated over 7 day window"
  )

# yeah - plot it
ggplot(fit) +
  aes(
    x = end, y = growth - 1,
    ymin = lci_growth - 1, ymax = uci_growth - 1
  ) +
  geom_errorbar(width = 0, colour = "orange") +
  geom_line() +
  geom_point() +
  scale_y_continuous(expand = c(0.2, 0), labels = scales::percent_format()) +
  labs(
    x = "End date of 7 day period",
    y = "Daily % growth",
    #title = "Daily growth estimated over 7 day window - new cases"
    title = "Daily growth estimated over 7 day window - cumulative cases"
  )

#ggsave("growth-new cases2.pdf")
ggsave("growth-cumulative cases2.pdf")
