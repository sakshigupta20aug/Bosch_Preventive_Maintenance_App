select * from bosch_data;

---------------------------------------------------------
-- BOSCH Preventive Maintenance Project
-- SQL Analytics Queries

-- NOTE:
-- This analysis is based on a SAMPLE dataset (~50,000 rows)
-- created from the original Bosch dataset for demonstration
-- purposes. As a result, exact failure rates, averages, and
-- percentages may not reflect the full dataset.
--
-- Objective:
-- To demonstrate SQL-based descriptive and diagnostic analytics

---------------------------------------------------------
/*
Class Distribution (Pass vs Fail) → Show how many products pass vs fail QC.

Cycle Time Summary → Avg, min, max cycle time across units.

Pass vs Fail Comparison → Differences in num_mean, num_median, cycle_time.

Numeric Feature Summary → Statistical summary for num_mean.

Failure Rate by Cycle Time Buckets → Trend of failure vs production cycle time.

Missing Value Check → Ensure key engineered features are not null.

Top 10 Records → Sample inspection data table.

Failure Count per 1000 Units → Failure density metric for planners.
*/

---------------------------------------------------------
-- 1. Class Distribution (Pass vs Fail)
---------------------------------------------------------
SELECT 
    target, 
    COUNT(*) AS record_count,
    CAST(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER() AS DECIMAL(5,2)) AS percentage
FROM bosch_data
GROUP BY target;


---------------------------------------------------------
	-- 2. Cycle Time Summary - Average, Min, Max Cycle Time
	---------------------------------------------------------
	SELECT 
		AVG(cycle_time) AS avg_cycle_time,
		MIN(cycle_time) AS min_cycle_time,
		MAX(cycle_time) AS max_cycle_time
	FROM bosch_data;


---------------------------------------------------------
-- 3. Compare Numeric Feature Averages (Pass vs Fail)
---------------------------------------------------------
SELECT 
    target,
    AVG(num_mean) AS avg_num_mean,
    AVG(num_median) AS avg_num_median,
    AVG(cycle_time) AS avg_cycle_time
FROM bosch_data
GROUP BY target;


---------------------------------------------------------
-- 4. Numeric Feature Summary (example: num_mean)
---------------------------------------------------------
SELECT 
    AVG(num_mean) AS avg_num_mean,
    STDEV(num_mean) AS stddev_num_mean,
    MIN(num_mean) AS min_num_mean,
    MAX(num_mean) AS max_num_mean
FROM bosch_data;


---------------------------------------------------------
-- 5. Failure Rate by Cycle Time Bucket
---------------------------------------------------------
SELECT 
    CASE 
        WHEN cycle_time < 500 THEN '<500'
        WHEN cycle_time BETWEEN 500 AND 1000 THEN '500-1000'
        WHEN cycle_time BETWEEN 1000 AND 2000 THEN '1000-2000'
        ELSE '>2000'
    END AS cycle_time_bucket,
    COUNT(*) AS total_records,
    SUM(target) AS failed_count,
    CAST(SUM(target) * 100.0 / COUNT(*) AS DECIMAL(5,2)) AS failure_rate_percent
FROM bosch_data
GROUP BY 
    CASE 
        WHEN cycle_time < 500 THEN '<500'
        WHEN cycle_time BETWEEN 500 AND 1000 THEN '500-1000'
        WHEN cycle_time BETWEEN 1000 AND 2000 THEN '1000-2000'
        ELSE '>2000'
    END
ORDER BY cycle_time_bucket;


---------------------------------------------------------
-- 6. Missing Value Check (for key columns)
---------------------------------------------------------
SELECT 
    COUNT(*) AS total_records,
    SUM(CASE WHEN cycle_time IS NULL THEN 1 ELSE 0 END) AS missing_cycle_time,
    SUM(CASE WHEN num_mean IS NULL THEN 1 ELSE 0 END) AS missing_num_mean
FROM bosch_data;


---------------------------------------------------------
-- 7. Top 10 Records (for inspection / Power BI sample table)
---------------------------------------------------------
SELECT TOP 10 * 
FROM bosch_data;


---------------------------------------------------------
-- 8. Failure Count per 1000 Units
---------------------------------------------------------
SELECT 
    (COUNT(*) / 1000) AS units_per_thousand,
    SUM(target) AS failed_units
FROM bosch_data;
