
# 01_fetch_to_csv.R
library(quantmod)

tickers <- c("AAPL", "MSFT")                 # <-- change tickers here
from    <- as.Date("2022-01-01")             # <-- change start date
to      <- Sys.Date()                         # <-- change end date

dir.create("data", showWarnings = FALSE)

fetch_one <- function(sym) {
  x <- getSymbols(sym, src = "yahoo", from = from, to = to, auto.assign = FALSE)
  df <- data.frame(Date = index(x), coredata(x))
  names(df) <- sub(paste0("^", sym, "\\."), "", names(df))  # Remove 'SYM.' prefix
  df$Ticker <- sym
  df[, c("Date","Open","High","Low","Close","Volume","Adjusted","Ticker")]
}

all <- do.call(rbind, lapply(tickers, fetch_one))

# Write one combined CSV + per-ticker CSVs
write.csv(all, "data/stock_prices_all.csv", row.names = FALSE)
invisible(lapply(split(all, all$Ticker), function(d) {
  write.csv(d, file.path("data", paste0(unique(d$Ticker), "_prices.csv")), row.names = FALSE)
}))

cat("Saved:\n - data/stock_prices_all.csv\n - data/<TICKER>_prices.csv\n")

