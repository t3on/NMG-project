library("languageR")
library("lme4")
library("ez")
library("ggplot2")


data = read.delim('~/Dropbox/Experiments/NMG/data/group/group_duration_ds.txt', header=T)
#data = data[data$condition == 'first_constituent' | data$condition == 'control_constituent',]
#model = lmer(duration~(1|subject) + log_freq + condition + opaque + transparent + novel + opaque*condition + transparent*condition + 
#               novel*condition, data= data)

#Definition of constituent contrast
data$condition = factor(data$condition)
data$wordtype = factor(data$wordtype)
model = lmer(latency ~ log_freq + condition*wordtype + (wordtype|subject), data=data)
model = lmer(latency~(wordtype|subject) + log_freq + condition + opaque + transparent + novel + opaque*condition + transparent*condition + 
            novel*condition, data= data)

###
#this model is probably correct
model = lmer(latency~(wordtype|subject) + log_freq + condition + opaque + transparent + novel + opaque*condition + transparent*condition + 
              novel*condition + (1+wordtype|subject) + (1+condition|subject), data= data)
###
lml = lm(latency~log_freq + condition + opaque + transparent + novel + opaque*condition + transparent*condition + novel*condition, data= data)
# anova = ezANOVA(
#   data = data
#   , dv = .(latency)
#   , within_covariates = .(log_freq)
#   , wid = .(subject)
#   , within = .(condition, wordtype)
#   , type =3
# )

#Marginal Means
means = aggregate(latency ~ condition + wordtype, data = data, FUN = mean)


#Plots
png('~/Dropbox/Experiments/NMG/results/plots/behavioral/latency_constituent.png')
ggplot(constituent.RT.means, aes(x=p_cat, y=RT, fill=factor(p_cond))) + geom_bar(stat='identity', position='dodge') + geom_errorbar(limits, position= 'dodge')
dev.off()


#Planned Comparison
p_constituent.cond = data[(data$p_cond == 'control_constituent' | data$p_cond == 'first_constituent') & (data$p_cat == 'opaque' | data$p_cat == 'transparent') & (data$block_type == 'experiment') ,]
p_constituent.anova = ezANOVA(
  data = p_constituent.cond
  , dv = .(RT)
  , wid = .(subject)
  , within = .(p_cond, p_cat, block)
)
p_constituent.RT.means = aggregate(RT ~ p_cond + p_cat, data = p_constituent.cond, FUN = mean)



sink("~/Dropbox/Experiments/NMG/results/anovas/behavioral/NMG_group_latency_analysis.txt")
cat("Identity ANOVA", "", "\n")
print(identity.anova)
cat("","","\n")

cat("First Constituent ANOVA", "", "\n")
print(constituent.anova)
cat("","", "\n")

cat("Planned Comparison: Opaque vs. Transparent ANOVA", "", "\n")
print(p_constituent.anova)
cat("","", "\n")
sink()
