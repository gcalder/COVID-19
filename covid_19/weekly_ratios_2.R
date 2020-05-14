#df <- scot_deaths %>% select(new_deaths, date) %>%
#      mutate(outcome = new_deaths)

#df <- scot_data %>% select(new_cases, date) %>%
#  mutate(outcome = new_cases)


#weekly_ratios(df) %>% View()


weekly_ratios_ci <- function(A, B){
  
  e <- sqrt(1/A + 1/B)
  
  est <- c(exp(log(A/B) - e * 1.96),
           exp(log(A/B) + e * 1.96))
  
  tab <- tibble(type = c("ratio_m","lci", "uci"),
         est = c(A/B, est[[1]], est[[2]]))
  return(tab)
  
}


weekly_ratios_2 <- function(df, outcome, smooth_by = 7){

df <- df %>% 
  subset(date >= lubridate::ymd("2020-02-20")) %>%
  filter(!is.na(outcome)) %>% 
  mutate(change = roll_sumr(outcome, n = smooth_by),
         change_prev = lag(change, n = smooth_by),
         ratio = change/change_prev) %>%
  mutate(comparison = if_else(ratio >1, "greater than", "less than")) 

df_long <- df %>%
  filter(!is.na(ratio) & !is.infinite(ratio)) %>%
  group_by(date) %>%
  nest() %>%
  mutate(tab = map(data, ~ weekly_ratios_ci(.x$change, .x$change_prev))) %>%
  mutate(ratio_m = map_dbl(tab, ~parse_number(as.character((.x[1,2]))))) %>% 
  mutate(lci = map_dbl(tab, ~parse_number(as.character((.x[2,2]))))) %>% 
  mutate(uci = map_dbl(tab, ~parse_number(as.character((.x[3,2]))))) %>% 
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
  #df$significance[df$significance %in% c("not significantly greater than 1") ] <- "not significantly different to 1"
  return(df)
}
