
# app.R
library(shiny)
library(shinydashboard)
library(quantmod)
library(TTR)
library(xts)

ui <- dashboardPage(
  dashboardHeader(title = "Stock Trend Dashboard"),
  dashboardSidebar(
    textInput("ticker", "Ticker (Yahoo):", value = "AAPL"),
    dateRangeInput("dater", "Date range:", start = Sys.Date() - 365, end = Sys.Date()),
    numericInput("smaShort", "SMA (short):", value = 20, min = 2, max = 200),
    numericInput("smaLong",  "SMA (long):",  value = 50, min = 2, max = 400),
    numericInput("bbN",      "BBands N:",    value = 20, min = 5, max = 60),
    numericInput("bbK",      "BBands K:",    value = 2,  min = 1, max = 4, step = 0.5),
    downloadButton("dlcsv", "Download CSV")
  ),
  dashboardBody(
    fluidRow(
      box(title = "Candlestick with SMA & Bollinger Bands", width = 12, solidHeader = TRUE, status = "primary",
          plotOutput("chart", height = 420))
    ),
    fluidRow(
      box(title = "Latest Signals", width = 6, status = "info",
          tableOutput("signals")),
      box(title = "Quick Summary", width = 6, status = "warning",
          verbatimTextOutput("summary"))
    ),
    fluidRow(
      box(title = "RSI (14)", width = 6, status = "primary",
          plotOutput("rsiPlot", height = 260)),
      box(title = "MACD (12,26,9)", width = 6, status = "primary",
          plotOutput("macdPlot", height = 260))
    ),
    fluidRow(
      box(title = "Volume & 20-Day Volume MA", width = 6, status = "primary",
          plotOutput("volPlot", height = 260)),
      box(title = "Daily Returns Distribution", width = 6, status = "primary",
          plotOutput("retHist", height = 260),
          verbatimTextOutput("retStats"))
    )
  )
)

