library(dplyr)
library(tidyr)
library(ggplot2)
library(ggpubr)

old_wd <- getwd()
setwd("R")

collect_data <- function(file) {
  data <- read.delim(file)
  
  # We reorganize data into rows since it was created manually.
  # May not be necessary if generated by a script.
  data <- data %>% gather(key="method", value="F1", -k)
  
  # Remove methods not discussed in the thesis.
  data <- data %>% filter(method!="ngram")
  data <- data %>% filter(method!="fastNgram")
  
  # Set user friendly names.
  data$method <- gsub("SI", "Sense inventory", data$method)
  data$method <- gsub("fastType", "n-gram", data$method)
  
  return(data)
}

plot_data <- function(data, title) {
  g <- ggplot(data=data, aes(x=k, y=F1, group=method)) +
    geom_line(aes(color=method, linetype=method)) +
    geom_point(size=0.5) +
    scale_x_continuous(minor_breaks=seq(1,20,1)) +
    scale_y_continuous(breaks=seq(0,1,0.1), limits=c(0,1)) +
    ggtitle(title) +
    xlab("k") +
    ylab("F1") +
    theme_linedraw() +
    theme(legend.position="bottom", legend.title=element_blank())
  return(g)
}

strict_data <- collect_data("strict.tsv")
strict_plot <- plot_data(strict_data, "Strict matching")

lenient_data <- collect_data("lenient.tsv")
lenient_plot <- plot_data(lenient_data, "Lenient matching")

ggarrange(strict_plot, lenient_plot, nrow=2, common.legend = TRUE, legend="bottom") %>%
  ggexport(filename="plots.pdf", width=5)

setwd(old_wd)