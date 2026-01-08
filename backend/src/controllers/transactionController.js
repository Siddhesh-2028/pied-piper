// src/controllers/transactionController.js
import prisma from '../lib/prisma.js';

// 1. Get All Transactions (with Filters)
export const getTransactions = async (req, res) => {
  try {
    const { page = 1, limit = 20, category } = req.query;
    const skip = (page - 1) * limit;

    const where = {
      userId: req.userId, // Secure: only fetch OWN data
      ...(category && { category }), // Optional filter
    };

    // Parallel fetch: Data + Count (for pagination)
    const [transactions, total] = await prisma.$transaction([
      prisma.transaction.findMany({
        where,
        skip: parseInt(skip),
        take: parseInt(limit),
        orderBy: { date: 'desc' }, // Newest first
        include: { splits: true }  // Show who owes you on this transaction
      }),
      prisma.transaction.count({ where })
    ]);

    res.json({
      transactions,
      pagination: {
        total,
        page: parseInt(page),
        pages: Math.ceil(total / limit)
      }
    });
  } catch (error) {
    console.error("Get Transactions Error:", error);
    res.status(500).json({ error: "Server Error" });
  }
};

// 2. Get Dashboard Stats (Total Spent, Recent Activity, Monthly Chart)
export const getDashboardStats = async (req, res) => {
  try {
    const { month, year } = req.query;
    const now = new Date();
    
    // Use provided month/year or default to current
    const currentYear = year ? parseInt(year) : now.getFullYear();
    const currentMonth = month ? parseInt(month) - 1 : now.getMonth(); // 0-indexed in JS Date

    const startOfMonth = new Date(currentYear, currentMonth, 1);
    const endOfMonth = new Date(currentYear, currentMonth + 1, 0, 23, 59, 59, 999);

    const startOfPrevMonth = new Date(currentYear, currentMonth - 1, 1);
    const endOfPrevMonth = new Date(currentYear, currentMonth, 0, 23, 59, 59, 999);

    // 1. Total Spent This Month
    const currentMonthAgg = await prisma.transaction.aggregate({
      _sum: { amount: true },
      where: {
        userId: req.userId,
        date: {
          gte: startOfMonth,
          lte: endOfMonth
        }
      }
    });

    // 2. Total Spent Previous Month (For Trend)
    const prevMonthAgg = await prisma.transaction.aggregate({
      _sum: { amount: true },
      where: {
        userId: req.userId,
        date: {
          gte: startOfPrevMonth,
          lte: endOfPrevMonth
        }
      }
    });

    const currentTotal = currentMonthAgg._sum.amount ? parseFloat(currentMonthAgg._sum.amount) : 0;
    const prevTotal = prevMonthAgg._sum.amount ? parseFloat(prevMonthAgg._sum.amount) : 0;

    // Calculate Trend
    let trendValue = 0;
    let isIncrease = false;
    if (prevTotal > 0) {
      trendValue = ((currentTotal - prevTotal) / prevTotal) * 100;
      isIncrease = trendValue > 0;
    }

    // 3. Category Breakdown
    const categoryStats = await prisma.transaction.groupBy({
      by: ['category'],
      _sum: { amount: true },
      where: {
        userId: req.userId,
        date: {
          gte: startOfMonth,
          lte: endOfMonth
        }
      },
    });

    // 4. Daily Stats for Chart
    // Prisma doesn't support grouping by date part easily in all DBs without raw query.
    // Fetching all transactions for the month implies lighter load than raw query sometimes, 
    // but raw query is better for aggregation. Let's use raw query or js grouping.
    // Since it's a personal expense tracker, volume per month is likely low (<1000). JS grouping is fine.
    
    const transactions = await prisma.transaction.findMany({
      where: {
        userId: req.userId,
        date: {
          gte: startOfMonth,
          lte: endOfMonth
        }
      },
      select: {
        date: true,
        amount: true
      }
    });

    // Bucket into days or weeks ( ExpenseDataCard MOCK_DATA has ~7 points, likely weekly or simplified daily)
    // Let's create an array of values for the chart. 
    // If the mock data has ~7 points, maybe we can aggregate into, say, every 3-4 days or just return daily sums.
    // However, the card might expect specific number of points?
    // The previous MOCK_DATA had 7 points. Let's try to give daily data or weekly.
    // Let's stick to daily data for better granularity if the chart supports it, or aggregate to 4 weeks.
    // The mock data keys were 'Nov 2023' etc.
    // Let's return the daily series and let frontend handle visualization.
    
    // Initialize day map
    const daysInMonth = endOfMonth.getDate();
    const dailyData = new Array(daysInMonth).fill(0);

    transactions.forEach(t => {
      const day = new Date(t.date).getDate(); // 1-31
      if (day >= 1 && day <= daysInMonth) {
        dailyData[day - 1] += parseFloat(t.amount);
      }
    });

    // To match the mock data style (array of numbers), we can just return dailyData.
    // Or if we want to compress it to 7 points (like weekly segments), we can do that too.
    // 30 days / 7 ≈ 4 days per point.
    // Let's just return daily stats and let's update frontend to maybe use "Total per week" or just "Daily trend".
    // For now, returning full daily array might be most flexible.
    
    res.json({
      totalSpent: currentTotal,
      prevTotalSpent: prevTotal,
      trend: {
        value: Math.abs(trendValue).toFixed(1),
        isIncrease: isIncrease,
        isPositive: !isIncrease // Assuming spending less (decrease) is positive for expenses
      },
      categoryBreakdown: categoryStats.map(stat => ({
        category: stat.category,
        amount: parseFloat(stat._sum.amount || 0)
      })),
      dailyStats: dailyData
    });
  } catch (error) {
    console.error("Stats Error:", error);
    res.status(500).json({ error: "Server Error" });
  }
};

// 3. Manual Transaction Creation
export const createTransaction = async (req, res) => {
  try {
    const { amount, merchant, date, category, description } = req.body;

    const transaction = await prisma.transaction.create({
      data: {
        userId: req.userId,
        amount: parseFloat(amount),
        merchant: merchant || "Unknown",
        date: new Date(date), // Expect ISO string
        category: category || "Uncategorized",
        description,
        source: "MANUAL",
        currency: "INR"
      }
    });

    res.status(201).json(transaction);
  } catch (error) {
    console.error("Create Transaction Error:", error);
    res.status(500).json({ error: "Server Error" });
  }
};

// 4. Update Transaction (Categorization Fixes)
export const updateTransaction = async (req, res) => {
  try {
    const { id } = req.params;
    const updates = req.body; // e.g., { category: "Food", merchant: "Zomato" }

    // Ensure user owns the transaction
    const existing = await prisma.transaction.findUnique({ where: { id } });
    if (!existing || existing.userId !== req.userId) {
      return res.status(403).json({ error: "Unauthorized" });
    }

    const transaction = await prisma.transaction.update({
      where: { id },
      data: updates
    });

    res.json(transaction);
  } catch (error) {
    console.error("Update Transaction Error:", error);
    res.status(500).json({ error: "Server Error" });
  }
};