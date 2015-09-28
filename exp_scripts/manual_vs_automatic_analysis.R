library(lme4)
library(ez)
library(gtools)
control = lmerControl(optimizer='bobyqa')

manual <- read.delim("~/Dropbox/academic/Experiments/NMG/data/duration_manual_alignment_match_ds.txt")

auto <- read.delim("~/Dropbox/academic/Experiments/NMG/data/duration_automatic_alignment_match_ds.txt")

shuffle = permute(1:length(auto$c1_dur))
idx = shuffle[1:round(.75*(length(auto$c1_dur)))]
t.test(auto[idx,]$c1_dur, manual[idx,]$c1_dur)

constituent = data[(data$condition == 'control_constituent') | (data$condition == 'first_constituent'),]
identity = data[(data$condition == 'control_identity') | (data$condition == 'identity'),]

model <- lmer(duration~condition*wordtype + (condition*wordtype|subject) + (condition|word), 
              data = constituent)
model.f <- lmer(duration~log_freq + block + condition*wordtype + (condition*wordtype|subject) + (condition|word), 
                data = constituent)

model_i <- lmer(duration~condition*wordtype + (condition*wordtype|subject) + (condition|word),
                data = identity, control=control)
model_i.f <- lmer(duration~log_freq + block + condition*wordtype + (condition*wordtype|subject) + (condition|word),
                  data = identity, control=control)

anova = ezANOVA(dv = duration, within = .(condition, wordtype), wid = subject, data = constituent)
anova.item = ezANOVA(dv = duration, within = condition, between = wordtype, wid = word, data = constituent)

anova_i = ezANOVA(dv = duration, within = .(condition, wordtype), wid = subject, data = identity)
anova_i.item = ezANOVA(dv = duration, within = condition, between = wordtype, wid = word, data = identity)


#Marginal Means
means = aggregate(duration ~ condition + wordtype, data = constituent, FUN = mean)
means_i = aggregate(duration ~ condition + wordtype, data = identity, FUN = mean)


# 
# model1 <- lmer(duration~log_freq + block + condition*wordtype + (condition/wordtype|subject) + (condition|word), 
#               data = constituent)
# 
# identity = duration_ds[(duration_ds$condition == 'control_identity') | 
#                             (duration_ds$condition == 'identity'),]
# model <- lmer(duration~log_freq + block + condition*wordtype + (condition*wordtype|subject) + (condition|word), 
#               data = identity)
# 
# 
# # old
# setwd("/Users/teon/Dropbox/Experiments/NMG/data/group")
# 
# data = read.table('duration_ds.txt', header=T)
# constituent = data[data['condition'] == 'control_constituent' | data['condition'] == 'first_constituent',]
# constituent$wordtype = C(constituent$wordtype,base=3)
# constituent$duration = constituent$c1_dur #+ constituent$c2_dur 
# lm = lmer(duration~wordtype*condition + (1 + wordtype*condition|subject) + (1+ wordtype*condition|word), data=constituent)
# lm_simple = lmer(duration~wordtype*condition + (1 + wordtype+condition|subject) + (1 + wordtype+condition|word), data=constituent)
# means = aggregate(duration ~ condition + wordtype, data = constituent, FUN = mean)
# 
# lm_l = lmer(latency~wordtype*condition + (1 + wordtype*condition|subject) + (1+ wordtype*condition|word), data=constituent)
# means_l = aggregate(latency ~ condition + wordtype, data = constituent, FUN = mean)
# 
# identity = data[data['condition'] == 'control_identity' | data['condition'] == 'identity',]
# identity$duration = identity$c1_dur + identity$c2_dur 
# identity$wordtype = C(identity$wordtype,base=3)
# lm = lmer(duration~wordtype*condition + (1 + wordtype+condition|subject) , data=identity)
# lm = lmer(duration~wordtype*condition + log_freq + (1 + wordtype+condition|subject) , data=identity)
# lm = lmer(duration~wordtype*condition + (1 + wordtype*condition|subject) + (1+ wordtype*condition|word), data=identity)
# means_d = aggregate(duration ~ condition + wordtype, data = identity, FUN = mean)
# 
# p = ggplot(means, aes(fill=condition, y=duration, x=wordtype))
# p+geom_bar(position='dodge')
