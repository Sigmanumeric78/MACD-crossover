//+------------------------------------------------------------------+
//| MACD_Crossover_Manual.mq5                                       |
//| Manual MACD crossover strategy for EURUSD H1                     |
//+------------------------------------------------------------------+
#property strict

#include <Trade/Trade.mqh>

input int FastPeriod = 12;
input int SlowPeriod = 26;
input int SignalPeriod = 9;
input double LotSize = 0.10;
input int MagicNumber = 26012024;
input int SlippagePoints = 10;
input bool PrintDebug = false;

CTrade trade;
datetime lastBarTime = 0;

bool HasNumericValue(const double value)
{
   return value != EMPTY_VALUE && MathIsValidNumber(value);
}

bool ManualEMA(const double &values[], const int count, const int period, double &ema[])
{
   if(period <= 0 || count <= 0)
      return false;

   ArrayResize(ema, count);
   ArrayInitialize(ema, EMPTY_VALUE);

   const double alpha = 2.0 / (period + 1.0);
   double seedSum = 0.0;
   int seedCount = 0;
   bool seeded = false;
   double previous = EMPTY_VALUE;

   for(int i = 0; i < count; i++)
   {
      const double value = values[i];
      if(!HasNumericValue(value))
      {
         ema[i] = EMPTY_VALUE;
         continue;
      }

      if(!seeded)
      {
         seedSum += value;
         seedCount++;
         if(seedCount == period)
         {
            previous = seedSum / period;
            ema[i] = previous;
            seeded = true;
         }
         continue;
      }

      previous = alpha * value + (1.0 - alpha) * previous;
      ema[i] = previous;
   }

   return seeded;
}

bool CalculateMACD(
   const double &closes[],
   const int count,
   const int fastPeriod,
   const int slowPeriod,
   const int signalPeriod,
   double &macd[],
   double &signal[]
)
{
   double fastEma[];
   double slowEma[];

   if(!ManualEMA(closes, count, fastPeriod, fastEma))
      return false;
   if(!ManualEMA(closes, count, slowPeriod, slowEma))
      return false;

   ArrayResize(macd, count);
   ArrayInitialize(macd, EMPTY_VALUE);

   for(int i = 0; i < count; i++)
   {
      if(HasNumericValue(fastEma[i]) && HasNumericValue(slowEma[i]))
         macd[i] = fastEma[i] - slowEma[i];
   }

   return ManualEMA(macd, count, signalPeriod, signal);
}

bool HasManagedLongPosition(ulong &positionTicket)
{
   positionTicket = 0;

   for(int i = PositionsTotal() - 1; i >= 0; i--)
   {
      const ulong ticket = PositionGetTicket(i);
      if(ticket == 0)
         continue;

      if(PositionGetString(POSITION_SYMBOL) != _Symbol)
         continue;

      if((int)PositionGetInteger(POSITION_MAGIC) != MagicNumber)
         continue;

      if((ENUM_POSITION_TYPE)PositionGetInteger(POSITION_TYPE) == POSITION_TYPE_BUY)
      {
         positionTicket = ticket;
         return true;
      }
   }

   return false;
}

void PrintTradeFailure(const string action)
{
   PrintFormat(
      "%s failed. retcode=%u comment=%s description=%s",
      action,
      trade.ResultRetcode(),
      trade.ResultComment(),
      trade.ResultRetcodeDescription()
   );
}

bool CloseManagedLongPositions()
{
   bool allClosed = true;

   for(int i = PositionsTotal() - 1; i >= 0; i--)
   {
      const ulong ticket = PositionGetTicket(i);
      if(ticket == 0)
         continue;

      if(PositionGetString(POSITION_SYMBOL) != _Symbol)
         continue;

      if((int)PositionGetInteger(POSITION_MAGIC) != MagicNumber)
         continue;

      if((ENUM_POSITION_TYPE)PositionGetInteger(POSITION_TYPE) != POSITION_TYPE_BUY)
         continue;

      if(!trade.PositionClose(ticket, SlippagePoints))
      {
         allClosed = false;
         PrintTradeFailure("Close long");
      }
      else if(PrintDebug)
      {
         PrintFormat("Closed long position ticket=%I64u", ticket);
      }
   }

   return allClosed;
}

