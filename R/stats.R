library(stats)

data <- read.delim("summary.tsv")

for (i in 3:ncol(data)) {
  htest <- mcnemar.test(data[,2], data[,i], correct=FALSE)
  print(htest)
}
