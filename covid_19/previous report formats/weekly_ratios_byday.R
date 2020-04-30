#dat <- scot_data %>% select(date, new_cases) %>%
#  mutate(outcome = new_cases) %>%
#  mutate(dayofweek = weekdays(date)) %>%
#  mutate(dayofweek = factor(dayofweek, levels = c("Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"))) 


weekly_ratios_dayadj <-function(dat){
  
  # add windows
  dat <- dat %>%
    crossing(tibble(
      start = seq(from = min(dat$date),
                  to = max(dat$date) - days(13),
                  by = 1),
      end   = seq(from = min(dat$date) + days(13),
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
  
 fit <-  fit %>%
   mutate(data = map(data, 
                     ~ mutate(.x, 
                              week = floor_date(date, "weeks", week_start = .x$dayofweek[1]))))

  
  # fit lm(log) to each dataset and get growth etc
  fit <- fit %>%
    #new cases 
    mutate(mod = map(data, ~ glm(new_cases ~ as.factor(week) + dayofweek,
                                 family = "poisson",
                                data = .x
    ))) %>%
    mutate(ratio_m = map_dbl(mod, ~ exp(coef(.x)[2]))) %>% 
    mutate(lci = map_dbl(mod, ~ exp(confint(.x)[2, "2.5 %"]))) %>%
    mutate(uci = map_dbl(mod, ~ exp(confint(.x)[2, "97.5 %"]))) %>%
    ungroup() %>%
    select(end, ratio_m, lci, uci) %>%
   # mutate(sign = if_else(growth >1, "+", "")) %>%
   # mutate(comparison = if_else(growth >1, "greater than", "less than")) %>%
    rename("date" = end) 
  
  return(fit)
}

