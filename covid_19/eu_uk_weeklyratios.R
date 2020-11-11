library(tidyverse)
library(lubridate)

hols <- read_csv("School_Hols.csv") %>%
      mutate(Holiday1_Start = dmy(Holiday1_Start),
             Holiday1_End = dmy(Holiday1_End),
             #Holiday1_Shading = dmy(Holiday1_Shading),
             Holiday2_Start = dmy(Holiday2_Start),
             Holiday2_End = dmy(Holiday2_End)) %>%
  rename("country" = "Country") %>%
  mutate(ymin = -Inf,
         ymax = Inf) %>%
  filter(!country %in% c("Wales", "Northern Ireland", "Iceland", "Luxembourg", "United Kingdom"))

countries <- c("Belgium",	"Denmark",	"Finland",	"France",	"Germany",	"Iceland",	"Italy",	"Luxembourg",	"Netherlands",	"Norway",
               "Portugal",	"Spain",	"Sweden", "Ireland", "Switzerland")	

eu <- read_csv("https://opendata.ecdc.europa.eu/covid19/casedistribution/csv/data.csv") %>%
  filter(countriesAndTerritories %in% countries) %>%
  rename("new_cases" = cases,
         "country" = countriesAndTerritories) %>%
  mutate(date = dmy(dateRep)) %>%
  select(new_cases, country, date)
  

uk_nation <- read_csv("https://api.coronavirus.data.gov.uk/v1/data?filters=areaType=nation&structure=%7B%22areaType%22:%22areaType%22,%22areaName%22:%22areaName%22,%22areaCode%22:%22areaCode%22,%22date%22:%22date%22,%22newCasesByPublishDate%22:%22newCasesByPublishDate%22,%22cumCasesByPublishDate%22:%22cumCasesByPublishDate%22%7D&format=csv")
uk_nation <- uk_nation %>%
  mutate(date = ymd(date)) %>%
  rename("country" = areaName,
         "new_cases" = newCasesByPublishDate) %>%
  select(new_cases, country, date) %>%
  mutate(UK = "yes")

uk_total <- read_csv("https://api.coronavirus.data.gov.uk/v1/data?filters=areaName=United%2520Kingdom;areaType=overview&structure=%7B%22areaType%22:%22areaType%22,%22areaName%22:%22areaName%22,%22areaCode%22:%22areaCode%22,%22date%22:%22date%22,%22newCasesByPublishDate%22:%22newCasesByPublishDate%22,%22cumCasesByPublishDate%22:%22cumCasesByPublishDate%22%7D&format=csv")
uk_total <- uk_total %>%
  mutate(date = ymd(date)) %>%
  rename("country" = areaName,
         "new_cases" = newCasesByPublishDate) %>%
  select(new_cases, country, date) %>%
  mutate(UK = "yes")

eu_uk <- bind_rows(eu, uk_nation, uk_total) %>%
  filter(!country %in% c("Wales", "Northern Ireland", "Iceland", "Luxembourg", "United Kingdom"))

wk_gr_newcases_euuk <- eu_uk %>% rename("outcome" = new_cases) %>%
  arrange(date) %>%
  group_by(country) %>%
  nest() %>%
  mutate(gr = map(data, ~weekly_ratios(.x))) %>%
  unnest(gr) %>%
  filter(date >= ymd("2020-03-23")) %>%
  filter(!is.na(ratio) & !is.infinite(ratio))  


ggplot(wk_gr_newcases_euuk  %>%
 filter(date >= dmy("1/9/2020") & date < (max(wk_gr_newcases_euuk$date)-days(4)))) +
  geom_rect(data=hols,
  aes(xmin=Holiday1_Start, xmax=Holiday1_End, ymin=ymin, ymax=ymax, fill = Holiday1_Shading)) +
  geom_rect(data=hols,
            aes(xmin=Holiday2_Start, xmax=Holiday2_End, ymin=ymin, ymax=ymax), fill = "grey70") +
  geom_point(aes(x=date, y = ratio_m), colour = "black", size = 0.5) +
  scale_fill_manual(values = c("Dark"="grey40", "Light"="grey70"), labels = c("National","Staggered or Localised"),
                    name = "Holiday Type") + 
  geom_line(aes(x=date, y = ratio_m), colour = "black" ) +
  geom_hline(yintercept = 1, colour = "red", linetype = "dashed", size = 0.2, alpha = 0.7) +
  scale_y_continuous(expand = expansion(mult = c(0, 0.05))) +
  #facet_grid(Health_board~CAName, scales = "free_y") + 
  facet_wrap(~country, strip.position = "top", scales = "free_y", ncol = 3) +
  theme(#panel.spacing = unit(0, "lines"), 
    panel.spacing.y=unit(0.5, "lines"),
    strip.background = element_blank(),
    strip.placement = "outside") +
  labs(x = "End Date of Current Week", y = "Weekly Ratio of New Cases") +
  theme(legend.position=c(0.95,1.05),
        legend.direction="horizontal",
        legend.justification=c(1, 0), 
        legend.key.width=unit(1, "lines"), 
        legend.key.height=unit(1, "lines"), 
        plot.margin = unit(c(3.5, 0, 0.5, 0.5), "lines")) +
  theme(#legend.position = "top",
        #legend.text.align = 1,
        #legend.position = "top",
        #legend.direction = "horizontal",
        panel.background = element_blank(),
        axis.line = element_line(colour = "black"),
        axis.text = element_text(size = 8),
        legend.key = element_rect(colour = NA, fill = NA)) 

ggsave("weekly_ratios_cases_eu.png", width = 9, height = 9, units = "in", dpi = 200)
