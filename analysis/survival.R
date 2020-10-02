library(survival)
library(survminer)
library(glrt)
library(icenReg)


data <- read.csv("event_data.csv");

surv_fit <- survfit(Surv(time_left, time_right, censor_type, type = 'interval') ~ strata(system), data = data);

all_systems = unique(data$system);

strata_names <- c()
for (name in names(surv_fit$strata)) {
  strata_names <- c(strata_names, strsplit(name, "=")[[1]][2])
}
fontsize <- 20
legend_size <- 40
ggsurvplot(
  surv_fit,
  data = data,
  font.x = fontsize,
  font.y = fontsize,
  font.legend = legend_size,
  font.tickslab = fontsize,
  legend.labs = strata_names,
  legend.title = "Systems",
  size=4,
);

significance_cutoff = 0.05;
n_bonferroni = (length(all_systems) * (length(all_systems) - 1)) / 2;   #  number of compared pairs

for (i in seq(1, length(all_systems) - 1)) {
  for (j in seq(i + 1, length(all_systems))) {
    sys1 = all_systems[i];
    sys2 = all_systems[j];
    sub_frame = subset(data, system == sys1 | system == sys2);
    
    mat <- matrix(data = 0, nrow = length(sub_frame$X), ncol = 3);
    mat[,1] = sub_frame$time_left;
    mat[,2] = sub_frame$time_right;
    mat[,3] = sub_frame$system == sys1;
    
    test <- gLRT(mat, k = 2);
    
    if (test$p < (significance_cutoff / n_bonferroni)) {
      significant_after_correction <- 'yes'
    } else {
      significant_after_correction <- 'no'
    }
    
    cat(sys1, sys2, test$p, significant_after_correction,'\n')
  }
}


for (i in seq(1, length(all_systems))) {
  cat(all_systems[i], '\n')
  show(ic_sp(Surv(time_left, time_right, censor_type, type = 'interval') ~ fluent + specific + sensible, data = subset(data, system == all_systems[i]), bs_samples = 200))
  cat('\n')
}