void EvaluateClosedBars()
{
   int barsToCopy = SlowPeriod + SignalPeriod + 50;
   if(barsToCopy < 300)
      barsToCopy = 300;

   MqlRates rates[];
   ArraySetAsSeries(rates, true);

   const int copied = CopyRates(_Symbol, PERIOD_H1, 1, barsToCopy, rates);
   const int minBars = SlowPeriod + SignalPeriod + 2;
   if(copied < minBars)
   {
      if(PrintDebug)
         PrintFormat("Not enough closed H1 bars. copied=%d required=%d", copied, minBars);
      return;
   }

   double closes[];
   ArrayResize(closes, copied);

   for(int i = 0; i < copied; i++)
      closes[i] = rates[copied - 1 - i].close;

   double macd[];
   double signal[];
   if(!CalculateMACD(closes, copied, FastPeriod, SlowPeriod, SignalPeriod, macd, signal))
   {
      if(PrintDebug)
         Print("Manual MACD values are not ready yet.");
      return;
   }

   const int currentIndex = copied - 1;
   const int previousIndex = copied - 2;

   if(!HasNumericValue(macd[currentIndex]) ||
      !HasNumericValue(signal[currentIndex]) ||
      !HasNumericValue(macd[previousIndex]) ||
      !HasNumericValue(signal[previousIndex]))
   {
      if(PrintDebug)
         Print("Current or previous manual MACD signal values are not ready.");
      return;
   }

   const bool bullishCross =
      macd[previousIndex] <= signal[previousIndex] &&
      macd[currentIndex] > signal[currentIndex];
   const bool bearishCross =
      macd[previousIndex] >= signal[previousIndex] &&
      macd[currentIndex] < signal[currentIndex];

   ulong longTicket = 0;
   const bool hasLong = HasManagedLongPosition(longTicket);

   if(PrintDebug)
   {
      PrintFormat(
         "Closed bar=%s macd=%.8f signal=%.8f previous_macd=%.8f previous_signal=%.8f has_long=%s",
         TimeToString(rates[0].time, TIME_DATE | TIME_MINUTES),
         macd[currentIndex],
         signal[currentIndex],
         macd[previousIndex],
         signal[previousIndex],
         hasLong ? "true" : "false"
      );
   }

   if(bullishCross && !hasLong)
   {
      if(!trade.Buy(LotSize, _Symbol, 0.0, 0.0, 0.0, "Manual MACD long entry"))
      {
         PrintTradeFailure("Buy");
      }
      else if(PrintDebug)
      {
         PrintFormat("Opened long %.2f lots on %s", LotSize, _Symbol);
      }
   }
   else if(bearishCross && hasLong)
   {
      CloseManagedLongPositions();
   }
}

int OnInit()
{
   if(FastPeriod <= 0)
   {
      Print("Invalid FastPeriod. It must be greater than zero.");
      return INIT_FAILED;
   }

   if(SlowPeriod <= FastPeriod)
   {
      Print("Invalid SlowPeriod. It must be greater than FastPeriod.");
      return INIT_FAILED;
   }

   if(SignalPeriod <= 0)
   {
      Print("Invalid SignalPeriod. It must be greater than zero.");
      return INIT_FAILED;
   }

   if(LotSize <= 0.0)
   {
      Print("Invalid LotSize. It must be greater than zero.");
      return INIT_FAILED;
   }

   trade.SetExpertMagicNumber((ulong)MagicNumber);
   trade.SetDeviationInPoints(SlippagePoints);

   PrintFormat(
      "Manual MACD crossover initialized. symbol=%s timeframe=H1 fast=%d slow=%d signal=%d lot=%.2f magic=%d slippage_points=%d",
      _Symbol,
      FastPeriod,
      SlowPeriod,
      SignalPeriod,
      LotSize,
      MagicNumber,
      SlippagePoints
   );

   return INIT_SUCCEEDED;
}

void OnTick()
{
   const datetime currentBarTime = iTime(_Symbol, PERIOD_H1, 0);
   if(currentBarTime <= 0)
      return;

   if(lastBarTime == 0)
   {
      lastBarTime = currentBarTime;
      return;
   }

   if(currentBarTime == lastBarTime)
      return;

   lastBarTime = currentBarTime;
   EvaluateClosedBars();
}
