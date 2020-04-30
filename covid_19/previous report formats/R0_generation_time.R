library(R0)
R0::estimate.R()

## Outbreak during 1918 influenza pandemic in Germany)
data(Germany.1918)

mGT<-generation.time("gamma", c(3, 1.5))
estR0<-estimate.R(Germany.1918, mGT, begin=1, methods=c("EG", "ML", "TD", "AR", "SB"), 
                  pop.size=100000)
estR0<-estimate.R(bla, mGT, methods=c("EG", "ML", "TD", "AR", "SB"), 
                  pop.size=100000)

estR0<-estimate.R(Germany.1918, GT = 7, begin=1, end=27, methods=c("EG", "ML", "TD", "AR", "SB"), 
                  pop.size=100000, nsim=100)

attributes(estR0)
## $names
## [1] "epid"      "GT"        "begin"     "end"       "estimates"
## 
## $class
## [1] "R0.sR"

bla <- select(scot_data, date, new_cases)
row.names(bla) <- bla$date
bla <- select(bla, new_cases)

est.R0.ML(bla, mGT, begin="1918-09-29", end="1918-10-25", range=c(0.01,100))

#Generation time/interval
#https://math.stackexchange.com/questions/1810257/gamma-functions-mean-and-standard-deviation-through-shape-and-rate
# The observed value of the growth rate r can be related to the value of reproductive number R through 
#a linear equation: RZ1CrTc (Anderson & May 1991;  Pybus et al. 2001; Ferguson et al. 2005). Here, Tc is the
#mean generation interval, defined as the mean duration between time of infection of a secondary infectee and the
#time of infection of its primary infector (sometimes this is called the serial interval or generation time).
# Lotka–Euler equation 