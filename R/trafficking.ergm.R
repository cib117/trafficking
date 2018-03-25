rm(list=ls())
#Set Directory
setwd("C:/Users/TC/Dropbox/29_Human Trafficking")

#Loading required packages
library(statnet)

#Loading Data
load("ergm.trafficking0916.RData")

#Fitting ERGM
m1<-ergm(net0916
         ~edges+mutual+isolates
         +threetrail(keep=1)
         +gwidegree(log(3),fixed=T)
         +gwodegree(log(3),fixed=T)
         +dgwdsp(log(3),fixed=T,cutoff=30,type="OTP")
         +ttriple+dgwesp(log(3),fixed=T,cutoff=30,type="OTP")
         +ctriple
         +nodeicov("gdppc")+nodeocov("gdppc")
         +nodeicov("deaths",transform=function(x)log(x+0.0001))+nodeocov("deaths",transform=function(x)log(x+0.0001))
         +nodeicov("hr.score")+nodeocov("hr.score")
         +nodeicov("fm.labour.ratio")+nodeocov("fm.labour.ratio")
         +nodeicov("prohibit.childmarriage")+nodeocov("prohibit.childmarriage")
         +nodeicov("law")+nodeocov("law")
         +edgecov(logged.imm.mat)
         +edgecov(logged.ref.mat0916)
         +edgecov(logged.trade.mat)
         +edgecov(contigland.mat)
         +edgecov(contigsea.mat)
         ,verbose=T,control=control.ergm(MCMC.samplesize=10000,MCMC.interval=5000,MCMC.burnin=5000000,seed=324892,MCMLE.check.degeneracy=T,MCMLE.maxit=50)
)
#Export "m1"
save("m1",file="m1.ergm.RData")

#Assessing goodness-of-fit
gof.m1<-gof(m1)

#Export "gof.m1"
save("gof.m1",file="m1.gof.RData")

#MCMC diagnostics
sink("m1.mcmcdiag.txt")
pdf("m1.mcmcplot.pdf",height=10,width=10)
mcmc.diagnostics(m1)
dev.off()
sink()


