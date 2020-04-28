#df <- scot_deaths %>% select(new_deaths, date) %>%
#      mutate(outcome = new_deaths)

#df <- scot_data %>% select(new_cases, date) %>%
#  mutate(outcome = new_cases)


#weekly_ratios(df) %>% View()

weekly_ratios <- function(df, outcome, smooth_by = 7){

df <- df %>% 
  subset(date >= lubridate::ymd("2020-02-20")) %>%
  filter(!is.na(outcome)) %>% 
  mutate(change = roll_sumr(outcome, n = smooth_by),
         change_prev = lag(change, n = smooth_by),
         ratio = change/change_prev) %>%
  mutate(comparison = if_else(ratio >1, "greater than", "less than")) 

df_long <- df %>%
  filter(!is.na(ratio) & !is.infinite(ratio)) %>%
  pivot_longer(change:change_prev, names_to = "week", values_to = "new_numbers_week") %>%
  mutate(week = factor(week, levels = c("change_prev", "change"))) %>%
  group_by(date) %>%
  nest() %>%
  mutate(mod = map(data, ~ glm(new_numbers_week ~ week,
                              data = .x, family = poisson))) %>%
  #mutate(log_growth = map_dbl(coef, "weekchange_prev")) %>% 
  mutate(ratio_m = map_dbl(mod, ~ exp(coef(.x)["weekchange"]))) %>% 
  mutate(lci = map_dbl(mod, ~ exp(confint(.x)["weekchange", "2.5 %"]))) %>%
  mutate(uci = map_dbl(mod, ~ exp(confint(.x)["weekchange", "97.5 %"]))) %>%
  ungroup() %>%
  select(date, ratio_m, lci, uci) 

return(left_join(df, df_long))
}

significance_wk <- function(df){
  significant <- vector()
  for (i in 1:nrow(df)){
    sig <- !inside.range(x =1, r = c(df$lci[i], df$uci[i]))
    significant <- c(significant, sig)
  }
  df$significance <- paste(if_else(significant, "significantly", "not significantly"), df$comparison, 1, sep = " ")
  df$significance[df$significance %in% c("not significantly less than 1", "not significantly greater than 1") ] <- "not significantly different to 1"
  return(df)
}
