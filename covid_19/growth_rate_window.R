# # data
# #dat <- read_csv("~/Documents/GitHub/COVID-19/covid_19/growth_rates/scot_cases.csv") %>%
# #  mutate(date = ymd(date))
# path <- paste0("COVID-19_Scotland_data_all_", {Sys.Date()}, ".xlsx")
# 
# # Scottish cases data
# scot_data_raw <- read_excel(path, sheet = "Cases By Health Board", skip = 1)
# scot_data_raw <- filter(scot_data_raw, !Health_Board %in% c("Increase", "pIncrease")) %>%
#   rename(confirmed_cases= Total,
#          Date = Health_Board) %>%
#   mutate(date = lubridate::ymd(Date)) %>%
#   select(-Date)
# 
# scot_data_raw$date[nrow(scot_data_raw)] <- scot_data_raw$date[nrow(scot_data_raw)-1] + days(1)
# #scot_data_raw$confirmed_cases[nrow(scot_data_raw)] <- 4565 ## REMOVE
# 
# scot_data <- scot_data_raw %>%
#   mutate(new_cases = confirmed_cases - replace_na(lag(confirmed_cases),0)) %>%
#   mutate(doubling_time_week = 7*log(2)/log(confirmed_cases/replace_na(lag(confirmed_cases,7),0))) 
# 
# #dat <-scot_data
# growth_rates(dat = scot_data %>% rename("outcome" = new_cases))
# growth_rates(dat = scot_deaths %>% rename("outcome" = deaths)) -> fit
# scot_data_health_board %>% rename("outcome" = confirmed_cases) %>%
#   group_by(health_board) %>%
#   nest() %>%
#   mutate(gr = map(data, ~growth_rates(dat = .x))) %>%
#   unnest(gr) -> fit
#dat <- subset(scot_data_health_board, health_board == unique(scot_data_health_board$health_board)[1])
#dat <- subset(dat, date >= (ymd("2020-04-17")-days(6)) & date <= ymd("2020-04-17"))
#dat$day <- 1:7
#mod <- glm(log(new_cases) ~ as.numeric(date), data = subset(dat, new_cases >0) )
#mod <- glm(log(new_cases) ~ as.numeric(day), data = subset(dat, new_cases >0) )
#coef(mod) %>% exp()

growth_rates <-function(dat){

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
  filter(outcome >0) %>% # run this if you want to fit new cases instead of cumulative cases
  group_by(start, end) %>%
  nest()

# examples
#fit$data[[1]]
#fit$data[[4]]

# fit lm(log) to each dataset and get growth etc
fit <- fit %>%
  #new cases 
  mutate(mod = map(data, ~ lm(log(outcome) ~ date_num,
                              data = .x
  ))) %>%
  mutate(coef = map(mod, coef)) %>%
  mutate(log_growth = map_dbl(coef, "date_num")) %>% 
  mutate(lci_log_growth = map_dbl(mod, ~ confint(.x)["date_num", "2.5 %"])) %>%
  mutate(uci_log_growth = map_dbl(mod, ~ confint(.x)["date_num", "97.5 %"])) %>%
  mutate(growth = map_dbl(log_growth, exp)) %>%
  mutate(lci_growth = map_dbl(lci_log_growth, exp)) %>%
  mutate(uci_growth = map_dbl(uci_log_growth, exp)) %>%
  ungroup() %>%
  select(end, growth, lci_growth, uci_growth) %>%
  mutate(sign = if_else(growth >1, "+", "")) %>%
  mutate(comparison = if_else(growth >1, "greater than", "less than")) %>%
  rename("date" = end) 

return(fit)
}

significance <- function(df){
  significant <- vector()
  for (i in 1:nrow(df)){
    sig <- !inside.range(x =1, r = c(df$lci_growth[i], df$uci_growth[i]))
    significant <- c(significant, sig)
  }
  df$significance <- paste(if_else(significant, "significantly", "not significantly"), df$comparison, 0, sep = " ")
  df$significance[df$significance %in% c("not significantly less than 0", "not significantly greater than 0") ] <- "not significantly different to 0"
  return(df)
}


# # yeah - plot it
# fit$uci_growth[fit$uci_growth > 60] <- NA
# fit$uci_growth[fit$uci_growth > 10] <- NA
# ggplot(fit) +
#   aes(
#     x = date, y = growth - 1,
#     #ymin = lci_growth - 1, ymax = uci_growth - 1,
#     colour = health_board, fill = health_board
#   ) +
#   #geom_errorbar(width = 0, colour = "orange") +
#   geom_hline(yintercept = 0, colour = "red", linetype = "dashed", size = 0.2) +
#   geom_line() +
#   geom_point() +
#   scale_y_continuous(expand = c(0.2, 0), labels = scales::percent_format()) +
#   labs(
#     x = "End date of 7 day period",
#     y = "Daily % growth",
#     #title = "Daily growth estimated over 7 day window - new cases"
#     title = "Daily growth estimated over 7 day window - new cases"
#   ) #+
#   #facet_grid(health_board ~.)
# 
# #ggsave("growth-new cases2.pdf")
# ggsave("growth-cumulative cases2.pdf")
