library("languageR")
library("lme4")
library("ez")
library("ggplot2")
control = lmerControl(optimizer='bobyqa')


data = read.delim('~/Dropbox/academic/Experiments/NMG/data/latency_ds.txt', header=T)

#Definition of constituent contrast
data$condition = factor(data$condition)
data$wordtype = C(data$wordtype, base=3)
constituent = data[(data$condition == 'control_constituent') | (data$condition == 'first_constituent'),]
identity = data[(data$condition == 'control_identity') | (data$condition == 'identity'),]

model <- lmer(latency~condition*wordtype + (condition*wordtype|subject) + (condition|word),
              data = constituent, control=control)
model.f <- lmer(latency~log_freq + block + condition*wordtype + (condition*wordtype|subject) + (condition|word),
              data = constituent, control=control)

model_i <- lmer(latency~condition*wordtype + (condition*wordtype|subject) + (condition|word),
                data = identity, control=control)
model_i.f <- lmer(latency~log_freq + block + condition*wordtype + (condition*wordtype|subject) + (condition|word),
              data = identity, control=control)

anova = ezANOVA(
  data = constituent
  , dv = .(latency)
#   , within_covariates = .(log_freq, block)
  , wid = .(subject)
  , within = .(condition, wordtype)
  , type =3
)

anova = ezANOVA(dv = latency, within = .(condition, wordtype), wid = subject, data = constituent)
anova.item = ezANOVA(dv = latency, within = condition, between = wordtype, wid = word, data = constituent)

anova_i = ezANOVA(dv = latency, within = .(condition, wordtype), wid = subject, data = identity)
anova_i.item = ezANOVA(dv = latency, within = condition, between = wordtype, wid = word, data = identity)


#Marginal Means
means = aggregate(latency ~ condition + wordtype, data = constituent, FUN = mean)
means_i = aggregate(latency ~ condition + wordtype, data = identity, FUN = mean)


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
