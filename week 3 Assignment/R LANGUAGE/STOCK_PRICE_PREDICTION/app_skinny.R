
library(shiny); library(quantmod); library(TTR)
ui <- fluidPage(
  titlePanel("Skinny Stock Viewer"),
  sidebarLayout(
    sidebarPanel(
      textInput("t","Ticker","AAPL"),
      dateRangeInput("d","Dates",start=Sys.Date()-365,end=Sys.Date()),
      numericInput("s1","SMA short",20,2,200),
      numericInput("s2","SMA long",50,2,400),
      numericInput("n","BBands n",20,5,60),
      numericInput("k","BBands k",2,1,4,0.5),
      downloadButton("dl","Download CSV")
    ),
    mainPanel(
      plotOutput("p",height=420),
      fluidRow(
        column(6, plotOutput("rsi",height=240)),
        column(6, plotOutput("macd",height=240))
      ),
      fluidRow(
        column(6, plotOutput("vol",height=240)),
        column(6, plotOutput("hist",height=240), verbatimTextOutput("stats"))
      )
    )
  )
)

server <- function(input, output, session){
  dat <- reactive({
    getSymbols(input$t, src="yahoo", from=input$d[1], to=input$d[2], auto.assign=FALSE)
  })
  ind <- reactive({
    x <- dat(); cl <- Cl(x)
    s1 <- SMA(cl, n=input$s1); s2 <- SMA(cl, n=input$s2); bb <- BBands(HLC(x), n=input$n, sd=input$k)
    up <- Lag(s1)<Lag(s2) & s1>s2; dn <- Lag(s1)>Lag(s2) & s1<s2; lo <- cl<bb$dn; hi <- cl>bb$up
    st <- rep(NA_character_, NROW(x)); st[which(up)] <- "SMA Bullish"; st[which(dn)] <- "SMA Bearish"; st[which(lo)] <- "BB Low Touch"; st[which(hi)] <- "BB Upper Break"
    list(x=x, cl=cl, st=st, rsi=RSI(cl,14), macd=MACD(cl,12,26,9, maType=EMA),
         vol=Vo(x), volMA=SMA(Vo(x),20), rets=dailyReturn(cl, type="log"))
  })
  output$p <- renderPlot({
    x <- dat(); chartSeries(x, theme="white", type="candlesticks")
    addSMA(n=input$s1, on=1, col="blue"); addSMA(n=input$s2, on=1, col="red"); addBBands(n=input$n, sd=input$k, on=1)
  })
  output$rsi <- renderPlot({
    r <- ind()$rsi; plot(index(r), as.numeric(r), type="l", col="darkblue", xlab="Date", ylab="RSI(14)", main="RSI (14)")
    abline(h=c(30,70), col=c("darkgreen","firebrick"), lty=2)
  })
  output$macd <- renderPlot({
    m <- ind()$macd
    plot(index(m$macd), as.numeric(m$macd), type="l", col="steelblue", xlab="Date", ylab="MACD", main="MACD (12,26,9)")
    lines(index(m$signal), as.numeric(m$signal), col="tomato"); abline(h=0, col="gray40", lty=2)
  })
  output$vol <- renderPlot({
    o <- ind(); v <- o$vol; vma <- o$volMA; d <- index(v)
    bars <- ifelse(as.numeric(o$cl) >= as.numeric(Lag(o$cl)), "#2e8b57", "#b22222")
    plot(d, as.numeric(v), type="h", lwd=2, col=bars, xlab="Date", ylab="Volume", main="Volume + 20D MA"); lines(index(vma), as.numeric(vma), col="navy", lwd=2)
  })
  output$hist <- renderPlot({
    r <- na.omit(ind()$rets); if(NROW(r)==0) return()
    hist(as.numeric(r), breaks=40, col="goldenrod", main="Daily Log Returns", xlab="Return")
    abline(v=mean(as.numeric(r)), col="red", lwd=2, lty=2)
  })
  output$stats <- renderPrint({
    r <- na.omit(ind()$rets); if(NROW(r)==0){cat("Not enough data");return()}
    mu <- mean(as.numeric(r)); sdv <- sd(as.numeric(r)); cat(sprintf("Mean(daily)=%.6f\nSD(daily)=%.6f\nAnn.Return=%.6f\nAnn.Vol=%.6f", mu, sdv, mu*252, sdv*sqrt(252)))
  })
  output$dl <- downloadHandler(
    filename = function() paste0(input$t, "_prices.csv"),
    content = function(file){
      x <- dat(); df <- data.frame(Date=index(x), coredata(x)); names(df) <- sub(paste0("^", input$t, "\\."), "", names(df)); df$Ticker <- input$t
      write.csv(df[,c("Date","Open","High","Low","Close","Volume","Adjusted","Ticker")], file, row.names=FALSE)
    }
  )
}
shinyApp(ui, server)
