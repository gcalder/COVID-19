library(tidyverse)
library(rsample)
library(incidence)


dat <- read_csv("growth_rates/scot_cases.csv") %>%
  mutate(date = ymd(date)) %>%
  select(date, new_cases)

set.seed(9256)

boot <- rsample::bootstraps(dat, times = 1000) %>%
  mutate(data = map(splits, as.data.frame)) %>%
  mutate(inc = map(
    data,
    ~ possibly(as.incidence, NA)(x = .x$new_cases,
      dates = .x$date)
  )) %>%
  filter(!is.na(inc)) %>%
  mutate(fit = map(inc, fit)) %>%
  mutate(r = map_dbl(fit, c("info", "r")))

qplot(boot$r)