server <- function(input, output, session) {
  
  get_data <- reactive({
    req(input$ticker, input$dater)
    x <- try(
      getSymbols(input$ticker, src = "yahoo",
                 from = input$dater[1], to = input$dater[2],
                 auto.assign = FALSE),
      silent = TRUE
    )
    validate(need(!inherits(x, "try-error"), "Failed to download data. Check ticker/date."))
    x
  })
  
  ind_obj <- reactive({
    x <- get_data()
    Clx <- Cl(x); Opn <- Op(x); H <- Hi(x); L <- Lo(x); V <- Vo(x)
    
    smaS <- SMA(Clx, n = input$smaShort)
    smaL <- SMA(Clx, n = input$smaLong)
    bb   <- BBands(HLC(x), n = input$bbN, sd = input$bbK)
    
    crossUp   <- Lag(smaS) < Lag(smaL) & smaS > smaL
    crossDown <- Lag(smaS) > Lag(smaL) & smaS < smaL
    touchLow  <- Clx < bb$dn
    touchUp   <- Clx > bb$up
    
    sigType <- rep(NA_character_, NROW(x))
    sigType[which(crossUp)]   <- "SMA Bullish Cross (Buy)"
    sigType[which(crossDown)] <- "SMA Bearish Cross (Sell)"
    sigType[which(touchLow)]  <- ifelse(is.na(sigType[which(touchLow)]),
                                        "BBands Lower Touch (Potential Buy)",
                                        sigType[which(touchLow)])
    sigType[which(touchUp)]   <- ifelse(is.na(sigType[which(touchUp)]),
                                        "BBands Upper Break (Potential Sell)",
                                        sigType[which(touchUp)])
    
    rsi14   <- RSI(Clx, n = 14)
    macd    <- MACD(Clx, nFast = 12, nSlow = 26, nSig = 9, maType = EMA)
    volMA20 <- SMA(V, n = 20)
    rets    <- dailyReturn(Clx, type = "log")
    
    list(x = x, Clx = Clx, V = V,
         smaS = smaS, smaL = smaL, bb = bb, sigType = sigType,
         rsi14 = rsi14, macd = macd, volMA20 = volMA20, rets = rets)
  })
  
  output$chart <- renderPlot({
    o <- ind_obj()
    chartSeries(o$x, name = paste0(input$ticker, " (Yahoo)"),
                theme = "white", type = "candlesticks")
    addSMA(n = input$smaShort, on = 1, col = "blue")
    addSMA(n = input$smaLong,  on = 1, col = "red")
    addBBands(n = input$bbN, sd = input$bbK, on = 1)
  })
  
  output$signals <- renderTable({
    o <- ind_obj()
    idx <- which(!is.na(o$sigType))
    if (length(idx) == 0) return(data.frame(Message = "No signals in range"))
    d <- data.frame(
      Date   = index(o$Clx)[idx],
      Close  = as.numeric(o$Clx[idx]),
      Signal = o$sigType[idx],
      check.names = FALSE
    )
    tail(d, 10)
  })
  
  output$summary <- renderPrint({
    o <- ind_obj()
    lastClose <- as.numeric(last(o$Clx))
    lastS     <- as.numeric(last(na.omit(o$smaS)))
    lastL     <- as.numeric(last(na.omit(o$smaL)))
    pos <- if (!is.na(lastS) && !is.na(lastL)) {
      if (lastS > lastL) "Uptrend (SMA short > SMA long)" else "Downtrend (SMA short < SMA long)"
    } else {
      "Not enough data"
    }
    bb <- o$bb
    lastBB <- data.frame(
      Upper  = as.numeric(last(na.omit(bb$up))),
      Middle = as.numeric(last(na.omit(bb$m))),
      Lower  = as.numeric(last(na.omit(bb$dn)))
    )
    list(Ticker = input$ticker, Last_Close = lastClose, Trend = pos, Last_BBands = lastBB)
  })
  
  output$dlcsv <- downloadHandler(
    filename = function() {
      paste0(input$ticker, "_prices.csv")
    },
    content = function(file) {
      x <- get_data()
      sym <- input$ticker
      df <- data.frame(Date = index(x), coredata(x))
      names(df) <- sub(paste0("^", sym, "\\."), "", names(df))
      df$Ticker <- sym
      write.csv(df[, c("Date","Open","High","Low","Close","Volume","Adjusted","Ticker")],
                file, row.names = FALSE)
    }
  )
  
  output$rsiPlot <- renderPlot({
    o <- ind_obj(); r <- o$rsi14
    plot(index(r), as.numeric(r), type = "l", col = "darkblue",
         xlab = "Date", ylab = "RSI(14)", main = "RSI (14)")
    abline(h = c(30, 70), col = c("darkgreen", "firebrick"), lty = 2)
  })
  
  output$macdPlot <- renderPlot({
    o <- ind_obj(); m <- o$macd
    plot(index(m$macd), as.numeric(m$macd), type = "l", col = "steelblue",
         xlab = "Date", ylab = "MACD", main = "MACD (12,26,9)")
    lines(index(m$signal), as.numeric(m$signal), col = "tomato")
    abline(h = 0, col = "gray40", lty = 2)
  })
  
  output$volPlot <- renderPlot({
    o <- ind_obj(); v <- o$V; vma <- o$volMA20
    dates <- index(v)
    barCols <- ifelse(as.numeric(o$Clx) >= as.numeric(Lag(o$Clx)), "#2e8b57", "#b22222")
    plot(dates, as.numeric(v), type = "h", lwd = 2, col = barCols,
         xlab = "Date", ylab = "Volume", main = "Volume with 20-Day MA")
    lines(index(vma), as.numeric(vma), col = "navy", lwd = 2)
  })
  
  output$retHist <- renderPlot({
    o <- ind_obj(); r <- na.omit(o$rets)
    if (NROW(r) == 0) return()
    hist(as.numeric(r), breaks = 40, col = "goldenrod",
         main = "Daily Log Returns Distribution", xlab = "Return")
    abline(v = mean(as.numeric(r), na.rm = TRUE), col = "red", lwd = 2, lty = 2)
  })
  
  output$retStats <- renderPrint({
    o <- ind_obj(); r <- na.omit(o$rets)
    if (NROW(r) == 0) { cat("Not enough data for returns stats"); return() }
    mu <- mean(as.numeric(r)); sdv <- sd(as.numeric(r))
    annMu <- mu * 252; annVol <- sdv * sqrt(252)
    list(Mean_Daily = mu, SD_Daily = sdv, Ann_Return = annMu, Ann_Vol = annVol)
  })
}

shinyApp(ui, server)
