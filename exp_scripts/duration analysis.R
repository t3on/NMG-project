library(lme4)
library(ez)

library('lme4')

duration_ds <- read.delim("~/Dropbox/academic/Experiments/NMG/data/group/duration_ds.txt")
duration_ds$compare = C(constituent$opaque + constituent$novel + constituent$transparent)
duration_ds$wordtype = C(duration_ds$wordtype, base=3)
constituent = duration_ds[(duration_ds$condition == 'control_constituent') | 
                            (duration_ds$condition == 'first_constituent'),]
model <- lmer(constituent_duration~log_freq + condition*wordtype + (1|subject) + (1+wordtype|word), 
              data = constituent)
model = lmer(constituent_duration~log_freq + opaque + transparent + novel + condition + (1+condition|subject)
             + (1+condition|word), data = constituent)

# old
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
