library(lme4)
library(ez)
setwd("/Users/teon/Dropbox/Experiments/NMG/data/group")

data = read.table('duration_ds.txt', header=T)
constituent = data[data['condition'] == 'control_constituent' | data['condition'] == 'first_constituent',]
constituent$wordtype = C(constituent$wordtype,base=3)
constituent$duration = constituent$c1_dur #+ constituent$c2_dur 
lm = lmer(duration~wordtype*condition + (1 + wordtype*condition|subject) + (1+ wordtype*condition|word), data=constituent)
lm_simple = lmer(duration~wordtype*condition + (1 + wordtype+condition|subject) + (1 + wordtype+condition|word), data=constituent)
means = aggregate(duration ~ condition + wordtype, data = constituent, FUN = mean)

lm_l = lmer(latency~wordtype*condition + (1 + wordtype*condition|subject) + (1+ wordtype*condition|word), data=constituent)
means_l = aggregate(latency ~ condition + wordtype, data = constituent, FUN = mean)

identity = data[data['condition'] == 'control_identity' | data['condition'] == 'identity',]
identity$duration = identity$c1_dur + identity$c2_dur 
identity$wordtype = C(identity$wordtype,base=3)
lm = lmer(duration~wordtype*condition + (1 + wordtype+condition|subject) , data=identity)
lm = lmer(duration~wordtype*condition + log_freq + (1 + wordtype+condition|subject) , data=identity)
lm = lmer(duration~wordtype*condition + (1 + wordtype*condition|subject) + (1+ wordtype*condition|word), data=identity)
means_d = aggregate(duration ~ condition + wordtype, data = identity, FUN = mean)

p = ggplot(means, aes(fill=condition, y=duration, x=wordtype))
p+geom_bar(position='dodge')
