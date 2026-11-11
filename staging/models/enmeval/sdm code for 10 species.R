source(file.path(dirname(normalizePath(sub("^--file=", "", grep("^--file=", commandArgs(), value=TRUE)[1]))), "train.R"))
